import os
import unittest

from ebook_utils.books_loader import BooksLoader

class TestBookLoader(unittest.TestCase):
    def test_load_from_csv(self):
        filename ='data/Bookwire OS Products-20231018153431-fragment.csv'
        directory = os.path.dirname(os.path.abspath(__file__))
        source = os.path.join(directory, filename)
        loader = BooksLoader.from_csv(source)

        self.assertIsNot(len(loader.books), 0)

    def test_load_from_xlxs(self):
        filename = 'data/new_e-artnow.txt_2024.01.05_1201.xlsx'
        directory = os.path.dirname(os.path.abspath(__file__))
        source = os.path.join(directory, filename)
        loader = BooksLoader.from_xlsx(source)

        self.assertIsNot(len(loader.books), 0)

if __name__ == '__main__':
    unittest.main()