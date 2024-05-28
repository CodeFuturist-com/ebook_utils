#dependencias
import os
import shutil
import zipfile
from bs4 import BeautifulSoup

root_folders = [
  'OEBPS',
  'OPS'
]

def find_root_folder(directory):
  for item in os.listdir(directory):
    if item in root_folders:
      return item
  return ''

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

#borrar folders
def rem_dir(dir: str):
  if os.path.exists(dir):
    shutil.rmtree(dir)
  # print('Succesful delete')

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

#crear una carpeta en caso de que no exista
def create_folder(path: str):
  if not os.path.exists(path):
    os.makedirs(path)
    
#reiniciar una carpeta
def reset_folder(path: str):
  rem_dir(path)
  create_folder(path)

