import os
import time
import math
import requests
import subprocess
import logging



# Custom imports
from constants import SONAR_API, SONAR_PASSWORD, SONAR_PROJECT_PROPS_FNAME, SONAR_SCANNER, SONAR_TOKEN, SONAR_USERNAME
from lib import store_json



# Useful constants
MAX_ISSUES = 10_000
WAIT_TIME = 5
ACTIVITY_STATUSES = ['pending', 'inProgress', 'failing']

ISSUES_API = f'{SONAR_API}/issues/search'
ACTIVITY_API = f'{SONAR_API}/ce/activity_status'
DELETE_API = f'{SONAR_API}/projects/delete'



# CLASSES
class Sonar():

    def __init__(self, project):
        self.project = project

        # Define authentication for SonarQube server
        self.sonar_auth = (SONAR_USERNAME, SONAR_PASSWORD)



    def delete(self):
        logging.info(f'Deleting project `{self.project.name}` on SonarQube...')

        # Define parameters to delete project on SonarQube server
        params = {'project': self.project.name}

        try:
            res = requests.post(DELETE_API, params=params, auth=self.sonar_auth)
            res.raise_for_status()

            logging.info('Project deleted.')

        except requests.exceptions.HTTPError as err:
            if res.status_code == 404:
                logging.info('Project did not exist.')
                return
            
            raise err



    def scan(self):
        logging.info('Scanning for smells in current revision...')

        # Move to project's directory
        os.chdir(self.project.dir)

        # Add project properties to project's directory
        self.add_properties()

        # Launch SonarQube analysis of code smells
        #subprocess.run([SONAR_SCANNER, f'-Dsonar.login={SONAR_TOKEN}'], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        subprocess.run([SONAR_SCANNER, f'-Dsonar.login={SONAR_TOKEN}'], stdout=subprocess.DEVNULL)



    def add_properties(self):
        logging.info('Generating SonarQube project properties file...')
        
        with open(f'{self.project.dir}/{SONAR_PROJECT_PROPS_FNAME}', 'w', encoding='UTF-8') as f:
            f.write(
                f'sonar.projectKey={self.project.name}\n' +
                'sonar.sources=.\n' +
                'sonar.sourceEncoding=UTF-8\n' +
                'sonar.inclusions=**/*.js,**/*.ts\n' +
                'sonar.exclusions=**/test/**/*,**/tests/**/*,**/*test*\n' +
                'sonar.coverage.exclusions=**/*\n' +
                'sonar.cpd.exclusions=**/*'
            )



    def is_ready(self):

        """
        Find out if SonarQube server is ready to serve issues.
        """

        # Define parameters to fetch project's activity status on SonarQube server
        params = {'component': self.project.name}

        # Fetch activity status on server
        res = requests.get(ACTIVITY_API, params=params, auth=self.sonar_auth)
        res.raise_for_status()

        # Extract data from call
        data = res.json()

        # Look at activity statuses to determine whether server is ready to serve issues
        statuses = ACTIVITY_STATUSES
        ready = True

        for status, s in [(status, int(data[status])) for status in statuses]:
            ready = ready and s == 0
            logging.info(f'{status.upper()}: {s}')

        if not ready:
            logging.info('SonarQube server is not ready to serve issues.')

        return ready



    def poll_issues(self, to_path):

        """
        WARNINGS:
        - Code smells in SonarQube do not have the same definition than that of Martin Fowler
        - SonarQube doesn't seem to be able to differentiate test code from production code using the 'scopes' argument
        """

        while True:
            try:
                if self.is_ready():
                    break
                else:
                    logging.info(f'Waiting {WAIT_TIME} seconds...')
                    time.sleep(WAIT_TIME)

            except requests.exceptions.HTTPError as e:
                logging.error(e)

        # Fetch smells
        issues = self.fetch_issues()
        logging.info(f'Found {len(issues)} issues.')

        # Store issues
        if not os.path.exists(self.project.issues_dir):
            os.makedirs(self.project.issues_dir)

        store_json(issues, to_path)



    def fetch_issues(self):
        logging.info('Fetching issues from server...')

        # Define parameters to fetch project's smells on SonarQube server
        params = {
            'componentKeys': self.project.name,
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
            res = requests.get(ISSUES_API, params=current_params, auth=self.sonar_auth)
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
            if n_issues > MAX_ISSUES:
                raise SystemError('Too many issues to be fetched from SonarQube server.')

            # All issues found: exit
            if page == n_pages:
                break

            # Increment page index
            page += 1

        return issues