import datetime



# Custom imports
from constants import DATETIME_FORMAT



# Classes
class Commit():

    def __init__(self, hash, date, author):
        self.hash = hash
        self.date = date
        self.author = author



    def __str__(self):
        return f'{self.hash} ({self.date.strftime(DATETIME_FORMAT)}) {self.author}'



    def to_json(self):
        return {
            'hash': self.hash,
            'date': datetime.datetime.strftime(self.date, DATETIME_FORMAT),
            'author': self.author,
        }



    @staticmethod
    def from_json(commit):
        return Commit(commit['hash'], datetime.datetime.strptime(commit['date'], DATETIME_FORMAT), commit['author'])