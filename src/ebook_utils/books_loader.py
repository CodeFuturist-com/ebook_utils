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
    def __init__(self, productID, title, author, subtitle, bisac_1, bisac_1_text, bisac_2, bisac_2_text,  thema_1, wgs_text_1, price, keywords, description, author_bio, language='en'):
        self.productID = productID
        self.title = title
        self.author = author
        self.subtitle = subtitle
        self.bisac_1 = bisac_1
        self.bisac_1_text = bisac_1_text
        self.bisac_2 = bisac_2
        self.bisac_2_text = bisac_2_text
        self.keywords = keywords
        self.description = description
        self.author_bio = author_bio
        self.thema_1 = thema_1
        self.thema_1_text = ''
        self.thema_2 = ''
        self.thema_2_text = ''

        self.wgs_code_1 = ''
        self.wgs_text_1 = wgs_text_1
        self.wgs_code_2 = ''
        self.wgs_text_2 = ''
        self.price = price
        self.language = utils.get_language_from_code(language)
        self.new_description = ''

class BooksLoader():
    current_dir = os.path.dirname(__file__)
    _books = []
    _process_only = None

    def __init__(self, books) -> None:
        self._books = books

    @property
    def books(self):
        return self._books

    @classmethod
    def from_csv(cls, source, start=0, end=9348, process_only_path=''):
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
            productID = row[UNIQUE_COLUMN]
            title = row[COLUMN_TITLE]
            contributor = row[COLUMN_AUTHOR]
            author = utils.get_author_from_contributors_row(contributor)
            subtitle = row.get(COLUMN_SUBTITLE, '')
            language = row[COLUMN_LANGUAGE]
            bisac_1 = row.get(COLUMN_BISAC_1_CODE, '')
            bisac_2 = row.get(COLUMN_BISAC_2_CODE, '')
            bisac_1_text = row.get(COLUMN_BISAC_1_TEXT, '')
            bisac_2_text = row.get(COLUMN_BISAC_2_TEXT, '')
            thema_1 = row.get(COLUMN_THEMA_1_TEXT, '')
            wgs_text_1 = row.get(COLUMN_WGS_1_TEXT, '')
            keywords = row.get(COLUMN_KEYWORDS, '')
            description = row.get(COLUMN_DESCRIPTION, '')
            author_bio = row.get(COLUMN_AUTHOR_BIO, '')
        
            price  = row.get(COLUMN_PRICES, '')
            nbook = Book(productID, title, author, subtitle , bisac_1, bisac_1_text, bisac_2, bisac_2_text, thema_1, wgs_text_1, price,  keywords, description, author_bio, language=language)
            books.append(nbook)
        df.columns = original_column_names
        return cls(books)
    
    @classmethod
    def from_xlsx(cls, source, start=0, end=9348, process_only_path=''):
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

            productID = row[UNIQUE_COLUMN]
            title = row[COLUMN_TITLE]
            contributor = row[COLUMN_AUTHOR]
            author = utils.get_author_from_contributors_row(contributor)
            subtitle = row[COLUMN_SUBTITLE]
            bisac_1 = row.get(COLUMN_BISAC_1_CODE, '')
            bisac_2 = row.get(COLUMN_BISAC_2_CODE, '')
            bisac_1_text = row.get(COLUMN_BISAC_1_TEXT, '')
            bisac_2_text = row.get(COLUMN_BISAC_2_TEXT, '')
            
            thema_1 = ''
            wgs_text_1 = ''
            keywords = row.get(COLUMN_KEYWORDS, '')
            description = row.get(COLUMN_DESCRIPTION, '')
            author_bio = ''
            language = row[COLUMN_LANGUAGE]
            price  = ''
            
            nbook = Book(productID, title, author, subtitle, bisac_1, bisac_1_text, bisac_2, bisac_2_text, thema_1, wgs_text_1, price, keywords, description, author_bio, language=language)
            books.append(nbook)
        df.columns = original_column_names
        return cls(books)