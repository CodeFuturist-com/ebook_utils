from templates import *

#metodos auxiliares
from utils import create_folder, compress, rem_dir, check_epub

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

class BookChapter:
    def __init__(self, title: str, content: str) -> None:
        self._title = title
        self._content = content

    @property
    def title(self) -> str:
        return self._title

    @property
    def content(self) -> str:
        return self._content

class BookToc:
    def __init__(self, title: str, contents: list) -> None:
        self._title = title
        pages = []
        tocs = []

        for item in contents:
            # If the type is BookToc add it to tocs list
            if isinstance(item, self.__class__):
                tocs.append(item)
            else:
                pages.append(item)
           
        self._pages = pages
        self._tocs = tocs

    # TODO: Implement the book parsing here
    @classmethod
    def from_book(cls, book):
       contents = []
       return cls(contents)       

    # Returns the plain page list of toc recursively
    @property
    def pages(self):
        page_list = []
        page_list.extend(x.pages for x in self._tocs)
        page_list.extend(self._pages)        
        return page_list
    
    @property
    def title(self):
       return self._title

    @property
    def tocs(self):
        return self._tocs

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
    result += f'<content src="Text/part000{self._index - 3}.xhtml"/>\n'
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
    return result
    
  @property
  def content(self) -> str:
    return self._gen_content()

class Book:
  def __init__(self, toc: BookToc, meta: BookMeta) -> None:
      self._meta = meta
      self._toc = toc

  def export(self) -> str:
    #estructura fija
    self._gen_static_structure()
    
    #estructura variable
    self._gen_toc_ncx()
    self._gen_content()
    self._gen_text()
  
    #comprimir el epub, borrar el descomprimido y chequear el epub
    compress('my_epub', self._meta['ean'], '.epub')
    rem_dir(['my_epub'])
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

    # TODO: esto hay que cambiarlo a la nueva estructura recursiva de BookToc
    for page in self._toc._pages:
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

    for i in range(len(self._toc._pages)):
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

    # TODO: adaptarlo a la nueva estructura recursiva de BookToc
    for i in range(len(self._toc._pages)):
      result += f'<itemref idref="section{i}.xhtml"/>\n'

    return result
  
  #generar carpeta text
  def _gen_text(self):
    self._gen_front_toc()
    self._gen_chapters()
    
  #generar la presentacion del libro y el toc
  def _gen_front_toc(self):
    #crear la frontpage
    with open('my_epub/OEBPS/Text/frontpage.xhtml', 'w') as f:
      f.write(FRONTPAGE.format(self._meta['title'], self._meta['author'], self._meta['subtitle'], self._meta['publisher'],
                               '' if self._meta['email'] == '' else 'Contact: ',self._meta['email'], self._meta['ean'])) 
                              
    #crear la toc
    with open('my_epub/OEBPS/Text/contents.xhtml', 'w') as f:
      links = ''
      
      # TODO: adaptarlo a la nueva estructura recursiva de BookToc
      for i in range(len(self._toc._pages)):
        links += TocLink(i, self._toc[i].title).content
        
      f.write(TOC.format(links))

  #generar los capitulos
  def _gen_chapters(self):
      i = 0

      for page in self._toc._pages:  
        with open(f'my_epub/OEBPS/Text/part000{i}.xhtml', 'w') as f:
          f.write(CHAPTER.format(self._meta['title'], page.title, page.content))
          
        i += 1
