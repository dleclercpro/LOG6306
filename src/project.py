import os
import time
import math
import requests
import subprocess
import logging



# Custom imports
from constants import ISSUES_DIR, REPOS_DIR, SONAR_API, SONAR_PASSWORD, SONAR_PROJECT_PROPS_FNAME, SONAR_SCANNER, SONAR_TOKEN, SONAR_USERNAME, STATS_DIR
from repository import Repo
from lib import store_json



# CLASSES
class Project():

    def __init__(self, project):

        # Compute owner and name of project
        owner, name = project.split('/')

        self.owner = owner
        self.name = name

        self.repo = None
        self.remaining_commits = []
        self.remaining_tags = []

        self.dir = f'{REPOS_DIR}/{name}'
        self.stats_fname = f'{STATS_DIR}/{name}.csv'
        self.issues_dir = f'{ISSUES_DIR}/{name}'

        # Define authentication for SonarQube server
        self.sonar_auth = (SONAR_USERNAME, SONAR_PASSWORD)



    def initialize(self):
        logging.info(f'Initializing repository for: {self.name}')

        # Move to data directory
        os.chdir(REPOS_DIR)


        # Initialize repo
        if os.path.exists(self.dir):
            self.repo = Repo(self.owner, self.name, self.dir)
        else:
            self.repo = Repo(self.owner, self.name)
            self.repo.clone(self.dir)

        # Load repo's list of commits
        #self.repo.load_commits()
        self.repo.load_tags()

        # Load repo's stats
        self.repo.load_stats()

        # If some commits have already been processed
        #self.compute_remaining_commits()
        self.compute_remaining_tags()



    def get_recent_commits(self, n=100):
        return self.repo.commits[-n:]

    def get_recent_tags(self, n=25):
        return self.repo.tags[-n:]



    def compute_remaining_commits(self):
        logging.info('Computing remaining commits to process for project...')
        
        # Compute list of commits which have already been processed
        hashes = []
        
        if os.path.exists(self.issues_dir):
            for fname in os.listdir(self.issues_dir):
                hashes += [fname.split('.')[0]]

        # Only consider the last X commits [time constraint]
        recent_commits = self.get_recent_commits()

        # Compute the commits that are not yet processed
        self.remaining_commits = list(filter(lambda c: c.hash not in hashes, recent_commits))
        logging.info(f'Found {len(self.remaining_commits)} commits to process.')



    def compute_remaining_tags(self):
        logging.info('Computing remaining tags to process for project...')
        
        # Compute list of tags which have already been processed
        hashes = []
        
        if os.path.exists(self.issues_dir):
            for fname in os.listdir(self.issues_dir):
                hashes += [fname.split('.')[0]]

        # Only consider the last X tags [time constraint]
        recent_tags = self.get_recent_tags()

        # Compute the tags that are not yet processed
        self.remaining_tags = list(filter(lambda t: t.commit_hash not in hashes, recent_tags))
        logging.info(f'Found {len(self.remaining_tags)} tags to process.')



    def add_properties(self):
        logging.info('Generating SonarQube project properties file...')
        
        with open(f'{self.dir}/{SONAR_PROJECT_PROPS_FNAME}', 'w', encoding='UTF-8') as f:
            f.write(
                f'sonar.projectKey={self.name}\n' +
                'sonar.sources=.\n' +
                'sonar.sourceEncoding=UTF-8\n' +
                'sonar.inclusions=**/*.js,**/*.ts\n' +
                'sonar.exclusions=**/test/**/*,**/*test*\n' +
                'sonar.coverage.exclusions=**/*\n' +
                'sonar.cpd.exclusions=**/*'
            )



    def checkout(self, tag):
        self.repo.checkout(tag)

        # Regenerate SonarQube project properties file
        self.add_properties()



    def scan(self):
        logging.info('Scanning for smells in current revision...')

        # Move to project's directory
        os.chdir(self.dir)

        # Launch SonarQube analysis of code smells
        #subprocess.run([SONAR_SCANNER, f'-Dsonar.login={SONAR_TOKEN}'], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        subprocess.run([SONAR_SCANNER, f'-Dsonar.login={SONAR_TOKEN}'], stdout=subprocess.DEVNULL)



    def are_issues_ready(self):

        # Define parameters to fetch project's activity status on SonarQube server
        params = {'component': self.name}

        # Fetch activity status on server
        res = requests.get(f'{SONAR_API}/ce/activity_status', params=params, auth=self.sonar_auth)
        res.raise_for_status()

        # Extract data from call
        data = res.json()

        # Look at activity statuses to determine whether server is ready to serve issues
        statuses = ['pending', 'inProgress', 'failing']
        ready = True

        for status, s in [(status, int(data[status])) for status in statuses]:
            ready = ready and s == 0
            logging.info(f'{status.upper()}: {s}')

        if not ready:
            logging.info('SonarQube server is not ready to serve issues.')

        return ready



    def fetch_issues(self):
        logging.info('Fetching issues from server...')

        # Define parameters to fetch project's smells on SonarQube server
        params = {
            'componentKeys': self.name,
            'languages': 'js,ts',
            'types': 'BUG,CODE_SMELL',
            'statuses': 'OPEN,REOPENED,CONFIRMED',
        }

        # Fetch smells in batches
        page = 1
        page_size = 500
        n_pages = -1
        n_issues = -1
        issues = []

        while True:
            current_params = {'p': page, 'ps': page_size, **params}

            # Fetch issues on server
            logging.info(f"Fetching page: {page}/{n_pages if n_pages != -1 else '?'}")
            res = requests.get(f'{SONAR_API}/issues/search', params=current_params, auth=self.sonar_auth)
            res.raise_for_status()

            # Extract data from call
            data = res.json()

            # Add issues from this batch to results array
            issues += data['issues']

            # Read more info on next batches
            n_issues = int(data['paging']['total'])
            n_pages = math.ceil(n_issues / page_size)

            # No issues found: exit
            if n_issues == 0:
                raise SystemError('No issues found?')

            # Max number of issues polled: exit
            if n_issues > 10_000:
                raise SystemError('Too many issues to be fetched from SonarQube server.')

            # All issues found: exit
            if page == n_pages:
                break

            # Increment page index
            page += 1

        return issues



    def extract_smells(self):

        """
        WARNINGS:
        - Code smells in SonarQube do not have the same definition than that of Martin Fowler
        - SonarQube doesn't seem to be able to differentiate test code from production code using the 'scopes' argument
        """

        # Wait until the SonarQube server has processed the issues in the
        # current revision of the repository
        wait = 5

        while True:
            try:
                if self.are_issues_ready():
                    break
                else:
                    logging.info(f'Waiting {wait} seconds...')
                    time.sleep(wait)

            except requests.exceptions.HTTPError as e:
                logging.error(e)

        # Fetch smells
        issues = self.fetch_issues()
        logging.info(f'Found {len(issues)} issues.')

        # Store issues
        if not os.path.exists(self.issues_dir):
            os.makedirs(self.issues_dir)

        store_json(issues, f'{self.issues_dir}/{self.repo.current_commit.hash}.json')