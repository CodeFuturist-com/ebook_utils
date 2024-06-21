import os

from bs4 import BeautifulSoup
from ebook_utils.templates import *

#metodos auxiliares
from ebook_utils.utils import create_folder, compress, rem_dirs, check_epub, unzip, dir_toc, p_group, p_content, find_root_folder, epub_id, in_links

#devolver un 'BookMeta' con la metadata de un epub
def meta(epub: str):
  metadata_info: dict = {}  #estructura donde se almacenara la data
  tags = ['title', 'creator', 'identifier', 'publisher', 'subtitle', 'email'] #tags de la metadata en content
  
  #armar el directorio
  root_folder = find_root_folder(f"{epub.replace('.epub', '')}")
  dir = f"{epub.replace('.epub', '')}/{root_folder}"
    
  for file in os.listdir(dir):
    if '.opf' in file:
      dir += f'/{file}'
      break
  
  with open(dir, 'r') as f:
    doc = BeautifulSoup(f.read(), 'xml')
    
    #si el tag esta en la metadata del libro devuelve su contenido
    for tag in tags:
      tag_value = doc.find(f'dc:{tag}')
      metadata_info[tag] = tag_value.string.replace('&', '&amp') if tag_value != None else ''
        
  return BookMeta(metadata_info['title'], metadata_info['creator'], metadata_info['identifier'],
                  metadata_info['subtitle'], metadata_info['publisher'], metadata_info['email'])

def _child_text(epub: str, toc, path_toc: str, visited_links: set) -> dict:
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
        links = []
        i = 1 #enumerador de elementos para trabajar con llaves repetidas
        
        for element in doc.body.findAll('a'):
          if element.text != None and 'href' in element.attrs:
            if not in_links(links, element):
              links.append(element)
                
        for tag in links:
          if tag['href'].split('/')[-1] in visited_links:
            continue
          
          result[f'{i}.{tag.text}'] = epub_id(tag['href'], dir)
          i += 1

      return result

def _content_chapter(chapter: tuple[str, str], id_end=None) -> str:
      with open(chapter[0], 'r') as f:
        doc = BeautifulSoup(f, 'xml')

        #si no es 'None' significa que se referencia a un id
        if chapter[1] != None:
          return p_group(p_content(doc, doc.find(id=chapter[1]), id_end))
        
        #si es 'None' pero tiene limite significa que abarca todo el body hasta el limite
        if chapter[1] == None and id_end != None:
          return p_group(p_content(doc, doc.body, id_end))

        #dame todos los 'p' del directorio
        return p_group(p_content(doc))

def _content_rec(epub: str, result: list, absolute_toc: str, visited_links: set, link_path=None) -> list:
      data_toc = _child_text(epub, link_path, absolute_toc, visited_links) #por cada titulo, el path de lo que apunta cada link
      values = list(data_toc.values()) #valores del diccionario para preguntar por el id siguiente
      i = 0 #inicializar el iterador

      for key in data_toc:
        with open(data_toc[key][0], 'r') as f:
          doc = BeautifulSoup(f, 'xml')

          #si tiene mas de un tag 'a' y no tiene tags 'p' es una toc
          if len(doc.find_all('a')) > 1 and doc.find('p') == None:
            visited_links.add(f"{data_toc[key][0].split('/')[-1]}#{data_toc[key][1]}" if data_toc[key][1] != None else f"{data_toc[key][0].split('/')[-1]}")
            content = _content_rec(epub, [], absolute_toc, visited_links, data_toc[key][0])

            if len(content) != 0:
              result.append(BookToc(key[2:], content))

          #si hay 2 path iguales consecutivos, el title referencia a un id
          elif i < len(data_toc) - 1 and data_toc[key][0] == values[i + 1][0]:
            value_visit = f"{data_toc[key][0].split('/')[-1]}#{data_toc[key][1]}" if data_toc[key][1] != None else f"{data_toc[key][0].split('/')[-1]}"
            content = '' if value_visit in visited_links else _content_chapter(data_toc[key], values[i + 1][1])
            visited_links.add(value_visit)
            
            if content != '':
              result.append(BookChapter(key[2:], content))

          #en cualquier oto caso, dame todos los p
          else:
            value_visit = f"{data_toc[key][0].split('/')[-1]}#{data_toc[key][1]}" if data_toc[key][1] != None else f"{data_toc[key][0].split('/')[-1]}"
            content = '' if value_visit in visited_links else _content_chapter(data_toc[key])
            visited_links.add(value_visit)

            if content != '':
              result.append(BookChapter(key[2:], content))

        i += 1

      return result

def _content(epub: str) -> dict:
  unzip(epub) #descomprimir el epub
  absolute_toc = dir_toc(epub) #guardar la direccion de la toc del epub
  aux = set()
  aux.add(absolute_toc)
  result = _content_rec(epub, [], absolute_toc, aux) #respuesta
  rem_dirs([f"{epub.replace('.epub', '')}"]) #borrar el descomprimido luego del parsing
  return result

def is_toc(page: any) -> bool:
    if isinstance(page, BookToc): return True
    return False

class BookMeta:
    def __init__(self, title: str, author: str, ean: str, subtitle='', publisher='', email=''):
        self._meta = {
            'title': title,
            'author': author,
            'ean': ean,
            'subtitle': subtitle,
            'publisher': publisher,
            'email': email
        }

    def __getitem__(self, key):
        return self._meta[key]
    
    @classmethod
    def from_book(cls, book):
        metadata_info: dict = {}  #estructura donde se almacenara la data
        tags = ['title', 'creator', 'identifier', 'publisher', 'subtitle', 'email'] #tags de la metadata en content
        
        unzip(book)
        #armar el directorio
        root_folder = find_root_folder(f"{book.replace('.epub', '')}")
        dir = f"{book.replace('.epub', '')}/{root_folder}"
        
        for file in os.listdir(dir):
            if '.opf' in file:
                dir += f'/{file}'
                break
        
        with open(dir, 'r') as f:
            doc = BeautifulSoup(f.read(), 'xml')
          
            #si el tag esta en la metadata del libro devuelve su contenido
            for tag in tags:
                tag_value = doc.find(f'dc:{tag}')
                metadata_info[tag] = tag_value.string.replace('&', '&amp;') if tag_value != None else ''
        
        rem_dirs([f"{book.replace('.epub', '')}"]) 
              
        return cls(metadata_info['title'], metadata_info['creator'], metadata_info['identifier'],
                        metadata_info['subtitle'], metadata_info['publisher'], metadata_info['email'])

class BookChapter:
    def __init__(self, title: str, content: str) -> None:
        self._title = title
        self._content = content.replace('&', '&amp;')

    @property
    def title(self) -> str:
        return self._title

    @property
    def content(self) -> str:
        return self._content
    
    @content.setter
    def content(self, value: str):
       self._content = value.replace('&', '&amp;')
    
    def __str__(self) -> str:
        return self.title
    
    @property
    def ref(self) -> str:
       return self._ref
    
    def generate(self, meta: BookMeta, index: int) -> int:
        with open(f'my_epub/OEBPS/Text/part000{index}.xhtml', 'w') as f:
          self._ref = f'part000{index}.xhtml'
          f.write(CHAPTER.format(meta['title'], self.title, self.content))
        return index

class BookToc:
    def __init__(self, title: str, contents: list) -> None:
        self._title = title
        self._contents = contents

    @classmethod
    def from_book(cls, title: str, book: str):
      contents = _content(book)
      return cls(title, contents)   
    

    # Returns the plain page list of toc recursively
    @property
    def pages(self):
        page_list = []

        for item in self._contents:
            if is_toc(item):
                page_list = page_list + item.pages
            else:
                page_list.append(item)
        return page_list
    
    @property
    def title(self):
       return self._title

    @property
    def tocs_count(self):
        count = 1
        for page in self._contents:
           if is_toc(page):
              count += page.tocs_count
        return count
    
    def __str__(self) -> str:
       return f"{self.title}"
    
    def generate(self, meta: BookMeta, index: str, is_main=False) -> int:
        l_index = index

        if is_main:
            with open('my_epub/OEBPS/Text/contents.xhtml', 'w') as f:
                links = ''
              
                for page in self._contents:
                    links += TocLink(l_index + 1, page.title).content

                    if is_toc(page):
                        l_index = page.generate(meta, l_index + 1)
                    else:
                        l_index = page.generate(meta, l_index + 1)
                    
                f.write(TOC.format(links))
        else:
            with open(f'my_epub/OEBPS/Text/part000{l_index}.xhtml', 'w') as f:
                links = ''
              
                for page in self._contents:
                    links += TocLink(l_index + 1, page.title).content

                    if is_toc(page):
                        l_index = page.generate(meta, l_index + 1)
                    else:
                        l_index = page.generate(meta, l_index + 1)
                    
                f.write(NESTED_TOC.format(self.title, links))
        return l_index

#objeto para manejar los navpoints de toc.ncx
class NavPoint:
  def __init__(self, page: BookChapter, index: int) -> None:
    self._page = page
    self._index = index
    
  #generar el navpoint
  def _gen_content(self) -> str:
    result = ''
    result += f'<navPoint id="navPoint-{self._index}" playOrder="{self._index}">\n'
    result += '<navLabel>\n'
    result += f'<text>{self._page.title}</text>\n'
    result += '</navLabel>\n'
    result += f'<content src="Text/{self._page.ref}"/>\n'
    result += '</navPoint>\n'
    return result
    
  @property
  def content(self) -> str:
    return self._gen_content()

#objeto para manejar los links de la toc
class TocLink:
  def __init__(self, index: int, title: str) -> None:
    self._index = index
    self._title = title
    
  #generar el link
  def _gen_content(self) -> str:
    result = ''
    result += '<div class="sgc-toc-level-1 sgc-1">\n'
    result += f' <a href="part000{self._index}.xhtml">{self._title}</a>\n'
    result += '</div>\n'
    return result.replace('&', '&amp;')
    
  @property
  def content(self) -> str:
    return self._gen_content()

class Book:
    def __init__(self, toc: BookToc, meta: BookMeta) -> None:
        self._meta = meta
        self._toc = toc

    @classmethod
    def from_book(cls, book):
       meta = BookMeta.from_book(book)
       toc = BookToc.from_book(meta['title'], book)
       return cls(toc, meta)
    
    @property
    def title(self):
        return self._meta['title']

    @property
    def subtitle(self):
        return self._meta['subtitle']
    
    @property
    def author(self):
        return self._meta['author']
    
    @property
    def chapters(self):
        return self._get_chapters(self._toc)

    def _get_chapters(self, toc):
        chapters = []
        for item in toc.pages:
            if isinstance(item, BookChapter):
                chapters.append(item)
            elif isinstance(item, BookToc):
                chapters.extend(self._get_chapters(item))
        return chapters

    def export(self) -> str:
        #estructura fija
        self._gen_static_structure()
        
        #estructura variable
        self._gen_text()
        self._gen_toc_ncx()
        self._gen_content()
    
        #comprimir el epub, borrar el descomprimido y chequear el epub
        compress('my_epub', self._meta['ean'], '.epub')
        rem_dirs(['my_epub'])
        check_epub(f'{self._meta["ean"]}.epub')
        
        #devolver la ruta
        return f"{self._meta['ean']}.epub "
        
    #crear la estructura inicial que no varia en ningun epub  
    def _gen_static_structure(self):
        #carpetas iniciales
        create_folder('my_epub')
        create_folder('my_epub/META-INF')
        create_folder('my_epub/OEBPS')
        create_folder('my_epub/OEBPS/Images')
        create_folder('my_epub/OEBPS/Styles')
        create_folder('my_epub/OEBPS/Text')
    
        #styles
        with open('my_epub/OEBPS/Styles/frontpage.css', 'w') as f1:
            f1.write(FRONTPAGE_STYLES)
            
        #mimetype
        with open('my_epub/mimetype', 'w') as f:
            f.write('application/epub+zip')
        
        #container.xml
        with open('my_epub/META-INF/container.xml', 'w') as f1:
            f1.write(CONTAINERT_XML)
            
    #generar el toc.ncx     
    def _gen_toc_ncx(self):
        with open('my_epub/OEBPS/toc.ncx', 'w') as f1:
            f1.write(NCX.format(self._meta['ean'], self._meta['title'], self._gen_navPoint()))
                
    #generar los navPoints
    def _gen_navPoint(self) -> str:
        result = ''
        i = 3

        for page in self._toc.pages:
            result += NavPoint(page, i).content
            i += 1

        return result
    
    #generar la estructura inicial de content.opf   
    def _gen_content(self):
        with open('my_epub/OEBPS/content.opf', 'w') as f:
            f.write(CONTENT.format(self._meta['ean'], self._meta['title'], self._meta['author'], self._meta['publisher'],
                                self._gen_manifest(), self._gen_spine()))
                
    #indexar los textos en manifest
    def _gen_manifest(self) -> str:
        result = ''

        #agregar las referencias a la fontpage y a la toc en manifest 
        result += '<item id="frontpage.xhtml" href="Text/frontpage.xhtml" media-type="application/xhtml+xml"/>\n'
        result += '<item id="contents.xhtml" href="Text/contents.xhtml" media-type="application/xhtml+xml"/>\n'

        for i in range(1, len(self._toc.pages) + self._toc.tocs_count):
            result += f'<item id="section{i}.xhtml" href="Text/part000{i}.xhtml" media-type="application/xhtml+xml"/>\n'

        #agregar la referencia al css
        result += '<item id="frontpage.css" href="Styles/frontpage.css" media-type="text/css"/>\n'
        return result
    
    #generar el contenido de spine
    def _gen_spine(self) -> str:
        result = ''

        #agregar las referencias a la fontpage y a la toc en manifest 
        result += '<itemref idref="frontpage.xhtml"/>\n'
        result += '<itemref idref="contents.xhtml"/>\n'

        for i in range(1, len(self._toc.pages) + self._toc.tocs_count):
            result += f'<itemref idref="section{i}.xhtml"/>\n'

        return result
    
    #generar carpeta text
    def _gen_text(self):
        self._toc.generate(self._meta, 0, True)
        self._gen_front_toc()
        # self._gen_chapters()
        
    #generar la presentacion del libro y el toc
    def _gen_front_toc(self):
        #crear la frontpage
        with open('my_epub/OEBPS/Text/frontpage.xhtml', 'w') as f:
            f.write(FRONTPAGE.format(self._meta['title'], self._meta['author'], self._meta['subtitle'], self._meta['publisher'],
                                '' if self._meta['email'] == '' else 'Contact: ',self._meta['email'], self._meta['ean'])) 
                                
        #crear la toc
    
