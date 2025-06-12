📚 Generador de Diccionarios Avanzado (DictGen)


💡 Descripción General
DictGen es un generador de diccionarios de contraseñas potente y altamente optimizado, diseñado para crear listas de palabras personalizadas con un bajo consumo de RAM y CPU. Utiliza procesamiento paralelo para maximizar la velocidad de generación, aprovechando al máximo los recursos de tu sistema.

A diferencia de otras herramientas que pueden agotar rápidamente tu memoria, DictGen escribe directamente las claves generadas en el archivo de salida, lo que lo hace ideal para entornos con recursos limitados o para generar diccionarios masivos sin comprometer el rendimiento de tu máquina.

✨ Características Destacadas
Optimizado para Recursos Bajos: Genera diccionarios masivos sin saturar la RAM, escribiendo directamente al disco.
Procesamiento Paralelo: Aprovecha todos los núcleos de tu CPU para una generación ultra-rápida.
Modo Interactivo Intuitivo: Una interfaz de menú fácil de usar para configurar tus opciones sin necesidad de comandos complejos.
Generación de Variaciones Flexibles:
Números: Añade rangos de años o números con una cantidad específica de dígitos.
Caracteres Especiales: Incluye tus propios caracteres especiales personalizados.
Mezcla de Mayúsculas/Minúsculas: Crea todas las combinaciones posibles de mayúsculas y minúsculas para tus palabras clave.
Límites por Palabra Clave: Controla la cantidad de claves generadas para cada palabra base.
Deduplicación Automática Inteligente: Elimina duplicados de forma eficiente al finalizar, detectando automáticamente tu sistema operativo (sort -u para Linux/macOS/WSL, PowerShell para Windows).
Modo Verboso: Obtén información detallada sobre el proceso de generación si necesitas depurar o simplemente quieres ver más a fondo lo que sucede.
Modular y Fácil de Mantener: Código bien estructurado en módulos separados para una mayor claridad y futuras expansiones.
🚀 Instalación
Clonar el Repositorio:
Bash

git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME
Instalar Dependencias:
Bash

pip install -r requirements.txt
Asegúrate de que tu archivo requirements.txt contenga al menos:
tqdm
📖 Uso
DictGen ofrece dos modos de operación: interactivo (recomendado para la mayoría de usuarios) y línea de comandos (CLI) (para usuarios avanzados o scripting).

Modo Interactivo (Recomendado)
Simplemente ejecuta el script con la opción -i o --interactive:

Bash

python dictgen.py -i
Se te guiará a través de un menú paso a paso para ingresar tus palabras clave y configurar todas las opciones de generación. Al finalizar, se te preguntará si deseas deduplicar el archivo automáticamente.

Modo Línea de Comandos (CLI)
Puedes especificar todas las opciones directamente al ejecutar el script.

Bash

python dictgen.py [OPCIONES]
Ejemplo Básico:

Bash

python dictgen.py -k nombre apellido -o mi_diccionario.txt
Esto genera un diccionario con variaciones básicas de "nombre" y "apellido" en el archivo mi_diccionario.txt.

Ejemplo Avanzado (con deduplicación y verbosidad):

Bash

python dictgen.py -k "palabra clave" "otra clave" -n -y 1990-2023 -s "!@$" -c -l 1000 -x -v
-k "palabra clave" "otra clave": Palabras clave base. Usa comillas si tienen espacios.
-n: Activa la inclusión de números.
-y 1990-2023: Rango de años a añadir (se ignoraría -d si estuviera presente).
-s "!@$": Caracteres especiales a añadir.
-c: Genera todas las combinaciones posibles de mayúsculas/minúsculas.
-l 1000: Limita a 1000 claves por cada palabra clave base.
-x: Elimina automáticamente los duplicados al finalizar.
-v: Activa el modo verboso para ver más detalles del proceso.
Opciones Disponibles
Opción Larga	Opción Corta	Descripción
--keywords	-k	[OBLIGATORIO en CLI] Palabras clave base para generar el diccionario. Sepáralas por espacios. Usa comillas si tienen espacios.
--output	-o	Nombre del archivo de salida para el diccionario (por defecto: dictionary.txt).
--numbers	-n	Incluir números (años o dígitos) en las contraseñas. Requiere --years o --digits.
--years	-y	Rango de años a incluir si se usa --numbers (ej. 1990-2025). Ignora --digits.
--digits	-d	Cantidad de dígitos aleatorios a incluir si se usa --numbers (ej. 3 para 000-999). Ignora --years.
--special-chars	-s	Caracteres especiales a incluir (ej. -s ! @ # $). Se añadirán al inicio, al final o entre la palabra y los números.
--limit	-l	Limita el número de claves por palabra clave base. No hay límite por defecto para permitir grandes volúmenes.
--case-mix	-c	Generar todas las combinaciones posibles de mayúsculas y minúsculas para cada palabra clave (ej. 'Palabra' -> 'PaLaBrA').
--interactive	-i	Forzar el inicio del generador en modo interactivo. Si se usa, otras opciones de CLI se ignoran.
--processes	-p	Número de procesos a usar para la generación paralela. Por defecto, usa todos los núcleos disponibles (generalmente os.cpu_count()).
--deduplicate	-x	Elimina automáticamente los duplicados del archivo generado al finalizar. Ver advertencia importante abajo.
--verbose	-v	Activa el modo verboso para ver mensajes de detalle adicionales durante el proceso.

Exportar a Hojas de cálculo
⚠️ Advertencia Importante: Deduplicación de Archivos Grandes
La función de deduplicación (-x o la opción interactiva) es muy útil, pero es crucial entender su impacto:

Si el archivo generado es MUY GRANDE (varios GB o decenas de millones de líneas), la deduplicación puede consumir una cantidad SIGNIFICATIVA de RAM y CPU, y tomar mucho tiempo.

En sistemas con recursos limitados, esta operación podría incluso ralentizar drásticamente o colapsar el sistema. Si tu máquina tiene recursos escasos o estás generando un diccionario masivo, es posible que prefieras realizar la deduplicación manualmente después de que DictGen haya terminado, utilizando herramientas de línea de comandos más optimizadas para esto:

Para Linux / macOS / WSL (Bash):
Bash

sort -u "tu_diccionario.txt" > "tu_diccionario_unique.txt"
Para Windows (PowerShell):
PowerShell

Get-Content "tu_diccionario.txt" | Sort-Object -Unique | Set-Content "tu_diccionario_unique.txt"
🛠️ Estructura del Proyecto
El proyecto está modularizado para facilitar su comprensión y mantenimiento:

dictgen.py: El script principal ejecutable. Orquesta la lógica del programa, maneja la entrada inicial y llama a las funciones de los otros módulos.
contenido.py: Contiene la clase DictionaryGenerator y toda la lógica central para la generación de las variaciones de contraseñas.
parametros.py: Maneja la interacción con el usuario, incluyendo el parser de argumentos de línea de comandos y el flujo del modo interactivo. También incluye la función de deduplicación de archivos.
🤝 Contribuciones
¡Las contribuciones son bienvenidas! Si tienes ideas para mejorar, encuentras un error o quieres añadir una nueva funcionalidad, no dudes en:

Hacer un "fork" del repositorio.
Crear una nueva rama (git checkout -b feature/nueva-funcionalidad).
Realizar tus cambios.
Abrir un "Pull Request" describiendo tus modificaciones.
📄 Licencia
Este proyecto está bajo la Licencia MIT. Consulta el archivo LICENSE en este repositorio para más detalles.
