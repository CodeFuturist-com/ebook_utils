import os
import glob

from book import Book, BookChapter, BookMeta, BookToc
from utils import rem_dirs


#EXPORT
#meta = BookMeta('ALL ABOUT SEX', 'Sr Sex', 'sex123',subtitle='Sex Edition', email='sex@gmail.com')
#pages = BookToc([BookChapter('cap1', 'sex1'), BookChapter('cap2', 'sex2'), BookChapter('cap3', 'sex3')])
#book = Book(pages, meta)
#print(book.export())

#PARSE_BOOK
#rel_path = os.path.dirname(os.path.abspath(__file__))
#content_path = os.path.join(rel_path, "assets")
#data = BookToc.from_book('sex', os.path.join(content_path, '9788027244980.epub'))
#print(data)

PROCESS_SINGLE_FILE = False

if PROCESS_SINGLE_FILE:
    rel_path = os.path.dirname(os.path.abspath(__file__))
    content_path = os.path.join(rel_path, "parse_epub/assets")
    data = Book.from_book(os.path.join(content_path, '4064066399238.epub'))
    data.export()
else:
    rel_path = os.path.dirname(os.path.abspath(__file__))
    content_path = os.path.join(rel_path, "parse_epub/assets")
    epub_files = glob.glob(os.path.join(content_path, '*.epub'))

    for epub_file in epub_files:
        data = Book.from_book(epub_file)
        data.export()
#print(data)


