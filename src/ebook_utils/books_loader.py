import os
import pandas as pd

import ebook_utils.utils as utils

DELIMITER = ';'

UNIQUE_COLUMN = 'id'

COLUMN_TITLE = 'Title'
COLUMN_SUBTITLE = 'Subtitle'
COLUMN_AUTHOR = 'Contributors'
COLUMN_DESCRIPTION = 'ProductInfoText'
COLUMN_KEYWORDS = 'Keywords'
COLUMN_AUTHOR_BIO = 'AuthorBiography'
COLUMN_LANGUAGE = 'ProductLanguage'
COLUMN_PRICES = 'StandardPrices'
COLUMN_BISAC_1_CODE = 'GenreCodeBisac1'
COLUMN_BISAC_1_TEXT = 'GenreTextBisac1'
COLUMN_WGS_1_CODE = 'GenreCodeWgs1'
COLUMN_WGS_1_TEXT = 'GenreTextWgs1'
COLUMN_THEMA_1_CODE = 'GenreCodeThema1'
COLUMN_THEMA_1_TEXT = 'GenreTextThema1'
COLUMN_BISAC_2_CODE = 'GenreCodeBisac2'
COLUMN_BISAC_2_TEXT = 'GenreTextBisac2'
COLUMN_WGS_2_CODE = 'GenreCodeWgs2'
COLUMN_WGS_2_TEXT = 'GenreTextWgs2'
COLUMN_THEMA_2_CODE = 'GenreCodeThema2'
COLUMN_THEMA_2_TEXT = 'GenreTextThema2'

COLUMN_NAME_MAPPING = {
    UNIQUE_COLUMN: ['ProductId', 'ID'],
    COLUMN_TITLE: ['Title', 'Name'],
    COLUMN_SUBTITLE: ['Subtitle'],
    COLUMN_AUTHOR: ['Author', 'Authors', 'Contributors', 'contributors_bookwire', 'Creator'],
    COLUMN_DESCRIPTION: ['ProductInfoText', 'Description', 'ProductDescription'],
    COLUMN_KEYWORDS: ['Keywords', 'Tags', 'ProductTags'],
    COLUMN_AUTHOR_BIO: ['AuthorBiography', 'AuthorBio', 'AuthorInfo', 'AuthorDescription', 'AuthorDescription', 'AuthorInformation'],
    COLUMN_LANGUAGE: ['Language', 'ProductLanguage'],
    COLUMN_PRICES: ['StandardPrices', 'Price'],
}

class Book: 
    """
        Represents a Book's metadata fields
    """

    def __init__(self, initial_fields: dict, language='en') -> None:
        self._fields = dict()

        for field in initial_fields.keys():
            self._fields[field] = initial_fields[field]

        if 'language' not in self._fields.keys():
            self._fields['language'] = utils.get_language_from_code(language)

    def fields(self):
        """
            Returns the field list on Book object
        """
        return self._fields.keys()

    def __getitem__(self, key):
        return self._fields[key]

    def __setitem__(self, key, value):
        self._fields[key] = value

class BooksLoader():
    """
        Loads Book's metadata from csv or excel files.
    """

    current_dir = os.path.dirname(__file__)

    def __init__(self, books) -> None:
        self._books = books

    @property
    def books(self) -> list[Book]:
        """
            Books metadata currently loaded.
        """
        return self._books

    @classmethod
    def from_csv(cls, source, start=0, end=9348, process_only_path=''):
        """
            Loads books metadata from a csv file.
            
            source: Path to csv file.
            process_only_path: Path to file with subset of book ids to process.
        """

        df = pd.read_csv(source, delimiter=DELIMITER, low_memory=False)
        books = []

        if process_only_path:
            #open file and get product ids
            only_path = os.path.join(cls.current_dir, process_only_path)
            process_only_df = pd.read_csv(only_path, delimiter=DELIMITER, low_memory=False)
            process_only_ids = set(process_only_df[UNIQUE_COLUMN])

        original_column_names = df.columns.copy()
        df = utils.map_column_names(df, COLUMN_NAME_MAPPING)

        for index, row in df.iterrows():
            if index < start:
                continue
            if index == end:
                break
            if process_only_path:
                if row[UNIQUE_COLUMN] not in process_only_ids:
                    continue
                
            book_fields = {
                'productID': row[UNIQUE_COLUMN],
                'title': row[COLUMN_TITLE],
                'contributor': row[COLUMN_AUTHOR],
                'author': utils.get_author_from_contributors_row(row[COLUMN_AUTHOR]),
                'subtitle': row.get(COLUMN_SUBTITLE, ''),
                'language': row[COLUMN_LANGUAGE],
                'bisac_1': row.get(COLUMN_BISAC_1_CODE, ''),
                'bisac_2': row.get(COLUMN_BISAC_2_CODE, ''),
                'bisac_1_text': row.get(COLUMN_BISAC_1_TEXT, ''),
                'bisac_2_text': row.get(COLUMN_BISAC_2_TEXT, ''),
                'thema_1': row.get(COLUMN_THEMA_1_TEXT, ''),
                'wgs_text_1': row.get(COLUMN_WGS_1_TEXT, ''),
                'keywords': row.get(COLUMN_KEYWORDS, ''),
                'description': row.get(COLUMN_DESCRIPTION, ''),
                'author_bio': row.get(COLUMN_AUTHOR_BIO, ''),
                'price': row.get(COLUMN_PRICES, '')
            }
            
            nbook = Book(book_fields)
            books.append(nbook)
        df.columns = original_column_names
        return cls(books)
    
    @classmethod
    def from_xlsx(cls, source, start=0, end=9348, process_only_path=''):
        """
            Loads books metadata from an excel file.
            
            source: Path to csv file.
            process_only_path: Path to file with subset of book ids to process.
        """

        df = pd.read_excel(source, engine='openpyxl')
        books = []
        
        if process_only_path:
            only_path = os.path.join(cls.current_dir, process_only_path)
            process_only_df = pd.read_csv(only_path, delimiter=DELIMITER, low_memory=False)
            process_only_ids = set(process_only_df['id'])

        original_column_names = df.columns.copy()
        df = utils.map_column_names(df, COLUMN_NAME_MAPPING)
        for index, row in df.iterrows():
            if index < start:
                continue
            if index == end:
                break
            if process_only_path:
                if row['id'] not in process_only_ids:
                    continue
            
            book_fields = {
                'productID': row[UNIQUE_COLUMN],
                'title': row[COLUMN_TITLE],
                'contributor': row[COLUMN_AUTHOR],
                'author': utils.get_author_from_contributors_row(row[COLUMN_AUTHOR]),
                'subtitle': row[COLUMN_SUBTITLE],
                'bisac_1': row.get(COLUMN_BISAC_1_CODE, ''),
                'bisac_2': row.get(COLUMN_BISAC_2_CODE, ''),
                'bisac_1_text': row.get(COLUMN_BISAC_1_TEXT, ''),
                'bisac_2_text': row.get(COLUMN_BISAC_2_TEXT, ''),
                'thema_1': '',
                'wgs_text_1': '',
                'keywords': row.get(COLUMN_KEYWORDS, ''),
                'description': row.get(COLUMN_DESCRIPTION, ''),
                'author_bio': '',
                'language': row[COLUMN_LANGUAGE],
                'price': ''
            }            
            
            nbook = Book(book_fields)
            books.append(nbook)
        df.columns = original_column_names
        return cls(books)
