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