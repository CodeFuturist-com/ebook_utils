from extract import content
from utils import create_folder, reset_folder

data = content('src/ebook_utils/parse_epub/assets/collections/collection1.epub')
reset_folder('src/ebook_utils/parse_epub/parse')

def print_data(data: dict, path='src/ebook_utils/parse_epub/parse'):
  for key in data:
    if type(data[key]) != dict:
      with open(f'{path}/{key}', 'w') as f:
        f.write(f'CONTENT:\n{data[key]}')
    
    else:
      create_folder(f'{path}/{key}')
      print_data(data[key], f'{path}/{key}')
      
#print_data(data)


    