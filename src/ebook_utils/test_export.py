from book import Book, BookChapter, BookMeta, BookToc

#no_request_data.keys(): publisher_name, publisher_email, subtitle
meta = BookMeta('ALL ABOUT SEX', 'Sr Sex', 'sex123')
pages = BookToc([BookChapter('cap1', 'sex1'), BookChapter('cap2', 'sex2'), BookChapter('cap3', 'sex3')])
book = Book(pages, meta)
book.export()