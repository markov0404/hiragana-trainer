def check_option(self, selected_idx):
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
            self.study_history[current_char] = {"times_shown": 0, "correct": 0, "incorrect": 0}
        
        # Comprobar si es correcta
        if selected_text == correct_text:
            # Respuesta correcta
            self.quiz_result_var.set("¡Correcto!")
            self.last_answer_correct = True
            self.score += 1
            self.streak += 1
            self.max_streak = max(self.max_streak, self.streak)
            self.study_history[current_char]["correct"] += 1
            
            # Cambiar color del botón
            self.option_buttons[selected_idx].config(style="Correct.TButton")
        else:
            # Respuesta incorrecta
            self.quiz_result_var.set(f"Incorrecto. La respuesta es: {correct_text}")
            self.last_answer_correct = False
            self.streak = 0
            self.study_history[current_char]["incorrect"] += 1
            
            # Marcar como difícil
            if self.quiz_direction.get() == "hira_to_rom":
                self.difficult_characters.add(current_char)
            
            # Resaltar visualmente la respuesta incorrecta y la correcta
            self.option_buttons[selected_idx].config(style="Incorrect.TButton")
            
            # Buscar y resaltar la opción correcta
            for i, btn in enumerate(self.option_buttons):
                if btn.cget("text") == correct_text:
                    btn.config(style="Correct.TButton")
                    break
        
        # Actualizar estadísticas
        self.study_history[current_char]["times_shown"] += 1
        self.total_attempts += 1
        self.update_quiz_stats()
        
        # Avanzar automáticamente después de un tiempo
        self.root.after(1500, self.next_quiz_question)
    except Exception as e:
        messagebox.showerror("Error", f"Error al comprobar opción: {str(e)}")
        self.next_quiz_question()

def check_answer_direct(self, selected_idx):
    """Comprueba la respuesta seleccionada directamente mediante un botón"""
    try:
        if not hasattr(self, 'correct_option_index'):
            return
            
        # Deshabilitar todos los botones temporalmente
        for btn in self.quiz_options_buttons:
            btn.config(state=tk.DISABLED)
        
        # Obtener el texto del botón seleccionado
        selected_answer = self.quiz_options_buttons[selected_idx].cget("text")
        correct_answer = self.current_quiz_answer
        
        # Registrar en estudio
        current_char = self.current_quiz_question
        if current_char not in self.study_history:
            self.study_history[current_char] = {"times_shown": 0, "correct": 0, "incorrect": 0}
        
        # Cambiar el color del botón seleccionado según sea correcto o incorrecto
        if selected_idx == self.correct_option_index:
            # Respuesta correcta
            self.style.configure(f"Correct.TButton", background="green")
            self.quiz_options_buttons[selected_idx].config(style="Correct.TButton")
            self.quiz_result_var.set("¡Correcto!")
            
            self.last_answer_correct = True
            self.score += 1
            self.streak += 1
            self.max_streak = max(self.max_streak, self.streak)
            self.study_history[current_char]["correct"] += 1
            
            # Mejorar con 3 aciertos seguidos
            if current_char in self.difficult_characters:
                if not hasattr(self, 'correct_answers_count'):
                    self.correct_answers_count = {}
                
                self.correct_answers_count[current_char] = self.correct_answers_count.get(current_char, 0) + 1
                
                if self.correct_answers_count.get(current_char, 0) >= 3:
                    self.difficult_characters.remove(current_char)
                    self.update_difficult_chars_display()
                    messagebox.showinfo("¡Mejorado!", f"El carácter '{current_char}' ya no está marcado como difícil después de 3 respuestas correctas.")
                    self.correct_answers_count[current_char] = 0
        else:
            # Respuesta incorrecta
            self.style.configure(f"Incorrect.TButton", background="red")
            self.quiz_options_buttons[selected_idx].config(style="Incorrect.TButton")
            
            # Destacar la respuesta correcta
            self.style.configure(f"Correct.TButton", background="green")
            self.quiz_options_buttons[self.correct_option_index].config(style="Correct.TButton")
            
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
                        if r == self.current_quiz_question:
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
        
        # Programar carga de siguiente pregunta después de un breve retraso
        self.root.after(1500, self.next_quiz_question)
        
    except Exception as e:
        messagebox.showerror("Error", f"Error al comprobar respuesta: {str(e)}")
        self.next_quiz_question()
            
def next_quiz_question(self):
    """Carga la siguiente pregunta de quiz"""
    self.load_quiz_question()
        
def toggle_order(self, is_random):
    """Cambia entre modo aleatorio y secuencial"""
    try:
        # Actualizar variable de modo aleatorio
        self.random_mode.set(is_random)
        
        # Aplicar el nuevo orden
        if is_random:
            self.randomize()
        else:
            # Detener la práctica actual si está en ejecución
            self.is_running = False
            self.start_button.config(text="Iniciar")
            
            # Reorganizar de forma secuencial por categorías
            self.update_hiragana_list()
            
            # Desactivar explícitamente el modo aleatorio
            self.random_mode.set(False)
            
            # Notificar al usuario
            messagebox.showinfo("Modo secuencial", "Lista ordenada por categorías.")
    except Exception as e:
        messagebox.showerror("Error", f"Error al cambiar el orden: {str(e)}")

from tkinter import ttk, messagebox
import random
import json
import os
from datetime import datetime, timedelta

import tkinter as tk
from tkinter import ttk, messagebox
import random
import json
import os
from datetime import datetime, timedelta

class HiraganaTrainer:
    def __init__(self, root):
        self.root = root
        self.root.title("Entrenador de Hiragana Avanzado")
        self.root.geometry("900x600")
        
        # Variables de control de modo
        self.in_difficult_mode = False  # Para controlar si estamos en modo difíciles
        
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
        
        # Variables
        self.hiragana_list = []
        self.current_index = 0
        self.show_romanji = False
        self.is_running = False
        self.delay_var = tk.DoubleVar(value=3.0)
        self.time_display = tk.StringVar(value="3.0")
        self.progress_var = tk.StringVar(value="0/0")
        self.score = 0
        self.total_attempts = 0
        self.streak = 0
        self.max_streak = 0
        self.difficult_characters = set()
        self.study_mode = tk.StringVar(value="flash")  # flash, quiz, inverse
        self.study_history = {}  # Para seguimiento del aprendizaje
        self.last_answer_correct = False
        self.session_start_time = datetime.now()
        self.session_chars_shown = 0
        
        # Variables para las categorías
        self.category_vars = {}
        for category in self.hiragana_categories:
            self.category_vars[category] = tk.BooleanVar(value=True)
        
        # Configuración de estilo
        self.style = ttk.Style()
        self.style.configure("TFrame", background="#f5f5f5")
        self.style.configure("TLabel", background="#f5f5f5")
        self.style.configure("TButton", padding=5)
        self.style.configure("TCheckbutton", background="#f5f5f5")
        self.style.configure("TNotebook", background="#f5f5f5")
        self.style.configure("TNotebook.Tab", padding=[10, 5], font=('Arial', 10))
        
        # Crear widgets
        self.setup_ui()
        
        # Actualizar la lista de hiragana seleccionados
        self.update_hiragana_list()
        
        # Cargar datos guardados
        self.load_data()
        
    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Notebook (pestañas)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # ===== Pestaña 1: Tarjetas Flash =====
        flash_tab = ttk.Frame(self.notebook)
        self.notebook.add(flash_tab, text="Tarjetas Flash")
        
        # Dividir en panel izquierdo y derecho
        flash_paned = ttk.PanedWindow(flash_tab, orient=tk.HORIZONTAL)
        flash_paned.pack(fill=tk.BOTH, expand=True)
        
        # Panel izquierdo (configuraciones)
        left_frame = ttk.Frame(flash_paned, padding=10)
        flash_paned.add(left_frame, weight=1)
        
        # Sección de categorías
        ttk.Label(left_frame, text="Categorías a practicar:", font=('Arial', 11, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        for category, var in self.category_vars.items():
            ttk.Checkbutton(
                left_frame, 
                text=category, 
                variable=var, 
                command=self.update_hiragana_list
            ).pack(anchor=tk.W, padx=5)
        
        # Sección de caracteres difíciles
        ttk.Separator(left_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        ttk.Label(left_frame, text="Caracteres difíciles:", font=('Arial', 11, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        
        self.diff_chars_frame = ttk.Frame(left_frame)
        self.diff_chars_frame.pack(fill=tk.X)
        
        ttk.Button(
            left_frame,
            text="Practicar solo difíciles",
            command=self.practice_difficult_only
        ).pack(anchor=tk.W, pady=5)
        
        # Control de tiempo
        ttk.Separator(left_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        ttk.Label(left_frame, text="Tiempo (segundos):", font=('Arial', 11, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        
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
        
        # Botones
        ttk.Separator(left_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        self.start_button = ttk.Button(
            left_frame, 
            text="Iniciar", 
            command=self.toggle_practice,
            width=15
        )
        self.start_button.pack(pady=5)
        
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
        
        # Gestión de caracteres difíciles
        ttk.Separator(left_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        ttk.Label(left_frame, text="Gestión de difíciles:", font=('Arial', 11, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        
        ttk.Button(
            left_frame,
            text="Practicar solo difíciles",
            command=self.practice_difficult_only,
            width=20
        ).pack(anchor=tk.W, pady=2)
        
        ttk.Button(
            left_frame,
            text="Limpiar lista difíciles",
            command=self.clear_difficult_chars,
            width=20
        ).pack(anchor=tk.W, pady=2)
        
        ttk.Button(
            left_frame,
            text="Actualizar lista actual",
            command=self.update_current_list,
            width=20
        ).pack(anchor=tk.W, pady=2)
        
        # Estadísticas
        ttk.Separator(left_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        ttk.Label(left_frame, text="Estadísticas de sesión:", font=('Arial', 11, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        
        stats_frame = ttk.Frame(left_frame)
        stats_frame.pack(fill=tk.X)
        
        self.stats_text = tk.Text(stats_frame, height=6, width=20, wrap=tk.WORD, relief=tk.GROOVE, font=('Arial', 9))
        self.stats_text.pack(fill=tk.X, expand=True)
        self.stats_text.config(state=tk.DISABLED)
        
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
        
        self.random_mode = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            random_frame,
            text="Modo aleatorio",
            variable=self.random_mode
        ).pack(side=tk.RIGHT)
        
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
            font=("Arial", 100),
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
            wraplength=500,  # Para que el texto se ajuste si es largo
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
            command=lambda: self.mark_difficult(True)
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            feedback_frame,
            text="Fácil",
            width=15,
            command=lambda: self.mark_difficult(False)
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            feedback_frame,
            text="Mostrar ejemplo",
            width=15,
            command=self.show_example
        ).pack(side=tk.LEFT, padx=5)
        
        # Barra de estado
        status_frame = ttk.Frame(right_frame)
        status_frame.pack(fill=tk.X)
        
        ttk.Label(status_frame, text="Progreso:").pack(side=tk.LEFT)
        ttk.Label(status_frame, textvariable=self.progress_var).pack(side=tk.LEFT, padx=5)
        
        # ===== Pestaña 2: Modo Quiz =====
        quiz_tab = ttk.Frame(self.notebook)
        self.notebook.add(quiz_tab, text="Modo Quiz")
        
        # Variables específicas del quiz
        self.quiz_mode = tk.StringVar(value="write")  # write, multiple
        self.quiz_direction = tk.StringVar(value="hira_to_rom")  # hira_to_rom, rom_to_hira
        
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
        
        self.quiz_difficult_only = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            extra_frame,
            text="Solo caracteres difíciles",
            variable=self.quiz_difficult_only,
            command=self.update_quiz_questions
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            extra_frame,
            text="Iniciar nuevo quiz",
            command=self.reset_quiz,
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
        
        ttk.Label(quiz_stats_frame, text="Aciertos:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.correct_var = tk.StringVar(value="0")
        ttk.Label(quiz_stats_frame, textvariable=self.correct_var).grid(row=0, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(quiz_stats_frame, text="Intentos:").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.attempts_var = tk.StringVar(value="0")
        ttk.Label(quiz_stats_frame, textvariable=self.attempts_var).grid(row=0, column=3, sticky=tk.W, padx=5)
        
        ttk.Label(quiz_stats_frame, text="Precisión:").grid(row=0, column=4, sticky=tk.W, padx=5)
        self.accuracy_var = tk.StringVar(value="0%")
        ttk.Label(quiz_stats_frame, textvariable=self.accuracy_var).grid(row=0, column=5, sticky=tk.W, padx=5)
        
        ttk.Label(quiz_stats_frame, text="Racha:").grid(row=0, column=6, sticky=tk.W, padx=5)
        self.streak_var = tk.StringVar(value="0")
        ttk.Label(quiz_stats_frame, textvariable=self.streak_var).grid(row=0, column=7, sticky=tk.W, padx=5)
        
        # Variables para el modo de opción múltiple
        self.quiz_options_vars = []  # Para los radiobuttons
        self.quiz_option_var = tk.StringVar(value="")  # Para almacenar la selección
        
        # Crear la interfaz inicial
        self.update_quiz_interface()
        
        # ===== Pestaña 3: Estadísticas =====
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
        
        # Estadísticas generales
        general_frame = ttk.LabelFrame(stats_container, text="Estadísticas Generales", padding=10)
        general_frame.pack(fill=tk.X, pady=5)
        
        self.general_stats = tk.Text(general_frame, height=10, width=60, wrap=tk.WORD)
        self.general_stats.pack(fill=tk.X)
        self.general_stats.config(state=tk.DISABLED)
        
        # Progreso por categoría
        category_frame = ttk.LabelFrame(stats_container, text="Progreso por Categoría", padding=10)
        category_frame.pack(fill=tk.X, pady=5)
        
        self.category_stats = tk.Text(category_frame, height=10, width=60, wrap=tk.WORD)
        self.category_stats.pack(fill=tk.X)
        self.category_stats.config(state=tk.DISABLED)
        
        # Caracteres difíciles
        difficult_frame = ttk.LabelFrame(stats_container, text="Caracteres Difíciles", padding=10)
        difficult_frame.pack(fill=tk.X, pady=5)
        
        self.difficult_stats = tk.Text(difficult_frame, height=5, width=60, wrap=tk.WORD)
        self.difficult_stats.pack(fill=tk.X)
        self.difficult_stats.config(state=tk.DISABLED)
        
        # Botón para generar informe
        ttk.Button(
            stats_container,
            text="Actualizar Estadísticas",
            command=self.update_stats_display
        ).pack(pady=10)
        
        # Inicializar modo quiz
        self.load_quiz_question()
        
        # Configurar eventos de cambio de pestaña
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

        # Botón para reiniciar todas las estadísticas (justo después del botón "Actualizar Estadísticas")
        ttk.Button(
            stats_container,
            text="Reiniciar todas las estadísticas",
            command=self.reset_all_stats,
            style="Danger.TButton"  # Puedes crear este estilo para darle un color rojo de advertencia
        ).pack(pady=5)

        # Definir el estilo de botón peligroso (rojo)
        self.style.configure("Danger.TButton", foreground="white", background="red")
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
                self.study_history[current_char] = {"times_shown": 0, "correct": 0, "incorrect": 0}
            
            # Comprobar si es correcta
            if selected_text == correct_text:
                # Respuesta correcta
                self.quiz_result_var.set("¡Correcto!")
                self.last_answer_correct = True
                self.score += 1
                self.streak += 1
                self.max_streak = max(self.max_streak, self.streak)
                self.study_history[current_char]["correct"] += 1
                
                # Cambiar color del botón
                self.option_buttons[selected_idx].config(style="Correct.TButton")
            else:
                # Respuesta incorrecta
                self.quiz_result_var.set(f"Incorrecto. La respuesta es: {correct_text}")
                self.last_answer_correct = False
                self.streak = 0
                self.study_history[current_char]["incorrect"] += 1
                
                # Marcar como difícil
                if self.quiz_direction.get() == "hira_to_rom":
                    self.difficult_characters.add(current_char)
                
                # Resaltar visualmente la respuesta incorrecta y la correcta
                self.option_buttons[selected_idx].config(style="Incorrect.TButton")
                
                # Buscar y resaltar la opción correcta
                for i, btn in enumerate(self.option_buttons):
                    if btn.cget("text") == correct_text:
                        btn.config(style="Correct.TButton")
                        break
            
            # Actualizar estadísticas
            self.study_history[current_char]["times_shown"] += 1
            self.total_attempts += 1
            self.update_quiz_stats()
            
            # Avanzar automáticamente después de un tiempo
            self.root.after(1500, self.next_quiz_question)
        except Exception as e:
            messagebox.showerror("Error", f"Error al comprobar opción: {str(e)}")
            self.next_quiz_question()

    def update_time_display(self, *args):
        self.time_display.set(f"{self.delay_var.get():.1f}")
        
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
            messagebox.showerror("Error", f"Error al actualizar lista: {str(e)}")
    
    def update_progress(self):
        """Actualiza el indicador de progreso"""
        try:
            total = len(getattr(self, 'practice_list', []) or self.hiragana_list)
            current = self.current_index + 1 if total > 0 else 0
            self.progress_var.set(f"{current}/{total}")
        except Exception as e:
            self.progress_var.set("Error")
            print(f"Error al actualizar progreso: {str(e)}")
        
    def toggle_practice(self):
        """Inicia o detiene la práctica de hiragana"""
        try:
            if not self.hiragana_list:
                messagebox.showinfo("Sin caracteres", "No hay caracteres disponibles para practicar. Selecciona al menos una categoría.")
                return
                
            if self.is_running:
                self.is_running = False
                self.start_button.config(text="Iniciar")
            else:
                self.is_running = True
                self.start_button.config(text="Detener")
                
                # Crear una copia de la lista antes de modificarla
                if self.study_mode.get() == "inverse":
                    # Si estamos en modo inverso, invertimos los pares hiragana-romanji
                    self.practice_list = [(romanji, hiragana) for hiragana, romanji in self.hiragana_list]
                else:
                    self.practice_list = self.hiragana_list.copy()
                
                self.practice_hiragana()
        except Exception as e:
            messagebox.showerror("Error", f"Error al iniciar práctica: {str(e)}")
    
    def practice_hiragana(self):
        """Función principal para la práctica de hiragana"""
        try:
            if not self.is_running or not getattr(self, 'practice_list', []):
                return
            
            # Ocultar ejemplo
            self.example_label.config(text="")
            
            if self.show_romanji:
                # Mostrar el romanji al lado del hiragana
                _, romanji = self.practice_list[self.current_index]
                self.romanji_label.config(text=romanji)
                
                # Registrar carácter mostrado en estadísticas
                self.register_character_shown()
                
                # Preparar para el siguiente hiragana
                self.show_romanji = False
                self.current_index = (self.current_index + 1) % len(self.practice_list)
                self.update_progress()
                
                # Programar el siguiente hiragana usando el mismo tiempo configurado
                delay_ms = int(self.delay_var.get() * 1000)
                self.root.after(delay_ms, self.practice_hiragana)
            else:
                # Mostrar solo el hiragana (limpiar el romanji)
                hiragana, _ = self.practice_list[self.current_index]
                self.hiragana_label.config(text=hiragana)
                self.romanji_label.config(text="")
                
                # Preparar para mostrar el romanji
                self.show_romanji = True
                
                # Programar mostrar el romanji después del tiempo configurado
                delay_ms = int(self.delay_var.get() * 1000)
                self.root.after(delay_ms, self.practice_hiragana)
        except Exception as e:
            messagebox.showerror("Error", f"Error en la práctica: {str(e)}")
            self.is_running = False
            self.start_button.config(text="Iniciar")
    
    def randomize(self):
        """Mezcla la lista de hiragana aleatoriamente si el modo aleatorio está activado"""
        try:
            # Detener la práctica actual si está en ejecución
            self.is_running = False
            self.start_button.config(text="Iniciar")
            
            # Solo mezclar si el modo aleatorio está activado
            if self.random_mode.get():
                # Mezclar la lista de hiragana
                if self.hiragana_list:
                    random.shuffle(self.hiragana_list)
                    messagebox.showinfo("Modo aleatorio", "Lista mezclada aleatoriamente.")
            else:
                # Reorganizar en orden original (por categorías)
                self.update_hiragana_list()
                messagebox.showinfo("Modo secuencial", "Lista ordenada por categorías.")
            
            # Reiniciar el índice actual
            self.current_index = 0
            self.update_progress()
            
            # Limpiar la visualización
            self.show_romanji = False
            self.hiragana_label.config(text="")
            self.romanji_label.config(text="")
            self.example_label.config(text="")
        except Exception as e:
            messagebox.showerror("Error", f"Error al reorganizar: {str(e)}")
    
    def mark_difficult(self, is_difficult):
        """Marca o desmarca un carácter como difícil"""
        try:
            if not self.hiragana_list:
                messagebox.showinfo("Información", "No hay caracteres para marcar.")
                return
                
            # Obtener el carácter actual
            if self.study_mode.get() == "flash":
                current_char, _ = self.hiragana_list[self.current_index]
            else:  # modo inverso
                _, current_char = self.hiragana_list[self.current_index]
            
            if is_difficult:
                self.difficult_characters.add(current_char)
                messagebox.showinfo("Marcado como difícil", f"El carácter '{current_char}' ha sido marcado como difícil.")
            else:
                if current_char in self.difficult_characters:
                    self.difficult_characters.remove(current_char)
                    messagebox.showinfo("Marcado como fácil", f"El carácter '{current_char}' ya no está marcado como difícil.")
                else:
                    messagebox.showinfo("Información", f"El carácter '{current_char}' no estaba marcado como difícil.")
            
            # Actualizar visualización
            self.update_difficult_chars_display()
            
            # Si estamos en modo difíciles, actualizar la lista en tiempo real
            if getattr(self, 'in_difficult_mode', False) and not is_difficult:
                # Actualizar la lista actual
                current_char_index = self.current_index
                self.practice_difficult_only()
                
                # Ajustar el índice actual si es necesario
                if current_char_index >= len(self.hiragana_list):
                    self.current_index = 0 if self.hiragana_list else current_char_index
                    
                self.update_progress()
        except Exception as e:
            messagebox.showerror("Error", f"Error al marcar carácter: {str(e)}")
    
    def update_difficult_chars_display(self):
        # Limpiar el frame
        for widget in self.diff_chars_frame.winfo_children():
            widget.destroy()
            
        # Mostrar caracteres difíciles
        if self.difficult_characters:
            diff_text = ", ".join(sorted(self.difficult_characters))
            ttk.Label(self.diff_chars_frame, text=diff_text, wraplength=200).pack()
        else:
            ttk.Label(self.diff_chars_frame, text="No hay caracteres marcados como difíciles").pack()
    
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
            messagebox.showinfo("Modo difíciles", f"Practicando {len(difficult_list)} caracteres difíciles. Se han ignorado las selecciones de categorías.")
            
            # Iniciar la práctica
            if not self.is_running:
                self.toggle_practice()
        except Exception as e:
            messagebox.showerror("Error", f"Error al iniciar modo difíciles: {str(e)}")
    
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
    
    def update_current_list(self):
        """Actualiza la lista actual de caracteres según el modo actual"""
        try:
            # Si estamos en modo difíciles, actualizar solo con los caracteres actualmente difíciles
            if getattr(self, 'in_difficult_mode', False):
                self.practice_difficult_only()
            else:
                # De lo contrario, actualizar según las categorías seleccionadas
                self.update_hiragana_list()
                
            messagebox.showinfo("Actualizado", "Lista de caracteres actualizada correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar la lista: {str(e)}")
    
    def show_example(self):
        """Muestra un ejemplo de palabra para el carácter que se está mostrando actualmente"""
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
    def update_quiz_interface(self):
        """Actualiza la interfaz del quiz según el modo seleccionado"""
        try:
            # Limpiar el frame de respuesta
            for widget in self.quiz_response_frame.winfo_children():
                widget.destroy()
            
            # Configurar según el modo seleccionado
            if self.quiz_mode.get() == "write":
                # Modo de escritura
                ttk.Label(
                    self.quiz_response_frame,
                    text=f"Escribe la {'pronunciación (romanji)' if self.quiz_direction.get() == 'hira_to_rom' else 'sílaba (hiragana)'}:",
                    font=("Arial", 12, "bold")
                ).pack(pady=(0, 10))
                
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
                
                # Crear 4 botones para las opciones
                # Crear 4 botones para las opciones
                self.option_buttons = []
                for i in range(4):
                    btn = ttk.Button(
                        options_frame,
                        text="",
                        width=20,
                        command=lambda idx=i: self.check_answer_from_button(idx)
                    )
                    btn.pack(pady=5, padx=20)
                    self.option_buttons.append(btn)
            
            # Cargar una nueva pregunta
            self.load_quiz_question()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar la interfaz del quiz: {str(e)}")
    
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
            
            if not self.quiz_available_chars:
                messagebox.showinfo("Sin caracteres", "No hay caracteres disponibles con la configuración actual.")
                return
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar preguntas: {str(e)}")
    
    def load_quiz_question(self):
        """Carga una nueva pregunta de quiz según la configuración actual"""
        try:
            # Actualizar lista de preguntas disponibles
            self.update_quiz_questions()
            
            if not getattr(self, 'quiz_available_chars', []):
                self.quiz_char_label.config(text="")
                self.quiz_result_var.set("No hay caracteres disponibles")
                return
                
            # Elegir un carácter aleatorio
            random_idx = random.randint(0, len(self.quiz_available_chars) - 1)
            question, answer = self.quiz_available_chars[random_idx]
            
            # Mostrar la pregunta
            self.quiz_char_label.config(text=question)
            
            # Guardar la respuesta correcta
            self.current_quiz_answer = answer
            self.current_quiz_question = question
            
            # Limpiar resultado anterior
            self.quiz_result_var.set("")
            
            if self.quiz_mode.get() == "write":
                # Limpiar la entrada y el resultado
                self.quiz_entry.delete(0, tk.END)
                self.quiz_entry.focus_set()
                
                # Habilitar el botón de enviar y deshabilitar el de siguiente
                self.submit_btn.config(state=tk.NORMAL)
                self.next_btn.config(state=tk.DISABLED)
            else:
                # Modo opción múltiple con botones directos
                try:
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
                    
                    # Actualizar los botones con las opciones
                    for i, option in enumerate(options):
                        self.option_buttons[i].config(text=option, state=tk.NORMAL, style="TButton")
                    
                except Exception as e:
                    print(f"Error al generar opciones: {e}")
                    # En caso de error, simplemente usar opciones genéricas
                    for i in range(4):
                        self.option_buttons[i].config(
                            text=f"Opción {i+1}" if i != 0 else answer, 
                            state=tk.NORMAL, 
                            style="TButton"
                        )
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar pregunta: {str(e)}")
    
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
                self.study_history[current_char] = {"times_shown": 0, "correct": 0, "incorrect": 0}
            
            if user_answer == correct_answer:
                self.quiz_result_var.set("¡Correcto!")
                self.last_answer_correct = True
                self.score += 1
                self.streak += 1
                self.max_streak = max(self.max_streak, self.streak)
                self.study_history[current_char]["correct"] += 1
                
                # Si era difícil y se responde correctamente 3 veces seguidas, lo quitamos de difíciles
                if current_char in self.difficult_characters:
                    if not hasattr(self, 'correct_answers_count'):
                        self.correct_answers_count = {}
                    
                    self.correct_answers_count[current_char] = self.correct_answers_count.get(current_char, 0) + 1
                    
                    if self.correct_answers_count.get(current_char, 0) >= 3:
                        self.difficult_characters.remove(current_char)
                        self.update_difficult_chars_display()
                        messagebox.showinfo("¡Mejorado!", f"El carácter '{current_char}' ya no está marcado como difícil después de 3 respuestas correctas.")
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
                            if r == correct_answer:
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
            
            # Deshabilitar el botón de enviar y habilitar el de siguiente
            self.submit_btn.config(state=tk.DISABLED)
            self.next_btn.config(state=tk.NORMAL)
            self.next_btn.focus_set()
        except Exception as e:
            messagebox.showerror("Error", f"Error al comprobar respuesta: {str(e)}")
    
    def check_answer_multiple(self):
        """Comprueba la respuesta seleccionada en opción múltiple"""
        try:
            selected_option = self.quiz_option_var.get()
            
            if not selected_option:
                messagebox.showinfo("Sin selección", "Por favor, selecciona una opción.")
                return
                
            selected_idx = int(selected_option)
            selected_answer = self.quiz_options_vars[selected_idx].get()
            correct_answer = self.current_quiz_answer
            
            # Registrar en estudio
            current_char = self.current_quiz_question
            if current_char not in self.study_history:
                self.study_history[current_char] = {"times_shown": 0, "correct": 0, "incorrect": 0}
            
            if selected_answer == correct_answer:
                self.quiz_result_var.set("¡Correcto!")
                self.last_answer_correct = True
                self.score += 1
                self.streak += 1
                self.max_streak = max(self.max_streak, self.streak)
                self.study_history[current_char]["correct"] += 1
                
                # Mejorar con 3 aciertos seguidos
                if current_char in self.difficult_characters:
                    if not hasattr(self, 'correct_answers_count'):
                        self.correct_answers_count = {}
                    
                    self.correct_answers_count[current_char] = self.correct_answers_count.get(current_char, 0) + 1
                    
                    if self.correct_answers_count.get(current_char, 0) >= 3:
                        self.difficult_characters.remove(current_char)
                        self.update_difficult_chars_display()
                        messagebox.showinfo("¡Mejorado!", f"El carácter '{current_char}' ya no está marcado como difícil después de 3 respuestas correctas.")
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
                            if r == self.current_quiz_question:
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
            
            # Deshabilitar el botón de enviar y habilitar el de siguiente
            self.submit_btn.config(state=tk.DISABLED)
            self.next_btn.config(state=tk.NORMAL)
            self.next_btn.focus_set()
        except Exception as e:
            messagebox.showerror("Error", f"Error al comprobar respuesta: {str(e)}")
    
    def next_quiz_question(self):
        """Carga la siguiente pregunta de quiz"""
        self.load_quiz_question()
    
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
    
    def update_quiz_stats(self):
        self.correct_var.set(str(self.score))
        self.attempts_var.set(str(self.total_attempts))
        
        if self.total_attempts > 0:
            accuracy = (self.score / self.total_attempts) * 100
            self.accuracy_var.set(f"{accuracy:.1f}%")
        else:
            self.accuracy_var.set("0%")
            
        self.streak_var.set(str(self.streak))
    
    # ==== Funciones de estadísticas ====
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
                    self.study_history[current_char] = {"times_shown": 0, "correct": 0, "incorrect": 0}
                    
                self.study_history[current_char]["times_shown"] += 1
            
            # Actualizar estadísticas de sesión en tiempo real
            self.update_session_stats()
        except Exception as e:
            print(f"Error al registrar carácter: {str(e)}")
    
    def update_session_stats(self):
        # Calcular estadísticas
        session_duration = datetime.now() - self.session_start_time
        minutes = session_duration.total_seconds() / 60
        
        chars_per_minute = 0
        if minutes > 0:
            chars_per_minute = self.session_chars_shown / minutes
            
        # Actualizar texto de estadísticas
        stats_text = (
            f"Caracteres revisados: {self.session_chars_shown}\n"
            f"Tiempo de estudio: {int(minutes)} min\n"
            f"Velocidad: {chars_per_minute:.1f} car/min\n"
            f"Racha actual: {self.streak}\n"
            f"Mejor racha: {self.max_streak}\n"
        )
        
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, stats_text)
        self.stats_text.config(state=tk.DISABLED)
    
    def update_stats_display(self):
        # Estadísticas generales
        total_shown = sum(char_data["times_shown"] for char_data in self.study_history.values())
        total_correct = sum(char_data["correct"] for char_data in self.study_history.values())
        total_incorrect = sum(char_data["incorrect"] for char_data in self.study_history.values())
        
        # Calcular precisión solo si hay intentos
        if total_correct + total_incorrect > 0:
            accuracy = (total_correct / (total_correct + total_incorrect) * 100)
            accuracy_text = f"{accuracy:.1f}%"
        else:
            accuracy_text = "0.0%"
        
        general_stats_text = (
            f"Total de caracteres estudiados: {len(self.study_history)}\n"
            f"Total de repeticiones: {total_shown}\n"
            f"Respuestas correctas: {total_correct}\n"
            f"Respuestas incorrectas: {total_incorrect}\n"
            f"Precisión general: {accuracy_text} (si has usado el modo quiz)\n"
            f"Mejor racha: {self.max_streak}\n\n"
            f"Caracteres difíciles: {len(self.difficult_characters)}\n"
        )
        
        self.general_stats.config(state=tk.NORMAL)
        self.general_stats.delete(1.0, tk.END)
        self.general_stats.insert(tk.END, general_stats_text)
        self.general_stats.config(state=tk.DISABLED)
        
        # El resto del método sigue igual...
        
        # ==== Funciones de carga/guardado ====
    def load_data(self):
        try:
            if os.path.exists('hiragana_data.json'):
                with open('hiragana_data.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    if 'difficult_characters' in data:
                        self.difficult_characters = set(data['difficult_characters'])
                        
                    if 'study_history' in data:
                        self.study_history = data['study_history']
                        
                    if 'max_streak' in data:
                        self.max_streak = data['max_streak']
                        
                # Actualizar visualización
                self.update_difficult_chars_display()
                self.update_stats_display()
        except Exception as e:
            print(f"Error al cargar datos: {e}")
    
    def save_data(self):
        try:
            data = {
                'difficult_characters': list(self.difficult_characters),
                'study_history': self.study_history,
                'max_streak': self.max_streak
            }
            
            with open('hiragana_data.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            print("Datos guardados correctamente")
        except Exception as e:
            print(f"Error al guardar datos: {e}")
    
    def on_tab_change(self, event):
        # Si cambiamos a la pestaña de estadísticas, actualizarlas
        if self.notebook.index(self.notebook.select()) == 2:
            self.update_stats_display()

    def reset_all_stats(self):
        """Reinicia todas las estadísticas y el historial de estudio"""
        if messagebox.askyesno("Confirmar", "¿Estás seguro de que quieres reiniciar TODAS las estadísticas?\n\nEsto borrará todo el historial de estudio y la lista de caracteres difíciles."):
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
            
            # Actualizar estadísticas
            self.update_quiz_stats()
            self.update_session_stats()
            self.update_stats_display()
            
            # Guardar datos reiniciados
            self.save_data()
            
            messagebox.showinfo("Completado", "Todas las estadísticas han sido reiniciadas.")

    def toggle_order(self, is_random):
        """Cambia entre modo aleatorio y secuencial"""
        try:
            # Actualizar variable de modo aleatorio
            self.random_mode.set(is_random)
            
            # Aplicar el nuevo orden
            if is_random:
                self.randomize()
            else:
                # Detener la práctica actual si está en ejecución
                self.is_running = False
                self.start_button.config(text="Iniciar")
                
                # Reorganizar de forma secuencial por categorías
                self.update_hiragana_list()
                
                # Desactivar explícitamente el modo aleatorio
                self.random_mode.set(False)
                
                # Notificar al usuario
                messagebox.showinfo("Modo secuencial", "Lista ordenada por categorías.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al cambiar el orden: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = HiraganaTrainer(root)
    
    # Guardar datos al cerrar
    def on_closing():
        app.save_data()
        root.destroy()
        
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()