from models import BookProduction
from src.ebook_utils.book import Book

book_inst = Book.from_book('4064066459796.epub')

# book_prod = BookProduction(title='La Dama y el Vagabundo', subtitle='Bienvenido', author='Yandi Vargas', narrator='Libni Borrego', output_path='output/', description='Ease una vez...')
# book_prod.add_chapter("Chapter Title", "Chapter Content")
# book_prod.generate_voices(model="tts-1-hd", voice="alloy")
# book_prod.process_audio_files()
# Crear una instancia de BookProduction para el libro importado
book_prod = BookProduction(title=book_inst.title, subtitle=book_inst.subtitle, 
                           author=book_inst.author, narrator='Libni Borrego', 
                           output_path='output/', description='SSSSSSSSSSSSSS')

# Iterar sobre los capítulos del libro importado
for chapter in book_inst.chapters:
    # Agregar cada capítulo a la instancia de BookProduction
    book_prod.add_chapter(chapter.title, chapter.content)

# Generar voces para los capítulos
book_prod.generate_voices(model="tts-1-hd", voice="alloy", api_key='')

# Procesar archivos de audio para los capítulos
book_prod.process_audio_files()
