# hiragana-trainer


## Descripción

Hiragana Trainer es una aplicación completa diseñada para ayudarte a aprender y practicar hiragana, el silabario básico japonés. Con múltiples modos de estudio, seguimiento de progreso y características adaptativas, esta herramienta te permite dominar los caracteres hiragana de forma eficiente y personalizada.


## Características Principales

- 📚 **Estudio completo de hiragana**: Incluye los 46 caracteres básicos, caracteres con dakuten y combinaciones yōon.
- 🔄 **Múltiples modos de estudio**:
  - Tarjetas flash (hiragana → romanji)
  - Modo inverso (romanji → hiragana)
  - Modo quiz con opciones múltiples o escritura
- 📊 **Seguimiento de progreso**: Estadísticas detalladas sobre tu rendimiento y tiempo de estudio.
- ⚙️ **Personalización**: Selecciona categorías específicas para practicar.
- 🔍 **Sistema de caracteres difíciles**: Identifica y enfócate en los caracteres que te resultan más desafiantes.
- 📝 **Ejemplos contextuales**: Palabras de ejemplo para cada carácter hiragana.
- 🎲 **Modo aleatorio o secuencial**: Adapta tu estudio según tus preferencias.

## Requisitos

- Python 3.6 o superior
- Tkinter (incluido en la mayoría de las instalaciones de Python)

## Instalación

1. Clona o descarga este repositorio.
2. Asegúrate de tener Python instalado.
3. Ejecuta la aplicación:

```bash
python hiragana.py
```

## Guía de Uso

### Interfaz Principal

La aplicación está dividida en tres pestañas principales:

1. **Tarjetas Flash**: Para practicar mediante la visualización de caracteres.
2. **Modo Quiz**: Para evaluar tu conocimiento mediante pruebas.
3. **Estadísticas**: Para revisar tu progreso y rendimiento.

### Modo Tarjetas Flash

- **Selección de categorías**: Activa/desactiva las categorías que deseas practicar.
- **Control de tiempo**: Ajusta la velocidad de las tarjetas (1-10 segundos).
- **Modo aleatorio/secuencial**: Elige cómo quieres recorrer los caracteres.
- **Gestión de difíciles**: Marca caracteres como difíciles para practicarlos más tarde.
- **Ejemplos**: Visualiza palabras de ejemplo para cada carácter.

### Modo Quiz

- **Modo de respuesta**: 
  - Escritura: Escribe la pronunciación o el carácter.
  - Opción múltiple: Selecciona entre cuatro opciones.
- **Dirección**:
  - Hiragana → Romanji: Muestra el carácter y debes dar su pronunciación.
  - Romanji → Hiragana: Muestra la pronunciación y debes identificar el carácter.
- **Dificultad**: Opción para practicar solo caracteres difíciles.

### Estadísticas

- **Estadísticas generales**: Caracteres estudiados, repeticiones, precisión, etc.
- **Progreso por categoría**: Rendimiento en cada grupo de caracteres.
- **Caracteres difíciles**: Lista de caracteres que necesitan más práctica.

## Características Avanzadas

### Sistema de Adaptación

- Los caracteres con respuestas incorrectas se marcan automáticamente como difíciles.
- Los caracteres difíciles que aciertas 3 veces consecutivas se eliminan de la lista de difíciles.

### Persistencia de Datos

- La aplicación guarda automáticamente tu progreso y configuraciones.
- Al reiniciar la aplicación, se carga tu historial de estudio anterior.

### Ejemplos Contextuales

Cada carácter hiragana viene con un ejemplo de palabra que lo utiliza, junto con:
- La palabra en hiragana
- Su pronunciación en romanji
- Su significado en español

## Categorías de Hiragana

1. **Básicos**: Incluye los 46 caracteres básicos (a, i, u, e, o, ka, ki...).
2. **Con dakuten**: Caracteres modificados con dakuten (ga, gi, gu...).
3. **Combinados (yōon)**: Combinaciones especiales (kya, kyu, kyo...).

## Consejos para el Estudio

1. **Comienza con los básicos**: Domina primero las vocales y los caracteres básicos.
2. **Usa el modo secuencial**: Para principiantes, es mejor aprender en orden.
3. **Practica diariamente**: Sesiones cortas y regulares son más efectivas.
4. **Alterna los modos**: Usa tarjetas flash para familiarizarte y el quiz para evaluar.
5. **Revisa los difíciles**: Dedica tiempo extra a los caracteres que te resultan complicados.

---

## Licencia

Este proyecto está disponible como software libre y de código abierto.

## Contribuciones

Las contribuciones son bienvenidas. Si encuentras errores o tienes sugerencias, no dudes en abrir un issue o enviar un pull request.

---

Desarrollado con ❤️ para estudiantes de japonés.
