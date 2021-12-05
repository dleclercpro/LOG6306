import os
import json
import requests
import subprocess
import logging



# Custom imports
from constants import ISSUES_DIR, REPOS_DIR, SONAR_API, SONAR_PASSWORD, SONAR_PROJECT_PROPS_FNAME, SONAR_SCANNER, SONAR_TOKEN, SONAR_USERNAME
from repo import Repo



# CLASSES
class Project():

    def __init__(self, project):

        # Compute organization and name of project
        organization, name = project.split('/')

        self.organization = organization
        self.name = name

        self.repo = None
        self.remaining_commits = []

        self.dir = f'{REPOS_DIR}/{name}'
        self.issues_dir = f'{ISSUES_DIR}/{name}'



    def initialize(self):
        logging.info("Initializing project's repository...")

        # Move to data directory
        os.chdir(REPOS_DIR)


        # Initialize repo
        if os.path.exists(self.dir):
            self.repo = Repo(self.organization, self.name, self.dir)
        else:
            self.repo = Repo(self.organization, self.name)
            self.repo.clone(self.dir)


        # Get list of commits
        self.repo.load_commits()

        # If some commits have already been processed
        self.compute_remaining_commits()



    def compute_remaining_commits(self):
        logging.info("Computing remaining commits to process for project...")
        
        hashes = []

        # Compute list of commits which have already been processed
        if os.path.exists(self.issues_dir):
            for fname in os.listdir(self.issues_dir):
                hashes += [fname.split('.')[0]]

        # Compute the commits that are not yet processed
        self.remaining_commits = list(filter(lambda c: c.hash not in hashes, self.repo.commits))

        # Stats on commits
        n_commits = len(self.repo.commits)
        n_remaining_commits = len(self.remaining_commits)
        n_processed_commits = n_commits - n_remaining_commits



    def add_properties(self):
        logging.info('Generating SonarQube project properties file...')
        
        with open(f'{self.dir}/{SONAR_PROJECT_PROPS_FNAME}', 'w', encoding='UTF-8') as f:
            f.write(
                f'sonar.projectKey={self.name}\n' +
                'sonar.sources=.\n'+
                'sonar.sourceEncoding=UTF-8'
            )



    def checkout(self, commit):
        self.repo.checkout(commit)

        # Regenerate SonarQube project properties file
        self.add_properties()



    def scan(self):
        logging.info('Scanning for smells in current revision...')

        # Move to project's directory
        os.chdir(self.dir)

        # Launch SonarQube analysis of code smells
        subprocess.run([SONAR_SCANNER, f'-Dsonar.login={SONAR_TOKEN}'], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)



    def extract_smells(self):

        """
        WARNINGS:
        - Code smells in SonarQube do not have the same definition than that of Martin Fowler
        - SonarQube doesn't seem to be able to differentiate test code from production code using the 'scopes' argument
        """

        logging.info('Extracting smells from server...')


        # Define parameters to fetch project's smells on SonarQube server
        params = {
            'componentKeys': self.name,
            'languages': 'js,ts',
            #'types': 'CODE_SMELL',
            #'scopes': 'MAIN',
            'statuses': 'OPEN,REOPENED,CONFIRMED',
            #'rules': '',
        }

        # Define authentication for SonarQube server
        auth = (SONAR_USERNAME, SONAR_PASSWORD)


        # Fetch smells in batches
        batch = 1
        issues = []

        while True:
            res = requests.get(SONAR_API, params={'p': batch, **params}, auth=auth)
            res = res.json()

            # Add issues from this batch to results array
            issues += res['issues']

            # Read more info on next batches
            n_issues = res['total']
            batch_size = res['ps']

            # If all issues found: exit
            if batch * batch_size >= n_issues:
                break

            # Increment page index
            batch += 1

        logging.info(f'Found {len(issues)} issues.')


        # Store issues
        if not os.path.exists(self.issues_dir):
            os.makedirs(self.issues_dir)

        with open(f'{self.issues_dir}/{self.repo.current_commit.hash}.json', 'w', encoding='UTF-8') as f:
            json.dump(issues, f, sort_keys=True, indent=2)