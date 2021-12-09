class Tag():

    def __init__(self, name, commit_hash):
        self.name = name
        self.commit_hash = commit_hash



    def __str__(self):
        return f'{self.name} [{self.commit_hash}]'



    def to_json(self):
        return {
            'name': self.name,
            'commit_hash': self.commit_hash,
        }



    @staticmethod
    def from_json(tag):
        return Tag(tag['name'], tag['commit_hash'])