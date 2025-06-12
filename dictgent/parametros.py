import argparse
import os
import sys
from tqdm import tqdm
from contenido import set_verbose_mode, _print_verbose # Importar funciones desde contenido

def get_interactive_input(prompt, validation_func=None, error_message="Entrada inválida. Inténtalo de nuevo."):
    """Helper para obtener entrada de usuario con validación."""
    while True:
        try:
            user_input = input(prompt).strip()
            if validation_func is None or validation_func(user_input):
                return user_input
            else:
                print(error_message)
        except KeyboardInterrupt:
            print("\nOperación cancelada por el usuario.")
            return None

def parse_cli_arguments():
    """
    Se encarga de recibir y procesar los argumentos de la línea de comandos usando argparse.
    """
    parser = argparse.ArgumentParser(
        description="Generador de diccionarios de contraseñas personalizado. Optimizado para bajos recursos.",
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        "-k", "--keywords",
        nargs='+',
        help="Palabras clave base para generar el diccionario (ej. -k nombre ciudad mascota)."
    )
    parser.add_argument(
        "-o", "--output",
        default="dictionary.txt",
        help="Nombre del archivo de salida para el diccionario (por defecto: dictionary.txt)."
    )
    parser.add_argument(
        "-n", "--numbers",
        action="store_true",
        help="Incluir números (años o dígitos) en las contraseñas."
    )
    parser.add_argument(
        "-y", "--years",
        help="Rango de años a incluir si se usa --numbers (ej. 1990-2025). Ignora --digits."
    )
    parser.add_argument(
        "-d", "--digits",
        type=int,
        help="Cantidad de dígitos aleatorios a incluir si se usa --numbers (ej. 3 para 000-999). Ignora --years."
    )
    parser.add_argument(
        "-s", "--special-chars",
        nargs='+',
        help="Caracteres especiales a incluir (ej. -s ! @ # $)."
    )
    parser.add_argument(
        "-l", "--limit",
        type=int,
        help="Limita el número de claves *por palabra clave base*. No hay límite por defecto para permitir grandes volúmenes."
    )
    parser.add_argument(
        "-c", "--case-mix",
        action="store_true",
        help="Generar todas las combinaciones posibles de mayúsculas y minúsculas para cada palabra clave (ej. 'Palabra' -> 'PaLaBrA')."
    )
    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="Forzar el inicio del generador en modo interactivo (útil si pasas otros argumentos pero quieres el menú)."
    )
    parser.add_argument(
        "-p", "--processes",
        type=int,
        help=f"Número de procesos a usar para la generación paralela. Por defecto, usa todos los núcleos disponibles ({os.cpu_count() if os.cpu_count() else 'desconocidos'})."
    )
    parser.add_argument(
        "-x", "--deduplicate",
        action="store_true",
        help="Elimina automáticamente los duplicados al finalizar la generación."
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Activa el modo verboso para ver mensajes de detalle adicionales."
    )

    try:
        args = parser.parse_args()

        if args.numbers:
            if args.years and args.digits:
                parser.error("No puedes usar --years y --digits al mismo tiempo. Elige uno o ninguno.")
        
        if args.limit is not None and args.limit <= 0:
            parser.error("El límite de claves debe ser un número positivo si se especifica.")
        
        if args.processes is not None and args.processes <= 0:
            parser.error("El número de procesos debe ser un número positivo si se especifica.")

        return parser, args
    except SystemExit as e:
        if e.code != 0:
            print("Error al procesar los argumentos de línea de comandos.")
        sys.exit(e.code)

def deduplicate_file_auto(input_filepath):
    """
    Elimina duplicados del archivo generado, detectando el SO.
    """
    output_filepath = f"{os.path.splitext(input_filepath)[0]}_unique{os.path.splitext(input_filepath)[1]}"
    
    tqdm.write(f"\nIniciando deduplicación automática de '{input_filepath}' a '{output_filepath}'...")
    _print_verbose(f"Detectando sistema operativo para deduplicación...")

    if sys.platform.startswith('linux') or sys.platform == 'darwin' or sys.platform == 'cygwin':
        # Linux, macOS, WSL, Git Bash
        command = f"sort -u \"{input_filepath}\" > \"{output_filepath}\""
        _print_verbose(f"Ejecutando comando: {command}")
        try:
            os.system(command)
            tqdm.write(f"Deduplicación completada con 'sort -u'. Archivo único guardado en '{output_filepath}'.")
        except Exception as e:
            tqdm.write(f"Error al ejecutar 'sort -u': {e}. Por favor, hazlo manualmente.")
            tqdm.write(f"Comando sugerido: sort -u \"{input_filepath}\" > \"{output_filepath}\"")
    elif sys.platform == 'win32':
        # Windows
        command = f"powershell -command \"Get-Content \\\"{input_filepath}\\\" | Sort-Object -Unique | Set-Content \\\"{output_filepath}\\\"\""
        _print_verbose(f"Ejecutando comando PowerShell: {command}")
        try:
            os.system(command)
            tqdm.write(f"Deduplicación completada con PowerShell. Archivo único guardado en '{output_filepath}'.")
        except Exception as e:
            tqdm.write(f"Error al ejecutar PowerShell: {e}. Por favor, hazlo manualmente.")
            tqdm.write(f"Comando sugerido en PowerShell: Get-Content '{input_filepath}' | Sort-Object -Unique | Set-Content '{output_filepath}'")
    else:
        tqdm.write("Sistema operativo no soportado para deduplicación automática. Por favor, hazlo manualmente.")
        tqdm.write(f"Para Linux/macOS: sort -u \"{input_filepath}\" > \"{output_filepath}\"")
        tqdm.write(f"Para Windows (PowerShell): Get-Content '{input_filepath}' | Sort-Object -Unique | Set-Content '{output_filepath}'")

def run_interactive_mode(generator, global_args):
    """
    Ejecuta el generador de diccionarios en modo interactivo.
    """
    print("\n--- Modo Interactivo del Generador de Diccionarios (Optimizado para MUY bajos recursos y Multi-Proceso) ---")
    
    # Preguntar por verbosidad al inicio del modo interactivo
    verbose_choice = get_interactive_input("¿Deseas activar el modo verboso (más mensajes de detalle)? (y/N): ",
                                           lambda x: x.lower() in ['y', 'n'],
                                           "Por favor, ingresa 'y' o 'n'. ").lower() == 'y'
    set_verbose_mode(verbose_choice) # Actualizar la variable global en contenido.py
    _print_verbose("Modo verboso activado.")
    
    print("Las contraseñas se escribirán directamente al archivo. El archivo final puede contener duplicados.")
    print("Puedes añadir múltiples palabras clave y configurar opciones para cada una.")
    print(f"Detectados {os.cpu_count() if os.cpu_count() else 'desconocidos'} núcleos de CPU. Por defecto, usaremos {global_args.processes if global_args.processes else os.cpu_count() if os.cpu_count() else '1'} procesos.")
    print("Escribe 'fin' en la palabra clave para terminar de añadir y comenzar la generación.")

    initial_output_file = get_interactive_input(
        f"Ingresa el nombre del archivo de salida (Enter para '{generator.output_file}'): ",
        validation_func=lambda x: x.strip() != "" or generator.output_file != "",
        error_message="El nombre del archivo no puede estar vacío."
    )
    if initial_output_file is None:
        return
    if initial_output_file:
        generator.output_file = initial_output_file

    output_dir = os.path.dirname(generator.output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        _print_verbose(f"Directorio de salida '{output_dir}' creado.")
        
    keywords_for_parallel_processing = [] # Aquí almacenaremos los datos para cada palabra clave

    try:
        # Asegurarse de que el archivo se crea vacío o se trunca antes de empezar a escribir
        with open(generator.output_file, "w") as f:
            pass # Solo abrir y cerrar para asegurar que el archivo esté vacío
        _print_verbose(f"Archivo de salida '{generator.output_file}' creado/truncado.")
            
        while True:
            base_word_input = get_interactive_input("\nIngresa una palabra clave base (o 'fin' para terminar de añadir): ")
            if base_word_input is None: 
                break
            if base_word_input.lower() == 'fin':
                break
            if not base_word_input:
                print("¡La palabra clave no puede estar vacía! Inténtalo de nuevo.")
                continue

            _print_verbose(f"Configurando opciones para palabra clave: '{base_word_input}'")
            # Crear un namespace temporal para esta palabra clave con sus settings
            current_keyword_settings = argparse.Namespace(
                numbers=False, digits=0, years_range=None,
                special_chars=None, case_mix=False, limit=None
            )

            add_numbers_choice = get_interactive_input("¿Deseas añadir números a esta palabra clave? (y/N): ",
                                                       lambda x: x.lower() in ['y', 'n'],
                                                       "Por favor, ingresa 'y' o 'n'. ").lower() == 'y'
            current_keyword_settings.numbers = add_numbers_choice
            
            if add_numbers_choice:
                num_type_choice = get_interactive_input("¿Quieres añadir años específicos (a) o números de una cantidad de dígitos (d)? (a/d): ",
                                                        lambda x: x.lower() in ['a', 'd'],
                                                        "Por favor, ingresa 'a' o 'd'. ").lower()
                if num_type_choice == 'a':
                    while True:
                        years_str = get_interactive_input("Ingresa el rango de años (ej. 1990-2025): ")
                        if years_str is None: break
                        try:
                            start_year, end_year = map(int, years_str.split('-'))
                            if start_year > end_year:
                                print("El año de inicio no puede ser mayor que el año de fin.")
                                continue
                            current_keyword_settings.years_range = (start_year, end_year)
                            _print_verbose(f"  Años configurados: {start_year}-{end_year}")
                            break
                        except ValueError:
                            print("Formato de años incorrecto. Usa 'AAAA-AAAA'.")
                elif num_type_choice == 'd':
                    while True:
                        num_digits_str = get_interactive_input("¿Cuántos dígitos quieres que tengan los números (ej. 3 para 000-999)? ")
                        if num_digits_str is None: break
                        try:
                            current_keyword_settings.digits = int(num_digits_str)
                            if current_keyword_settings.digits <= 0:
                                print("El número de dígitos debe ser positivo.")
                                continue
                            _print_verbose(f"  Dígitos configurados: {current_keyword_settings.digits}")
                            break
                        except ValueError:
                            print("Entrada inválida. Por favor, ingresa un número entero.")
                else:
                    _print_verbose("  No se añadieron números (opción inválida).")
                    current_keyword_settings.numbers = False

            add_special_chars_choice = get_interactive_input("¿Deseas añadir caracteres especiales a esta palabra clave? (y/N): ",
                                                             lambda x: x.lower() in ['y', 'n'],
                                                             "Por favor, ingresa 'y' o 'n'. ").lower() == 'y'
            if add_special_chars_choice:
                chars_input = get_interactive_input("Ingresa los caracteres especiales que deseas usar (ej. !,@,#,$): ")
                if chars_input is None: break
                current_keyword_settings.special_chars = [char.strip() for char in chars_input.split(',') if char.strip()]
                if not current_keyword_settings.special_chars:
                    print("No se ingresaron caracteres especiales válidos, no se añadirán.")
                    current_keyword_settings.special_chars = None
                    _print_verbose("  Caracteres especiales no válidos o vacíos.")
                else:
                    _print_verbose(f"  Caracteres especiales configurados: {', '.join(current_keyword_settings.special_chars)}")
            
            add_case_mix_choice = get_interactive_input("¿Deseas generar combinaciones de mayúsculas/minúsculas (ej. 'Palabra' -> 'pAlAbRa')? (y/N): ",
                                                        lambda x: x.lower() in ['y', 'n'],
                                                        "Por favor, ingresa 'y' o 'n'. ").lower() == 'y'
            current_keyword_settings.case_mix = add_case_mix_choice
            if add_case_mix_choice:
                _print_verbose("  Mezcla de mayúsculas/minúsculas activada.")

            limit_count = None
            limit_keys_choice = get_interactive_input("¿Deseas limitar el número de claves generadas para esta palabra? (y/N): ",
                                                      lambda x: x.lower() in ['y', 'n'],
                                                      "Por favor, ingresa 'y' o 'n'. ").lower() == 'y'
            if limit_keys_choice:
                while True:
                    limit_count_str = get_interactive_input(f"¿Cuántas claves deseas generar para '{base_word_input}' (Enter para sin límite)? ")
                    if limit_count_str is None: break
                    try:
                        if limit_count_str == "":
                            limit_count = None
                        else:
                            limit_count = int(limit_count_str)
                            if limit_count <= 0:
                                print("El número debe ser positivo.")
                                continue
                        _print_verbose(f"  Límite de claves configurado: {limit_count}")
                        break
                    except ValueError:
                            print("Entrada inválida. Por favor, ingresa un número entero.")
            current_keyword_settings.limit = limit_count
            
            keywords_for_parallel_processing.append({
                'keyword': base_word_input,
                'args': current_keyword_settings
            })
        
        if keywords_for_parallel_processing:
            _print_verbose(f"Total de palabras clave para procesar: {len(keywords_for_parallel_processing)}")
            generator.generate_dictionary_parallel(
                keywords_data=keywords_for_parallel_processing,
                output_filepath=generator.output_file,
                num_processes=global_args.processes
            )
            tqdm.write("\nNota: El archivo generado puede contener duplicados. La deduplicación se realiza después de la generación.")

            tqdm.write("\n--- Deduplicación del Diccionario ---")
            tqdm.write("ADVERTENCIA: Si el archivo generado es MUY GRANDE, la deduplicación puede consumir una cantidad SIGNIFICATIVA de RAM y CPU, y tomar mucho tiempo.")
            tqdm.write("En sistemas con recursos limitados, esta operación podría incluso ralentizar o colapsar el sistema.")
            deduplicate_choice = get_interactive_input("¿Deseas eliminar los duplicados automáticamente ahora? (y/N): ",
                                                       lambda x: x.lower() in ['y', 'n'],
                                                       "Por favor, ingresa 'y' o 'n'. ").lower() == 'y'
            if deduplicate_choice:
                deduplicate_file_auto(generator.output_file)
            else:
                tqdm.write("Deduplicación omitida. Puedes hacerlo manualmente más tarde si lo deseas.")
                tqdm.write(f"Para Linux/macOS: sort -u \"{generator.output_file}\" > \"{os.path.splitext(generator.output_file)[0]}_unique{os.path.splitext(generator.output_file)[1]}\"")
                tqdm.write(f"Para Windows (PowerShell): Get-Content '{generator.output_file}' | Sort-Object -Unique | Set-Content '{os.path.splitext(generator.output_file)[0]}_unique{os.path.splitext(generator.output_file)[1]}'")

        else:
            tqdm.write("No se ingresaron palabras clave. No se generó ningún diccionario.")

    except KeyboardInterrupt:
        tqdm.write(f"\nOperación cancelada por el usuario.")
    except Exception as e:
        tqdm.write(f"Ocurrió un error inesperado durante la generación interactiva: {e}")