import os
import json
import requests
import subprocess
from dotenv import load_dotenv




# Load environment variables
load_dotenv()

SONAR_TOKEN = os.environ['SONAR_TOKEN']
SONAR_USERNAME = os.environ['SONAR_USERNAME']
SONAR_PASSWORD = os.environ['SONAR_PASSWORD']




# Paths
ROOT_PATH = '/Users/david/Projects/LOG6306'
REPOS_PATH = f'{ROOT_PATH}/repos'
DATA_PATH = f'{ROOT_PATH}/data'

SONAR_PROJECT_PROPS_FNAME = 'sonar-project.properties'
SONAR_SCANNER_PROPS_FNAME = 'sonar-scanner.properties'

SONAR_SCANNER = '/Users/david/Downloads/sonar-scanner-4.6.2.2472-macosx/bin/sonar-scanner'
SONAR_API = 'http://localhost:9000/api/issues/search'



# Helper functions
def printJSON(obj):
    print(json.dumps(obj, sort_keys=True, indent=2))



# CLASSES
class Project():

    def __init__(self, project):

        # Compute organization and name of project
        organization, name = project.split('/')
        
        self.organization = organization
        self.name = name
        self.path = f'{REPOS_PATH}/{name}'


    def initialize(self):

        # Move to data directory
        os.chdir(REPOS_PATH)

        # If project has not already been cloned locally, do it
        if not os.path.exists(self.path):
            subprocess.run(['git', 'clone', f'https://github.com/{self.organization}/{self.name}.git'])

        # Generate SonarQube project properties file
        with open(f'{self.path}/{SONAR_PROJECT_PROPS_FNAME}', 'w', encoding='UTF-8') as f:
            f.write(
                f'sonar.projectKey={self.name}\n' +
                'sonar.sources=.\n'+
                'sonar.sourceEncoding=UTF-8'
            )


    def scan(self):

        # Move to project's directory
        os.chdir(self.path)

        # Launch SonarQube analysis of code smells
        subprocess.run([SONAR_SCANNER, f'-Dsonar.login={SONAR_TOKEN}'])


    def extract_smells(self):

        """
        WARNINGS:
        - Code smells in SonarQube do not have the same definition than that of Martin Fowler
        - SonarQube doesn't seem to be able to differentiate test code from production code using the 'scopes' argument
        """

        # Define parameters to fetch project's smells on SonarQube server
        params = {
            'componentKeys': self.name,
            'languages': 'js',
            #'types': 'CODE_SMELL',
            #'scopes': 'MAIN',
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

        # Store issues
        with open(f'{DATA_PATH}/{self.name}.json', 'w', encoding='UTF-8') as f:
            json.dump(issues, f, sort_keys=True, indent=2)




def main():

    """
    NOTE: Please set working directory to where this main file exists for it to work.

    Steps:
    1 - Run a server instance of SonarQube.
    2 - Define a user with 'Browse' permissions on all projects.
    3 - Run this file.
    """

    # Define projects
    projects = ['expressjs/express', 'bower/bower', 'less/less.js', 'request/request', 'gruntjs/grunt', 'jquery/jquery', 'vuejs/vue', 'ramda/ramda', 'Leaflet/Leaflet', 'hexojs/hexo', 'chartjs/Chart.js', 'webpack/webpack', 'moment/moment', 'webtorrent/webtorrent', 'riot/riot']

    # Generate data and results directories (if they do not already exist)
    for path in [REPOS_PATH, DATA_PATH]:
        if not os.path.exists(path):
            os.makedirs(path)

    # Process every project
    for project in projects:
        print(f'Processing project: {project}')

        p = Project(project)

        p.initialize()
        p.scan()
        p.extract_smells()




if __name__ == '__main__':
    main()