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
        self.path = f'{DATA_PATH}/{name}'


    def init(self):

        # Move to data directory
        os.chdir(DATA_PATH)

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

        # Define parameters to fetch project's smells on SonarQube server
        params = {
            'componentKeys': self.name,
            'metricKeys': 'code_smells',
            'languages': 'js',
            'types': 'CODE_SMELL',
            'scope': 'MAIN',
        }

        # Define authentication for SonarQube server
        auth = (SONAR_USERNAME, SONAR_PASSWORD)

        # Fetch smells
        res = requests.get(SONAR_API, params=params, auth=auth)

        return res.json()




def main():

    """
    NOTE: Please set working directory to where this main file exists for it to work.

    Steps:
    1 - Run a server instance of SonarQube.
    2 - Define a user with 'Browse' permissions on all projects.
    3 - Run this file.
    """

    # Define projects
    PROJECTS = ['jquery/jquery']#, 'expressjs/express']

    # Generate project's path if it doesn't exist already
    if not os.path.exists(DATA_PATH):
        os.makedirs(DATA_PATH)

    # Process every project
    for project in PROJECTS:
        print(f'Processing project: {project}')

        p = Project(project)

        #p.init()
        #p.scan()
        raw_smells = p.extract_smells()
        printJSON(raw_smells)




if __name__ == '__main__':
    main()