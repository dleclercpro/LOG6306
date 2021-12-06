import json
import logging



def printJSON(obj):
    logging.info(json.dumps(obj, sort_keys=True, indent=2))

def formatSeconds(seconds):
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



def store_dataframe(df, path):
    with open(path, 'w', encoding='UTF-8') as f:
        df.to_csv(f, index = False, header = True, line_terminator = '\n')

def store_series(s, path):
    with open(path, 'w', encoding='UTF-8') as f:
        s.to_csv(f, index = True, header = False, line_terminator = '\n')