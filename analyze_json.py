import os
import re
import pandas as pd
import numpy as np
import json
import preprocessing_script as ps
import random
import json
from IPython.display import display, JSON
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import OrdinalEncoder, StandardScaler
from fast_langdetect import detect
from deep_translator import GoogleTranslator
from collections import Counter

def extract_QID11_TEXT(column):
    """
    extract and return specific value in json data
    """
    try:
        json_text = json.loads(column)['values']["QID11_TEXT"]
    except KeyError:
        json_text = "No QID11_TEXT"
    except json.JSONDecodeError:
        json_text = "Expecting ',' delimiter: line 1 column 10982 (char 10981)"
    return json_text

def extract_QID18_TEXT(column):
    """
    extract and return specific value in json data
    """
    try:
        json_text = json.loads(column)['values']["QID18_TEXT"]
    except KeyError:
        json_text = "No QID18_TEXT"
    except json.JSONDecodeError:
        json_text = "Expecting ',' delimiter: line 1 column 10982 (char 10981)"
    return json_text

def extract_QID22_TEXT(column):
    """
    extract and return specific value in json data
    """
    try:
        json_text = json.loads(column)['values']["QID22_TEXT"]
    except KeyError:
        json_text = "No QID22_TEXT"
    except json.JSONDecodeError:
        json_text = "Expecting ',' delimiter: line 1 column 10982 (char 10981)"
    return json_text

def extract_QID31_TEXT(column):
    """
    extract and return specific value in json data
    """
    try:
        json_text = json.loads(column)['values']["QID31_TEXT"]
    except KeyError:
        json_text = "No QID31_TEXT"
    except json.JSONDecodeError:
        json_text = "Expecting ',' delimiter: line 1 column 10982 (char 10981)"
    except AttributeError: 
        json_text = "DataFrame object has no attribute QID31_TEXT"
    return json_text

def extract_eyal_QID81_TEXT(column):
    """
    extract and return specific value in json data
    """
    try:
        json_text = json.loads(column)['values']["QID81_TEXT"]
    except TypeError:
        json_text = "No answer"
    except KeyError:
        json_text = "No QID81_TEXT"
    except json.JSONDecodeError:
        json_text = "Expecting ',' delimiter: line 1 column 10982 (char 10981)"
    except AttributeError: 
        json_text = "DataFrame object has no attribute QID81_TEXT"
    return json_text

def extract_eyal_QID84_TEXT(column):
    """
    extract and return specific value in json data
    """
    try:
        json_text = json.loads(column)['values']["QID84_TEXT"]
    except TypeError:
        json_text = "No answer"
    except KeyError:
        json_text = "No QID84_TEXT"
    except json.JSONDecodeError:
        json_text = "Expecting ',' delimiter: line 1 column 10982 (char 10981)"
    except AttributeError: 
        json_text = "DataFrame object has no attribute QID84_TEXT"
    return json_text

def extract_eyal_QID110_TEXT(column):
    """
    extract and return specific value in json data
    """
    try:
        json_text = json.loads(column)['values']["QID110_TEXT"]
    except TypeError:
        json_text = "No answer"
    except KeyError:
        json_text = "No QID110_TEXT"
    except json.JSONDecodeError:
        json_text = "Expecting ',' delimiter: line 1 column 10982 (char 10981)"
    except AttributeError: 
        json_text = "DataFrame object has no attribute QID110_TEXT"
    return json_text

def extract_eyal_QID154_TEXT(column):
    """
    extract and return specific value in json data
    """
    try:
        json_text = json.loads(column)['values']["QID154_TEXT"]
    except TypeError:
        json_text = "Empty Input"
    except KeyError:
        json_text = "No QID154_TEXT"
    except json.JSONDecodeError:
        json_text = "Expecting ',' delimiter: line 1 column 10982 (char 10981)"
    except AttributeError: 
        json_text = "DataFrame object has no attribute QID154_TEXT"
    return json_text

def extract_eyal_QID140_4_TEXT(column):
    """
    extract and return specific value in json data
    """
    try:
        json_text = json.loads(column)['values']["QID140_4_TEXT"]
    except TypeError:
        json_text = "No answer"
    except KeyError:
        json_text = "No QID140_TEXT"
    except json.JSONDecodeError:
        json_text = "Expecting ',' delimiter: line 1 column 10982 (char 10981)"
    except AttributeError: 
        json_text = "DataFrame object has no attribute QID140_TEXT"
    return json_text

def get_demography_text(df):
    df['QID11_TEXT'] = df['demography_body'].apply(extract_QID11_TEXT)
    df['QID18_TEXT'] = df['demography_body'].apply(extract_QID18_TEXT)
    df['QID22_TEXT'] = df['demography_body'].apply(extract_QID22_TEXT)
    df['QID31_TEXT'] = df['demography_body'].apply(extract_QID31_TEXT)
    return df

def get_eyal_answer_text(df):
    df['eyal_QID81_TEXT'] = df['eyal_answers'].apply(extract_eyal_QID81_TEXT)
    df['eyal_QID84_TEXT'] = df['eyal_answers'].apply(extract_eyal_QID84_TEXT)
    df['eyal_QID110_TEXT'] = df['eyal_answers'].apply(extract_eyal_QID110_TEXT)
    df['eyal_QID154_TEXT'] = df['eyal_answers'].apply(extract_eyal_QID154_TEXT)
    df['eyal_QID140_4_TEXT'] = df['eyal_answers'].apply(extract_eyal_QID140_4_TEXT)
    return df

def translate_2_en(column):
    translated = GoogleTranslator(source='auto', target='en').translate(column)
    if translated == None:
        return "Meaningless input"  # it can return the original column
    return translated

def translate(df):
    columns = ['QID11_TEXT', 'QID18_TEXT', 'QID22_TEXT', 'QID31_TEXT', 'eyal_QID81_TEXT', 'eyal_QID84_TEXT', 'eyal_QID110_TEXT', 'eyal_QID154_TEXT', 'eyal_QID140_4_TEXT']
    for column in columns:
        column_name = f"{column}_translated"
        df[column_name] = df[column].apply(translate_2_en)
    return df

def save_list_2_text(data, text_name):
    with open(f"./outputs/{text_name}.txt", "w") as file:
        for string in data:
            file.write(string + "\n")
    print(f"The data has been saved to {text_name}.txt.")

def read_text_to_list(text_name):
    with open(f"{text_name}.txt", 'r') as f:
        lines = f.readlines()
    return [line.rstrip() for line in lines]

def language_detect(sentence_list):
    ru, uk, en, others = 0, 0, 0, 0
    others_la = []
    for sentence in sentence_list:
        sentence = sentence.replace("\n", "")
        result = detect(sentence, low_memory=False)
        lang = result['lang']
        if lang == 'uk':
            uk += 1
        elif lang == 'ru':
            ru += 1
        elif lang == 'en':
            en += 1
        else:
            others += 1
            others_la.append(lang)

    print(f"Russian = {ru}, Ukrainian = {uk}, English = {en}, other languages = {others}.")
    print(f"For other languages: ", Counter(others_la).most_common())



# demography = profile_df[['demography_body']].apply(lambda x: x.str.replace('""', '"')) # replace "" to "
