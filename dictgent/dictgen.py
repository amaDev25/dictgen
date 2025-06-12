# dictgen.py

import os
import sys
from tqdm import tqdm # Necesario para tqdm.write en el main
import argparse # Necesario para argparse.Namespace

# Importar las clases y funciones de los otros módulos
from contenido import DictionaryGenerator, set_verbose_mode # set_verbose_mode ahora viene de contenido
from parametros import parse_cli_arguments, run_interactive_mode, deduplicate_file_auto, _print_verbose

def main():
    """
    Función principal que orquesta la ejecución del generador de diccionarios.
    """
    # --- ASCII Art de Título ---
    print(r"""
          ___ ___ ___ _____ ___ ___ _  _ 
         |   \_ _/ __|_   _/ __| __| \| |
         | |) | | (__  | || (_ | _|| .` |
         |___/___\___| |_| \___|___|_|\_|
                                         
    """)
    # --- Fin ASCII Art ---
    print("\n--- Generador de Diccionarios Avanzado (Optimizado para Bajos Recursos y Multi-Proceso) ---\n") # Añadí un \n para más espacio
    
    parser_obj = None 
    args = None       
    try:
        parser_obj, args = parse_cli_arguments()
    except SystemExit:
        return 

    # Asignar el valor de verbosidad desde los argumentos CLI a la variable global en 'contenido.py'
    set_verbose_mode(args.verbose)
    _print_verbose("Modo verboso activado desde CLI.")

    # Determina si se proporcionaron argumentos relevantes por CLI (para no iniciar el interactivo por defecto)
    relevant_cli_args_provided = any(
        (key == 'keywords' and args.keywords is not None and len(args.keywords) > 0) or
        (key == 'numbers' and args.numbers) or
        (key == 'years' and args.years is not None) or
        (key == 'digits' and args.digits is not None) or
        (key == 'special_chars' and args.special_chars is not None and len(args.special_chars) > 0) or
        (key == 'limit' and args.limit is not None) or
        (key == 'case_mix' and args.case_mix)
        for key in ['keywords', 'numbers', 'years', 'digits', 'special_chars', 'limit', 'case_mix']
    )

    generator = None 
    try:
        generator = DictionaryGenerator(output_file=args.output)
    except ValueError as e:
        tqdm.write(f"Error de inicialización: {e}")
        return

    # Prepara el rango de años si se especificó (para pasar a los procesos)
    years_range = None
    if args.years:
        try:
            start_year, end_year = map(int, args.years.split('-'))
            if start_year > end_year:
                raise ValueError("El año de inicio no puede ser mayor que el año de fin.")
            years_range = (start_year, end_year)
            _print_verbose(f"Rango de años configurado: {years_range}")
        except ValueError as e:
            tqdm.write(f"Error en el formato de años: {e}. No se añadirán años.")
            args.numbers = False # Desactivar números si el formato de años es incorrecto
    
    # Asigna years_range a args para pasarlo a los procesos
    # Esto es importante porque 'args' se pasa completo a run_interactive_mode o a la generación directa.
    args.years_range = years_range

    try: # Bloque try-except para KeyboardInterrupt en el modo CLI y general
        if args.interactive or not relevant_cli_args_provided:
            # Ejecuta el modo interactivo
            run_interactive_mode(generator, args) 
        else: # Ejecuta el modo de línea de comandos (CLI)
            if not args.keywords: 
                tqdm.write("Error: En modo de línea de comandos, debes proporcionar al menos una palabra clave con -k o --keywords.")
                return
            
            output_dir = os.path.dirname(generator.output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                _print_verbose(f"Directorio de salida '{output_dir}' creado.")

            # Asegúrate de que el archivo se crea vacío o se trunca antes de empezar a escribir
            with open(generator.output_file, "w") as f:
                pass # Solo abrir y cerrar para asegurar que el archivo esté vacío
            _print_verbose(f"Archivo de salida '{generator.output_file}' creado/truncado.")

            # Prepara los datos para los procesos en CLI
            keywords_data_for_parallel = []
            for keyword in args.keywords:
                # En modo CLI, las configuraciones (numbers, digits, etc.) son globales para todas las keywords
                # Creamos un namespace para cada keyword para que _process_keyword pueda leerlo uniformemente
                keyword_specific_args = argparse.Namespace(
                    numbers=args.numbers,
                    digits=args.digits,
                    years_range=args.years_range, # Ya parseado arriba
                    special_chars=args.special_chars, # Ya es una lista o None
                    case_mix=args.case_mix,
                    limit=args.limit
                )
                keywords_data_for_parallel.append({
                    'keyword': keyword,
                    'args': keyword_specific_args # Las configuraciones son las mismas para todas las keywords en CLI
                })
            
            _print_verbose(f"Iniciando generación CLI para {len(keywords_data_for_parallel)} palabras clave.")
            # Llama a la función de generación paralela
            generator.generate_dictionary_parallel(
                keywords_data=keywords_data_for_parallel,
                output_filepath=generator.output_file,
                num_processes=args.processes
            )
            
            # Deduplicación automática si se solicitó en CLI
            if args.deduplicate:
                deduplicate_file_auto(generator.output_file)
            else:
                tqdm.write("Deduplicación omitida. Puedes hacerlo manualmente más tarde si lo deseas.")
                tqdm.write(f"Para Linux/macOS: sort -u \"{generator.output_file}\" > \"{os.path.splitext(generator.output_file)[0]}_unique{os.path.splitext(generator.output_file)[1]}\"")
                tqdm.write(f"Para Windows (PowerShell): Get-Content '{generator.output_file}' | Sort-Object -Unique | Set-Content '{os.path.splitext(generator.output_file)[0]}_unique{os.path.splitext(generator.output_file)[1]}'")

    except KeyboardInterrupt:
        tqdm.write(f"\nOperación principal cancelada por el usuario. Diccionario parcial guardado en '{generator.output_file}'.")
    except IOError as e:
        tqdm.write(f"Error de E/S al abrir o escribir el diccionario en '{generator.output_file}': {e}")
        tqdm.write("Verifica permisos de escritura o la ruta del archivo.")
    except Exception as e:
        tqdm.write(f"Ocurrió un error inesperado: {e}")


if __name__ == "__main__":
    # Importante para que multiprocessing funcione correctamente en Windows
    # Este bloque asegura que main() solo se ejecute cuando el script se inicia directamente.
    main()