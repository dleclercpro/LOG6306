import os
import git
import logging
import requests
import pandas as pd



# Custom imports
from constants import RELEASES_DIR, TAGS_DIR, STATS_DIR, GITHUB_TOKEN, GITHUB_API
from lib import store_json, store_series, load_json, load_series
from tag import Tag



# Classes
class Repo():

    def __init__(self, owner, name, dir=None):
        self.owner = owner
        self.name = name

        self.url = f'https://github.com/{owner}/{name}.git'
        self.api = f'{GITHUB_API}/repos/{owner}/{name}'
        self.dir = dir

        self.repo = git.Repo(dir) if dir is not None else None
        self.current_release = None
        
        self.stats = {}
        self.tags = []
        self.releases = []

        self.stats_fname = f'{STATS_DIR}/{name}.csv'
        self.tags_fname = f'{TAGS_DIR}/{name}.json'
        self.releases_fname = f'{RELEASES_DIR}/{name}.json'



    def get_hash(self):
        if self.current_release is None:
            return None
        
        return self.current_release.commit_hash



    def clone(self, dir):
        logging.info(f'Cloning `{self.name}`...')

        # Clone repo locally
        self.repo = git.Repo.clone_from(self.url, to_path=dir)

        # Store repo's directory
        self.dir = dir



    def checkout(self, release):
        logging.info(f'Checking out repository to release: {release.name}...')

        # Store current commit hash
        self.current_release = release

        # Reset repo to given commit hash
        self.repo.head.reset(release.commit_hash, working_tree=True)
        self.repo.git.clean('-xdf')



    def call(self, endpoint=None):

        """
        Simple call to GitHub REST API (single page).
        """
        
        url = f'{self.api}/{endpoint}' if endpoint is not None else self.api
        logging.info(f'Calling: {url}')

        headers = {'Authorization': f'Bearer {GITHUB_TOKEN}'}
        
        res = requests.get(url, headers=headers)
        res = res.json()

        return res



    def big_call(self, endpoint=None):

        """
        Paginated call to GitHub REST API.
        """
        
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
        self.stats['tags_count'] = len(self.big_call('tags'))

        # Compute proportion of code taken up by each language
        bytes_by_language = pd.Series(self.call('languages'), dtype=float)
        languages = bytes_by_language / sum(bytes_by_language)

        self.stats['js_ratio'] = languages['JavaScript'] if 'JavaScript' in languages else 0
        self.stats['ts_ratio'] = languages['TypeScript'] if 'TypeScript' in languages else 0

        # Compute manually filtered recent releases
        self.stats['filtered_releases_count'] = len(self.releases)

        # Convert to dataframe
        self.stats = pd.Series(self.stats)

        # Store repo's stats
        store_series(self.stats, self.stats_fname)



    def read_stats(self):
        logging.info('Reading stats from disk...')
        
        self.stats = load_series(self.stats_fname)
        print(self.stats)



    def load_stats(self):
        logging.info('Loading stats...')

        # If stats haven't been generated, do it
        if not os.path.exists(self.stats_fname):
            self.fetch_stats()
        else:
            self.read_stats()

        logging.info(f'Stats loaded.')



    def fetch_tags(self):
        logging.info('Generating chronological list of tags...')

        # Fetch tags using GitHub API
        tags = self.big_call('tags')

        for tag in tags:
            self.tags += [Tag(tag['name'], tag['commit']['sha'])]

        # Reverse tag order to get chronological order
        self.tags = list(reversed(self.tags))

        # Store them
        store_json([tag.to_json() for tag in self.tags], self.tags_fname)



    def read_releases(self):
        logging.info('Reading releases from disk...')
        
        self.releases = [Tag.from_json(release) for release in load_json(self.releases_fname)]



    def load_releases(self):
        logging.info('Loading releases...')

        # If list of releases hasn't been generated, do it
        if not os.path.exists(self.releases_fname):
            self.fetch_tags()

            # WARNING: manual preprocessing of tags into release tags needed!
            raise RuntimeError('Preprocessing of tags not done!')

        else:
            self.read_releases()

        logging.info(f'Found {len(self.releases)} releases.')