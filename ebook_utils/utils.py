import re
import pandas as pd

from babel import Locale

def map_column_names(df, column_mapping):
    inverse_mapping = {variant.lower(): standard for standard, variants in column_mapping.items() for variant in variants}

    for col in df.columns:
        if col.lower() in inverse_mapping:
            df.rename(columns={col: inverse_mapping[col.lower()]}, inplace=True)

    return df

def get_language_from_code(code):
    code = code.lower()
    code = code.replace('"', "'")
    pattern = r"\['(.*?)'\]"
    match = re.match(pattern, code)
    if match:
        code = match.group(1)
    return Locale(code).get_display_name('en')

def get_author_from_contributors_row(row):
    if not pd.notnull(row):
        return ''
    match = re.search(r'\[AUTHOR\|(.*?)\|.*?]', row)
    if match:
        return match.group(1)
    return row