import os
import pandas as pd
import re
import shutil
import zipfile

from babel import Locale
from epubcheck import EpubCheck

def map_column_names(df, column_mapping):
    inverse_mapping = {variant.lower(): standard for standard, variants in column_mapping.items() for variant in variants}

    for col in df.columns:
        if col.lower() in inverse_mapping:
            df.rename(columns={col: inverse_mapping[col.lower()]}, inplace=True)

    return df

def get_language_from_code(code):
    code = code.lower()
    code = code.replace('"', "'")
    pattern = r"\['(.*?)'\]"
    match = re.match(pattern, code)
    if match:
        code = match.group(1)
    return Locale(code).get_display_name('en')

def get_author_from_contributors_row(row):
    if not pd.notnull(row):
        return ''
    match = re.search(r'\[AUTHOR\|(.*?)\|.*?]', row)
    if match:
        return match.group(1)
    return row

#comprimir un archivo
def compress(current_folder, new_path: str, extension: str):
  try:
    # Crear un archivo ZIP
    with zipfile.ZipFile(new_path, 'w') as z:
        # Agregar todos los archivos y subdirectorios de la carpeta de origen al archivo ZIP
        for raiz, directorios, archivos in os.walk(current_folder):
            for archivo in archivos:
                ruta_completa = os.path.join(raiz, archivo)
                ruta_relativa = os.path.relpath(ruta_completa, current_folder)
                z.write(ruta_completa, ruta_relativa)
    # Cambiar la extensión del archivo ZIP a .epub
    os.rename(new_path, new_path + extension)
    # print(f'Folder compressed to "{new_path}{extension}" succesfully')
        
  except Exception as e:
    # print(e)
    pass
  
#borrar folders
def rem_dir(dir: list):
  for d in dir:
    shutil.rmtree(d)
    # print('Succesful delete')

#crear una carpeta en caso de que no exista
def create_folder(path: str):
  if not os.path.exists(path):
    os.makedirs(path)
    
#validacion de epubs
def check_epub(epub_path):
    #imprime ok si el epub es valido en caso contrario los errores
    result = EpubCheck(epub_path)
    response, errors = result.valid, result.messages
    print('SUCCESFUL VALIDATION' if response else f'FAILED VALIDATION: {errors}')

