import os
import git
import json
import logging
import requests
import pandas as pd



# Custom imports
from constants import STATS_DIR, COMMITS_DIR, GITHUB_TOKEN, GITHUB_API
from lib import store_series
from commit import Commit



# Classes
class Repo():

    def __init__(self, owner, name, dir=None):
        self.owner = owner
        self.name = name

        self.url = f'https://github.com/{owner}/{name}.git'
        self.api = f'{GITHUB_API}/repos/{owner}/{name}'
        self.dir = dir
        self.stats = {}

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



    def call(self, endpoint=None):
        url = f'{self.api}/{endpoint}' if endpoint is not None else self.api
        logging.info(f'Calling: {url}')

        headers = {'Authorization': f'Bearer {GITHUB_TOKEN}'}
        
        res = requests.get(url, headers=headers)
        res = res.json()

        return res



    def big_call(self, endpoint=None):
        url = f'{self.api}/{endpoint}' if endpoint is not None else self.api
        logging.info(f'GET: {url}')

        # Initialize pagination variables
        page = 1
        last_page = 1
        per_page = 100

        # Initialize results
        results = []

        # Poll until end of results
        while True:
            logging.info(f"Fetching page: {page}/{last_page if last_page != 1 else '?'}")

            params = {'page': page, 'per_page': per_page}
            headers = {'Authorization': f'Bearer {GITHUB_TOKEN}'}
            
            res = requests.get(url, params=params, headers=headers)
            results += res.json()

            # Parse last page from 'Link' header (if it exists) on first call
            if page == 1 and 'Link' in res.headers:
                last_page = int(
                    res.headers['Link']
                        .split(f'&per_page={per_page}>; rel="last"')[0]
                        .split('?page=')[-1]
                )

            if page == last_page:
                break
            else:
                page += 1

        return results



    def fetch_stats(self):
        logging.info('Fetching repository info...')

        # General info
        info = self.call()

        self.stats['created_at'] = info['created_at']
        self.stats['forks_count'] = info['forks_count']
        self.stats['stargazers_count'] = info['stargazers_count']
        self.stats['watchers_count'] = info['watchers_count']
        self.stats['open_issues_count'] = info['open_issues_count']
        self.stats['commits_count'] = len(self.big_call('commits'))
        self.stats['contributors_count'] = len(self.big_call('contributors'))
        self.stats['releases_count'] = len(self.big_call('releases'))

        # Compute proportion of code taken up by each language
        bytes_by_language = pd.Series(self.call('languages'), dtype=float)
        languages = bytes_by_language / sum(bytes_by_language)

        self.stats['js_proportion'] = languages['JavaScript'] if 'JavaScript' in languages else 0
        self.stats['ts_proportion'] = languages['TypeScript'] if 'TypeScript' in languages else 0

        # Convert to dataframe
        self.stats = pd.Series(self.stats)
        print(self.stats)

        # Store repo's stats
        store_series(self.stats, f'{STATS_DIR}/{self.name}.csv')



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