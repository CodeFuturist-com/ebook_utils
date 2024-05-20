from book import Book, BookChapter, BookMeta, BookToc

meta = BookMeta('ALL ABOUT SEX', 'Sr Sex', 'sex123',subtitle='Sex Edition', email='sex@mail.com')
pages = BookToc([BookChapter('cap1', 'sex1'), BookChapter('cap2', 'sex2'), BookChapter('cap3', 'sex3')])
book = Book(pages, meta)
print(book.export())