import os
import unittest
import random

from books_loader import BooksLoader
from book import BookToc, BookChapter

class TestBookLoader(unittest.TestCase):
    def test_load_from_csv(self):
        filename ='tests/data/Bookwire OS Products-20231018153431-fragment.csv'
        directory = os.path.dirname(os.path.abspath(__file__))
        source = os.path.join(directory, filename)
        loader = BooksLoader.from_csv(source)

        self.assertIsNot(len(loader.books), 0)
    
    def test_load_from_xlxs(self):
        filename = 'tests/data/new_e-artnow.txt_2024.01.05_1201.xlsx'
        directory = os.path.dirname(os.path.abspath(__file__))
        source = os.path.join(directory, filename)
        loader = BooksLoader.from_xlsx(source)

        self.assertIsNot(len(loader.books), 0)

class TestBookToc(unittest.TestCase):
    def test_recursive_pages(self):
        toc1 = BookToc('Inner', [BookChapter("Ch1", "Content"), BookChapter("Ch2", "Content")])
        toc2 = BookToc("Outer", [toc1, BookChapter("Ch3", "Content")])

        self.assertEqual(len(toc2.pages), 3)

if __name__ == '__main__':
    unittest.main()
