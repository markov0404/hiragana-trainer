#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Hiragana Trainer - Aplicación para aprender y practicar hiragana
Versión mejorada con múltiples funcionalidades avanzadas
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import random
import json
import os
import time
import csv
import logging
from datetime import datetime, timedelta
import threading
import webbrowser
from collections import defaultdict

# Constantes
APP_VERSION = "2.0.0"
DATA_FILE = "hiragana_data.json"
SESSION_HISTORY_FILE = "session_history.json"
LOG_FILE = "hiragana_trainer.log"

# Configuración de logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)
logger = logging.getLogger('HiraganaTrainer')

# Clases de excepciones personalizadas
class HiraganaTrainerError(Exception):
    """Clase base para excepciones del entrenador de hiragana"""
    pass

class DataLoadError(HiraganaTrainerError):
    """Error al cargar datos"""
    pass

class QuizGenerationError(HiraganaTrainerError):
    """Error al generar preguntas de quiz"""
    pass

# Clase para el sistema de repetición espaciada (SRS)
class SRSScheduler:
    """Sistema de Repetición Espaciada para optimizar el aprendizaje"""
    
    def __init__(self):
        # Intervalos en días para las repeticiones (similar a Anki)
        self.intervals = [1, 3, 7, 14, 30, 90, 180]
    
    def calculate_next_review(self, char_data, correct):
        """Calcula la próxima fecha de repaso basada en el rendimiento"""
        if "srs_level" not in char_data:
            char_data["srs_level"] = 0
            
        if correct:
            # Avanzar al siguiente nivel si la respuesta es correcta
            char_data["srs_level"] = min(char_data["srs_level"] + 1, len(self.intervals) - 1)
        else:
            # Retroceder al nivel inicial si es incorrecta
            char_data["srs_level"] = 0
            
        days = self.intervals[char_data["srs_level"]]
        next_review = datetime.now() + timedelta(days=days)
        char_data["next_review"] = next_review.isoformat()
        
        return next_review
    
    def get_due_cards(self, study_history):
        """Retorna los caracteres que deben repasarse hoy"""
        today = datetime.now()
        due_chars = []
        
        for char, data in study_history.items():
            if "next_review" not in data:
                due_chars.append(char)
            else:
                next_review = datetime.fromisoformat(data["next_review"])
                if next_review <= today:
                    due_chars.append(char)
                    
        return due_chars

# Clase para algoritmo de aprendizaje adaptativo
class AdaptiveLearning:
    """Algoritmo para priorizar caracteres según dificultad y otros factores"""
    
    def __init__(self):
        self.difficulty_weight = 2.0  # Peso para caracteres difíciles
        self.recency_weight = 1.5     # Peso para caracteres no vistos recientemente
        self.frequency_weight = 1.0   # Peso para frecuencia de uso en japonés
    
    def calculate_priority(self, character, history):
        """Calcula la prioridad de un carácter para ser mostrado"""
        # Si no hay historial, alta prioridad
        if character not in history:
            return 10.0
            
        char_data = history[character]
        
        # Factor de dificultad - más errores = mayor prioridad
        if char_data.get("times_shown", 0) > 0:
            error_rate = char_data.get("incorrect", 0) / char_data["times_shown"]
            difficulty_factor = error_rate * self.difficulty_weight
        else:
            difficulty_factor = 0
            
        # Factor de recencia - más tiempo sin ver = mayor prioridad
        if "last_shown" in char_data:
            last_shown = datetime.fromisoformat(char_data["last_shown"])
            days_since = (datetime.now() - last_shown).days
            recency_factor = min(days_since / 7, 1.0) * self.recency_weight
        else:
            recency_factor = self.recency_weight
            
        return difficulty_factor + recency_factor
    
    def sort_by_priority(self, characters, history):
        """Ordena caracteres por prioridad para optimizar el aprendizaje"""
        char_priorities = [(char, self.calculate_priority(char[0], history)) 
                          for char in characters]
        sorted_chars = [char for char, _ in sorted(char_priorities, 
                                                 key=lambda x: x[1], reverse=True)]
        return sorted_chars

# Clase de logros para gamificación
class Achievement:
    """Sistema de logros para motivar el aprendizaje"""
    
    def __init__(self, id, title, description, condition_func, icon=None, reward=None):
        self.id = id
        self.title = title 
        self.description = description
        self.condition_func = condition_func
        self.unlocked = False
        self.unlock_date = None
        self.icon = icon
        self.reward = reward
    
    def check_condition(self, user_data):
        """Verifica si se cumple la condición para desbloquear el logro"""
        if not self.unlocked and self.condition_func(user_data):
            self.unlocked = True
            self.unlock_date = datetime.now().isoformat()
            return True
        return False
    
    def to_dict(self):
        """Convierte el logro a diccionario para guardar"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "unlocked": self.unlocked,
            "unlock_date": self.unlock_date
        }
    
    @classmethod
    def from_dict(cls, data, condition_func):
        """Crea un objeto Achievement desde un diccionario"""
        achievement = cls(
            data["id"], 
            data["title"], 
            data["description"],
            condition_func
        )
        achievement.unlocked = data.get("unlocked", False)
        achievement.unlock_date = data.get("unlock_date")
        return achievement

# Sistema de logros predefinidos
def create_achievements():
    """Crea la lista de logros disponibles"""
    return [
        Achievement(
            'first_session', 
            'Primer Paso', 
            'Completa tu primera sesión de estudio',
            lambda data: data.get('sessions_completed', 0) >= 1
        ),
        Achievement(
            'hiragana_master', 
            'Maestro de Hiragana', 
            'Consigue una precisión del 90% en todos los caracteres básicos',
            lambda data: check_category_mastery(data, 'Básicos', 0.9)
        ),
        Achievement(
            'dakuten_expert', 
            'Experto en Dakuten', 
            'Consigue una precisión del 90% en caracteres con dakuten',
            lambda data: check_category_mastery(data, 'Con dakuten', 0.9)
        ),
        Achievement(
            'yoon_pro', 
            'Profesional de Yōon', 
            'Consigue una precisión del 90% en caracteres combinados',
            lambda data: check_category_mastery(data, 'Combinados (yōon)', 0.9)
        ),
        Achievement(
            'perfect_quiz', 
            'Perfeccionista', 
            'Obtén 100% en un quiz de al menos 20 preguntas',
            lambda data: data.get('perfect_quiz_count', 0) >= 1
        ),
        Achievement(
            'streak_warrior', 
            'Guerrero de Racha', 
            'Alcanza una racha de 50 respuestas correctas seguidas',
            lambda data: data.get('max_streak', 0) >= 50
        ),
        Achievement(
            'study_habit', 
            'Hábito de Estudio', 
            'Estudia durante 7 días consecutivos',
            lambda data: check_consecutive_days(data, 7)
        ),
        Achievement(
            'hiragana_complete', 
            'Hiragana Completo', 
            'Estudia todos los caracteres hiragana al menos una vez',
            lambda data: check_all_chars_studied(data)
        ),
        Achievement(
            'dedication', 
            'Dedicación', 
            'Acumula 5 horas de estudio',
            lambda data: data.get('total_study_time', 0) >= 300
        )
    ]

# Funciones auxiliares para verificar logros
def check_category_mastery(data, category, threshold):
    """Verifica si se ha dominado una categoría"""
    if 'category_stats' not in data:
        return False
    
    if category not in data['category_stats']:
        return False
    
    stats = data['category_stats'][category]
    return stats.get('accuracy', 0) >= threshold

def check_consecutive_days(data, days_required):
    """Verifica si se ha estudiado durante días consecutivos"""
    if 'study_dates' not in data or len(data['study_dates']) < days_required:
        return False
    
    # Convertir fechas de texto a objetos datetime
    study_dates = [datetime.fromisoformat(date) for date in data['study_dates']]
    study_dates.sort()
    
    # Verificar secuencia consecutiva
    max_consecutive = 1
    current_consecutive = 1
    
    for i in range(1, len(study_dates)):
        date_diff = (study_dates[i].date() - study_dates[i-1].date()).days
        
        if date_diff == 1:
            current_consecutive += 1
            max_consecutive = max(max_consecutive, current_consecutive)
        elif date_diff > 1:
            current_consecutive = 1
    
    return max_consecutive >= days_required

def check_all_chars_studied(data):
    """Verifica si se han estudiado todos los caracteres hiragana"""
    if 'all_hiragana' not in data or 'studied_chars' not in data:
        return False
    
    all_hiragana = set(data['all_hiragana'])
    studied_chars = set(data['studied_chars'])
    
    return all_hiragana.issubset(studied_chars)

# Clase principal de la aplicación
class HiraganaTrainer:
    def __init__(self, root):
        """Inicializar la aplicación de entrenamiento de hiragana"""
        self.root = root
        self.root.title(f"Entrenador de Hiragana Avanzado v{APP_VERSION}")
        self.root.geometry("1000x650")
        self.root.minsize(900, 600)
        
        # Configurar el icono si existe
        icon_path = "assets/icon.ico"
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)
        
        # Variables de control de modo
        self.in_difficult_mode = False  # Para controlar si estamos en modo difíciles
        self.random_mode = tk.BooleanVar(value=True)
        self.show_romanji = False
        self.is_running = False
        self.current_index = 0
        self.hiragana_list = []
        self.practice_list = []
        self.srs_mode = tk.BooleanVar(value=False)  # Sistema de repetición espaciada
        
        # Variables de estadísticas
        self.delay_var = tk.DoubleVar(value=3.0)
        self.time_display = tk.StringVar(value="3.0")
        self.progress_var = tk.StringVar(value="0/0")
        self.score = 0
        self.total_attempts = 0
        self.streak = 0
        self.max_streak = 0
        self.session_chars_shown = 0
        self.difficult_characters = set()
        self.study_mode = tk.StringVar(value="flash")  # flash, quiz, inverse
        self.study_history = {}  # Para seguimiento del aprendizaje
        self.last_answer_correct = False
        self.session_start_time = datetime.now()
        
        # Inicializar componentes avanzados
        self.srs_scheduler = SRSScheduler()
        self.adaptive_learning = AdaptiveLearning()
        self.achievements = create_achievements()
        self.achievement_data = {
            'sessions_completed': 0,
            'perfect_quiz_count': 0,
            'max_streak': 0,
            'study_dates': [],
            'total_study_time': 0,  # en minutos
            'category_stats': {},
            'all_hiragana': [],
            'studied_chars': []
        }
        
        # Variables para datos de hiragana
        self.import_hiragana_data()
        
        # Variables para las categorías
        self.category_vars = {}
        for category in self.hiragana_categories:
            self.category_vars[category] = tk.BooleanVar(value=True)
        
        # Variables para el modo quiz
        self.quiz_mode = tk.StringVar(value="write")  # write, multiple
        self.quiz_direction = tk.StringVar(value="hira_to_rom")  # hira_to_rom, rom_to_hira
        self.quiz_difficult_only = tk.BooleanVar(value=False)
        self.correct_answers_count = {}  # Para seguimiento de respuestas correctas consecutivas
        
        # Inicializar widgets críticos como None para evitar errores
        self.quiz_entry = None
        self.submit_btn = None
        self.next_btn = None
        self.option_buttons = []
        self.correct_option_index = 0
        self.timer_id = None
        self.session_timer_id = None
        
        # Configuración de estilo mejorado
        self.setup_styles()
        
        # Crear la interfaz de usuario
        self.setup_ui()
        
        # Actualizar la lista de hiragana seleccionados
        self.update_hiragana_list()
        
        # Cargar datos guardados
        self.load_data()
        
        # Configurar atajos de teclado
        self.setup_keyboard_shortcuts()
        
        # Mostrar notificación de bienvenida
        self.show_welcome_message()
    
    def import_hiragana_data(self):
        """Importa los datos de hiragana y ejemplos desde archivos o define los predeterminados"""
        # Intentar cargar desde archivos JSON si existen
        data_loaded = False
        
        try:
            hiragana_file = "data/hiragana.json"
            examples_file = "data/examples.json"
            
            if os.path.exists(hiragana_file) and os.path.exists(examples_file):
                with open(hiragana_file, 'r', encoding='utf-8') as f:
                    self.hiragana_categories = json.load(f)
                with open(examples_file, 'r', encoding='utf-8') as f:
                    self.example_words = json.load(f)
                data_loaded = True
        except Exception as e:
            logger.error(f"Error al cargar archivos de datos: {e}")
        
        # Si no se pudieron cargar, usar los datos predeterminados
        if not data_loaded:
            # Hiragana categorizado
            self.hiragana_categories = {
                "Básicos": [
                    ("あ", "a"), ("い", "i"), ("う", "u"), ("え", "e"), ("お", "o"),
                    ("か", "ka"), ("き", "ki"), ("く", "ku"), ("け", "ke"), ("こ", "ko"),
                    ("さ", "sa"), ("し", "shi"), ("す", "su"), ("せ", "se"), ("そ", "so"),
                    ("た", "ta"), ("ち", "chi"), ("つ", "tsu"), ("て", "te"), ("と", "to"),
                    ("な", "na"), ("に", "ni"), ("ぬ", "nu"), ("ね", "ne"), ("の", "no"),
                    ("は", "ha"), ("ひ", "hi"), ("ふ", "fu"), ("へ", "he"), ("ほ", "ho"),
                    ("ま", "ma"), ("み", "mi"), ("む", "mu"), ("め", "me"), ("も", "mo"),
                    ("や", "ya"), ("ゆ", "yu"), ("よ", "yo"),
                    ("ら", "ra"), ("り", "ri"), ("る", "ru"), ("れ", "re"), ("ろ", "ro"),
                    ("わ", "wa"), ("を", "wo"), ("ん", "n")
                ],
                "Con dakuten": [
                    ("が", "ga"), ("ぎ", "gi"), ("ぐ", "gu"), ("げ", "ge"), ("ご", "go"),
                    ("ざ", "za"), ("じ", "ji"), ("ず", "zu"), ("ぜ", "ze"), ("ぞ", "zo"),
                    ("だ", "da"), ("ぢ", "ji"), ("づ", "zu"), ("で", "de"), ("ど", "do"),
                    ("ば", "ba"), ("び", "bi"), ("ぶ", "bu"), ("べ", "be"), ("ぼ", "bo"),
                    ("ぱ", "pa"), ("ぴ", "pi"), ("ぷ", "pu"), ("ぺ", "pe"), ("ぽ", "po")
                ],
                "Combinados (yōon)": [
                    ("きゃ", "kya"), ("きゅ", "kyu"), ("きょ", "kyo"),
                    ("しゃ", "sha"), ("しゅ", "shu"), ("しょ", "sho"),
                    ("ちゃ", "cha"), ("ちゅ", "chu"), ("ちょ", "cho"),
                    ("にゃ", "nya"), ("にゅ", "nyu"), ("にょ", "nyo"),
                    ("ひゃ", "hya"), ("ひゅ", "hyu"), ("ひょ", "hyo"),
                    ("みゃ", "mya"), ("みゅ", "myu"), ("みょ", "myo"),
                    ("りゃ", "rya"), ("りゅ", "ryu"), ("りょ", "ryo"),
                    ("ぎゃ", "gya"), ("ぎゅ", "gyu"), ("ぎょ", "gyo"),
                    ("じゃ", "ja"), ("じゅ", "ju"), ("じょ", "jo"),
                    ("びゃ", "bya"), ("びゅ", "byu"), ("びょ", "byo"),
                    ("ぴゃ", "pya"), ("ぴゅ", "pyu"), ("ぴょ", "pyo")
                ]
            }
            
            # Palabras de ejemplo para cada hiragana (solo algunas como demostración)
            self.example_words = {
                # Básicos - Vowels
                "あ": ("あめ", "ame", "lluvia"),
                "い": ("いぬ", "inu", "perro"),
                "う": ("うみ", "umi", "mar"),
                "え": ("えき", "eki", "estación"),
                "お": ("おと", "oto", "sonido"),
                
                # Básicos - K-row
                "か": ("かばん", "kaban", "bolso"),
                "き": ("きって", "kitte", "sello postal"),
                "く": ("くつ", "kutsu", "zapatos"),
                "け": ("けいたい", "keitai", "teléfono móvil"),
                "こ": ("こども", "kodomo", "niño"),
                
                # Básicos - S-row
                "さ": ("さくら", "sakura", "cerezo"),
                "し": ("しんぶん", "shinbun", "periódico"),
                "す": ("すし", "sushi", "sushi"),
                "せ": ("せんせい", "sensei", "profesor"),
                "そ": ("そら", "sora", "cielo"),
                
                # Básicos - T-row
                "た": ("たべもの", "tabemono", "comida"),
                "ち": ("ちず", "chizu", "mapa"),
                "つ": ("つくえ", "tsukue", "escritorio"),
                "て": ("てがみ", "tegami", "carta"),
                "と": ("とけい", "tokei", "reloj"),
                
                # Básicos - N-row
                "な": ("なつ", "natsu", "verano"),
                "に": ("にく", "niku", "carne"),
                "ぬ": ("ぬま", "numa", "pantano"),
                "ね": ("ねこ", "neko", "gato"),
                "の": ("のみもの", "nomimono", "bebida"),
                
                # Básicos - H-row
                "は": ("はな", "hana", "flor"),
                "ひ": ("ひと", "hito", "persona"),
                "ふ": ("ふゆ", "fuyu", "invierno"),
                "へ": ("へや", "heya", "habitación"),
                "ほ": ("ほん", "hon", "libro"),
                
                # Básicos - M-row
                "ま": ("まど", "mado", "ventana"),
                "み": ("みず", "mizu", "agua"),
                "む": ("むし", "mushi", "insecto"),
                "め": ("めがね", "megane", "gafas"),
                "も": ("もり", "mori", "bosque"),
                
                # Básicos - Y-row
                "や": ("やま", "yama", "montaña"),
                "ゆ": ("ゆき", "yuki", "nieve"),
                "よ": ("よる", "yoru", "noche"),
                
                # Básicos - R-row
                "ら": ("らいねん", "rainen", "próximo año"),
                "り": ("りんご", "ringo", "manzana"),
                "る": ("るす", "rusu", "ausencia"),
                "れ": ("れいぞうこ", "reizouko", "refrigerador"),
                "ろ": ("ろうそく", "rousoku", "vela"),
                
                # Básicos - W-row and N
                "わ": ("わたし", "watashi", "yo"),
                "を": ("ほんをよむ", "hon wo yomu", "leer un libro"),
                "ん": ("でんわ", "denwa", "teléfono"),
                
                # Con dakuten - G-row
                "が": ("がっこう", "gakkou", "escuela"),
                "ぎ": ("ぎんこう", "ginkou", "banco"),
                "ぐ": ("ぐんて", "gunte", "guantes"),
                "げ": ("げんき", "genki", "energía"),
                "ご": ("ごはん", "gohan", "arroz"),
                
                # Con dakuten - Z-row
                "ざ": ("ざっし", "zasshi", "revista"),
                "じ": ("じかん", "jikan", "tiempo"),
                "ず": ("みずうみ", "mizuumi", "lago"),
                "ぜ": ("ぜんぶ", "zenbu", "todo"),
                "ぞ": ("ぞう", "zou", "elefante"),
                
                # Con dakuten - D-row
                "だ": ("だいがく", "daigaku", "universidad"),
                "ぢ": ("はなぢ", "hanaji", "sangrado nasal"),
                "づ": ("みづから", "mizukara", "por uno mismo"),
                "で": ("でんしゃ", "densha", "tren"),
                "ど": ("どあ", "doa", "puerta"),
                
                # Con dakuten - B-row
                "ば": ("ばす", "basu", "autobús"),
                "び": ("びょういん", "byouin", "hospital"),
                "ぶ": ("ぶたにく", "butaniku", "carne de cerdo"),
                "べ": ("べんきょう", "benkyou", "estudio"),
                "ぼ": ("ぼうし", "boushi", "sombrero"),
                
                # Con dakuten - P-row (handakuten)
                "ぱ": ("ぱん", "pan", "pan"),
                "ぴ": ("ぴかぴか", "pikapika", "brillante"),
                "ぷ": ("プール", "puuru", "piscina"),
                "ぺ": ("ペン", "pen", "bolígrafo"),
                "ぽ": ("ぽけっと", "poketto", "bolsillo"),
                
                # Combinados (yōon) - KY
                "きゃ": ("きゃく", "kyaku", "invitado"),
                "きゅ": ("きゅうり", "kyuuri", "pepino"),
                "きょ": ("きょうと", "kyouto", "Kioto"),
                
                # Combinados (yōon) - SH
                "しゃ": ("しゃしん", "shashin", "fotografía"),
                "しゅ": ("しゅみ", "shumi", "afición"),
                "しょ": ("しょうゆ", "shouyu", "salsa de soja"),
                
                # Combinados (yōon) - CH
                "ちゃ": ("おちゃ", "ocha", "té verde"),
                "ちゅ": ("ちゅうい", "chuui", "atención"),
                "ちょ": ("ちょうちょ", "choucho", "mariposa"),
                
                # Combinados (yōon) - NY
                "にゃ": ("にゃんこ", "nyanko", "gatito"),
                "にゅ": ("にゅうがく", "nyuugaku", "ingreso escolar"),
                "にょ": ("にょうぼう", "nyoubou", "esposa"),
                
                # Combinados (yōon) - HY
                "ひゃ": ("ひゃく", "hyaku", "cien"),
                "ひゅ": ("ひゅうが", "hyuuga", "Hyuga (nombre)"),
                "ひょ": ("ひょう", "hyou", "leopardo"),
                
                # Combinados (yōon) - MY
                "みゃ": ("みゃく", "myaku", "pulso"),
                "みゅ": ("みゅーじっく", "myuujikku", "música"),
                "みょ": ("みょうじ", "myouji", "apellido"),
                
                # Combinados (yōon) - RY
                "りゃ": ("りゃくご", "ryakugo", "abreviación"),
                "りゅ": ("りゅうがく", "ryuugaku", "estudiar en el extranjero"),
                "りょ": ("りょうり", "ryouri", "cocina"),
                
                # Combinados (yōon) - GY
                "ぎゃ": ("ぎゃくてん", "gyakuten", "revés, giro"),
                "ぎゅ": ("ぎゅうにく", "gyuuniku", "carne de vaca"),
                "ぎょ": ("ぎょうざ", "gyouza", "empanadilla china"),
                
                # Combinados (yōon) - J
                "じゃ": ("じゃがいも", "jagaimo", "patata"),
                "じゅ": ("じゅぎょう", "jugyou", "clase"),
                "じょ": ("じょうず", "jouzu", "habilidoso"),
                
                # Combinados (yōon) - BY
                "びゃ": ("びゃくや", "byakuya", "noche blanca"),
                "びゅ": ("びゅうびゅう", "byuubyuu", "silbido del viento"),
                "びょ": ("びょうき", "byouki", "enfermedad"),
                
                # Combinados (yōon) - PY
                "ぴゃ": ("ぴゃのぴゃの", "pyanopyano", "débilmente"),
                "ぴゅ": ("ぴゅあ", "pyua", "puro"),
                "ぴょ": ("ぴょんぴょん", "pyonpyon", "saltar repetidamente"),
            }
        
        # Recopilar todos los caracteres hiragana para logros y estadísticas
        all_hiragana = []
        for category in self.hiragana_categories.values():
            for hiragana, _ in category:
                all_hiragana.append(hiragana)
        
        self.achievement_data['all_hiragana'] = all_hiragana
    
    def setup_styles(self):
        """Configura los estilos visuales mejorados para la aplicación"""
        self.style = ttk.Style()
        
        # Intentar usar un tema moderno
        try:
            self.style.theme_use('clam')  # Alternativas: 'alt', 'default', 'classic'
        except tk.TclError:
            pass  # Si el tema no está disponible, usar el predeterminado
        
        # Colores principales
        bg_color = "#f0f0f5"
        fg_color = "#333333"
        accent_color = "#4a86e8"
        accent_dark = "#3a76d8"
        success_color = "#28a745"
        danger_color = "#dc3545"
        warning_color = "#ffc107"
        info_color = "#17a2b8"
        
        # Configuraciones generales
        self.style.configure("TFrame", background=bg_color)
        self.style.configure("TLabel", background=bg_color, foreground=fg_color)
        self.style.configure("TButton", 
                            padding=6, 
                            relief="flat",
                            background=accent_color,
                            foreground="white")
        self.style.map("TButton",
                      background=[('active', accent_dark), ('disabled', '#cccccc')],
                      foreground=[('disabled', '#999999')])
        
        self.style.configure("TCheckbutton", background=bg_color)
        self.style.configure("TRadiobutton", background=bg_color)
        self.style.configure("TNotebook", background=bg_color)
        self.style.configure("TNotebook.Tab", 
                            padding=[12, 6], 
                            background=bg_color,
                            foreground=fg_color)
        self.style.map("TNotebook.Tab",
                      background=[('selected', accent_color)],
                      foreground=[('selected', 'white')])
        
        # Estilos para botones específicos
        self.style.configure("Primary.TButton", 
                            background=accent_color,
                            foreground="white",
                            font=("Arial", 10, "bold"))
        self.style.configure("Success.TButton", 
                            background=success_color,
                            foreground="white")
        self.style.configure("Danger.TButton", 
                            background=danger_color,
                            foreground="white")
        self.style.configure("Warning.TButton", 
                            background=warning_color,
                            foreground=fg_color)
        self.style.configure("Info.TButton", 
                            background=info_color,
                            foreground="white")
        
        # Estilos para el sistema de quiz
        self.style.configure("Correct.TButton", 
                            background=success_color,
                            foreground="white")
        self.style.configure("Incorrect.TButton", 
                            background=danger_color,
                            foreground="white")
        
        # Estilos para etiquetas de caracteres difíciles
        self.style.configure("DifficultTag.TFrame", 
                            background=warning_color,
                            relief="raised",
                            borderwidth=1)
        self.style.configure("DifficultTag.TLabel", 
                            background=warning_color,
                            foreground=fg_color,
                            font=("Arial", 10, "bold"),
                            padding=3)
    
    def setup_keyboard_shortcuts(self):
        """Configura atajos de teclado para acciones comunes"""
        # Atajos globales
        self.root.bind("<F1>", lambda e: self.show_help())
        self.root.bind("<Control-q>", lambda e: self.on_closing())
        self.root.bind("<Control-s>", lambda e: self.save_data())
        
        # Atajos para modo tarjetas flash
        self.root.bind("<space>", lambda e: self.toggle_practice())
        self.root.bind("<Right>", lambda e: self.advance_card())
        self.root.bind("<Left>", lambda e: self.previous_card())
        self.root.bind("d", lambda e: self.mark_difficult(True))
        self.root.bind("f", lambda e: self.mark_difficult(False))
        self.root.bind("e", lambda e: self.show_example())
        
        # Atajos para modo quiz
        self.root.bind("<Return>", lambda e: self.check_answer())
        self.root.bind("<Control-n>", lambda e: self.next_quiz_question())
    
    def show_welcome_message(self):
        """Muestra un mensaje de bienvenida al iniciar la aplicación"""
        # Solo mostrar mensaje de bienvenida en la primera ejecución
        if not os.path.exists(DATA_FILE):
            welcome_text = (
                "¡Bienvenido a Hiragana Trainer 2.0!\n\n"
                "Esta aplicación te ayudará a aprender y practicar los caracteres hiragana "
                "japoneses de forma efectiva y personalizada.\n\n"
                "Para comenzar, selecciona las categorías que quieres practicar y "
                "haz clic en 'Iniciar'.\n\n"
                "Puedes usar la barra espaciadora para alternar entre hiragana y romanji, "
                "y las teclas de flecha para navegar entre caracteres."
            )
            
            messagebox.showinfo("¡Bienvenido!", welcome_text)
    
    def setup_ui(self):
        """Configura la interfaz de usuario principal"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Barra de menú
        self.create_menu()
        
        # Notebook (pestañas)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Crear pestañas
        self.create_flash_tab()
        self.create_quiz_tab()
        self.create_stats_tab()
        self.create_settings_tab()
        
        # Barra de estado
        self.create_status_bar(main_frame)
        
        # Primero actualizar la interfaz del quiz y LUEGO cargar una pregunta
        self.update_quiz_interface()
        self.load_quiz_question()
        
        # Configurar eventos de cambio de pestaña
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)
    
    def on_tab_change(self, event=None):
        """Maneja los eventos de cambio entre pestañas"""
        try:
            # Obtener índice de la pestaña actual
            current_tab = self.notebook.index(self.notebook.select())
            
            # Si cambiamos a la pestaña de estadísticas, actualizarlas
            if current_tab == 2:  # La tercera pestaña (índice 2) es Estadísticas
                self.update_stats_display()
                
            # Si cambiamos a la pestaña de quiz, actualizar interfaz
            elif current_tab == 1:  # La segunda pestaña (índice 1) es Quiz
                # Asegurarse de que la interfaz esté actualizada
                if hasattr(self, 'update_quiz_interface'):
                    self.update_quiz_interface()
                    
            # Actualizar la barra de estado
            tab_names = ["Tarjetas Flash", "Modo Quiz", "Estadísticas", "Configuración"]
            if 0 <= current_tab < len(tab_names):
                self.status_text.set(f"Pestaña actual: {tab_names[current_tab]}")
                
        except Exception as e:
            logger.error(f"Error al cambiar de pestaña: {str(e)}")

    def create_menu(self):
        """Crea la barra de menú de la aplicación"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menú Archivo
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=file_menu)
        file_menu.add_command(label="Guardar progreso", command=self.save_data, 
                             accelerator="Ctrl+S")
        file_menu.add_command(label="Cargar progreso", command=self.load_data)
        file_menu.add_separator()
        file_menu.add_command(label="Exportar estadísticas", command=self.export_statistics)
        file_menu.add_command(label="Importar datos", command=self.import_data)
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self.on_closing, 
                             accelerator="Ctrl+Q")
        
        # Menú Estudio
        study_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Estudio", menu=study_menu)
        study_menu.add_command(label="Iniciar/Detener práctica", 
                              command=self.toggle_practice, accelerator="Espacio")
        study_menu.add_command(label="Siguiente tarjeta", 
                              command=self.advance_card, accelerator="→")
        study_menu.add_command(label="Tarjeta anterior", 
                              command=self.previous_card, accelerator="←")
        study_menu.add_separator()
        study_menu.add_command(label="Modo aleatorio", 
                              command=lambda: self.toggle_order(True))
        study_menu.add_command(label="Modo secuencial", 
                              command=lambda: self.toggle_order(False))
        study_menu.add_separator()
        study_menu.add_command(label="Marcar como difícil", 
                              command=lambda: self.mark_difficult(True), accelerator="D")
        study_menu.add_command(label="Marcar como fácil", 
                              command=lambda: self.mark_difficult(False), accelerator="F")
        study_menu.add_command(label="Mostrar ejemplo", 
                              command=self.show_example, accelerator="E")
        
        # Menú Herramientas
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Herramientas", menu=tools_menu)
        tools_menu.add_command(label="Generador de sesión inteligente", 
                              command=self.generate_smart_session)
        tools_menu.add_command(label="Planificador de estudio", 
                              command=self.setup_study_plan)
        tools_menu.add_command(label="Ver logros", command=self.show_achievements)
        tools_menu.add_separator()
        tools_menu.add_command(label="Reiniciar estadísticas", 
                              command=self.reset_all_stats)
        tools_menu.add_command(label="Limpiar caracteres difíciles", 
                              command=self.clear_difficult_chars)
        
        # Menú Ayuda
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ayuda", menu=help_menu)
        help_menu.add_command(label="Guía de uso", command=self.show_help, 
                             accelerator="F1")
        help_menu.add_command(label="Consejos de estudio", command=self.show_study_tips)
        help_menu.add_command(label="Acerca de", command=self.show_about)
    
    def create_flash_tab(self):
        """Crea la pestaña de tarjetas flash"""
        flash_tab = ttk.Frame(self.notebook)
        self.notebook.add(flash_tab, text="Tarjetas Flash")
        
        # Dividir en panel izquierdo y derecho
        flash_paned = ttk.PanedWindow(flash_tab, orient=tk.HORIZONTAL)
        flash_paned.pack(fill=tk.BOTH, expand=True)
        
        # Panel izquierdo (configuraciones)
        left_frame = ttk.Frame(flash_paned, padding=10)
        flash_paned.add(left_frame, weight=1)
        
        # Sección de categorías
        ttk.Label(left_frame, text="Categorías a practicar:", 
                 font=('Arial', 11, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        
        # Frame con scroll para categorías (por si hay muchas)
        categories_canvas = tk.Canvas(left_frame, highlightthickness=0, 
                                     background=self.style.lookup("TFrame", "background"))
        categories_canvas.pack(fill=tk.X, anchor=tk.W, padx=0, pady=0)
        
        categories_frame = ttk.Frame(categories_canvas)
        categories_scroll = ttk.Scrollbar(left_frame, orient="vertical", 
                                        command=categories_canvas.yview)
        categories_canvas.configure(yscrollcommand=categories_scroll.set)
        
        categories_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        categories_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        categories_canvas.create_window((0, 0), window=categories_frame, anchor='nw')
        
        for category, var in self.category_vars.items():
            ttk.Checkbutton(
                categories_frame, 
                text=category, 
                variable=var, 
                command=self.update_hiragana_list
            ).pack(anchor=tk.W, padx=5)
        
        categories_frame.bind("<Configure>", 
                             lambda e: categories_canvas.configure(
                                 scrollregion=categories_canvas.bbox("all"),
                                 width=200))
        
        # Sección de caracteres difíciles
        ttk.Separator(left_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        ttk.Label(left_frame, text="Caracteres difíciles:", 
                 font=('Arial', 11, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        
        self.diff_chars_frame = ttk.Frame(left_frame)
        self.diff_chars_frame.pack(fill=tk.X)
        
        # Botones para caracteres difíciles
        difficult_btns = ttk.Frame(left_frame)
        difficult_btns.pack(fill=tk.X, pady=5)
        
        ttk.Button(
            difficult_btns,
            text="Practicar difíciles",
            command=self.practice_difficult_only,
            style="Warning.TButton",
            width=15
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            difficult_btns,
            text="Limpiar difíciles",
            command=self.clear_difficult_chars,
            width=15
        ).pack(side=tk.LEFT)
        
        # Control de tiempo
        ttk.Separator(left_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        ttk.Label(left_frame, text="Tiempo (segundos):", 
                 font=('Arial', 11, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        
        time_frame = ttk.Frame(left_frame)
        time_frame.pack(fill=tk.X)
        
        time_scale = ttk.Scale(
            time_frame, 
            from_=1.0, 
            to=10.0, 
            orient=tk.HORIZONTAL, 
            variable=self.delay_var,
            length=150,
            command=self.update_time_display
        )
        time_scale.pack(side=tk.LEFT)
        
        ttk.Label(time_frame, textvariable=self.time_display, width=3).pack(side=tk.LEFT, padx=5)
        
        # Sistema de repetición espaciada
        srs_frame = ttk.Frame(left_frame)
        srs_frame.pack(fill=tk.X, pady=5)
        
        ttk.Checkbutton(
            srs_frame,
            text="Usar sistema SRS",
            variable=self.srs_mode,
            command=self.toggle_srs_mode
        ).pack(side=tk.LEFT)
        
        ttk.Label(srs_frame, 
                text="?", 
                cursor="question_arrow").pack(side=tk.LEFT)
        
        # Botones de control
        ttk.Separator(left_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # Botón de iniciar/detener con estilo mejorado
        self.start_button = ttk.Button(
            left_frame, 
            text="Iniciar", 
            command=self.toggle_practice,
            width=15,
            style="Primary.TButton"
        )
        self.start_button.pack(pady=5)
        
        # Botones de modo
        order_frame = ttk.Frame(left_frame)
        order_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(
            order_frame, 
            text="Aleatorio", 
            command=lambda: self.toggle_order(True),
            width=15
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            order_frame, 
            text="Secuencial", 
            command=lambda: self.toggle_order(False),
            width=15
        ).pack(side=tk.LEFT)
        
        # Estadísticas de sesión
        ttk.Separator(left_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        ttk.Label(left_frame, text="Estadísticas de sesión:", 
                 font=('Arial', 11, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        
        stats_frame = ttk.Frame(left_frame)
        stats_frame.pack(fill=tk.X)
        
        self.stats_text = tk.Text(stats_frame, height=8, width=25, wrap=tk.WORD, 
                                 relief=tk.GROOVE, font=('Arial', 9), state=tk.DISABLED)
        self.stats_text.pack(fill=tk.X, expand=True)
        
        # Panel derecho (visualización)
        right_frame = ttk.Frame(flash_paned, padding=10)
        flash_paned.add(right_frame, weight=3)
        
        # Modos de estudio
        modes_frame = ttk.Frame(right_frame)
        modes_frame.pack(fill=tk.X, pady=(0, 10))
        
        study_modes_frame = ttk.Frame(modes_frame)
        study_modes_frame.pack(side=tk.LEFT)
        
        ttk.Radiobutton(
            study_modes_frame, 
            text="Tarjetas Flash (Hiragana → Romanji)",
            variable=self.study_mode,
            value="flash"
        ).pack(anchor=tk.W, padx=5)
        
        ttk.Radiobutton(
            study_modes_frame, 
            text="Inverso (Romanji → Hiragana)",
            variable=self.study_mode,
            value="inverse"
        ).pack(anchor=tk.W, padx=5)
        
        # Opción de aleatorio/secuencial
        random_frame = ttk.Frame(modes_frame)
        random_frame.pack(side=tk.RIGHT, padx=10)
        
        ttk.Checkbutton(
            random_frame,
            text="Modo aleatorio",
            variable=self.random_mode
        ).pack(side=tk.RIGHT)
        
        # Barra de progreso
        progress_frame = ttk.Frame(right_frame)
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(progress_frame, text="Progreso:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Label(progress_frame, textvariable=self.progress_var).pack(side=tk.LEFT, padx=5)
        
        self.progress_bar = ttk.Progressbar(progress_frame, length=200, mode='determinate')
        self.progress_bar.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        
        # Display de caracteres
        display_frame = ttk.Frame(right_frame, borderwidth=2, relief=tk.GROOVE)
        display_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        char_display = ttk.Frame(display_frame)
        char_display.pack(fill=tk.BOTH, expand=True)
        
        # Frame horizontal para contener hiragana y romanji lado a lado
        self.char_row = ttk.Frame(char_display)
        self.char_row.pack(expand=True)
        
        self.hiragana_label = ttk.Label(
            self.char_row, 
            text="", 
            font=("Arial", 120),
            width=3
        )
        self.hiragana_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.romanji_label = ttk.Label(
            self.char_row, 
            text="", 
            font=("Arial", 50),
            width=6
        )
        self.romanji_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Ejemplo de palabra (inicialmente oculto)
        self.example_frame = ttk.Frame(display_frame)
        self.example_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=20)

        self.example_label = ttk.Label(
            self.example_frame,
            text="",
            font=("Arial", 24, "bold"),
            foreground="#333333",
            wraplength=500,
            justify=tk.CENTER
        )
        self.example_label.pack(pady=10)
        
        # Botones de feedback
        feedback_frame = ttk.Frame(right_frame)
        feedback_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(
            feedback_frame,
            text="Difícil",
            width=15,
            style="Danger.TButton",
            command=lambda: self.mark_difficult(True)
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            feedback_frame,
            text="Fácil",
            width=15,
            style="Success.TButton",
            command=lambda: self.mark_difficult(False)
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            feedback_frame,
            text="Mostrar ejemplo",
            width=15,
            style="Info.TButton",
            command=self.show_example
        ).pack(side=tk.LEFT, padx=5)
    
    def create_quiz_tab(self):
        """Crea la pestaña del modo quiz"""
        quiz_tab = ttk.Frame(self.notebook)
        self.notebook.add(quiz_tab, text="Modo Quiz")
        
        # Contenedor principal
        quiz_frame = ttk.Frame(quiz_tab, padding=10)
        quiz_frame.pack(fill=tk.BOTH, expand=True)
        
        # Opciones del quiz
        quiz_options = ttk.LabelFrame(quiz_frame, text="Opciones del Quiz", padding=10)
        quiz_options.pack(fill=tk.X, pady=(0, 10))
        
        # Modo de respuesta
        resp_frame = ttk.Frame(quiz_options)
        resp_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(resp_frame, text="Modo de respuesta:").pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Radiobutton(
            resp_frame,
            text="Escribir respuesta",
            variable=self.quiz_mode,
            value="write",
            command=self.update_quiz_interface
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Radiobutton(
            resp_frame,
            text="Opción múltiple",
            variable=self.quiz_mode,
            value="multiple",
            command=self.update_quiz_interface
        ).pack(side=tk.LEFT, padx=5)
        
        # Dirección de la pregunta
        dir_frame = ttk.Frame(quiz_options)
        dir_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(dir_frame, text="Dirección:").pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Radiobutton(
            dir_frame,
            text="Hiragana → Romanji",
            variable=self.quiz_direction,
            value="hira_to_rom",
            command=self.update_quiz_interface
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Radiobutton(
            dir_frame,
            text="Romanji → Hiragana",
            variable=self.quiz_direction,
            value="rom_to_hira",
            command=self.update_quiz_interface
        ).pack(side=tk.LEFT, padx=5)
        
        # Opciones adicionales
        extra_frame = ttk.Frame(quiz_options)
        extra_frame.pack(fill=tk.X, pady=5)
        
        ttk.Checkbutton(
            extra_frame,
            text="Solo caracteres difíciles",
            variable=self.quiz_difficult_only,
            command=self.update_quiz_questions
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Checkbutton(
            extra_frame,
            text="Usar sistema SRS",
            variable=self.srs_mode
        ).pack(side=tk.LEFT, padx=20)
        
        ttk.Button(
            extra_frame,
            text="Iniciar nuevo quiz",
            command=self.reset_quiz,
            style="Primary.TButton",
            width=15
        ).pack(side=tk.RIGHT, padx=5)
        
        # Área principal del quiz
        quiz_pane = ttk.PanedWindow(quiz_frame, orient=tk.VERTICAL)
        quiz_pane.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Panel superior para la pregunta
        quiz_top = ttk.Frame(quiz_pane, padding=10)
        quiz_pane.add(quiz_top, weight=1)
        
        self.quiz_char_label = ttk.Label(
            quiz_top,
            text="",
            font=("Arial", 120),
            anchor=tk.CENTER
        )
        self.quiz_char_label.pack(expand=True)
        
        # Panel inferior para la respuesta
        self.quiz_bottom = ttk.Frame(quiz_pane, padding=10)
        quiz_pane.add(self.quiz_bottom, weight=1)
        
        # Este frame contendrá la interfaz de respuesta (se actualizará según el modo)
        self.quiz_response_frame = ttk.Frame(self.quiz_bottom)
        self.quiz_response_frame.pack(fill=tk.BOTH, expand=True)
        
        # Resultado
        self.quiz_result_var = tk.StringVar(value="")
        self.quiz_result_label = ttk.Label(
            self.quiz_bottom,
            textvariable=self.quiz_result_var,
            font=("Arial", 16, "bold")
        )
        self.quiz_result_label.pack(pady=10)
        
        # Estadísticas del quiz
        quiz_stats_frame = ttk.LabelFrame(self.quiz_bottom, text="Estadísticas", padding=5)
        quiz_stats_frame.pack(fill=tk.X, pady=10)
        
        # Grid para estadísticas
        grid_frame = ttk.Frame(quiz_stats_frame)
        grid_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Primera fila
        ttk.Label(grid_frame, text="Aciertos:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.correct_var = tk.StringVar(value="0")
        ttk.Label(grid_frame, textvariable=self.correct_var).grid(row=0, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(grid_frame, text="Intentos:").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.attempts_var = tk.StringVar(value="0")
        ttk.Label(grid_frame, textvariable=self.attempts_var).grid(row=0, column=3, sticky=tk.W, padx=5)
        
        # Segunda fila
        ttk.Label(grid_frame, text="Precisión:").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.accuracy_var = tk.StringVar(value="0%")
        ttk.Label(grid_frame, textvariable=self.accuracy_var).grid(row=1, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(grid_frame, text="Racha:").grid(row=1, column=2, sticky=tk.W, padx=5)
        self.streak_var = tk.StringVar(value="0")
        ttk.Label(grid_frame, textvariable=self.streak_var).grid(row=1, column=3, sticky=tk.W, padx=5)
        
        # Barra de progreso del quiz
        self.quiz_progress_bar = ttk.Progressbar(quiz_stats_frame, length=300, mode='determinate')
        self.quiz_progress_bar.pack(pady=5, fill=tk.X, padx=5)
        
        # Variables para el modo de opción múltiple
        self.quiz_options_vars = []  # Para los radiobuttons
        self.quiz_option_var = tk.StringVar(value="")  # Para almacenar la selección
    
    def create_stats_tab(self):
        """Crea la pestaña de estadísticas"""
        stats_tab = ttk.Frame(self.notebook)
        self.notebook.add(stats_tab, text="Estadísticas")
        
        stats_container = ttk.Frame(stats_tab, padding=10)
        stats_container.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(
            stats_container,
            text="Tu Progreso de Aprendizaje",
            font=("Arial", 18, "bold")
        ).pack(pady=(0, 20))
        
        # Dividir en columnas
        stats_columns = ttk.PanedWindow(stats_container, orient=tk.HORIZONTAL)
        stats_columns.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Columna izquierda
        left_stats = ttk.Frame(stats_columns)
        stats_columns.add(left_stats, weight=1)
        
        # Estadísticas generales
        general_frame = ttk.LabelFrame(left_stats, text="Estadísticas Generales", padding=10)
        general_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.general_stats = tk.Text(general_frame, height=12, width=40, wrap=tk.WORD)
        self.general_stats.pack(fill=tk.BOTH, expand=True)
        self.general_stats.config(state=tk.DISABLED)
        
        # Columna derecha
        right_stats = ttk.Frame(stats_columns)
        stats_columns.add(right_stats, weight=1)
        
        # Progreso por categoría
        category_frame = ttk.LabelFrame(right_stats, text="Progreso por Categoría", padding=10)
        category_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.category_stats = tk.Text(category_frame, height=12, width=40, wrap=tk.WORD)
        self.category_stats.pack(fill=tk.BOTH, expand=True)
        self.category_stats.config(state=tk.DISABLED)
        
        # Caracteres difíciles
        difficult_frame = ttk.LabelFrame(stats_container, text="Caracteres Difíciles", padding=10)
        difficult_frame.pack(fill=tk.X, pady=5)
        
        self.difficult_stats = tk.Text(difficult_frame, height=5, width=60, wrap=tk.WORD)
        self.difficult_stats.pack(fill=tk.X)
        self.difficult_stats.config(state=tk.DISABLED)
        
        # Botones de acciones
        buttons_frame = ttk.Frame(stats_container)
        buttons_frame.pack(pady=10)
        
        ttk.Button(
            buttons_frame,
            text="Actualizar Estadísticas",
            command=self.update_stats_display,
            style="Primary.TButton"
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            buttons_frame,
            text="Exportar a CSV",
            command=lambda: self.export_statistics("csv")
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            buttons_frame,
            text="Ver gráficos",
            command=self.show_stats_graphs
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            buttons_frame,
            text="Reiniciar estadísticas",
            command=self.reset_all_stats,
            style="Danger.TButton"
        ).pack(side=tk.LEFT, padx=5)
    
    def create_settings_tab(self):
        """Crea la pestaña de configuración"""
        settings_tab = ttk.Frame(self.notebook)
        self.notebook.add(settings_tab, text="Configuración")
        
        settings_container = ttk.Frame(settings_tab, padding=10)
        settings_container.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(
            settings_container,
            text="Configuración de la Aplicación",
            font=("Arial", 18, "bold")
        ).pack(pady=(0, 20))
        
        # Configuración de apariencia
        appearance_frame = ttk.LabelFrame(settings_container, text="Apariencia", padding=10)
        appearance_frame.pack(fill=tk.X, pady=5)
        
        # Temas disponibles
        theme_frame = ttk.Frame(appearance_frame)
        theme_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(theme_frame, text="Tema:").pack(side=tk.LEFT, padx=(0, 10))
        
        themes = ['clam', 'alt', 'default', 'classic']
        self.theme_var = tk.StringVar(value='clam')
        theme_combo = ttk.Combobox(theme_frame, textvariable=self.theme_var, values=themes, state="readonly", width=15)
        theme_combo.pack(side=tk.LEFT)
        theme_combo.bind("<<ComboboxSelected>>", self.change_theme)
        
        # Tamaño de fuente
        font_frame = ttk.Frame(appearance_frame)
        font_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(font_frame, text="Tamaño de fuente:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.font_size_var = tk.IntVar(value=120)
        font_scale = ttk.Scale(font_frame, from_=60, to=200, variable=self.font_size_var, orient=tk.HORIZONTAL, length=200)
        font_scale.pack(side=tk.LEFT)
        font_scale.bind("<ButtonRelease-1>", self.update_font_size)
        
        ttk.Label(font_frame, textvariable=self.font_size_var).pack(side=tk.LEFT, padx=5)
        
        # Configuración de comportamiento
        behavior_frame = ttk.LabelFrame(settings_container, text="Comportamiento", padding=10)
        behavior_frame.pack(fill=tk.X, pady=10)
        
        # Auto-guardado
        auto_save_frame = ttk.Frame(behavior_frame)
        auto_save_frame.pack(fill=tk.X, pady=5)
        
        self.auto_save_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            auto_save_frame,
            text="Auto-guardar al salir",
            variable=self.auto_save_var
        ).pack(side=tk.LEFT, padx=(0, 20))
        
        # Notificaciones
        self.show_notif_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            auto_save_frame,
            text="Mostrar notificaciones de logros",
            variable=self.show_notif_var
        ).pack(side=tk.LEFT)
        
        # Sistema de aprendizaje
        learning_frame = ttk.Frame(behavior_frame)
        learning_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(learning_frame, text="Algoritmo adaptativo:").pack(side=tk.LEFT, padx=(0, 10))
        
        algo_types = ['Estándar', 'SRS Básico', 'SRS Avanzado', 'Personalizado']
        self.algo_var = tk.StringVar(value='Estándar')
        algo_combo = ttk.Combobox(learning_frame, textvariable=self.algo_var, values=algo_types, state="readonly", width=15)
        algo_combo.pack(side=tk.LEFT)
        
        # Planificación de estudio
        plan_frame = ttk.LabelFrame(settings_container, text="Planificación de Estudio", padding=10)
        plan_frame.pack(fill=tk.X, pady=5)
        
        # Duración de sesión
        session_frame = ttk.Frame(plan_frame)
        session_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(session_frame, text="Duración de sesión (minutos):").pack(side=tk.LEFT, padx=(0, 10))
        
        self.session_duration_var = tk.IntVar(value=15)
        duration_spin = ttk.Spinbox(session_frame, from_=5, to=60, increment=5, textvariable=self.session_duration_var, width=10)
        duration_spin.pack(side=tk.LEFT)
        
        # Caracteres por sesión
        chars_frame = ttk.Frame(plan_frame)
        chars_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(chars_frame, text="Caracteres por sesión:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.chars_per_session_var = tk.IntVar(value=20)
        chars_spin = ttk.Spinbox(chars_frame, from_=5, to=100, increment=5, textvariable=self.chars_per_session_var, width=10)
        chars_spin.pack(side=tk.LEFT)
        
        # Recordatorio
        reminder_frame = ttk.Frame(plan_frame)
        reminder_frame.pack(fill=tk.X, pady=5)
        
        self.reminder_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            reminder_frame,
            text="Activar recordatorios de estudio",
            variable=self.reminder_var,
            command=self.toggle_reminders
        ).pack(side=tk.LEFT)
        
        # Botones de acción
        buttons_frame = ttk.Frame(settings_container)
        buttons_frame.pack(pady=20)
        
        ttk.Button(
            buttons_frame,
            text="Guardar configuración",
            command=self.save_settings,
            style="Primary.TButton"
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            buttons_frame,
            text="Restaurar valores predeterminados",
            command=self.reset_settings
        ).pack(side=tk.LEFT, padx=5)
    
    def create_status_bar(self, parent):
        """Crea la barra de estado en la parte inferior de la ventana"""
        status_bar = ttk.Frame(parent, relief=tk.SUNKEN, padding=(2, 2))
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Texto de estado
        self.status_text = tk.StringVar(value="Listo")
        status_label = ttk.Label(status_bar, textvariable=self.status_text, anchor=tk.W)
        status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Información de sesión
        self.session_info = tk.StringVar(value="Tiempo de estudio: 00:00")
        session_label = ttk.Label(status_bar, textvariable=self.session_info)
        session_label.pack(side=tk.RIGHT, padx=10)
        
        # Iniciar contador de tiempo
        self.start_session_timer()
    
    def start_session_timer(self):
        """Inicia un temporizador para seguir el tiempo de estudio"""
        # Variable de clase para almacenar el ID del temporizador
        self.session_timer_id = None
        
        def update_timer():
            if hasattr(self, 'session_start_time'):
                try:
                    elapsed = datetime.now() - self.session_start_time
                    hours, remainder = divmod(elapsed.total_seconds(), 3600)
                    minutes, seconds = divmod(remainder, 60)
                    if hasattr(self, 'session_info') and self.session_info is not None:
                        self.session_info.set(f"Tiempo de estudio: {int(hours):02}:{int(minutes):02}:{int(seconds):02}")
                    
                    # Guardar referencia al ID del temporizador para poder cancelarlo si es necesario
                    self.session_timer_id = self.root.after(1000, update_timer)
                except Exception as e:
                    logger.error(f"Error en el temporizador de sesión: {e}")
            else:
                # Si no existe session_start_time, no continuar
                logger.warning("No hay tiempo de inicio de sesión definido")
        
        # Iniciar el temporizador
        update_timer()
    
    # ===== Funciones de utilidad y manejo de eventos =====
    
    def update_time_display(self, *args):
        """Actualiza el display de tiempo en la escala"""
        self.time_display.set(f"{self.delay_var.get():.1f}")
    
    def toggle_practice(self):
        """Inicia o detiene la práctica de hiragana"""
        try:
            if not self.hiragana_list:
                messagebox.showinfo("Sin caracteres", 
                                "No hay caracteres disponibles para practicar. Selecciona al menos una categoría.")
                return
                    
            if self.is_running:
                # Detener la práctica
                self.is_running = False
                self.start_button.config(text="Iniciar")
                self.status_text.set("Práctica detenida")
                
                # Cancelar cualquier temporizador pendiente
                if hasattr(self, 'timer_id') and self.timer_id:
                    self.root.after_cancel(self.timer_id)
                    self.timer_id = None
            else:
                # Iniciar la práctica
                self.is_running = True
                self.start_button.config(text="Detener")
                self.status_text.set("Práctica en curso...")
                
                # Asegurarse de que no haya temporizadores activos
                if hasattr(self, 'timer_id') and self.timer_id:
                    self.root.after_cancel(self.timer_id)
                    
                # Crear una copia de la lista antes de modificarla
                if self.study_mode.get() == "inverse":
                    # Si estamos en modo inverso, invertimos los pares hiragana-romanji
                    self.practice_list = [(romanji, hiragana) for hiragana, romanji in self.hiragana_list]
                else:
                    self.practice_list = self.hiragana_list.copy()
                
                # Si está en modo SRS, filtrar por caracteres que toca repasar
                if self.srs_mode.get():
                    self.apply_srs_filter()
                
                # Si está activado el modo aleatorio, mezclar la lista
                if self.random_mode.get():
                    random.shuffle(self.practice_list)
                
                # Si está en modo adaptativo avanzado, ordenar por prioridad
                if hasattr(self, 'algo_var') and self.algo_var.get() == "SRS Avanzado":
                    self.practice_list = self.adaptive_learning.sort_by_priority(
                        self.practice_list, self.study_history)
                
                # Iniciar la práctica
                self.show_romanji = False  # Empezar mostrando hiragana
                self.practice_hiragana()
                
                # Registrar fecha de estudio para logros
                today_date = datetime.now().isoformat()
                if today_date not in self.achievement_data['study_dates']:
                    self.achievement_data['study_dates'].append(today_date)
                
                # Incrementar sesiones completadas
                self.achievement_data['sessions_completed'] += 1
                
                # Verificar logros
                self.check_achievements()
        except Exception as e:
            self.log_error(f"Error al iniciar práctica: {str(e)}")
    def apply_srs_filter(self):
        """Filtra la lista de práctica según el sistema SRS"""
        try:
            # Obtener caracteres que deben repasarse hoy
            due_chars = self.srs_scheduler.get_due_cards(self.study_history)
            
            if not due_chars:
                messagebox.showinfo("SRS", "¡Felicidades! No hay caracteres pendientes para repasar hoy.")
                self.is_running = False
                self.start_button.config(text="Iniciar")
                return
            
            # Filtrar lista de práctica
            filtered_list = []
            for pair in self.practice_list:
                hiragana = pair[0] if self.study_mode.get() == "flash" else pair[1]
                if hiragana in due_chars:
                    filtered_list.append(pair)
            
            if filtered_list:
                self.practice_list = filtered_list
                messagebox.showinfo("SRS", f"Practicando {len(filtered_list)} caracteres según programación SRS.")
            else:
                messagebox.showinfo("SRS", "No hay caracteres programados para hoy en las categorías seleccionadas.")
                self.is_running = False
                self.start_button.config(text="Iniciar")
        except Exception as e:
            self.log_error(f"Error al aplicar filtro SRS: {str(e)}")
    
    def practice_hiragana(self):
        """Función principal para la práctica de hiragana"""
        try:
            # Salir si no está corriendo o no hay lista de práctica
            if not self.is_running or not getattr(self, 'practice_list', []):
                return
            
            # Ocultar ejemplo
            if hasattr(self, 'example_label') and self.example_label is not None:
                self.example_label.config(text="")
            
            if self.show_romanji:
                # Mostrar el romanji al lado del hiragana
                _, romanji = self.practice_list[self.current_index]
                
                # Usar animación simple de transición
                if hasattr(self, 'romanji_label') and self.romanji_label is not None:
                    self.romanji_label.config(text=romanji)
                
                # Registrar carácter mostrado en estadísticas
                self.register_character_shown()
                
                # Preparar para el siguiente hiragana
                self.show_romanji = False
                self.current_index = (self.current_index + 1) % len(self.practice_list)
                self.update_progress()
                
                # Programar el siguiente hiragana usando el mismo tiempo configurado
                delay_ms = int(self.delay_var.get() * 1000)
                # Guardar el ID del temporizador para poder cancelarlo después
                self.timer_id = self.root.after(delay_ms, self.practice_hiragana)
            else:
                # Mostrar solo el hiragana (limpiar el romanji)
                hiragana, _ = self.practice_list[self.current_index]
                
                # Usar animación de transición si está habilitada
                self.animate_card(hiragana, "")
                
                # Preparar para mostrar el romanji
                self.show_romanji = True
                
                # Programar mostrar el romanji después del tiempo configurado
                delay_ms = int(self.delay_var.get() * 1000)
                # Guardar el ID del temporizador para poder cancelarlo después
                self.timer_id = self.root.after(delay_ms, self.practice_hiragana)
        except Exception as e:
            self.log_error(f"Error en la práctica: {str(e)}")
            self.is_running = False
            if hasattr(self, 'start_button') and self.start_button is not None:
                self.start_button.config(text="Iniciar")
    def animate_card(self, hiragana, romanji):
        """Animación suave para la transición de tarjetas"""
        try:
            # Comprobar si la configuración permite animaciones
            if hasattr(self, 'animations_enabled') and not self.animations_enabled:
                self.hiragana_label.config(text=hiragana)
                self.romanji_label.config(text=romanji)
                return
                
            # Animación de desvanecimiento simple (solo para hiragana)
            current_text = self.hiragana_label.cget("text")
            
            if current_text != hiragana:
                # Desvanecimiento
                for alpha in range(10, -1, -1):
                    # Crear color con alpha (menos visible gradualmente)
                    color = f"#{int(51*alpha/10):02x}{int(51*alpha/10):02x}{int(51*alpha/10):02x}"
                    self.hiragana_label.config(foreground=color)
                    self.root.update()
                    time.sleep(0.01)  # Tiempo muy corto para no afectar rendimiento
                
                # Cambiar texto
                self.hiragana_label.config(text=hiragana)
                
                # Aparecer
                for alpha in range(0, 11):
                    color = f"#{int(51*alpha/10):02x}{int(51*alpha/10):02x}{int(51*alpha/10):02x}"
                    self.hiragana_label.config(foreground=color)
                    self.root.update()
                    time.sleep(0.01)
            else:
                self.hiragana_label.config(text=hiragana)
            
            self.romanji_label.config(text=romanji)
        except Exception as e:
            # Si hay error en la animación, mostrar sin animación
            self.hiragana_label.config(text=hiragana)
            self.romanji_label.config(text=romanji)
    
    def advance_card(self, event=None):
        """Avanza manualmente a la siguiente tarjeta"""
        # Detener la práctica automática si está activa
        if self.is_running:
            self.toggle_practice()
        
        if not hasattr(self, 'practice_list') or not self.practice_list:
            return
            
        # Incrementar el índice
        self.current_index = (self.current_index + 1) % len(self.practice_list)
        
        # Mostrar el hiragana
        hiragana, _ = self.practice_list[self.current_index]
        if hasattr(self, 'hiragana_label') and self.hiragana_label is not None:
            self.hiragana_label.config(text=hiragana)
        if hasattr(self, 'romanji_label') and self.romanji_label is not None:
            self.romanji_label.config(text="")
        
        # Restablecer estado
        self.show_romanji = True
        if hasattr(self, 'example_label') and self.example_label is not None:
            self.example_label.config(text="")
        
        # Actualizar progreso
        self.update_progress()

    def previous_card(self, event=None):
        """Retrocede a la tarjeta anterior"""
        # Detener la práctica automática si está activa
        if self.is_running:
            self.toggle_practice()
        
        if not hasattr(self, 'practice_list') or not self.practice_list:
            return
            
        # Decrementar el índice
        self.current_index = (self.current_index - 1) % len(self.practice_list)
        
        # Mostrar el hiragana
        hiragana, _ = self.practice_list[self.current_index]
        if hasattr(self, 'hiragana_label') and self.hiragana_label is not None:
            self.hiragana_label.config(text=hiragana)
        if hasattr(self, 'romanji_label') and self.romanji_label is not None:
            self.romanji_label.config(text="")
        
        # Restablecer estado
        self.show_romanji = True
        if hasattr(self, 'example_label') and self.example_label is not None:
            self.example_label.config(text="")
        
        # Actualizar progreso
        self.update_progress()
    
    def update_progress(self):
        """Actualiza el indicador de progreso"""
        try:
            total = len(getattr(self, 'practice_list', []) or self.hiragana_list)
            current = self.current_index + 1 if total > 0 else 0
            self.progress_var.set(f"{current}/{total}")
            
            # Actualizar barra de progreso
            if hasattr(self, 'progress_bar'):
                progress_value = current / total if total > 0 else 0
                self.progress_bar['value'] = progress_value * 100
        except Exception as e:
            self.progress_var.set("Error")
            logger.error(f"Error al actualizar progreso: {str(e)}")
    
    def toggle_order(self, is_random):
        """Cambia entre modo aleatorio y secuencial"""
        try:
            # Actualizar variable de modo aleatorio
            self.random_mode.set(is_random)
            
            # Aplicar el nuevo orden
            if is_random:
                # Detener la práctica actual si está en ejecución
                self.is_running = False
                self.start_button.config(text="Iniciar")
                
                # Mezclar la lista de hiragana si hay alguna
                if self.hiragana_list:
                    random.shuffle(self.hiragana_list)
                    self.current_index = 0
                    self.update_progress()
                    messagebox.showinfo("Modo aleatorio", "Lista mezclada aleatoriamente.")
            else:
                # Detener la práctica actual si está en ejecución
                self.is_running = False
                self.start_button.config(text="Iniciar")
                
                # Reorganizar de forma secuencial por categorías
                self.update_hiragana_list()
                
                # Notificar al usuario
                messagebox.showinfo("Modo secuencial", "Lista ordenada por categorías.")
                
            # Limpiar la visualización
            self.show_romanji = False
            self.hiragana_label.config(text="")
            self.romanji_label.config(text="")
            self.example_label.config(text="")
        except Exception as e:
            self.log_error(f"Error al cambiar el orden: {str(e)}")
    
    def update_hiragana_list(self):
        """Actualiza la lista de hiragana según las categorías seleccionadas"""
        try:
            # Limpiar la lista actual
            self.hiragana_list = []
            
            # Agregar los hiragana de las categorías seleccionadas
            for category, var in self.category_vars.items():
                if var.get():
                    self.hiragana_list.extend(self.hiragana_categories[category])
            
            # Reiniciar índices y actualizar progreso
            self.current_index = 0
            self.update_progress()
            
            # Si no hay categorías seleccionadas, deshabilitar el botón de inicio
            if not self.hiragana_list:
                self.start_button.config(state=tk.DISABLED)
            else:
                self.start_button.config(state=tk.NORMAL)
                
                # Si está en modo aleatorio, mezclar la lista
                if hasattr(self, 'random_mode') and self.random_mode.get():
                    random.shuffle(self.hiragana_list)
            
            # Actualizar display de caracteres difíciles
            self.update_difficult_chars_display()
            
            # Marcar que ya no estamos en modo difíciles
            self.in_difficult_mode = False
        except Exception as e:
            self.log_error(f"Error al actualizar lista: {str(e)}")
    
    def mark_difficult(self, is_difficult):
        """Marca o desmarca un carácter como difícil"""
        try:
            if not hasattr(self, 'practice_list') or not self.practice_list:
                messagebox.showinfo("Información", "No hay caracteres para marcar.")
                return
                
            # Obtener el carácter actual
            if self.study_mode.get() == "flash":
                current_char, _ = self.practice_list[self.current_index]
            else:  # modo inverso
                _, current_char = self.practice_list[self.current_index]
            
            if is_difficult:
                self.difficult_characters.add(current_char)
                messagebox.showinfo("Marcado como difícil", 
                                   f"El carácter '{current_char}' ha sido marcado como difícil.")
            else:
                if current_char in self.difficult_characters:
                    self.difficult_characters.remove(current_char)
                    messagebox.showinfo("Marcado como fácil", 
                                       f"El carácter '{current_char}' ya no está marcado como difícil.")
                else:
                    messagebox.showinfo("Información", 
                                       f"El carácter '{current_char}' no estaba marcado como difícil.")
            
            # Actualizar visualización
            self.update_difficult_chars_display()
            
            # Si estamos en modo difíciles, actualizar la lista en tiempo real
            if getattr(self, 'in_difficult_mode', False) and not is_difficult:
                # Guardar índice actual
                current_char_index = self.current_index
                
                # Actualizar la lista
                self.practice_difficult_only()
                
                # Ajustar el índice actual si es necesario
                if current_char_index >= len(self.practice_list):
                    self.current_index = 0 if self.practice_list else current_char_index
                    
                self.update_progress()
        except Exception as e:
            self.log_error(f"Error al marcar carácter: {str(e)}")
    
    def update_difficult_chars_display(self):
        """Actualiza la visualización de caracteres difíciles"""
        # Limpiar el frame
        for widget in self.diff_chars_frame.winfo_children():
            widget.destroy()
            
        # Mostrar caracteres difíciles
        if self.difficult_characters:
            # Crear un frame con scroll si hay muchos caracteres
            if len(self.difficult_characters) > 15:
                canvas = tk.Canvas(self.diff_chars_frame, height=100, 
                                  highlightthickness=0, background="#f0f0f5")
                scrollbar = ttk.Scrollbar(self.diff_chars_frame, orient="vertical", 
                                        command=canvas.yview)
                
                tag_frame = ttk.Frame(canvas)
                canvas.create_window((0, 0), window=tag_frame, anchor='nw')
                
                canvas.configure(yscrollcommand=scrollbar.set)
                canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                
                chars_container = tag_frame
            else:
                chars_container = ttk.Frame(self.diff_chars_frame)
                chars_container.pack(fill=tk.X)
            
            # Crear etiquetas tipo tag para cada carácter
            row_frame = ttk.Frame(chars_container)
            row_frame.pack(fill=tk.X, pady=2)
            count = 0
            
            for char in sorted(self.difficult_characters):
                if count > 0 and count % 8 == 0:  # Nueva fila cada 8 caracteres
                    row_frame = ttk.Frame(chars_container)
                    row_frame.pack(fill=tk.X, pady=2)
                
                tag_frame = ttk.Frame(row_frame, style="DifficultTag.TFrame")
                tag_frame.pack(side=tk.LEFT, padx=2, pady=2)
                
                ttk.Label(tag_frame, text=char, 
                         style="DifficultTag.TLabel").pack(side=tk.LEFT, padx=2)
                
                ttk.Button(tag_frame, text="×", width=1, 
                          command=lambda c=char: self.remove_difficult_char(c)).pack(side=tk.LEFT)
                
                count += 1
            
            # Actualizar scrollregion después de añadir todos los tags
            if len(self.difficult_characters) > 15:
                tag_frame.update_idletasks()
                canvas.configure(scrollregion=canvas.bbox("all"))
        else:
            ttk.Label(self.diff_chars_frame, 
                     text="No hay caracteres marcados como difíciles").pack()
    
    def remove_difficult_char(self, char):
        """Elimina un carácter de la lista de difíciles"""
        if char in self.difficult_characters:
            self.difficult_characters.remove(char)
            self.update_difficult_chars_display()
            
            # Si estamos en modo difíciles, actualizar la lista
            if getattr(self, 'in_difficult_mode', False):
                self.practice_difficult_only()
    
    def practice_difficult_only(self):
        """Configura el entrenador para practicar solo los caracteres marcados como difíciles"""
        try:
            if not self.difficult_characters:
                messagebox.showinfo("Sin caracteres difíciles", "No hay caracteres marcados como difíciles.")
                return
                
            # Crear una lista con solo los caracteres difíciles
            difficult_list = []
            for category in self.hiragana_categories.values():
                for pair in category:
                    if pair[0] in self.difficult_characters:
                        difficult_list.append(pair)
            
            if not difficult_list:
                messagebox.showinfo("Advertencia", "No se encontraron caracteres difíciles en las categorías seleccionadas.")
                return
                
            # Actualizar la lista de hiragana
            self.hiragana_list = difficult_list
            self.current_index = 0
            self.update_progress()
            
            # Marcar que estamos en modo difíciles
            self.in_difficult_mode = True
            messagebox.showinfo("Modo difíciles", 
                               f"Practicando {len(difficult_list)} caracteres difíciles. Se han ignorado las selecciones de categorías.")
            
            # Si está en modo aleatorio, mezclar la lista
            if self.random_mode.get():
                random.shuffle(self.hiragana_list)
            
            # Iniciar la práctica si no está ya en ejecución
            if not self.is_running:
                self.toggle_practice()
        except Exception as e:
            self.log_error(f"Error al iniciar modo difíciles: {str(e)}")
    
    def clear_difficult_chars(self):
        """Limpia la lista de caracteres difíciles"""
        if not self.difficult_characters:
            messagebox.showinfo("Información", "No hay caracteres marcados como difíciles.")
            return
            
        if messagebox.askyesno("Confirmar", "¿Estás seguro de que quieres eliminar todos los caracteres difíciles?"):
            self.difficult_characters.clear()
            self.update_difficult_chars_display()
            messagebox.showinfo("Completado", "Lista de caracteres difíciles limpiada.")
            
            # Si estamos en modo difíciles, volver al modo normal
            if getattr(self, 'in_difficult_mode', False):
                self.update_hiragana_list()
                self.in_difficult_mode = False
    
    def show_example(self):
        """Muestra un ejemplo de palabra para el carácter que se está mostrando actualmente"""
        try:
            if not hasattr(self, 'practice_list') or not self.practice_list:
                return
            
            # Obtener el carácter que se está mostrando actualmente en la pantalla
            displayed_char = self.hiragana_label.cget("text")
            
            if not displayed_char:
                return
            
            # Buscar el ejemplo del carácter mostrado
            if displayed_char in self.example_words:
                word, romanji, meaning = self.example_words[displayed_char]
                example_text = f"Ejemplo: {word} ({romanji})\n{meaning}"
                self.example_label.config(text=example_text)
            else:
                self.example_label.config(text="No hay ejemplo disponible para este carácter.")
        except Exception as e:
            self.log_error(f"Error al mostrar ejemplo: {str(e)}")
    
    def register_character_shown(self):
        """Registra que un carácter ha sido mostrado para las estadísticas"""
        try:
            # Incrementar el contador de caracteres mostrados
            self.session_chars_shown += 1
            
            # Actualizar estadísticas
            if hasattr(self, 'practice_list') and self.practice_list:
                current_pair = self.practice_list[self.current_index]
                
                # En modo normal, el hiragana es el primer elemento
                # En modo inverso, el hiragana es el segundo elemento
                if self.study_mode.get() == "flash":
                    current_char = current_pair[0]  # Hiragana
                else:  # modo inverso
                    current_char = current_pair[1]  # Hiragana
                
                if current_char not in self.study_history:
                    self.study_history[current_char] = {
                        "times_shown": 0, 
                        "correct": 0, 
                        "incorrect": 0,
                        "last_shown": datetime.now().isoformat()
                    }
                else:
                    self.study_history[current_char]["last_shown"] = datetime.now().isoformat()
                    
                self.study_history[current_char]["times_shown"] += 1
                
                # Añadir a la lista de caracteres estudiados para logros
                if current_char not in self.achievement_data['studied_chars']:
                    self.achievement_data['studied_chars'].append(current_char)
            
            # Actualizar estadísticas de sesión en tiempo real
            self.update_session_stats()
        except Exception as e:
            logger.error(f"Error al registrar carácter: {str(e)}")
    
    def update_session_stats(self):
        """Actualiza las estadísticas de la sesión actual en tiempo real"""
        try:
            # Calcular estadísticas
            session_duration = datetime.now() - self.session_start_time
            minutes = session_duration.total_seconds() / 60
            
            chars_per_minute = 0
            if minutes > 0:
                chars_per_minute = self.session_chars_shown / minutes
                
            # Actualizar datos para logros
            self.achievement_data['total_study_time'] += minutes / 60  # Convertir a horas
                
            # Actualizar texto de estadísticas
            stats_text = (
                f"Caracteres revisados: {self.session_chars_shown}\n"
                f"Tiempo de estudio: {int(minutes)} min\n"
                f"Velocidad: {chars_per_minute:.1f} car/min\n"
                f"Racha actual: {self.streak}\n"
                f"Mejor racha: {self.max_streak}\n"
                f"Caracteres difíciles: {len(self.difficult_characters)}\n"
                f"Total estudiados: {len(self.study_history)}\n"
                f"Pendientes: {len(self.achievement_data['all_hiragana']) - len(self.study_history)}"
            )
            
            self.stats_text.config(state=tk.NORMAL)
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(tk.END, stats_text)
            self.stats_text.config(state=tk.DISABLED)
        except Exception as e:
            logger.error(f"Error al actualizar estadísticas de sesión: {str(e)}")
    
    # ==== Funciones de modo quiz ====
    
    def update_quiz_interface(self):
        """Actualiza la interfaz del quiz según el modo seleccionado"""
        try:
            # Limpiar el frame de respuesta si existe
            if hasattr(self, 'quiz_response_frame') and self.quiz_response_frame is not None:
                for widget in self.quiz_response_frame.winfo_children():
                    widget.destroy()
            else:
                # Si no existe, no podemos continuar
                logger.error("No se pudo encontrar quiz_response_frame")
                return
            
            # Configurar según el modo seleccionado
            if self.quiz_mode.get() == "write":
                # Modo de escritura
                ttk.Label(
                    self.quiz_response_frame,
                    text=f"Escribe la {'pronunciación (romanji)' if self.quiz_direction.get() == 'hira_to_rom' else 'sílaba (hiragana)'}:",
                    font=("Arial", 12, "bold")
                ).pack(pady=(0, 10))
                
                # Crear el widget de entrada
                self.quiz_entry = ttk.Entry(
                    self.quiz_response_frame,
                    font=("Arial", 14),
                    width=15,
                    justify=tk.CENTER
                )
                self.quiz_entry.pack(pady=5)
                self.quiz_entry.bind("<Return>", self.check_answer)
                
                quiz_btn_frame = ttk.Frame(self.quiz_response_frame)
                quiz_btn_frame.pack(pady=10)
                
                self.submit_btn = ttk.Button(
                    quiz_btn_frame,
                    text="Comprobar",
                    command=self.check_answer,
                    style="Primary.TButton",
                    width=15
                )
                self.submit_btn.pack(side=tk.LEFT, padx=5)
                
                self.next_btn = ttk.Button(
                    quiz_btn_frame,
                    text="Siguiente",
                    command=self.next_quiz_question,
                    width=15,
                    state=tk.DISABLED
                )
                self.next_btn.pack(side=tk.LEFT, padx=5)
                
            else:
                # Modo de opción múltiple
                ttk.Label(
                    self.quiz_response_frame,
                    text=f"Selecciona la {'pronunciación correcta (romanji)' if self.quiz_direction.get() == 'hira_to_rom' else 'sílaba correcta (hiragana)'}:",
                    font=("Arial", 12, "bold")
                ).pack(pady=(0, 10))
                
                # Frame para las opciones
                options_frame = ttk.Frame(self.quiz_response_frame)
                options_frame.pack(pady=10)
                
                # Crear grid de 2x2 para las opciones
                self.option_buttons = []
                for i in range(4):
                    row, col = divmod(i, 2)
                    btn = ttk.Button(
                        options_frame,
                        text="",
                        width=20,
                        command=lambda idx=i: self.check_answer_from_button(idx)
                    )
                    btn.grid(row=row, column=col, padx=10, pady=5)
                    self.option_buttons.append(btn)
            
            logger.info(f"Interfaz de quiz actualizada en modo: {self.quiz_mode.get()}")
            
        except Exception as e:
            self.log_error(f"Error al actualizar la interfaz del quiz: {str(e)}")
    def update_quiz_questions(self):
        """Actualiza la lista de preguntas disponibles para el quiz"""
        try:
            # Si solo caracteres difíciles está activado
            if self.quiz_difficult_only.get():
                if not self.difficult_characters:
                    messagebox.showinfo("Sin caracteres difíciles", "No hay caracteres marcados como difíciles.")
                    self.quiz_difficult_only.set(False)
                    return
                    
                # Crear lista con caracteres difíciles
                self.quiz_available_chars = []
                for category in self.hiragana_categories.values():
                    for pair in category:
                        if pair[0] in self.difficult_characters:
                            if self.quiz_direction.get() == "hira_to_rom":
                                self.quiz_available_chars.append(pair)  # hiragana -> romanji
                            else:
                                self.quiz_available_chars.append((pair[1], pair[0]))  # romanji -> hiragana
            else:
                # Usar todas las categorías seleccionadas
                self.quiz_available_chars = []
                for category, var in self.category_vars.items():
                    if var.get():
                        for pair in self.hiragana_categories[category]:
                            if self.quiz_direction.get() == "hira_to_rom":
                                self.quiz_available_chars.append(pair)  # hiragana -> romanji
                            else:
                                self.quiz_available_chars.append((pair[1], pair[0]))  # romanji -> hiragana
            
            # Si está activado el SRS, filtrar por caracteres a repasar
            if self.srs_mode.get():
                due_chars = self.srs_scheduler.get_due_cards(self.study_history)
                if due_chars:
                    self.quiz_available_chars = [pair for pair in self.quiz_available_chars 
                                              if pair[0] in due_chars]
            
            if not self.quiz_available_chars:
                if self.srs_mode.get():
                    messagebox.showinfo("SRS", "No hay caracteres programados para hoy con la configuración actual.")
                    self.srs_mode.set(False)
                else:
                    messagebox.showinfo("Sin caracteres", "No hay caracteres disponibles con la configuración actual.")
                
                # Volver a cargar todos los caracteres
                self.update_quiz_questions()
        except Exception as e:
            self.log_error(f"Error al actualizar preguntas: {str(e)}")
    
    def load_quiz_question(self):
        """Carga una nueva pregunta de quiz según la configuración actual"""
        try:
            # Actualizar lista de preguntas disponibles
            self.update_quiz_questions()
            
            # Verificar si hay caracteres disponibles
            if not hasattr(self, 'quiz_available_chars') or not self.quiz_available_chars:
                if hasattr(self, 'quiz_char_label') and self.quiz_char_label is not None:
                    self.quiz_char_label.config(text="")
                if hasattr(self, 'quiz_result_var') and self.quiz_result_var is not None:
                    self.quiz_result_var.set("No hay caracteres disponibles")
                return
            
            # Elegir un carácter aleatorio o según prioridad
            try:
                if hasattr(self, 'algo_var') and self.algo_var.get() == "SRS Avanzado":
                    # Ordenar por prioridad y tomar el primero
                    sorted_chars = self.adaptive_learning.sort_by_priority(
                        self.quiz_available_chars, self.study_history)
                    question, answer = sorted_chars[0]
                else:
                    # Elegir aleatoriamente
                    random_idx = random.randint(0, len(self.quiz_available_chars) - 1)
                    question, answer = self.quiz_available_chars[random_idx]
            except Exception as e:
                logger.error(f"Error al seleccionar carácter: {e}")
                question, answer = self.quiz_available_chars[0]  # Usar el primero como fallback
            
            # Mostrar la pregunta si existe el widget
            if hasattr(self, 'quiz_char_label') and self.quiz_char_label is not None:
                self.quiz_char_label.config(text=question)
            
            # Guardar la respuesta correcta
            self.current_quiz_answer = answer
            self.current_quiz_question = question
            
            # Limpiar resultado anterior si existe
            if hasattr(self, 'quiz_result_var') and self.quiz_result_var is not None:
                self.quiz_result_var.set("")
            
            # Manejar modo escritura con verificaciones
            if self.quiz_mode.get() == "write":
                # Verificar que los widgets existan antes de usarlos
                if hasattr(self, 'quiz_entry') and self.quiz_entry is not None:
                    try:
                        self.quiz_entry.delete(0, tk.END)
                        self.quiz_entry.focus_set()
                    except Exception as e:
                        logger.error(f"Error al manipular quiz_entry: {e}")
                
                if hasattr(self, 'submit_btn') and self.submit_btn is not None:
                    try:
                        self.submit_btn.config(state=tk.NORMAL)
                    except Exception as e:
                        logger.error(f"Error al configurar submit_btn: {e}")
                
                if hasattr(self, 'next_btn') and self.next_btn is not None:
                    try:
                        self.next_btn.config(state=tk.DISABLED)
                    except Exception as e:
                        logger.error(f"Error al configurar next_btn: {e}")
            else:
                # Modo opción múltiple con botones directos
                try:
                    if not hasattr(self, 'option_buttons') or not self.option_buttons:
                        logger.warning("No se encontraron option_buttons")
                        return
                    
                    # Generar opciones incorrectas
                    all_answers = [pair[1] if self.quiz_direction.get() == "hira_to_rom" else pair[0] 
                                for pair in self.quiz_available_chars]
                    incorrect_options = [opt for opt in all_answers if opt != answer]
                    
                    # Seleccionar 3 opciones aleatorias
                    if len(incorrect_options) >= 3:
                        random.shuffle(incorrect_options)
                        options = incorrect_options[:3] + [answer]
                    else:
                        # Si no hay suficientes opciones, duplicar algunas
                        options = incorrect_options + [answer]
                        while len(options) < 4:
                            if incorrect_options:
                                options.append(random.choice(incorrect_options))
                            else:
                                # Si no hay opciones incorrectas (muy improbable), rellenar con la respuesta
                                options.append(answer)
                    
                    # Mezclar las opciones
                    random.shuffle(options)
                    
                    # Guardar el índice de la respuesta correcta
                    self.correct_option_index = options.index(answer)
                    
                    # Actualizar los botones con las opciones
                    for i, option in enumerate(options):
                        if i < len(self.option_buttons):
                            self.option_buttons[i].config(text=option, state=tk.NORMAL, style="TButton")
                    
                except Exception as e:
                    logger.error(f"Error al generar opciones múltiples: {e}")
                    # En caso de error, simplemente usar opciones genéricas
                    for i in range(min(4, len(self.option_buttons))):
                        self.option_buttons[i].config(
                            text=f"Opción {i+1}" if i != 0 else answer, 
                            state=tk.NORMAL, 
                            style="TButton"
                        )
                    self.correct_option_index = 0
                    
            logger.info(f"Pregunta cargada: {question} -> {answer}")
            
        except Exception as e:
            self.log_error(f"Error al cargar pregunta: {str(e)}")
    def check_answer(self, event=None):
        """Comprueba la respuesta escrita por el usuario"""
        try:
            user_answer = self.quiz_entry.get().strip().lower()
            
            if not user_answer:
                messagebox.showinfo("Respuesta vacía", "Por favor, escribe una respuesta.")
                return
                
            correct_answer = self.current_quiz_answer.lower()
            
            # Registrar en estudio
            current_char = self.current_quiz_question
            if current_char not in self.study_history:
                self.study_history[current_char] = {
                    "times_shown": 0, 
                    "correct": 0, 
                    "incorrect": 0,
                    "last_shown": datetime.now().isoformat()
                }
            else:
                self.study_history[current_char]["last_shown"] = datetime.now().isoformat()
            
            # Añadir a la lista de caracteres estudiados para logros
            if current_char not in self.achievement_data['studied_chars']:
                self.achievement_data['studied_chars'].append(current_char)
            
            # Procesar resultado con SRS si está activado
            is_correct = user_answer == correct_answer
            if self.srs_mode.get():
                self.srs_scheduler.calculate_next_review(
                    self.study_history[current_char], is_correct)
            
            if is_correct:
                self.quiz_result_var.set("¡Correcto!")
                self.last_answer_correct = True
                self.score += 1
                self.streak += 1
                self.max_streak = max(self.max_streak, self.streak)
                self.study_history[current_char]["correct"] += 1
                
                # Actualizar estadísticas para logros
                self.achievement_data['max_streak'] = max(
                    self.achievement_data['max_streak'], self.streak)
                
                # Si era difícil y se responde correctamente 3 veces seguidas, lo quitamos de difíciles
                if current_char in self.difficult_characters:
                    if not hasattr(self, 'correct_answers_count'):
                        self.correct_answers_count = {}
                    
                    self.correct_answers_count[current_char] = self.correct_answers_count.get(current_char, 0) + 1
                    
                    if self.correct_answers_count.get(current_char, 0) >= 3:
                        self.difficult_characters.remove(current_char)
                        self.update_difficult_chars_display()
                        messagebox.showinfo("¡Mejorado!", 
                                           f"El carácter '{current_char}' ya no está marcado como difícil después de 3 respuestas correctas.")
                        self.correct_answers_count[current_char] = 0
            else:
                self.quiz_result_var.set(f"Incorrecto. La respuesta es: {correct_answer}")
                self.last_answer_correct = False
                self.streak = 0
                self.study_history[current_char]["incorrect"] += 1
                
                # Marcar automáticamente como difícil
                if self.quiz_direction.get() == "hira_to_rom":
                    self.difficult_characters.add(current_char)
                else:
                    # Buscar el hiragana correspondiente al romanji
                    for cat in self.hiragana_categories.values():
                        for h, r in cat:
                            if r == current_char:
                                self.difficult_characters.add(h)
                                break
                
                self.update_difficult_chars_display()
                
                # Resetear contadores de aciertos consecutivos
                if hasattr(self, 'correct_answers_count') and current_char in self.correct_answers_count:
                    self.correct_answers_count[current_char] = 0
            
            # Actualizar estadísticas
            self.study_history[current_char]["times_shown"] += 1
            self.total_attempts += 1
            self.update_quiz_stats()
            
            # Verificar logro de quiz perfecto (20+ preguntas con 100% acierto)
            if (self.score >= 20 and self.score == self.total_attempts and 
                self.achievement_data['perfect_quiz_count'] == 0):
                self.achievement_data['perfect_quiz_count'] = 1
                self.check_achievements()
            
            # Deshabilitar el botón de enviar y habilitar el de siguiente
            self.submit_btn.config(state=tk.DISABLED)
            self.next_btn.config(state=tk.NORMAL)
            self.next_btn.focus_set()
        except Exception as e:
            self.log_error(f"Error al comprobar respuesta: {str(e)}")
    
    def check_answer_from_button(self, selected_idx):
        """Comprueba la respuesta seleccionada directamente con un botón"""
        try:
            # Deshabilitar todos los botones
            for btn in self.option_buttons:
                btn.config(state=tk.DISABLED)
            
            # Obtener la respuesta seleccionada
            selected_text = self.option_buttons[selected_idx].cget("text")
            correct_text = self.current_quiz_answer
            
            # Registrar en estudio
            current_char = self.current_quiz_question
            if current_char not in self.study_history:
                self.study_history[current_char] = {
                    "times_shown": 0, 
                    "correct": 0, 
                    "incorrect": 0,
                    "last_shown": datetime.now().isoformat()
                }
            else:
                self.study_history[current_char]["last_shown"] = datetime.now().isoformat()
            
            # Añadir a la lista de caracteres estudiados para logros
            if current_char not in self.achievement_data['studied_chars']:
                self.achievement_data['studied_chars'].append(current_char)
                
            # Determinar si la respuesta es correcta
            is_correct = selected_text == correct_text
            
            # Procesar resultado con SRS si está activado
            if self.srs_mode.get():
                self.srs_scheduler.calculate_next_review(
                    self.study_history[current_char], is_correct)
                    
            # Comprobar si es correcta
            if is_correct:
                # Respuesta correcta
                self.quiz_result_var.set("¡Correcto!")
                self.last_answer_correct = True
                self.score += 1
                self.streak += 1
                self.max_streak = max(self.max_streak, self.streak)
                self.study_history[current_char]["correct"] += 1
                
                # Actualizar estadísticas para logros
                self.achievement_data['max_streak'] = max(
                    self.achievement_data['max_streak'], self.streak)
                
                # Cambiar color del botón
                self.option_buttons[selected_idx].config(style="Correct.TButton")
                
                # Si era difícil y se responde correctamente 3 veces seguidas
                if current_char in self.difficult_characters:
                    if not hasattr(self, 'correct_answers_count'):
                        self.correct_answers_count = {}
                    
                    self.correct_answers_count[current_char] = self.correct_answers_count.get(current_char, 0) + 1
                    
                    if self.correct_answers_count.get(current_char, 0) >= 3:
                        self.difficult_characters.remove(current_char)
                        self.update_difficult_chars_display()
                        messagebox.showinfo("¡Mejorado!", 
                                           f"El carácter '{current_char}' ya no está marcado como difícil después de 3 respuestas correctas.")
                        self.correct_answers_count[current_char] = 0
            else:
                # Respuesta incorrecta
                self.quiz_result_var.set(f"Incorrecto. La respuesta es: {correct_text}")
                self.last_answer_correct = False
                self.streak = 0
                self.study_history[current_char]["incorrect"] += 1
                
                # Marcar como difícil
                if self.quiz_direction.get() == "hira_to_rom":
                    self.difficult_characters.add(current_char)
                else:
                    # Buscar el hiragana correspondiente al romanji
                    for cat in self.hiragana_categories.values():
                        for h, r in cat:
                            if r == current_char:
                                self.difficult_characters.add(h)
                                break
                
                # Resaltar visualmente la respuesta incorrecta y la correcta
                self.option_buttons[selected_idx].config(style="Incorrect.TButton")
                
                # Buscar y resaltar la opción correcta
                self.option_buttons[self.correct_option_index].config(style="Correct.TButton")
                
                # Resetear contadores de aciertos consecutivos
                if hasattr(self, 'correct_answers_count') and current_char in self.correct_answers_count:
                    self.correct_answers_count[current_char] = 0
            
            # Actualizar estadísticas
            self.study_history[current_char]["times_shown"] += 1
            self.total_attempts += 1
            self.update_quiz_stats()
            
            # Verificar logro de quiz perfecto
            if (self.score >= 20 and self.score == self.total_attempts and 
                self.achievement_data['perfect_quiz_count'] == 0):
                self.achievement_data['perfect_quiz_count'] = 1
                self.check_achievements()
            
            # Avanzar automáticamente después de un tiempo
            self.root.after(1500, self.next_quiz_question)
        except Exception as e:
            self.log_error(f"Error al comprobar opción: {str(e)}")
            self.next_quiz_question()
    
    def next_quiz_question(self):
        """Carga la siguiente pregunta de quiz"""
        self.load_quiz_question()
    
    def update_quiz_stats(self):
        """Actualiza las estadísticas del quiz en la interfaz"""
        self.correct_var.set(str(self.score))
        self.attempts_var.set(str(self.total_attempts))
        
        if self.total_attempts > 0:
            accuracy = (self.score / self.total_attempts) * 100
            self.accuracy_var.set(f"{accuracy:.1f}%")
            
            # Actualizar barra de progreso
            if hasattr(self, 'quiz_progress_bar'):
                self.quiz_progress_bar['value'] = accuracy
        else:
            self.accuracy_var.set("0%")
            if hasattr(self, 'quiz_progress_bar'):
                self.quiz_progress_bar['value'] = 0
                
        self.streak_var.set(str(self.streak))
    
    def reset_quiz(self):
        """Reinicia las estadísticas del quiz actual y comienza uno nuevo"""
        if messagebox.askyesno("Confirmar", "¿Quieres reiniciar las estadísticas del quiz actual?"):
            self.score = 0
            self.total_attempts = 0
            self.streak = 0
            
            # Actualizar estadísticas
            self.update_quiz_stats()
            
            # Cargar nueva pregunta
            self.load_quiz_question()
    
    # ==== Funciones de estadísticas y logros ====
    
    def update_stats_display(self):
        """Actualiza la visualización de estadísticas en la pestaña correspondiente"""
        try:
            # Estadísticas generales
            total_shown = sum(char_data.get("times_shown", 0) for char_data in self.study_history.values())
            total_correct = sum(char_data.get("correct", 0) for char_data in self.study_history.values())
            total_incorrect = sum(char_data.get("incorrect", 0) for char_data in self.study_history.values())
            
            # Calcular precisión solo si hay intentos
            if total_correct + total_incorrect > 0:
                accuracy = (total_correct / (total_correct + total_incorrect) * 100)
                accuracy_text = f"{accuracy:.1f}%"
            else:
                accuracy_text = "0.0%"
            
            # Calcular progreso total
            total_chars = len(self.achievement_data['all_hiragana'])
            studied_chars = len(self.study_history)
            progress_percent = (studied_chars / total_chars * 100) if total_chars > 0 else 0
            
            # Generar texto para mostrar
            general_stats_text = (
                f"Total de caracteres estudiados: {studied_chars}/{total_chars} ({progress_percent:.1f}%)\n"
                f"Total de repeticiones: {total_shown}\n"
                f"Respuestas correctas: {total_correct}\n"
                f"Respuestas incorrectas: {total_incorrect}\n"
                f"Precisión general: {accuracy_text}\n"
                f"Mejor racha: {self.max_streak}\n"
                f"Caracteres difíciles: {len(self.difficult_characters)}\n\n"
                f"Tiempo total de estudio: {self.achievement_data['total_study_time']:.1f} horas\n"
                f"Sesiones completadas: {self.achievement_data['sessions_completed']}\n"
                f"Logros desbloqueados: {sum(1 for a in self.achievements if a.unlocked)}/{len(self.achievements)}"
            )
            
            self.general_stats.config(state=tk.NORMAL)
            self.general_stats.delete(1.0, tk.END)
            self.general_stats.insert(tk.END, general_stats_text)
            self.general_stats.config(state=tk.DISABLED)
            
            # Estadísticas por categoría
            category_stats_text = ""
            
            # Recopilar estadísticas por categoría
            category_data = {}
            for category, hiragana_list in self.hiragana_categories.items():
                category_correct = 0
                category_total = 0
                category_studied = 0
                
                for hiragana, _ in hiragana_list:
                    if hiragana in self.study_history:
                        char_data = self.study_history[hiragana]
                        category_correct += char_data.get("correct", 0)
                        category_total += char_data.get("correct", 0) + char_data.get("incorrect", 0)
                        category_studied += 1
                
                category_accuracy = 0
                if category_total > 0:
                    category_accuracy = (category_correct / category_total) * 100
                
                category_progress = (category_studied / len(hiragana_list)) * 100
                
                # Guardar datos para logros
                if category not in self.achievement_data['category_stats']:
                    self.achievement_data['category_stats'][category] = {}
                    
                self.achievement_data['category_stats'][category]['accuracy'] = category_accuracy
                self.achievement_data['category_stats'][category]['progress'] = category_progress
                
                category_stats_text += (
                    f"{category}:\n"
                    f"  Progreso: {category_studied}/{len(hiragana_list)} ({category_progress:.1f}%)\n"
                    f"  Precisión: {category_accuracy:.1f}%\n\n"
                )
            
            self.category_stats.config(state=tk.NORMAL)
            self.category_stats.delete(1.0, tk.END)
            self.category_stats.insert(tk.END, category_stats_text)
            self.category_stats.config(state=tk.DISABLED)
            
            # Lista de caracteres difíciles
            difficult_text = ""
            
            if self.difficult_characters:
                # Ordenar los caracteres difíciles por tasa de error
                difficult_with_data = []
                for char in self.difficult_characters:
                    if char in self.study_history:
                        char_data = self.study_history[char]
                        total = char_data.get("correct", 0) + char_data.get("incorrect", 0)
                        error_rate = char_data.get("incorrect", 0) / total if total > 0 else 0
                        difficult_with_data.append((char, error_rate))
                    else:
                        difficult_with_data.append((char, 0))
                
                # Ordenar por tasa de error (mayor primero)
                difficult_with_data.sort(key=lambda x: x[1], reverse=True)
                
                for i, (char, error_rate) in enumerate(difficult_with_data):
                    # Formatear para mostrar organizadamente en columnas
                    difficult_text += f"{char} ({error_rate*100:.0f}%)\t"
                    if (i + 1) % 5 == 0:
                        difficult_text += "\n"
            else:
                difficult_text = "No hay caracteres marcados como difíciles."
            
            self.difficult_stats.config(state=tk.NORMAL)
            self.difficult_stats.delete(1.0, tk.END)
            self.difficult_stats.insert(tk.END, difficult_text)
            self.difficult_stats.config(state=tk.DISABLED)
            
            # Verificar logros después de actualizar estadísticas
            self.check_achievements()
            
        except Exception as e:
            self.log_error(f"Error al actualizar estadísticas: {str(e)}")
    
    def check_achievements(self):
        """Verifica si se ha desbloqueado algún logro nuevo"""
        newly_unlocked = []
        
        for achievement in self.achievements:
            if not achievement.unlocked and achievement.check_condition(self.achievement_data):
                newly_unlocked.append(achievement)
        
        # Mostrar notificación solo si hay logros nuevos y está configurado para mostrarlas
        if newly_unlocked and getattr(self, 'show_notif_var', tk.BooleanVar(value=True)).get():
            self.show_achievements_notification(newly_unlocked)
    
    def show_achievements_notification(self, unlocked_achievements):
        """Muestra una notificación de logros desbloqueados"""
        if not unlocked_achievements:
            return
            
        achievements_text = "\n".join(f"• {a.title}: {a.description}" for a in unlocked_achievements)
        
        notification = tk.Toplevel(self.root)
        notification.title("¡Logros desbloqueados!")
        notification.geometry("400x300")
        notification.transient(self.root)
        notification.grab_set()
        
        # Contenido
        content_frame = ttk.Frame(notification, padding=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(
            content_frame, 
            text="¡Felicidades!", 
            font=("Arial", 16, "bold")
        ).pack(pady=(0, 10))
        
        ttk.Label(
            content_frame,
            text="Has desbloqueado los siguientes logros:",
            font=("Arial", 12)
        ).pack(pady=(0, 10))
        
        # Texto de logros con scroll
        achievements_frame = ttk.Frame(content_frame)
        achievements_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        scrollbar = ttk.Scrollbar(achievements_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        achievements_text_widget = tk.Text(
            achievements_frame,
            wrap=tk.WORD,
            height=6,
            yscrollcommand=scrollbar.set
        )
        achievements_text_widget.pack(fill=tk.BOTH, expand=True)
        achievements_text_widget.insert(tk.END, achievements_text)
        achievements_text_widget.config(state=tk.DISABLED)
        
        scrollbar.config(command=achievements_text_widget.yview)
        
        # Botón de cerrar
        ttk.Button(
            content_frame,
            text="¡Genial!",
            command=notification.destroy,
            style="Primary.TButton"
        ).pack(pady=10)
    
    def show_achievements(self):
        """Muestra una ventana con todos los logros disponibles"""
        achievements_window = tk.Toplevel(self.root)
        achievements_window.title("Logros")
        achievements_window.geometry("600x500")
        achievements_window.transient(self.root)
        achievements_window.grab_set()
        
        # Contenido
        content_frame = ttk.Frame(achievements_window, padding=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(
            content_frame, 
            text="Tus logros", 
            font=("Arial", 18, "bold")
        ).pack(pady=(0, 20))
        
        # Lista de logros con scroll
        achievements_frame = ttk.Frame(content_frame)
        achievements_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(achievements_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        canvas = tk.Canvas(achievements_frame, yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=canvas.yview)
        
        # Frame para los logros dentro del canvas
        inner_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=inner_frame, anchor='nw')
        
        # Agregar logros
        for i, achievement in enumerate(self.achievements):
            achievement_frame = ttk.Frame(inner_frame, style="TFrame")
            achievement_frame.pack(fill=tk.X, pady=5, padx=5)
            
            # Borde dependiendo de si está desbloqueado
            if achievement.unlocked:
                border_frame = ttk.Frame(achievement_frame, relief=tk.RIDGE, padding=10, style="Correct.TFrame")
            else:
                border_frame = ttk.Frame(achievement_frame, relief=tk.RIDGE, padding=10)
            border_frame.pack(fill=tk.X)
            
            # Contenido del logro
            title_frame = ttk.Frame(border_frame)
            title_frame.pack(fill=tk.X)
            
            # Título e icono de desbloqueado
            ttk.Label(
                title_frame, 
                text=achievement.title, 
                font=("Arial", 12, "bold")
            ).pack(side=tk.LEFT)
            
            if achievement.unlocked:
                ttk.Label(
                    title_frame,
                    text="✓ Desbloqueado",
                    foreground="green"
                ).pack(side=tk.RIGHT)
            else:
                ttk.Label(
                    title_frame,
                    text="🔒 Bloqueado",
                    foreground="gray"
                ).pack(side=tk.RIGHT)
            
            # Descripción
            ttk.Label(
                border_frame,
                text=achievement.description,
                wraplength=500
            ).pack(fill=tk.X, pady=(5, 0))
            
            # Fecha de desbloqueo si está disponible
            if achievement.unlocked and achievement.unlock_date:
                unlock_date = datetime.fromisoformat(achievement.unlock_date)
                date_str = unlock_date.strftime("%d/%m/%Y %H:%M")
                ttk.Label(
                    border_frame,
                    text=f"Desbloqueado el {date_str}",
                    font=("Arial", 8),
                    foreground="gray"
                ).pack(anchor=tk.E)
        
        # Actualizar scrollregion
        inner_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))
        
        # Botón de cerrar
        ttk.Button(
            content_frame,
            text="Cerrar",
            command=achievements_window.destroy
        ).pack(pady=10)
    
    def show_stats_graphs(self):
        """Muestra gráficos de estadísticas"""
        try:
            # Verificar si matplotlib está instalado
            try:
                import matplotlib.pyplot as plt
                from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
                import matplotlib as mpl
                
                # Configurar fuente que soporte caracteres japoneses
                plt.rcParams['font.family'] = 'Arial Unicode MS, Meiryo, MS Gothic, sans-serif'
                
            except ImportError:
                messagebox.showinfo("Matplotlib requerido", 
                                "Para ver gráficos, instala matplotlib con: pip install matplotlib")
                return
            
            # Crear ventana para gráficos
            graph_window = tk.Toplevel(self.root)
            graph_window.title("Gráficos de Estadísticas")
            graph_window.geometry("800x600")
            
            # Notebook para múltiples gráficos
            graph_notebook = ttk.Notebook(graph_window)
            graph_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Tab de precisión por categoría
            category_tab = ttk.Frame(graph_notebook)
            graph_notebook.add(category_tab, text="Precisión por Categoría")
            
            # Preparar datos
            categories = list(self.hiragana_categories.keys())
            accuracies = []
            
            for category in categories:
                if category in self.achievement_data['category_stats']:
                    accuracies.append(self.achievement_data['category_stats'][category].get('accuracy', 0))
                else:
                    accuracies.append(0)
            
            # Crear figura
            fig1, ax1 = plt.subplots(figsize=(8, 4))
            bars = ax1.bar(categories, accuracies, color=['skyblue', 'lightgreen', 'lightcoral'])
            
            # Añadir etiquetas
            ax1.set_ylabel('Precisión (%)')
            ax1.set_title('Precisión por Categoría de Hiragana')
            ax1.set_ylim(0, 100)
            
            # Añadir valores encima de las barras
            for bar in bars:
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.1f}%',
                        ha='center', va='bottom')
            
            # Mostrar en Tkinter
            canvas1 = FigureCanvasTkAgg(fig1, master=category_tab)
            canvas1.draw()
            canvas1.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            # Tab de progreso por categoría
            progress_tab = ttk.Frame(graph_notebook)
            graph_notebook.add(progress_tab, text="Progreso por Categoría")
            
            # Preparar datos
            progress_values = []
            for category in categories:
                if category in self.achievement_data['category_stats']:
                    progress_values.append(self.achievement_data['category_stats'][category].get('progress', 0))
                else:
                    progress_values.append(0)
            
            # Crear figura
            fig2, ax2 = plt.subplots(figsize=(8, 4))
            bars = ax2.bar(categories, progress_values, color=['skyblue', 'lightgreen', 'lightcoral'])
            
            # Añadir etiquetas
            ax2.set_ylabel('Progreso (%)')
            ax2.set_title('Progreso por Categoría de Hiragana')
            ax2.set_ylim(0, 100)
            
            # Añadir valores encima de las barras
            for bar in bars:
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.1f}%',
                        ha='center', va='bottom')
            
            # Mostrar en Tkinter
            canvas2 = FigureCanvasTkAgg(fig2, master=progress_tab)
            canvas2.draw()
            canvas2.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            # Tab de caracteres con más errores
            errors_tab = ttk.Frame(graph_notebook)
            graph_notebook.add(errors_tab, text="Caracteres con Más Errores")
            
            # Recopilar datos de caracteres con errores
            char_error_rates = []
            for char, data in self.study_history.items():
                times_shown = data.get("times_shown", 0)
                incorrect = data.get("incorrect", 0)
                
                if times_shown > 0 and incorrect > 0:
                    error_rate = incorrect / times_shown
                    char_error_rates.append((char, error_rate))
            
            # Ordenar por tasa de error y tomar los 10 peores
            char_error_rates.sort(key=lambda x: x[1], reverse=True)
            worst_chars = char_error_rates[:10]
            
            if worst_chars:
                chars = [c[0] for c in worst_chars]
                error_rates = [c[1] * 100 for c in worst_chars]
                
                # Usar etiquetas ASCII en lugar de caracteres japoneses para evitar problemas
                labels = [f'Char {i+1}' for i in range(len(chars))]
                
                # Crear figura
                fig3, ax3 = plt.subplots(figsize=(8, 4))
                bars = ax3.bar(labels, error_rates, color='lightcoral')
                
                # Añadir etiquetas
                ax3.set_ylabel('Tasa de Error (%)')
                ax3.set_title('Caracteres con Mayor Tasa de Error')
                ax3.set_ylim(0, 100)
                
                # Añadir los caracteres reales encima de las barras
                for i, bar in enumerate(bars):
                    height = bar.get_height()
                    ax3.text(bar.get_x() + bar.get_width()/2., height,
                            f'{chars[i]}\n{height:.1f}%',
                            ha='center', va='bottom')
                
                # Mostrar en Tkinter
                canvas3 = FigureCanvasTkAgg(fig3, master=errors_tab)
                canvas3.draw()
                canvas3.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            else:
                ttk.Label(errors_tab, text="No hay suficientes datos para mostrar esta gráfica.").pack(expand=True)
        except Exception as e:
            self.log_error(f"Error al generar gráficos: {str(e)}")
    
    def export_statistics(self, format_type="csv"):
        """Exporta las estadísticas a un archivo"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"hiragana_stats_{timestamp}.{format_type}"
            
            # Pedir al usuario la ubicación para guardar
            file_path = filedialog.asksaveasfilename(
                defaultextension=f".{format_type}",
                filetypes=[(f"{format_type.upper()} files", f"*.{format_type}")],
                initialfile=filename
            )
            
            if not file_path:
                return
            
            if format_type == "csv":
                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(["Carácter", "Veces mostrado", "Correctas", "Incorrectas", "Precisión", "Difícil"])
                    
                    for char, data in self.study_history.items():
                        times = data.get("times_shown", 0)
                        correct = data.get("correct", 0)
                        incorrect = data.get("incorrect", 0)
                        accuracy = (correct / (correct + incorrect) * 100) if (correct + incorrect) > 0 else 0
                        is_difficult = "Sí" if char in self.difficult_characters else "No"
                        
                        writer.writerow([char, times, correct, incorrect, f"{accuracy:.1f}%", is_difficult])
                    
                messagebox.showinfo("Exportación completa", f"Estadísticas exportadas a {file_path}")
            elif format_type == "json":
                export_data = {
                    "study_history": self.study_history,
                    "difficult_characters": list(self.difficult_characters),
                    "achievement_data": self.achievement_data,
                    "export_date": datetime.now().isoformat(),
                    "app_version": APP_VERSION
                }
                
                with open(file_path, 'w', encoding='utf-8') as jsonfile:
                    json.dump(export_data, jsonfile, ensure_ascii=False, indent=2)
                    
                messagebox.showinfo("Exportación completa", f"Datos exportados a {file_path}")
        except Exception as e:
            self.log_error(f"Error al exportar estadísticas: {str(e)}")
    
    def import_data(self):
        """Importa datos de un archivo JSON"""
        try:
            file_path = filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json")],
                title="Selecciona un archivo de datos para importar"
            )
            
            if not file_path:
                return
                
            with open(file_path, 'r', encoding='utf-8') as jsonfile:
                import_data = json.load(jsonfile)
            
            # Verificar si es un archivo de datos válido
            if "study_history" not in import_data:
                messagebox.showerror("Error de importación", "El archivo no contiene datos válidos.")
                return
            
            # Confirmar importación
            if not messagebox.askyesno("Confirmar importación", 
                                     "¿Estás seguro de importar estos datos? Se sobrescribirán tus datos actuales."):
                return
                
            # Importar datos
            self.study_history = import_data.get("study_history", {})
            
            if "difficult_characters" in import_data:
                self.difficult_characters = set(import_data["difficult_characters"])
            
            if "achievement_data" in import_data:
                self.achievement_data = import_data["achievement_data"]
            
            # Actualizar interfaz
            self.update_difficult_chars_display()
            self.update_stats_display()
            
            # Verificar logros
            self.check_achievements()
            
            messagebox.showinfo("Importación completa", "Datos importados correctamente.")
        except Exception as e:
            self.log_error(f"Error al importar datos: {str(e)}")
    
    def reset_all_stats(self):
        """Reinicia todas las estadísticas y el historial de estudio"""
        if messagebox.askyesno("Confirmar", 
                             "¿Estás seguro de que quieres reiniciar TODAS las estadísticas?\n\n"
                             "Esto borrará todo el historial de estudio, la lista de caracteres difíciles "
                             "y el progreso de los logros.",
                             icon=messagebox.WARNING):
            # Reiniciar estadísticas actuales
            self.score = 0
            self.total_attempts = 0
            self.streak = 0
            self.max_streak = 0
            self.session_chars_shown = 0
            self.session_start_time = datetime.now()
            
            # Reiniciar historial de estudio
            self.study_history = {}
            
            # Limpiar caracteres difíciles
            self.difficult_characters.clear()
            self.update_difficult_chars_display()
            
            # Reiniciar logros
            for achievement in self.achievements:
                achievement.unlocked = False
                achievement.unlock_date = None
            
            # Reiniciar datos de logros
            self.achievement_data = {
                'sessions_completed': 0,
                'perfect_quiz_count': 0,
                'max_streak': 0,
                'study_dates': [],
                'total_study_time': 0,
                'category_stats': {},
                'all_hiragana': self.achievement_data['all_hiragana'],
                'studied_chars': []
            }
            
            # Actualizar estadísticas
            self.update_quiz_stats()
            self.update_session_stats()
            self.update_stats_display()
            
            # Guardar datos reiniciados
            self.save_data()
            
            messagebox.showinfo("Completado", "Todas las estadísticas han sido reiniciadas.")
    
    # ==== Funciones de configuración ====
    
    def toggle_srs_mode(self):
        """Activa o desactiva el modo de repetición espaciada"""
        if self.srs_mode.get():
            messagebox.showinfo("Sistema SRS", 
                               "Sistema de Repetición Espaciada activado.\n\n"
                               "Los caracteres se mostrarán según un horario optimizado basado en tu rendimiento.")
        else:
            messagebox.showinfo("Sistema SRS", "Sistema de Repetición Espaciada desactivado.")
    
    def change_theme(self, event=None):
        """Cambia el tema de la aplicación"""
        try:
            theme = self.theme_var.get()
            self.style.theme_use(theme)
            
            # Reconfigurar estilos personalizados para que coincidan con el tema
            self.setup_styles()
        except Exception as e:
            self.log_error(f"Error al cambiar tema: {str(e)}")
    
    def update_font_size(self, event=None):
        """Actualiza el tamaño de fuente para los caracteres"""
        try:
            size = self.font_size_var.get()
            self.hiragana_label.config(font=("Arial", size))
            self.quiz_char_label.config(font=("Arial", size))
        except Exception as e:
            logger.error(f"Error al actualizar tamaño de fuente: {str(e)}")
    
    def toggle_reminders(self):
        """Activa o desactiva los recordatorios de estudio"""
        if self.reminder_var.get():
            self.setup_study_plan()
        else:
            messagebox.showinfo("Recordatorios", "Recordatorios desactivados.")
    
    def setup_study_plan(self):
        """Configura el plan de estudio semanal"""
        plan_window = tk.Toplevel(self.root)
        plan_window.title("Planificar Estudio")
        plan_window.geometry("500x300")
        plan_window.transient(self.root)
        plan_window.grab_set()
        
        # Contenido
        content_frame = ttk.Frame(plan_window, padding=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(
            content_frame, 
            text="Planificación de Estudio", 
            font=("Arial", 14, "bold")
        ).pack(pady=(0, 10))
        
        # Días de estudio
        ttk.Label(content_frame, text="Días de estudio:").pack(anchor=tk.W, pady=(10, 5))
        
        days_frame = ttk.Frame(content_frame)
        days_frame.pack(fill=tk.X, pady=5)
        
        days = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        self.day_vars = {}
        
        for i, day in enumerate(days):
            self.day_vars[day] = tk.BooleanVar(value=False)
            ttk.Checkbutton(
                days_frame, 
                text=day, 
                variable=self.day_vars[day]
            ).grid(row=0, column=i, padx=2)
        
        # Hora de estudio
        time_frame = ttk.Frame(content_frame)
        time_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(time_frame, text="Hora del día:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.hour_var = tk.IntVar(value=18)
        self.minute_var = tk.IntVar(value=0)
        
        hour_spin = ttk.Spinbox(time_frame, from_=0, to=23, width=3, textvariable=self.hour_var)
        hour_spin.pack(side=tk.LEFT)
        
        ttk.Label(time_frame, text=":").pack(side=tk.LEFT)
        
        minute_spin = ttk.Spinbox(time_frame, from_=0, to=59, width=3, textvariable=self.minute_var)
        minute_spin.pack(side=tk.LEFT)
        
        # Duración
        duration_frame = ttk.Frame(content_frame)
        duration_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(duration_frame, text="Duración (minutos):").pack(side=tk.LEFT, padx=(0, 10))
        
        duration_spin = ttk.Spinbox(
            duration_frame, 
            from_=5, 
            to=60, 
            increment=5, 
            width=5, 
            textvariable=self.session_duration_var
        )
        duration_spin.pack(side=tk.LEFT)
        
        # Botones
        buttons_frame = ttk.Frame(content_frame)
        buttons_frame.pack(fill=tk.X, pady=20)
        
        ttk.Button(
            buttons_frame,
            text="Guardar plan",
            command=lambda: self.save_study_plan(plan_window),
            style="Primary.TButton"
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            buttons_frame,
            text="Cancelar",
            command=plan_window.destroy
        ).pack(side=tk.LEFT, padx=5)
    
    def save_study_plan(self, window):
        """Guarda el plan de estudio configurado"""
        try:
            # Verificar si hay al menos un día seleccionado
            selected_days = [day for day, var in self.day_vars.items() if var.get()]
            
            if not selected_days:
                messagebox.showinfo("Selección incompleta", "Por favor, selecciona al menos un día de estudio.")
                return
            
            # Guardar configuración de recordatorios
            self.study_plan = {
                "days": selected_days,
                "hour": self.hour_var.get(),
                "minute": self.minute_var.get(),
                "duration": self.session_duration_var.get()
            }
            
            # Configurar recordatorios
            self.setup_reminder_thread()
            
            messagebox.showinfo("Plan guardado", 
                               f"Plan de estudio configurado para los días: {', '.join(selected_days)} "
                               f"a las {self.hour_var.get():02}:{self.minute_var.get():02} "
                               f"durante {self.session_duration_var.get()} minutos.")
            
            window.destroy()
        except Exception as e:
            self.log_error(f"Error al guardar plan de estudio: {str(e)}")
    
    def setup_reminder_thread(self):
        """Configura un hilo para los recordatorios"""
        if hasattr(self, 'reminder_thread') and self.reminder_thread.is_alive():
            # Si ya hay un hilo activo, detenerlo
            self.stop_reminder_thread = True
        
        # Crear un nuevo hilo
        self.stop_reminder_thread = False
        self.reminder_thread = threading.Thread(target=self.reminder_worker, daemon=True)
        self.reminder_thread.start()
    
    def reminder_worker(self):
        """Función para el hilo de recordatorios"""
        try:
            weekdays = {
                "Lunes": 0, "Martes": 1, "Miércoles": 2, "Jueves": 3,
                "Viernes": 4, "Sábado": 5, "Domingo": 6
            }
            
            study_days = [weekdays[day] for day in self.study_plan["days"]]
            study_hour = self.study_plan["hour"]
            study_minute = self.study_plan["minute"]
            
            while not getattr(self, 'stop_reminder_thread', False):
                now = datetime.now()
                
                # Verificar si es momento de recordatorio
                if (now.weekday() in study_days and 
                    now.hour == study_hour and 
                    now.minute == study_minute and 
                    now.second < 10):  # Dar un margen de 10 segundos
                    
                    # Enviar recordatorio
                    self.show_reminder()
                    
                    # Dormir por un minuto para no mostrar múltiples recordatorios
                    time.sleep(60)
                else:
                    # Verificar cada 30 segundos
                    time.sleep(30)
        except Exception as e:
            logger.error(f"Error en hilo de recordatorios: {str(e)}")
    
    def show_reminder(self):
        """Muestra una notificación de recordatorio de estudio"""
        try:
            # Traer la ventana principal al frente
            self.root.lift()
            self.root.attributes('-topmost', True)
            self.root.after_idle(self.root.attributes, '-topmost', False)
            
            # Mostrar recordatorio
            messagebox.showinfo("Recordatorio de estudio", 
                               f"¡Es hora de tu sesión de estudio de hiragana!\n\n"
                               f"Duración programada: {self.study_plan['duration']} minutos\n\n"
                               f"¡Continúa con tu buen trabajo!")
        except Exception as e:
            logger.error(f"Error al mostrar recordatorio: {str(e)}")
    
    def save_settings(self):
        """Guarda la configuración actual"""
        try:
            settings = {
                "theme": self.theme_var.get(),
                "font_size": self.font_size_var.get(),
                "auto_save": self.auto_save_var.get(),
                "show_notifications": self.show_notif_var.get(),
                "algorithm": self.algo_var.get(),
                "session_duration": self.session_duration_var.get(),
                "chars_per_session": self.chars_per_session_var.get(),
                "reminder_enabled": self.reminder_var.get()
            }
            
            # Guardar plan de estudio si está configurado
            if hasattr(self, 'study_plan'):
                settings["study_plan"] = self.study_plan
                
            # Guardar configuración en archivo
            with open("hiragana_settings.json", "w", encoding="utf-8") as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
                
            messagebox.showinfo("Configuración", "Configuración guardada correctamente.")
        except Exception as e:
            self.log_error(f"Error al guardar configuración: {str(e)}")
    
    def load_settings(self):
        """Carga la configuración guardada"""
        try:
            if os.path.exists("hiragana_settings.json"):
                with open("hiragana_settings.json", "r", encoding="utf-8") as f:
                    settings = json.load(f)
                
                # Aplicar configuración
                if "theme" in settings:
                    self.theme_var.set(settings["theme"])
                    self.change_theme()
                
                if "font_size" in settings:
                    self.font_size_var.set(settings["font_size"])
                    self.update_font_size()
                
                if "auto_save" in settings:
                    self.auto_save_var.set(settings["auto_save"])
                
                if "show_notifications" in settings:
                    self.show_notif_var.set(settings["show_notifications"])
                
                if "algorithm" in settings:
                    self.algo_var.set(settings["algorithm"])
                
                if "session_duration" in settings:
                    self.session_duration_var.set(settings["session_duration"])
                
                if "chars_per_session" in settings:
                    self.chars_per_session_var.set(settings["chars_per_session"])
                
                if "reminder_enabled" in settings:
                    self.reminder_var.set(settings["reminder_enabled"])
                    
                    # Configurar recordatorios si están activados
                    if self.reminder_var.get() and "study_plan" in settings:
                        self.study_plan = settings["study_plan"]
                        self.setup_reminder_thread()
        except Exception as e:
            logger.error(f"Error al cargar configuración: {str(e)}")
    
    def reset_settings(self):
        """Restaura la configuración a los valores predeterminados"""
        if messagebox.askyesno("Confirmar", "¿Restaurar toda la configuración a los valores predeterminados?"):
            # Valores predeterminados
            self.theme_var.set("clam")
            self.font_size_var.set(120)
            self.auto_save_var.set(True)
            self.show_notif_var.set(True)
            self.algo_var.set("Estándar")
            self.session_duration_var.set(15)
            self.chars_per_session_var.set(20)
            self.reminder_var.set(False)
            
            # Aplicar cambios
            self.change_theme()
            self.update_font_size()
            
            # Detener recordatorios si están activos
            if hasattr(self, 'reminder_thread') and self.reminder_thread.is_alive():
                self.stop_reminder_thread = True
            
            # Guardar configuración
            self.save_settings()
            
            messagebox.showinfo("Configuración", "Valores predeterminados restaurados.")
    
    # ==== Funciones inteligentes y avanzadas ====
    
    def generate_smart_session(self):
        """Genera una sesión de estudio inteligente basada en el rendimiento"""
        try:
            # Identificar caracteres con mayor tasa de error
            chars_with_errors = []
            
            for char, data in self.study_history.items():
                if data.get("times_shown", 0) > 0:
                    correct = data.get("correct", 0)
                    incorrect = data.get("incorrect", 0)
                    total = correct + incorrect
                    
                    if total > 0:
                        error_rate = incorrect / total
                        chars_with_errors.append((char, error_rate))
            
            # Ordenar por tasa de error (mayor primero)
            chars_with_errors.sort(key=lambda x: x[1], reverse=True)
            
            # Número de caracteres por sesión (configurable)
            chars_per_session = getattr(self, 'chars_per_session_var', tk.IntVar(value=20)).get()
            
            # Decidir qué caracteres incluir en la sesión
            session_chars = []
            
            # 60% de caracteres con más errores
            error_count = min(int(chars_per_session * 0.6), len(chars_with_errors))
            if error_count > 0:
                problem_chars = [c for c, _ in chars_with_errors[:error_count]]
                for cat in self.hiragana_categories.values():
                    for pair in cat:
                        if pair[0] in problem_chars and pair not in session_chars:
                            session_chars.append(pair)
            
            # 20% de caracteres poco practicados
            least_practiced = []
            for cat in self.hiragana_categories.values():
                for pair in cat:
                    char = pair[0]
                    times_shown = self.study_history.get(char, {}).get("times_shown", 0)
                    least_practiced.append((pair, times_shown))
            
            least_practiced.sort(key=lambda x: x[1])  # Ordenar por veces mostradas (menor primero)
            
            # Agregar caracteres poco practicados que no estén ya en la sesión
            rare_count = min(int(chars_per_session * 0.2), len(least_practiced))
            for pair, _ in least_practiced[:rare_count]:
                if pair not in session_chars:
                    session_chars.append(pair)
            
            # 20% de caracteres aleatorios
            all_pairs = []
            for cat in self.hiragana_categories.values():
                all_pairs.extend(cat)
                
            # Mezclar y agregar caracteres restantes
            random.shuffle(all_pairs)
            for pair in all_pairs:
                if pair not in session_chars and len(session_chars) < chars_per_session:
                    session_chars.append(pair)
            
            # Crear sesión
            if session_chars:
                # Actualizar la lista de hiragana
                self.hiragana_list = session_chars
                self.current_index = 0
                
                # Mezclar para que no sean predecibles
                random.shuffle(self.hiragana_list)
                
                # Actualizar interfaz
                self.update_progress()
                self.session_chars_shown = 0
                
                # Mostrar mensaje informativo
                messagebox.showinfo("Sesión Inteligente", 
                                   f"Se ha creado una sesión inteligente con {len(session_chars)} caracteres.\n\n"
                                   f"Esta sesión incluye:\n"
                                   f"- Caracteres con mayor tasa de error\n"
                                   f"- Caracteres menos practicados\n"
                                   f"- Algunos caracteres aleatorios para variedad\n\n"
                                   f"Haz clic en 'Iniciar' para comenzar.")
                                   
                # Cambiar a la pestaña de tarjetas flash
                self.notebook.select(0)
            else:
                messagebox.showinfo("Sesión Inteligente", "No hay suficientes datos para generar una sesión inteligente.")
        except Exception as e:
            self.log_error(f"Error al generar sesión inteligente: {str(e)}")
    
    # ==== Funciones de ayuda y soporte ====
    
    def show_help(self):
        """Muestra la guía de uso de la aplicación"""
        help_window = tk.Toplevel(self.root)
        help_window.title("Guía de Uso - Hiragana Trainer")
        help_window.geometry("700x500")
        
        # Frame principal con scroll
        main_frame = ttk.Frame(help_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Contenido con scroll
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Título
        ttk.Label(
            scrollable_frame, 
            text="Guía de Uso - Hiragana Trainer", 
            font=("Arial", 16, "bold")
        ).pack(pady=(0, 20))
        
        # Secciones de ayuda
        sections = [
            ("Tarjetas Flash", [
                "Selecciona las categorías que deseas estudiar.",
                "Ajusta el tiempo de visualización (1-10 segundos).",
                "Haz clic en 'Iniciar' para comenzar la práctica.",
                "La tarjeta mostrará primero el hiragana y luego su romanización.",
                "Usa las teclas de flecha para navegar manualmente entre caracteres.",
                "Marca caracteres como 'Difícil' o 'Fácil' según tu facilidad para recordarlos.",
                "Puedes ver ejemplos de palabras para cada carácter."
            ]),
            ("Modo Quiz", [
                "Elige entre escribir la respuesta o seleccionar entre opciones múltiples.",
                "Selecciona la dirección: Hiragana → Romanji o Romanji → Hiragana.",
                "Opcionalmente, practica solo los caracteres marcados como difíciles.",
                "El sistema registra tus aciertos y errores para mejorar tu aprendizaje.",
                "Después de 3 respuestas correctas consecutivas, un carácter difícil se marca como dominado."
            ]),
            ("Sistema SRS", [
                "El Sistema de Repetición Espaciada optimiza tu aprendizaje.",
                "Los caracteres que respondes correctamente se repasan con menos frecuencia.",
                "Los caracteres con errores se repasan más intensivamente.",
                "Esto maximiza la eficiencia de tu estudio a largo plazo."
            ]),
            ("Estadísticas", [
                "Visualiza tu progreso general y por categoría.",
                "Identifica los caracteres que más te cuestan.",
                "Exporta tus estadísticas para análisis externos.",
                "Visualiza gráficos de rendimiento y progreso."
            ]),
            ("Logros", [
                "Desbloquea logros a medida que avanzas en tu aprendizaje.",
                "Los logros son una forma divertida de medir tu progreso.",
                "Revisa tus logros desbloqueados y los pendientes en la sección correspondiente."
            ]),
            ("Configuración", [
                "Personaliza la apariencia de la aplicación.",
                "Ajusta el tamaño de fuente para mejor visibilidad.",
                "Configura recordatorios de estudio para mantener la constancia.",
                "Elige el algoritmo de aprendizaje que mejor se adapte a ti."
            ]),
            ("Atajos de Teclado", [
                "Espacio: Iniciar/Detener práctica",
                "Flecha derecha: Siguiente tarjeta",
                "Flecha izquierda: Tarjeta anterior",
                "D: Marcar como difícil",
                "F: Marcar como fácil",
                "E: Mostrar ejemplo",
                "Enter: Comprobar respuesta (en modo quiz)",
                "F1: Mostrar esta ayuda"
            ])
        ]
        
        # Crear secciones
        for title, items in sections:
            section_frame = ttk.LabelFrame(scrollable_frame, text=title, padding=10)
            section_frame.pack(fill=tk.X, pady=5)
            
            for item in items:
                ttk.Label(
                    section_frame, 
                    text=f"• {item}", 
                    wraplength=600,
                    justify=tk.LEFT
                ).pack(anchor=tk.W, pady=2)
        
        # Botón de cerrar
        ttk.Button(
            scrollable_frame,
            text="Cerrar",
            command=help_window.destroy
        ).pack(pady=20)
    
    def show_study_tips(self):
        """Muestra consejos de estudio para aprender hiragana"""
        tips_window = tk.Toplevel(self.root)
        tips_window.title("Consejos para Estudiar Hiragana")
        tips_window.geometry("700x500")
        
        # Frame principal con scroll
        main_frame = ttk.Frame(tips_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Contenido con scroll
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Título
        ttk.Label(
            scrollable_frame, 
            text="Consejos para Aprender Hiragana Eficientemente", 
            font=("Arial", 16, "bold")
        ).pack(pady=(0, 20))
        
        # Consejos
        tips = [
            ("Aprende por grupos lógicos", 
             "Estudia los caracteres por grupos (vocales, consonantes con la misma vocal, etc.) en lugar de aleatoriamente. "
             "Esto facilita reconocer patrones y similitudes."),
             
            ("Practica escritura y lectura", 
             "Complementa el uso de esta aplicación con práctica de escritura a mano. "
             "La memoria muscular ayuda significativamente al aprendizaje."),
             
            ("Usa mnemotécnicas", 
             "Asocia los caracteres con imágenes o formas que te ayuden a recordarlos. "
             "Por ejemplo,「め」(me) se parece a un ojo (めだま - medama)."),
             
            ("Consistencia sobre intensidad", 
             "Es mejor estudiar 15 minutos todos los días que 2 horas una vez por semana. "
             "La consistencia es clave para la memoria a largo plazo."),
             
            ("Contextualiza tu aprendizaje", 
             "Usa los ejemplos de palabras para dar contexto a los caracteres. "
             "Intenta crear oraciones simples con las palabras que aprendes."),
             
            ("Combina métodos de estudio", 
             "Alterna entre tarjetas flash, quiz y otros métodos para mantener el interés y "
             "aprovechar diferentes formas de memoria."),
             
            ("Repasa antes de dormir", 
             "Estudiar justo antes de acostarte ayuda a la consolidación de la memoria "
             "durante el sueño."),
             
            ("Explica lo aprendido", 
             "Enseñar o explicar a alguien más lo que has aprendido refuerza tu propio conocimiento."),
             
            ("Usa material auténtico", 
             "Cuando te sientas cómodo, intenta leer material simple en japonés como libros "
             "infantiles o manga para principiantes."),
             
            ("Aprovecha el Sistema SRS", 
             "El Sistema de Repetición Espaciada está basado en investigaciones científicas "
             "sobre la memoria. Confía en él para optimizar tus repasos."),
             
            ("Celebra tus logros", 
             "Reconoce y celebra tu progreso, por pequeño que sea. Ver cuánto has avanzado "
             "te motivará a seguir adelante.")
        ]
        
        for title, content in tips:
            tip_frame = ttk.Frame(scrollable_frame)
            tip_frame.pack(fill=tk.X, pady=10)
            
            ttk.Label(
                tip_frame, 
                text=title, 
                font=("Arial", 12, "bold")
            ).pack(anchor=tk.W)
            
            ttk.Label(
                tip_frame, 
                text=content, 
                wraplength=600,
                justify=tk.LEFT
            ).pack(anchor=tk.W, padx=10, pady=5)
        
        # Botón de cerrar
        ttk.Button(
            scrollable_frame,
            text="Cerrar",
            command=tips_window.destroy
        ).pack(pady=20)
    
    def show_about(self):
        """Muestra información sobre la aplicación"""
        about_window = tk.Toplevel(self.root)
        about_window.title("Acerca de Hiragana Trainer")
        about_window.geometry("500x400")
        about_window.transient(self.root)
        
        # Contenido
        content_frame = ttk.Frame(about_window, padding=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Logo (simulado con texto)
        ttk.Label(
            content_frame, 
            text="ひらがな\nトレーナー", 
            font=("Arial", 36, "bold"),
            foreground="#4a86e8"
        ).pack(pady=(0, 20))
        
        # Información
        ttk.Label(
            content_frame, 
            text=f"Hiragana Trainer v{APP_VERSION}", 
            font=("Arial", 14, "bold")
        ).pack()
        
        ttk.Label(
            content_frame, 
            text="Una aplicación para aprender y practicar hiragana japonés",
            wraplength=400
        ).pack(pady=5)
        
        ttk.Label(
            content_frame, 
            text="Desarrollado con ❤️ para estudiantes de japonés",
            foreground="#666666"
        ).pack(pady=10)
        
        # Separador
        ttk.Separator(content_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # Características
        ttk.Label(
            content_frame, 
            text="Características principales:",
            font=("Arial", 10, "bold"),
            justify=tk.LEFT
        ).pack(anchor=tk.W)
        
        features = [
            "Sistema de Repetición Espaciada (SRS)",
            "Múltiples modos de estudio",
            "Seguimiento detallado de progreso",
            "Algoritmo de aprendizaje adaptativo",
            "Ejemplos contextuales para cada carácter"
        ]
        
        features_text = "\n".join(f"• {feature}" for feature in features)
        ttk.Label(
            content_frame, 
            text=features_text,
            justify=tk.LEFT
        ).pack(anchor=tk.W, padx=10, pady=5)
        
        # Botones
        buttons_frame = ttk.Frame(content_frame)
        buttons_frame.pack(fill=tk.X, pady=20)
        
        ttk.Button(
            buttons_frame,
            text="Cerrar",
            command=about_window.destroy
        ).pack(side=tk.RIGHT)
        
        ttk.Button(
            buttons_frame,
            text="Sitio web",
            command=lambda: webbrowser.open("https://github.com/tuusuario/hiragana-trainer")
        ).pack(side=tk.LEFT)
        
        ttk.Button(
            buttons_frame,
            text="Reportar problema",
            command=lambda: webbrowser.open("https://github.com/tuusuario/hiragana-trainer/issues")
        ).pack(side=tk.LEFT, padx=5)
    
    def log_error(self, error_msg, show_to_user=True):
        """Registra un error en el log y muestra un mensaje al usuario si corresponde"""
        logger.error(error_msg)
        if show_to_user:
            messagebox.showerror("Error", error_msg)
    
    # ==== Funciones de carga/guardado de datos ====
    
    def load_data(self):
        """Carga los datos guardados de historial de estudio y configuración"""
        try:
            # Cargar datos de estudio
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    if 'difficult_characters' in data:
                        self.difficult_characters = set(data['difficult_characters'])
                        
                    if 'study_history' in data:
                        self.study_history = data['study_history']
                        
                    if 'max_streak' in data:
                        self.max_streak = data['max_streak']
                    
                    if 'achievements' in data:
                        # Cargar logros
                        achievement_data = data['achievements']
                        for a_data in achievement_data:
                            for achievement in self.achievements:
                                if achievement.id == a_data['id']:
                                    achievement.unlocked = a_data.get('unlocked', False)
                                    achievement.unlock_date = a_data.get('unlock_date')
                    
                    if 'achievement_data' in data:
                        # Preservar la lista de todos los caracteres hiragana
                        all_hiragana = self.achievement_data['all_hiragana']
                        self.achievement_data = data['achievement_data']
                        self.achievement_data['all_hiragana'] = all_hiragana
                
                # Actualizar visualización
                self.update_difficult_chars_display()
                self.update_stats_display()
                self.status_text.set("Datos cargados correctamente")
            
            # Cargar configuración
            self.load_settings()
        except Exception as e:
            self.log_error(f"Error al cargar datos: {e}")
    
    def save_data(self):
        """Guarda los datos de historial de estudio y configuración"""
        try:
            # Preparar datos para guardar
            achievement_data = [a.to_dict() for a in self.achievements]
            
            data = {
                'difficult_characters': list(self.difficult_characters),
                'study_history': self.study_history,
                'max_streak': self.max_streak,
                'achievements': achievement_data,
                'achievement_data': self.achievement_data,
                'app_version': APP_VERSION,
                'last_save': datetime.now().isoformat()
            }
            
            # Guardar en archivo
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # Guardar configuración
            self.save_settings()
                
            self.status_text.set("Datos guardados correctamente")
        except Exception as e:
            self.log_error(f"Error al guardar datos: {e}")
    
    def on_closing(self):
        """Acciones al cerrar la aplicación"""
        try:
            # Cancelar todos los temporizadores pendientes
            if hasattr(self, 'timer_id') and self.timer_id:
                try:
                    self.root.after_cancel(self.timer_id)
                except Exception:
                    pass
                
            if hasattr(self, 'session_timer_id') and self.session_timer_id:
                try:
                    self.root.after_cancel(self.session_timer_id)
                except Exception:
                    pass
            
            # Detener hilo de recordatorios si está activo
            if hasattr(self, 'reminder_thread') and self.reminder_thread.is_alive():
                self.stop_reminder_thread = True
            
            # Verificar si auto-guardado está activado
            should_save = True
            if hasattr(self, 'auto_save_var'):
                should_save = self.auto_save_var.get()
            
            # Guardar datos si corresponde
            if should_save:
                self.save_data()
            
            # Destruir ventana
            self.root.destroy()
        except Exception as e:
            logger.error(f"Error al cerrar aplicación: {e}")
            try:
                self.root.destroy()
            except Exception:
                pass
if __name__ == "__main__":
    import signal
    import sys
    
    # Función para manejar Ctrl+C
    def signal_handler(sig, frame):
        print("Cerrando la aplicación...")
        if 'app' in globals():
            app.on_closing()
        else:
            sys.exit(0)
    
    # Registrar el manejador para SIGINT (Ctrl+C)
    signal.signal(signal.SIGINT, signal_handler)
    
    root = tk.Tk()
    app = HiraganaTrainer(root)
    
    # Configurar evento de cierre
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Iniciar aplicación
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("Cerrando la aplicación...")
        app.on_closing()
