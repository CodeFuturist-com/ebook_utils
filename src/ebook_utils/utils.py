import os
import pandas as pd
import re
import shutil
import zipfile

from babel import Locale
from bs4 import BeautifulSoup
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

#descomprimir un archivo
def unzip(file_name: str):
  extension = f".{file_name.split('.')[1]}"
  
  try:
    z = zipfile.ZipFile(file_name)
    file_dir = file_name.replace(extension, '')

    for name in z.namelist():
      z.extract(name, file_dir)
    
    z.close() 
    # print("Successful unpack")
    return
    
  except Exception as e:
    # print(e)
    return

#guardar la TOC de un epub
def dir_toc(epub: str) -> str:  
  #metodos para obtener la toc
  toc1 = toc_ncx_toc(epub)
  toc2 = guide_toc(epub)
  toc3 = title_toc(epub)
  
  if toc1 != '':
    return toc1
  
  if toc2 != '':
    return toc2
    
  return toc3

#TOC de cada epub por toc.ncx
def toc_ncx_toc(epub: str) -> str:
  root_folder = find_root_folder(f"{epub.replace('.epub', '')}")
  
  #guardar el directorio de cada epub
  dir = f"{epub.replace('.epub', '')}/{root_folder}/toc.ncx"
  
  with open(dir , 'r') as f:
    tocStage = False
    
    for line in f.readlines():
      if tocStage:
        if 'content' in line:
          return f'{parse_toc(line)}'
        
      if 'Table of Content' in line:
        tocStage = True

  return ''

#info de guide_tag
def guide_toc(epub: str) -> str:
  root_folder = find_root_folder(f"{epub.replace('.epub', '')}")
  #guardar el directorio del epub
  dir = f"{epub.replace('.epub', '')}/{root_folder}"
  result = ''
    
  for file in os.listdir(dir):
    if '.opf' in file:
      dir += f'/{file}'
      break
  
  #capturar la etiqueta guide
  with open(dir, 'r') as f1:
    doc = BeautifulSoup(f1, 'xml')
    
    try:
      result = doc.find('guide').find(type='toc')['href'].split('/')[-1]
    
    except:
      try:
        result = doc.find('guide').find(title='Table of Content')['href'].split('/')[-1]
        
      #no esta referenciada la content en la guide tag
      except:
        result = ''
  
  return result
  
#TOC por title 
def title_toc(epub: str) -> str:
  root_folder = find_root_folder(f"{epub.replace('.epub', '')}")
  #guardar el directorio del epub
  dir = f"{epub.replace('.epub', '')}/{root_folder}"
  result = ''
  
  for file in os.listdir(dir):
    if file.lower() == 'text':
      dir += f'/{file}' 
      break
      
  for file in os.listdir(dir):
    if '.xhtml' in file or '.html' in file:
      with open(f'{dir}/{file}', 'r') as f:
        doc = BeautifulSoup(f, 'xml')
        
        try:
          tilte_name = doc.find('title').string.lower().strip() 
          
          if tilte_name == 'contents':
            result = file
            return result
        
        except:
          continue
  
  return ''

#encontrar la carpeta raiz de os textos
def find_root_folder(directory: str):
  meta = ''
  
  for folder in os.listdir(directory):
    if folder.lower() == 'meta-inf':
      meta = folder
      
  with open(f'{directory}/{meta}/container.xml', 'r') as f:
    doc = BeautifulSoup(f, 'xml')
    return doc.find('rootfile')['full-path'].split('/')[0]

#returnar los 'p' entre 2 tags 
def p_content(doc: BeautifulSoup, tag_start=None, id_end=None):
  result = []
  flag_tag = False
  
  if tag_start == None:
    return doc.body.find_all('p')
  
  for element in doc.body.find_all():
    if flag_tag and element.name == 'p':
      result.append(element)
    
    if element == tag_start:
      flag_tag = True
      
    if  id_end != None and element == doc.find(id=id_end):
      break
    
  return result
      
#dada una lista de 'p', devolver los textos concatenados    
def p_group(p_tags: list) -> str:
  result = ''
  
  for tag in p_tags:
    result += f'{tag.text}\n'
    
  return result

#guardar el toc leido en la linea donde leo content
def parse_toc(toc: str):
  parse = toc.split('/')
  response = parse[1]
  return response.split('"')[0]

#devolver si se referencia a un id
def epub_id(epub: str, dir: str) -> tuple:
  split_data = epub.split('#')
  
  if len(split_data) == 1:
    return (f'{dir}/{epub}', None)
  
  return (f'{dir}/{split_data[0]}', split_data[1])

#determinar si un elemento esta en una lista de link y sustituirlo
def in_links(links: list, element) -> bool:
  for i in range(len(links)):
    if links[i]['href'] == element['href']:
      links[i] = element
      return True
  
  return False