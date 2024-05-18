#metodos auxiliares
from utils import create_folder, compress, rem_dir, check_epub

class BookMeta:
    def __init__(self, title: str, author: str, ean: str, no_request_data={}) -> None:
        #desestructurar los valores no requeridos
        #no_request_data.keys(): publisher_name, publisher_email, subtitle, date_epub
        self._meta = {
            'title': title,
            'author': author,
            'ean': ean,
            'subtitle': '' if not 'subtitle' in no_request_data.keys() else no_request_data['subtitle'],
            'publisher': '' if not 'publisher_name' in no_request_data.keys() else no_request_data['publisher_name'],
            'email': '' if not 'publisher_email' in no_request_data.keys() else no_request_data['publisher_email']
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
    def __init__(self, pages: list[BookChapter]) -> None:
        self._pages = pages

    def __getitem__(self, key):
        return self._pages[key]

class Book:
  def __init__(self, toc: BookToc, meta: BookMeta) -> None:
      self._meta = meta
      self._toc = toc

  def export(self) -> None:
    #estructura fija
    self._gen_static_structure()
    
    #estructura variable
    self._gen_toc_ncx()
    self._gen_content()
    self._gen_text()
  
    #comprimir el epub y borrar el descomprimido
    compress('my_epub', self._meta['ean'], '.epub')
    rem_dir(['my_epub'])
    
    #chequear el epub
    check_epub(f'{self._meta["ean"]}.epub')
      
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
      with open('src/ebook_utils/assets/templates/presentation_epub_example.css', 'r') as f2:
        f1.write(f2.read())
        
    #mimetype
    with open('my_epub/mimetype', 'w') as f:
      f.write('application/epub+zip')
      
    #container.xml
    with open('my_epub/META-INF/container.xml', 'w') as f1:
      with open('src/ebook_utils/assets/templates/container_example.xml', 'r') as f2:
        f1.write(f2.read())
        
  #generar el toc.ncx     
  def _gen_toc_ncx(self):
    with open('my_epub/OEBPS/toc.ncx', 'w') as f1:
      with open('src/ebook_utils/assets/templates/toc_example.ncx', 'r') as f2:
        for line in f2.readlines():
          if 'Ingresar codigo ISBN aqui' in line:
            f1.write(line.replace('Ingresar codigo ISBN aqui', self._meta['ean']))
            
          elif 'Ingresar titulo aqui' in line:
            f1.write(line.replace('Ingresar titulo aqui', self._meta['title']))
          
          elif 'Ingresar capitulos aqui' in line:
            f1.write(self._gen_navPoint())
            
          else:
            f1.write(line)
            
  #generar los navPoints
  def _gen_navPoint(self) -> str:
    result = ''
    i = 3

    for page in self._toc._pages:
      result += f'<navPoint id="navPoint-{i}" playOrder="{i}">\n'
      result += '<navLabel>\n'
      result += f'<text>{page.title}</text>\n'
      result += '</navLabel>\n'
      result += f'<content src="Text/part000{i - 3}.xhtml"/>\n'
      result += '</navPoint>\n'
      i += 1

    return result
  
  #generar la estructura inicial de content.opf   
  def _gen_content(self):
    with open('src/ebook_utils/assets/templates/content_example.opf', 'r') as f1:
      with open('my_epub/OEBPS/content.opf', 'w') as f2:
        for line in f1.readlines():
          if 'Ingresar titulo aqui' in line:
            f2.write(line.replace('Ingresar titulo aqui', self._meta['title']))

          elif 'Ingresar autor aqui' in line:
            f2.write(line.replace('Ingresar autor aqui', self._meta['author']))

          elif 'Ingresar editorial aqui' in line:
            f2.write(line.replace('Ingresar editorial aqui', self._meta['publisher']))

          elif 'Ingresar codigo ISBN aqui' in line:
            f2.write(line.replace('Ingresar codigo ISBN aqui', self._meta['ean']))

          elif 'Ingresar textos de manifest aqui' in line:
            f2.write(self._gen_manifest())

          elif 'Ingresar contenido de spine aqui' in line:
            f2.write(self._gen_spine())

          else:
            f2.write(line)
            
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
    with open('src/ebook_utils/assets/templates/presentation_epub_example.xhtml', 'r') as f1:
      with open('my_epub/OEBPS/Text/frontpage.xhtml', 'w') as f2:
        for line in f1.readlines():
          if 'Ingresar autor aqui' in line:
            f2.write(line.replace('Ingresar autor aqui', self._meta['author']))

          elif 'Ingresar titulo aqui' in line:
            f2.write(line.replace('Ingresar titulo aqui', self._meta['title']))

          elif 'Ingresar subtitulo aqui' in line and self._meta['subtitle'] != '':
            f2.write(line.replace('Ingresar subtitulo aqui', self._meta['subtitle']))

          elif 'Ingresar subtitulo aqui' in line and self._meta['subtitle'] == '':
            continue
          
          elif 'Ingresar editorial aqui' in line and self._meta['publisher'] != '':
            f2.write(line.replace('Ingresar editorial aqui', self._meta['publisher']))

          elif 'Ingresar editorial aqui' in line and self._meta['publisher'] == '':
            continue
          
          elif 'Ingresar email de la editorial aqui' in line and self._meta['email'] != '':
            f2.write(line.replace('Ingresar email de la editorial aqui', self._meta['email']))

          elif 'Ingresar email de la editorial aqui' in line and self._meta['email'] == '':
            continue
          
          elif 'Ingresar codigo ISBN aqui' in line:
            f2.write(line.replace('Ingresar codigo ISBN aqui', self._meta['ean']))

          else:
            f2.write(line)

    #crear la toc
    with open('src/ebook_utils/assets/templates/toc_epub_example.xhtml', 'r') as f1:
      with open('my_epub/OEBPS/Text/contents.xhtml', 'w') as f2:
        for line in f1.readlines():
          if 'Ingresar capitulos aqui' in line:
            for i in range(len(self._toc._pages)):
              f2.write('<div class="sgc-toc-level-1 sgc-1">\n')
              f2.write(f'<a href="part000{i}.xhtml">{self._toc[i].title}</a>\n')
              f2.write('</div>\n')

          else:
            f2.write(line)
  
  #generar los capitulos
  def _gen_chapters(self):
      i = 0

      for page in self._toc._pages:  
        with open('src/ebook_utils/assets/templates/chapter_example.xhtml', 'r') as f1:
          with open(f'my_epub/OEBPS/Text/part000{i}.xhtml', 'w') as f2:
            for line in f1.readlines():
              if 'Ingresar titulo aqui' in line:
                f2.write(line.replace('Ingresar titulo aqui', self._meta['title']))

              elif 'Ingresar nombre del capitulo' in line:
                f2.write(line.replace('Ingresar nombre del capitulo', page.title))

              elif 'Ingresar capitulo aqui' in line:
                f2.write(f'<p>{page.content}</p>\n')

              else:
                f2.write(line)

            i += 1