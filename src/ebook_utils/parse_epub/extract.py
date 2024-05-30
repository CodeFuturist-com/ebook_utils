import os
from bs4 import BeautifulSoup
from utils import find_root_folder, parse_toc, unzip, rem_dir, epub_id, p_content, p_group

#dado un epub, parsear el contenido
def content(epub: str) -> dict:
  unzip(epub) #descomprimir el epub
  absolute_toc = dir_toc(epub) #guardar la direccion de la toc del epub
  result = content_rec(epub, {}, absolute_toc, absolute_toc) #respuesta
  rem_dir(f"{epub.replace('.epub', '')}") #borrar el descomprimido luego del parsing
  return result

#metodo recursivo para las collections
def content_rec(epub: str, result: dict, absolute_toc: str, parents_tocs: str, link_path=None) -> dict:
  data_toc = child_text(epub, link_path, absolute_toc, parents_tocs) #por cada titulo, el path de lo que apunta cada link
  values = list(data_toc.values()) #valores del diccionario para preguntar por el id siguiente
  i = 0 #inicializar el iterador
  
  for key in data_toc:
    with open(data_toc[key][0], 'r') as f:
      doc = BeautifulSoup(f, 'xml')
      
      #si tiene mas de un tag 'a' y no tiene tags 'p'
      if len(doc.find_all('a')) > 1 and doc.find('p') == None:
        content = content_rec(epub, {}, absolute_toc, f"{parents_tocs}|{data_toc[key][0].split('/')[-1]}", data_toc[key][0])
        
        if len(content) != 0:
          result[key] = content
        
      #si hay 2 path iguales consecutivos, el title referencia a un id
      elif i < len(data_toc) - 1 and data_toc[key][0] == values[i + 1][0]:
        content = content_chapter(data_toc[key], values[i + 1][1])

        if content != '':
          result[key] = content

      #en cualquier oto caso, dame todos los p
      else:
        content = content_chapter(data_toc[key])

        if content != '':
          result[key] = content
    
    i += 1
  
  return result
  
#guardar por cada title, la direccion de los capitulos
def child_text(epub: str, toc, path_toc: str, parents_tocs: str) -> dict:
  result = {} #respuesta
  root_folder = find_root_folder(f"{epub.replace('.epub', '')}") #carpeta raiz de los textos
  dir = f"{epub.replace('.epub', '')}/{root_folder}" #inicializar el directorio y la toc
  
  #construir el directorio
  for file in os.listdir(dir):
     if file.lower() == 'text':
       dir += f'/{file}'
       break
  
  #crear el toc
  if toc == None:
    toc = f'{dir}/{path_toc}'
   
  #obtener cada capitulo con el xhtml del texto
  with open(toc, 'r') as f:
    doc = BeautifulSoup(f, 'xml')
    links = [element for element in doc.body.findAll('a') if element.text != None and 'href' in element.attrs]
    parents = parents_tocs.split('|')
  
    for tag in links:
      in_href = False
      
      for element in parents:
        if element in tag['href']:
          in_href = True
          break
          
      if not in_href:
        result[f'{tag.text}'] = epub_id(tag['href'], dir)
    
  return result
    
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

#dado el nombre del capitulo extraer el texto correspondiente
def content_chapter(chapter: tuple[str, str], id_end=None) -> str:
  with open(chapter[0], 'r') as f:
    doc = BeautifulSoup(f, 'xml')
    
    if chapter[1] != None:
      return p_group(p_content(doc, doc.find(id=chapter[1]), id_end))
    
    return p_group(p_content(doc))
  