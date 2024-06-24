from models import BookProduction
from src.ebook_utils.book import Book

def generate_audiobook(book_path, narrator, output_path, description, model, voice, api_key):
    book_inst = Book.from_book(book_path)

    book_prod = BookProduction(title=book_inst.title, subtitle=book_inst.subtitle, 
                               author=book_inst.author, narrator=narrator, 
                               output_path=output_path, description=description)

    for chapter in book_inst.chapters:
        book_prod.add_chapter(chapter.title, chapter.content)

    book_prod.generate_voices(model=model, voice=voice, api_key=api_key)
    book_prod.process_audio_files()

generate_audiobook(book_path='test.epub', narrator='Yandi Vargas Domínguez', output_path='output/', description='', model='tts-1-hd', voice='alloy', api_key='')
