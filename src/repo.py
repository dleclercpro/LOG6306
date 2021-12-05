import os
import git
import json
import logging



# Custom imports
from constants import COMMITS_DIR
from commit import Commit



# Classes
class Repo():

    def __init__(self, organization, name, dir=None):
        self.organization = organization
        self.name = name

        self.url = f'https://github.com/{self.organization}/{self.name}.git'
        self.dir = dir

        self.repo = git.Repo(dir) if dir is not None else None
        self.commits = []
        self.current_commit = None
        self.commits_fname = f'{COMMITS_DIR}/{name}.json'



    def clone(self, dir):
        self.repo = git.Repo.clone_from(self.url, to_path=dir)

        # Store repo's directory
        self.dir = dir



    def checkout(self, commit):
        logging.info(f'Checking out repository to commit: {commit.hash}...')

        # Store current commit
        self.current_commit = commit

        # Reset repo to given commit
        self.repo.head.reset(commit.hash, working_tree=True)
        self.repo.git.clean('-xdf')



    def fetch_commits(self):
        logging.info('Generating chronological list of commits...')

        self.commits = []
        
        for c in self.repo.iter_commits():
            self.commits += [Commit(c.hexsha, c.committed_datetime, c.author.email)]

        # Reverse commit order to get chronological order
        self.commits = list(reversed(self.commits))

        with open(self.commits_fname, 'w', encoding='UTF-8') as f:
            json.dump([commit.to_json() for commit in self.commits], f, indent=2)



    def read_commits(self):
        logging.info('Reading commits from disk...')
        
        self.commits = []

        with open(self.commits_fname, 'r', encoding='UTF-8') as f:
            self.commits = [Commit.from_json(commit) for commit in json.load(f)]



    def load_commits(self):
        logging.info('Loading commits...')

        # If list of commits hasn't been generated, do it
        if not os.path.exists(self.commits_fname):
            self.fetch_commits()
        else:
            self.read_commits()

        logging.info(f'Found {len(self.commits)} commits.')