# Hiragana Trainer - Documentación Completa

## Índice

- [Introducción](#introducción)
- [Instalación](#instalación)
- [Estructura de la Aplicación](#estructura-de-la-aplicación)
- [Funcionalidades Principales](#funcionalidades-principales)
- [Guía de Uso por Módulos](#guía-de-uso-por-módulos)
  - [Modo Tarjetas Flash](#modo-tarjetas-flash)
  - [Modo Quiz](#modo-quiz)
  - [Sistema de Estadísticas](#sistema-de-estadísticas)
  - [Configuración](#configuración)
- [Sistema de Repetición Espaciada (SRS)](#sistema-de-repetición-espaciada-srs)
- [Aprendizaje Adaptativo](#aprendizaje-adaptativo)
- [Sistema de Logros](#sistema-de-logros)
- [Referencia de Funciones](#referencia-de-funciones)
- [Atajos de Teclado](#atajos-de-teclado)
- [Solución de Problemas](#solución-de-problemas)

## Introducción

Hiragana Trainer es una aplicación completa diseñada para ayudarte a aprender y practicar hiragana, el silabario básico japonés. Con múltiples modos de estudio, seguimiento de progreso y características adaptativas, esta herramienta te permite dominar los caracteres hiragana de forma eficiente y personalizada.

## Instalación

### Requisitos del Sistema

#### Requisitos Mínimos
- **Python**: Versión 3.6 o superior
- **Tkinter**: Biblioteca gráfica (incluida en la mayoría de instalaciones de Python)
- **Espacio en disco**: ~10 MB para la aplicación básica
- **RAM**: 256 MB mínimo recomendado

#### Requisitos Opcionales
- **Matplotlib**: Para visualización de gráficos estadísticos (recomendado)
- **Conexión a internet**: Solo para la instalación inicial (no necesaria para el uso normal)

### Verificación de Requisitos

Antes de instalar, puedes verificar si ya tienes los requisitos necesarios:

1. **Verificar la versión de Python**:
   ```bash
   python --version
   # o en algunos sistemas:
   python3 --version
   ```
   Deberías ver una salida como `Python 3.x.x`. Si no es así o tienes una versión inferior a 3.6, debes [descargar e instalar Python](https://www.python.org/downloads/).

2. **Verificar Tkinter**:
   ```bash
   # En sistemas Unix/Linux/macOS:
   python -m tkinter
   
   # En Windows:
   python -c "import tkinter; tkinter._test()"
   ```
   Esto debería abrir una pequeña ventana de prueba si Tkinter está correctamente instalado.

### Instalación Paso a Paso

#### Método 1: Instalación desde GitHub (Recomendado)

1. **Clonar el repositorio**:
   ```bash
   git clone https://github.com/tuusuario/hiragana-trainer.git
   cd hiragana-trainer
   ```

2. **Instalar dependencias**:
   ```bash
   # Instalar matplotlib (opcional pero recomendado para gráficos):
   pip install matplotlib
   
   # Alternativa con pip3 en algunos sistemas:
   pip3 install matplotlib
   ```

3. **Ejecutar la aplicación**:
   ```bash
   python hiragana.py
   # o en algunos sistemas:
   python3 hiragana.py
   ```

#### Método 2: Descarga Directa

1. **Descargar el código**:
   - Ve a la [página principal del repositorio](https://github.com/tuusuario/hiragana-trainer)
   - Haz clic en el botón "Code" y selecciona "Download ZIP"
   - Descomprime el archivo en la ubicación deseada

2. **Instalar dependencias**:
   - Abre una terminal o símbolo del sistema
   - Navega hasta la carpeta donde descomprimiste el código:
     ```bash
     cd ruta/a/hiragana-trainer
     ```
   - Instala las dependencias:
     ```bash
     pip install matplotlib
     ```

3. **Ejecutar la aplicación**:
   ```bash
   python hiragana.py
   ```

### Instrucciones Específicas por Sistema Operativo

#### Windows

1. **Instalación de Python** (si no lo tienes):
   - Descarga el instalador de [python.org](https://www.python.org/downloads/windows/)
   - Durante la instalación, marca la casilla "Add Python to PATH"
   - Completa la instalación siguiendo el asistente

2. **Instalación de Hiragana Trainer**:
   ```powershell
   # Clona el repositorio
   git clone https://github.com/tuusuario/hiragana-trainer.git
   cd hiragana-trainer
   
   # Instala dependencias
   pip install matplotlib
   
   # Ejecuta la aplicación
   python hiragana.py
   ```

3. **Alternativa sin Git**:
   - Descarga el ZIP desde la página de GitHub
   - Extráelo a una carpeta, por ejemplo `C:\Hiragana-Trainer`
   - Abre PowerShell o CMD
   - Navega a la carpeta: `cd C:\Hiragana-Trainer`
   - Instala matplotlib: `pip install matplotlib`
   - Ejecuta la aplicación: `python hiragana.py`

#### macOS

1. **Instalación de Python** (si no lo tienes):
   ```bash
   # Usando Homebrew (recomendado):
   brew install python
   
   # O descarga el instalador desde python.org
   ```

2. **Instalación de Hiragana Trainer**:
   ```bash
   # Clona el repositorio
   git clone https://github.com/tuusuario/hiragana-trainer.git
   cd hiragana-trainer
   
   # Instala dependencias
   pip3 install matplotlib
   
   # Ejecuta la aplicación
   python3 hiragana.py
   ```

#### Linux (Ubuntu/Debian)

1. **Instalación de Python y dependencias**:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip python3-tk
   ```

2. **Instalación de Hiragana Trainer**:
   ```bash
   # Clona el repositorio
   git clone https://github.com/tuusuario/hiragana-trainer.git
   cd hiragana-trainer
   
   # Instala dependencias
   pip3 install matplotlib
   
   # Ejecuta la aplicación
   python3 hiragana.py
   ```

### Verificación de Instalación

Para verificar que la instalación se realizó correctamente:

1. La aplicación debería iniciarse sin errores
2. Para verificar la funcionalidad gráfica:
   - Ve a la pestaña "Estadísticas"
   - Haz clic en "Ver gráficos"
   - Deberías poder ver gráficos estadísticos

### Solución de Problemas Comunes

#### ModuleNotFoundError: No module named 'matplotlib'
- Ejecuta nuevamente: `pip install matplotlib` o `pip3 install matplotlib`

#### No se puede encontrar Python/pip
- Verifica que Python esté en tu PATH (variable de entorno)
- Reinicia la terminal/consola después de instalar Python

#### Errores con Tkinter
- En Linux: `sudo apt-get install python3-tk`
- En macOS: Reinstala Python desde python.org o `brew reinstall python-tk`

#### Errores de permisos al instalar
- En Linux/macOS: Usa `sudo pip install matplotlib`
- En Windows: Ejecuta CMD o PowerShell como administrador

## Estructura de la Aplicación

La aplicación está organizada en varias clases principales:

1. **HiraganaTrainer**: Clase principal que gestiona toda la aplicación.
2. **SRSScheduler**: Gestiona el sistema de repetición espaciada.
3. **AdaptiveLearning**: Implementa el algoritmo de aprendizaje adaptativo.
4. **Achievement**: Define el sistema de logros.

## Funcionalidades Principales

- **Estudio completo de hiragana**: Incluye los 46 caracteres básicos, caracteres con dakuten y combinaciones yōon.
- **Múltiples modos de estudio**:
  - Tarjetas flash (hiragana → romanji)
  - Modo inverso (romanji → hiragana)
  - Modo quiz con opciones múltiples o escritura
- **Seguimiento de progreso**: Estadísticas detalladas sobre tu rendimiento y tiempo de estudio.
- **Personalización**: Selecciona categorías específicas para practicar.
- **Sistema de caracteres difíciles**: Identifica y enfócate en los caracteres que te resultan más desafiantes.
- **Ejemplos contextuales**: Palabras de ejemplo para cada carácter hiragana.
- **Modo aleatorio o secuencial**: Adapta tu estudio según tus preferencias.
- **Sistema de repetición espaciada (SRS)**: Algoritmo basado en la eficiencia del aprendizaje con repasos programados.
- **Aprendizaje adaptativo**: Prioriza automáticamente los caracteres que necesitan más atención.
- **Sistema de logros**: Gamificación para motivar el progreso.

## Guía de Uso por Módulos

### Modo Tarjetas Flash

El modo de tarjetas flash te permite practicar los caracteres hiragana mostrándote primero el carácter y luego su pronunciación en romanji.

#### Cómo utilizar:

1. **Selección de categorías**:
   - En el panel izquierdo, marca las categorías que deseas practicar.
   - Las categorías incluyen: Básicos, Con dakuten y Combinados (yōon).

2. **Configuración de tiempo**:
   - Ajusta el deslizador para configurar cuánto tiempo se mostrará cada tarjeta (1-10 segundos).

3. **Modos de práctica**:
   - **Aleatorio/Secuencial**: Selecciona si quieres que los caracteres aparezcan en orden o aleatoriamente.
   - **Normal/Inverso**: En modo normal ves hiragana→romanji, en inverso romanji→hiragana.

4. **Iniciar práctica**:
   - Pulsa el botón "Iniciar" o la barra espaciadora para comenzar.
   - La aplicación mostrará el carácter hiragana y luego, tras el tiempo configurado, su romanji.

5. **Feedback**:
   - Botón "Difícil": Marca el carácter actual como difícil para practicarlo más intensivamente.
   - Botón "Fácil": Desmarca un carácter como difícil.
   - Botón "Mostrar ejemplo": Muestra una palabra de ejemplo que utiliza el carácter.

6. **Navegación manual**:
   - Usa las flechas derecha/izquierda para avanzar o retroceder manualmente.

#### Funciones relacionadas:

- `toggle_practice()`: Inicia o detiene la práctica automática.
- `practice_hiragana()`: Muestra los caracteres durante la práctica.
- `mark_difficult()`: Marca o desmarca un carácter como difícil.
- `show_example()`: Muestra palabras de ejemplo para el carácter actual.
- `update_hiragana_list()`: Actualiza la lista de caracteres según las categorías seleccionadas.
- `practice_difficult_only()`: Configura el modo para practicar solo caracteres difíciles.

### Modo Quiz

El modo quiz te permite evaluar tu conocimiento mediante pruebas de opción múltiple o escritura.

#### Cómo utilizar:

1. **Configuración del quiz**:
   - **Modo de respuesta**: 
     - "Escribir respuesta": Debes escribir la pronunciación o el carácter.
     - "Opción múltiple": Seleccionas entre cuatro opciones posibles.
   - **Dirección**:
     - Hiragana → Romanji: Muestra el carácter y debes dar su pronunciación.
     - Romanji → Hiragana: Muestra la pronunciación y debes identificar el carácter.
   - **Filtrado**:
     - Opción para practicar solo caracteres difíciles.
     - Opción para usar el sistema SRS.

2. **Responder preguntas**:
   - En modo escritura: Escribe tu respuesta y haz clic en "Comprobar" o pulsa Enter.
   - En modo opción múltiple: Selecciona la opción que creas correcta.

3. **Feedback y progreso**:
   - Después de cada respuesta, la aplicación te indica si es correcta o incorrecta.
   - Las estadísticas (aciertos, intentos, precisión, racha) se actualizan en tiempo real.
   - Los caracteres respondidos incorrectamente se marcan automáticamente como difíciles.

#### Funciones relacionadas:

- `update_quiz_interface()`: Actualiza la interfaz según el modo seleccionado.
- `load_quiz_question()`: Carga una nueva pregunta.
- `check_answer()`: Verifica la respuesta escrita.
- `check_answer_from_button()`: Verifica la respuesta seleccionada en modo opción múltiple.
- `next_quiz_question()`: Avanza a la siguiente pregunta.
- `reset_quiz()`: Reinicia las estadísticas del quiz actual.

### Sistema de Estadísticas

La pestaña de estadísticas te proporciona información detallada sobre tu progreso y rendimiento.

#### Información disponible:

1. **Estadísticas generales**:
   - Total de caracteres estudiados
   - Número total de repeticiones
   - Respuestas correctas e incorrectas
   - Precisión general
   - Mejor racha
   - Tiempo total de estudio

2. **Progreso por categoría**:
   - Porcentaje de caracteres estudiados en cada categoría
   - Precisión de respuestas por categoría

3. **Caracteres difíciles**:
   - Lista de caracteres marcados como difíciles
   - Tasa de error para cada carácter difícil

#### Funciones avanzadas:

- **Exportar estadísticas**: Guarda tus datos en formato CSV para análisis externos.
- **Ver gráficos**: Visualiza tu progreso mediante gráficos (requiere matplotlib).

#### Funciones relacionadas:

- `update_stats_display()`: Actualiza la visualización de estadísticas.
- `show_stats_graphs()`: Muestra gráficos de rendimiento y progreso.
- `export_statistics()`: Exporta las estadísticas a un archivo.
- `reset_all_stats()`: Reinicia todas las estadísticas.

### Configuración

La pestaña de configuración te permite personalizar la aplicación según tus preferencias.

#### Opciones disponibles:

1. **Apariencia**:
   - Tema de la interfaz
   - Tamaño de fuente para los caracteres

2. **Comportamiento**:
   - Auto-guardado
   - Notificaciones de logros
   - Algoritmo de aprendizaje (Estándar, SRS Básico, SRS Avanzado, Personalizado)

3. **Planificación de estudio**:
   - Duración de sesión
   - Número de caracteres por sesión
   - Recordatorios de estudio

#### Funciones relacionadas:

- `save_settings()`: Guarda la configuración.
- `load_settings()`: Carga la configuración guardada.
- `reset_settings()`: Restaura la configuración a valores predeterminados.
- `setup_study_plan()`: Configura el plan de estudio semanal.
- `toggle_reminders()`: Activa o desactiva los recordatorios.

## Sistema de Repetición Espaciada (SRS)

El SRS es un método de aprendizaje que programa repasos en intervalos óptimos para maximizar la retención a largo plazo.

### Cómo funciona:

1. **Niveles de intervalo**: Cuando respondes correctamente un carácter, pasa al siguiente nivel con un intervalo más largo.
2. **Reinicios**: Si cometes un error, el carácter vuelve al nivel inicial.
3. **Programación**: Los caracteres se muestran cuando llega su fecha de repaso.

### Ventajas:

- Optimiza el tiempo de estudio
- Reduce el olvido
- Prioriza lo que necesita más atención

### Funciones relacionadas:

- `calculate_next_review()`: Calcula la próxima fecha de repaso para un carácter.
- `get_due_cards()`: Obtiene los caracteres que deben repasarse hoy.
- `apply_srs_filter()`: Filtra la lista de práctica según el SRS.

## Aprendizaje Adaptativo

El sistema de aprendizaje adaptativo ajusta automáticamente la prioridad de los caracteres según tu rendimiento.

### Factores que influyen:

1. **Dificultad**: Caracteres con mayor tasa de error tienen mayor prioridad.
2. **Recencia**: Caracteres no vistos recientemente tienen mayor prioridad.
3. **Frecuencia**: Caracteres más comunes en japonés pueden tener mayor prioridad.

### Funciones relacionadas:

- `calculate_priority()`: Calcula la prioridad de un carácter.
- `sort_by_priority()`: Ordena los caracteres por prioridad.
- `generate_smart_session()`: Crea una sesión de estudio inteligente basada en el rendimiento.

## Sistema de Logros

El sistema de logros gamifica el proceso de aprendizaje, motivándote a alcanzar objetivos específicos.

### Logros disponibles:

1. **Primer Paso**: Completa tu primera sesión de estudio.
2. **Maestro de Hiragana**: Consigue una precisión del 90% en todos los caracteres básicos.
3. **Experto en Dakuten**: Consigue una precisión del 90% en caracteres con dakuten.
4. **Profesional de Yōon**: Consigue una precisión del 90% en caracteres combinados.
5. **Perfeccionista**: Obtén 100% en un quiz de al menos 20 preguntas.
6. **Guerrero de Racha**: Alcanza una racha de 50 respuestas correctas seguidas.
7. **Hábito de Estudio**: Estudia durante 7 días consecutivos.
8. **Hiragana Completo**: Estudia todos los caracteres hiragana al menos una vez.
9. **Dedicación**: Acumula 5 horas de estudio.

### Funciones relacionadas:

- `check_achievements()`: Verifica si se ha desbloqueado algún logro.
- `show_achievements()`: Muestra todos los logros disponibles y su estado.
- `show_achievements_notification()`: Notifica cuando desbloqueas un logro.

## Referencia de Funciones

### Clase `HiraganaTrainer` (Principal)

- `__init__(self, root)`: Inicializa la aplicación.
- `import_hiragana_data(self)`: Importa los datos de hiragana y ejemplos.
- `setup_styles(self)`: Configura los estilos visuales de la aplicación.
- `setup_keyboard_shortcuts(self)`: Configura atajos de teclado.
- `show_welcome_message(self)`: Muestra mensaje de bienvenida al iniciar.
- `setup_ui(self)`: Configura la interfaz de usuario principal.
- `on_tab_change(self, event=None)`: Maneja eventos de cambio entre pestañas.
- `create_menu(self)`: Crea la barra de menú.
- `create_flash_tab(self)`: Crea la pestaña de tarjetas flash.
- `create_quiz_tab(self)`: Crea la pestaña del modo quiz.
- `create_stats_tab(self)`: Crea la pestaña de estadísticas.
- `create_settings_tab(self)`: Crea la pestaña de configuración.
- `create_status_bar(self, parent)`: Crea la barra de estado.
- `start_session_timer(self)`: Inicia el temporizador de sesión.
- `update_time_display(self, *args)`: Actualiza el display de tiempo.
- `toggle_practice(self)`: Inicia o detiene la práctica.
- `apply_srs_filter(self)`: Filtra la lista según el sistema SRS.
- `practice_hiragana(self)`: Función principal para practicar.
- `animate_card(self, hiragana, romanji)`: Anima la transición de tarjetas.
- `advance_card(self, event=None)`: Avanza a la siguiente tarjeta.
- `previous_card(self, event=None)`: Retrocede a la tarjeta anterior.
- `update_progress(self)`: Actualiza indicadores de progreso.
- `toggle_order(self, is_random)`: Cambia entre modo aleatorio y secuencial.
- `update_hiragana_list(self)`: Actualiza la lista según categorías seleccionadas.
- `mark_difficult(self, is_difficult)`: Marca o desmarca un carácter como difícil.
- `update_difficult_chars_display(self)`: Actualiza visualización de caracteres difíciles.
- `remove_difficult_char(self, char)`: Elimina un carácter de la lista de difíciles.
- `practice_difficult_only(self)`: Configura para practicar solo caracteres difíciles.
- `clear_difficult_chars(self)`: Limpia la lista de caracteres difíciles.
- `show_example(self)`: Muestra ejemplos para el carácter actual.
- `register_character_shown(self)`: Registra caracteres mostrados para estadísticas.
- `update_session_stats(self)`: Actualiza estadísticas de sesión en tiempo real.
- `update_quiz_interface(self)`: Actualiza interfaz del quiz.
- `update_quiz_questions(self)`: Actualiza preguntas disponibles.
- `load_quiz_question(self)`: Carga una nueva pregunta de quiz.
- `check_answer(self, event=None)`: Comprueba respuestas escritas.
- `check_answer_from_button(self, selected_idx)`: Comprueba respuestas de opción múltiple.
- `next_quiz_question(self)`: Carga la siguiente pregunta.
- `update_quiz_stats(self)`: Actualiza estadísticas del quiz.
- `reset_quiz(self)`: Reinicia estadísticas del quiz.
- `update_stats_display(self)`: Actualiza visualización de estadísticas.
- `check_achievements(self)`: Verifica logros nuevos.
- `show_achievements_notification(self, unlocked_achievements)`: Notifica logros.
- `show_achievements(self)`: Muestra ventana de logros.
- `show_stats_graphs(self)`: Muestra gráficos de estadísticas.
- `export_statistics(self, format_type="csv")`: Exporta estadísticas.
- `import_data(self)`: Importa datos desde archivo JSON.
- `reset_all_stats(self)`: Reinicia todas las estadísticas.
- `toggle_srs_mode(self)`: Activa/desactiva el modo SRS.
- `change_theme(self, event=None)`: Cambia el tema de la aplicación.
- `update_font_size(self, event=None)`: Actualiza tamaño de fuente.
- `toggle_reminders(self)`: Activa/desactiva recordatorios.
- `setup_study_plan(self)`: Configura plan de estudio.
- `save_study_plan(self, window)`: Guarda plan de estudio.
- `setup_reminder_thread(self)`: Configura hilo para recordatorios.
- `reminder_worker(self)`: Función para hilo de recordatorios.
- `show_reminder(self)`: Muestra notificación de recordatorio.
- `save_settings(self)`: Guarda configuración.
- `load_settings(self)`: Carga configuración guardada.
- `reset_settings(self)`: Restaura configuración predeterminada.
- `generate_smart_session(self)`: Genera sesión inteligente.
- `show_help(self)`: Muestra guía de uso.
- `show_study_tips(self)`: Muestra consejos de estudio.
- `show_about(self)`: Muestra información sobre la aplicación.
- `log_error(self, error_msg, show_to_user=True)`: Registra errores.
- `load_data(self)`: Carga datos guardados.
- `save_data(self)`: Guarda datos de estudio.
- `on_closing(self)`: Acciones al cerrar la aplicación.

### Clase `SRSScheduler`

- `__init__(self)`: Inicializa el sistema de repetición espaciada.
- `calculate_next_review(self, char_data, correct)`: Calcula próxima fecha de repaso.
- `get_due_cards(self, study_history)`: Obtiene caracteres para repasar hoy.

### Clase `AdaptiveLearning`

- `__init__(self)`: Inicializa el algoritmo de aprendizaje adaptativo.
- `calculate_priority(self, character, history)`: Calcula prioridad de un carácter.
- `sort_by_priority(self, characters, history)`: Ordena caracteres por prioridad.

### Clase `Achievement`

- `__init__(self, id, title, description, condition_func, icon=None, reward=None)`: Inicializa un logro.
- `check_condition(self, user_data)`: Verifica si se cumple condición para desbloqueo.
- `to_dict(self)`: Convierte el logro a diccionario para guardar.
- `from_dict(cls, data, condition_func)`: Crea objeto Achievement desde diccionario.

## Atajos de Teclado

- **Espacio**: Iniciar/Detener práctica
- **Flecha derecha (→)**: Avanzar a la siguiente tarjeta
- **Flecha izquierda (←)**: Volver a la tarjeta anterior
- **D**: Marcar carácter actual como difícil
- **F**: Marcar carácter actual como fácil
- **E**: Mostrar ejemplo para el carácter actual
- **Enter**: Comprobar respuesta en modo quiz
- **F1**: Mostrar ayuda
- **Ctrl+Q**: Salir de la aplicación
- **Ctrl+S**: Guardar datos
- **Ctrl+N**: Siguiente pregunta de quiz

## Solución de Problemas

### Problemas Comunes y Soluciones

1. **La aplicación no inicia**:
   - Verifica que tengas Python 3.6 o superior instalado.
   - Asegúrate de que Tkinter esté instalado (viene por defecto con Python).
   - Comprueba permisos de escritura en la carpeta para guardar datos.

2. **Gráficos no disponibles**:
   - Instala matplotlib: `pip install matplotlib`

3. **Errores al guardar datos**:
   - Verifica permisos de escritura en la carpeta.
   - Comprueba si hay suficiente espacio en disco.

4. **Caracteres japoneses no se muestran correctamente**:
   - Asegúrate de tener instaladas fuentes que soporten caracteres japoneses.

### Cómo reportar problemas

Si encuentras algún error, puedes reportarlo de las siguientes formas:

1. Abre un issue en el repositorio de GitHub.
2. Incluye información detallada sobre el error:
   - Pasos para reproducirlo
   - Mensaje de error (si hay alguno)
   - Versión de Python y sistema operativo
   - Capturas de pantalla si es posible

Los errores también se guardan en el archivo `hiragana_trainer.log` para referencia.
