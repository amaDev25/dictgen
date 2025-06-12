import itertools
import os
import sys
from tqdm import tqdm
from multiprocessing import Pool, Manager, Lock

# Variable global para controlar la verbosidad
# Se actualizará desde el módulo principal (dictgen.py)
_verbose_mode = False 

def set_verbose_mode(mode):
    """Establece el modo verboso globalmente."""
    global _verbose_mode
    _verbose_mode = mode

def _print_verbose(message):
    """Imprime un mensaje solo si el modo verboso está activado."""
    if _verbose_mode:
        tqdm.write(f"[DETALLE] {message}")

class DictionaryGenerator:
    """
    Clase para generar diccionarios de contraseñas con varias opciones de mutación.
    Optimizada para bajo consumo de RAM y CPU, y ahora con procesamiento paralelo.
    """
    def __init__(self, output_file="dictionary.txt"):
        if not isinstance(output_file, str) or not output_file:
            raise ValueError("El nombre del archivo de salida no puede estar vacío.")
        self.output_file = output_file
        self.file_lock = None # Será inicializado por Manager en generate_dictionary_parallel

    def _generate_basic_variations(self, base_word):
        """
        Genera variaciones básicas (original, minúscula, mayúscula, capitalizada) de una palabra.
        Devuelve un generador.
        """
        _print_verbose(f"Generando variaciones básicas para: {base_word}")
        yield base_word
        yield base_word.lower()
        yield base_word.upper()
        yield base_word.capitalize()

    def _generate_case_variations(self, base_word):
        """
        Genera todas las combinaciones de mayúsculas y minúsculas para una palabra.
        Devuelve un generador.
        """
        if not isinstance(base_word, str) or not base_word:
            raise ValueError("La palabra base no puede estar vacía o no ser una cadena.")
        
        _print_verbose(f"Generando mezclas de mayúsculas/minúsculas para: {base_word}")
        for bits in itertools.product([0, 1], repeat=len(base_word)):
            new_word = "".join(
                char.upper() if bit else char.lower()
                for char, bit in zip(base_word, bits)
            )
            yield new_word

    def _generate_numbers_for_word(self, word, num_digits=0, years_range=None):
        """
        Genera variaciones numéricas para una *única palabra*.
        Devuelve un generador que incluye la palabra original y sus mutaciones numéricas.
        """
        _print_verbose(f"Añadiendo números a: {word}")
        yield word # Incluir la palabra original sin números

        numbers_to_add = []

        if years_range:
            if not isinstance(years_range, tuple) or len(years_range) != 2:
                raise ValueError("years_range debe ser una tupla de dos enteros (inicio, fin).")
            start_year, end_year = years_range
            _print_verbose(f"  Rango de años: {start_year}-{end_year}")
            if not all(isinstance(y, int) for y in years_range) or start_year > end_year:
                raise ValueError("Los años deben ser enteros válidos y el año de inicio no puede ser mayor que el de fin.")
            numbers_to_add.extend(range(start_year, end_year + 1))
        elif num_digits > 0:
            if not isinstance(num_digits, int) or num_digits <= 0:
                raise ValueError("num_digits debe ser un entero positivo.")
            _print_verbose(f"  Dígitos aleatorios: {num_digits}")
            try:
                max_num = 10**num_digits
                for i in range(max_num):
                    numbers_to_add.append(str(i).zfill(num_digits))
            except OverflowError:
                tqdm.write(f"Advertencia: El número de dígitos ({num_digits}) es demasiado grande, lo que podría generar demasiados números o un error.")
        
        for num in numbers_to_add:
            yield f"{word}{num}"
            yield f"{num}{word}"
            yield f"{word}_{num}"
            yield f"{num}_{word}"
            yield f"{word}{num}{word}"

    def _generate_special_chars_for_word(self, word, special_chars_list):
        """
        Genera variaciones con caracteres especiales para una *única palabra*.
        Devuelve un generador que incluye la palabra original y sus mutaciones con caracteres especiales.
        """
        _print_verbose(f"Añadiendo caracteres especiales a: {word} (Chars: {', '.join(special_chars_list)})")
        yield word # Incluir la palabra original sin caracteres especiales

        if not isinstance(special_chars_list, list) or not all(isinstance(c, str) for c in special_chars_list):
            raise ValueError("special_chars_list debe ser una lista de cadenas.")
        
        for char in special_chars_list:
            yield f"{word}{char}"
            yield f"{char}{word}"
            yield f"{word}{char}{word}"

    def _process_keyword(self, keyword_data):
        """
        Genera variaciones para una palabra clave basándose en los datos proporcionados
        y escribe directamente al archivo. Esta función es para ser ejecutada por cada proceso.
        """
        keyword = keyword_data['keyword']
        output_filepath = keyword_data['output_filepath']
        args_dict = keyword_data['args_dict']
        pbar_lock = keyword_data['pbar_lock']
        file_lock_manager = keyword_data['file_lock']

        try:
            add_numbers = args_dict['numbers']
            num_digits = args_dict['digits']
            years_range = args_dict['years_range']
            add_special_chars = args_dict['special_chars'] is not None and len(args_dict['special_chars']) > 0
            special_chars_list = args_dict['special_chars']
            add_case_mix = args_dict['case_mix']
            limit_keys = args_dict['limit']

            _print_verbose(f"Procesando '{keyword}' con settings: Números={add_numbers}, Digitos={num_digits}, Años={years_range}, Especiales={add_special_chars}, MezclaMayus={add_case_mix}, Límite={limit_keys}")

            if add_case_mix:
                base_variations_generator = self._generate_case_variations(keyword)
            else:
                base_variations_generator = self._generate_basic_variations(keyword)

            generated_count = 0
            
            for base_var in base_variations_generator:
                if add_numbers:
                    numbered_variations_generator = self._generate_numbers_for_word(
                        base_var, num_digits, years_range
                    )
                else:
                    numbered_variations_generator = iter([base_var])

                for num_var in numbered_variations_generator:
                    if add_special_chars and special_chars_list:
                        final_variations_generator = self._generate_special_chars_for_word(
                            num_var, special_chars_list
                        )
                    else:
                        final_variations_generator = iter([num_var])

                    for final_var in final_variations_generator:
                        with file_lock_manager:
                            with open(output_filepath, "a") as f:
                                f.write(final_var + "\n")
                        
                        with pbar_lock:
                            tqdm.total_pbar.update(1)
                        
                        generated_count += 1
                        if limit_keys is not None and generated_count >= limit_keys:
                            tqdm.write(f"Límite de {limit_keys} claves alcanzado para '{keyword}' en este proceso.")
                            return

            tqdm.write(f"Proceso para '{keyword}' finalizado. Generadas {generated_count} variaciones.")
        except KeyboardInterrupt:
            tqdm.write(f"\nProceso para '{keyword}' interrumpido por el usuario.")
        except Exception as e:
            tqdm.write(f"Error inesperado en proceso para '{keyword}': {e}")
    
    def generate_dictionary_parallel(self, keywords_data, output_filepath, num_processes=None):
        if num_processes is None:
            num_processes = os.cpu_count()
            if num_processes is None or num_processes < 1:
                num_processes = 1
            tqdm.write(f"Detectados {os.cpu_count() if os.cpu_count() else 'desconocidos'} núcleos de CPU. Usando {num_processes} procesos para la generación.")
        else:
            tqdm.write(f"Usando {num_processes} procesos para la generación.")

        _print_verbose(f"Iniciando pool de procesos con {num_processes} workers.")
        with Manager() as manager:
            self.file_lock = manager.Lock()
            pbar_lock = manager.Lock()

            tqdm.total_pbar = tqdm(desc="Total generado", unit="claves", leave=True, file=sys.stdout)

            tasks = []
            for item in keywords_data:
                args_dict_for_process = {
                    'numbers': item['args'].numbers,
                    'digits': item['args'].digits,
                    'years_range': item['args'].years_range,
                    'special_chars': item['args'].special_chars,
                    'case_mix': item['args'].case_mix,
                    'limit': item['args'].limit
                }
                tasks.append({
                    'keyword': item['keyword'],
                    'output_filepath': output_filepath,
                    'args_dict': args_dict_for_process,
                    'pbar_lock': pbar_lock,
                    'file_lock': self.file_lock
                })
            
            _print_verbose(f"Tareas de generación creadas: {len(tasks)}")
            with Pool(processes=num_processes) as pool:
                pool.map(self._process_keyword, tasks)
            
            tqdm.total_pbar.close()
            tqdm.write(f"\n¡Generación completa! Diccionario guardado en '{output_filepath}'.")