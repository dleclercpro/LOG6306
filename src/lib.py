import os
import json
import logging
import pandas as pd

# Custom imports
from constants import EPSILON, JS_EXTENSIONS, TS_EXTENSIONS



def printJSON(obj):
    logging.info(json.dumps(obj, sort_keys=True, indent=2))



def format_seconds(seconds):
    time = seconds
    units = 's'

    if time >= 60:
        time /= 60.0
        units = 'm'
    
        if time >= 60:
            time /= 60.0
            units = 'h'

            if time >= 24:
                time /= 24.0
                units = 'd'

    return f'{round(time, 1)} {units}'



def ratio_to_percent(ratio, precision=0):
    percent = round(ratio * 100, precision)

    if abs(percent) < EPSILON:
        return '-'
    else:
        return f'{percent}%'



def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def load_dataframe(path, dtype=None, index_col=False):
    if os.path.isfile(path):
        with open(path, 'r', encoding='UTF-8') as f:
            return pd.read_csv(f, header=0, index_col=index_col, dtype=dtype)

def load_series(path, name=None, dtype=None):
    if os.path.isfile(path):
        with open(path, 'r', encoding='UTF-8') as f:
            s = pd.read_csv(f, header=None, index_col=0, squeeze=True, dtype=dtype)

            # Define series name
            s.name = name

            # Remove axis name
            s.axes[0].name = None

            return s



def store_json(obj, path):
    with open(path, 'w', encoding='UTF-8') as f:
        json.dump(obj, f, sort_keys=True, indent=2)

def store_dataframe(df, path, index=False):
    with open(path, 'w', encoding='UTF-8') as f:
        df.to_csv(f, index=index, header=True, line_terminator='\n')

def store_series(s, path):
    with open(path, 'w', encoding='UTF-8') as f:
        s.to_csv(f, index=True, header=False, line_terminator='\n')



def is_extension(file, extension):

    # No extension
    if '.' not in file:
        return False

    # Compute file extension
    ext = file.split('.')[-1]

    # Remove dot from extension
    extension = extension[1:]

    return ext == extension



def is_js_file(file):
    return any([is_extension(file, ext) for ext in JS_EXTENSIONS])

def is_ts_file(file):
    return any([is_extension(file, ext) for ext in TS_EXTENSIONS])

def is_test_file(file):
    if 'test' in file:
        return True

    return False