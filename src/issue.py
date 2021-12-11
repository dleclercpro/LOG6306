import pandas as pd



# Classes
class Issue():

    def __init__(self, project, commit_hash, file_name, language, rule, type, severity, tags):
        self.project = project
        self.commit_hash = commit_hash
        self.file_name = file_name
        self.language = language
        self.rule = rule
        self.type = type
        self.severity = severity
        self.tags = tags