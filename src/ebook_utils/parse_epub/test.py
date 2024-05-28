import os
from extract import content
from utils import create_folder, reset_folder

rel_path = os.path.dirname(os.path.abspath(__file__))

content_path = os.path.join(rel_path, "assets")
res_path = os.path.join(rel_path, "parse")

data = content(os.path.join(content_path, '9788026877301.epub'))
reset_folder(res_path)

def print_data(data: dict, path=res_path):
  for key in data:
    if type(data[key]) != dict:
      with open(f'{path}/{key}', 'w') as f:
        f.write(f'CONTENT:\n{data[key]}')
    
    else:
      create_folder(f'{path}/{key}')
      print_data(data[key], f'{path}/{key}')
      
#print_data(data)


    