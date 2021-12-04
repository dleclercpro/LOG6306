import os
import json
import datetime
import requests
import subprocess
import logging
from git import Repo
from dotenv import load_dotenv
from multiprocessing import Pool



# Load environment variables
load_dotenv()

SONAR_TOKEN = os.environ['SONAR_TOKEN']
SONAR_USERNAME = os.environ['SONAR_USERNAME']
SONAR_PASSWORD = os.environ['SONAR_PASSWORD']



# Paths
ROOT_DIR = '/Users/david/Projects/LOG6306'
REPOS_DIR = f'{ROOT_DIR}/repos'
LOGS_DIR = f'{ROOT_DIR}/logs'
DATA_DIR = f'{ROOT_DIR}/data'
COMMITS_DIR = f'{DATA_DIR}/commits'
ISSUES_DIR = f'{DATA_DIR}/issues'

SONAR_PROJECT_PROPS_FNAME = 'sonar-project.properties'
SONAR_SCANNER_PROPS_FNAME = 'sonar-scanner.properties'

SONAR_SCANNER = '/Users/david/Downloads/sonar-scanner-4.6.2.2472-macosx/bin/sonar-scanner'
SONAR_API = 'http://localhost:9000/api/issues/search'

DATETIME_FORMAT = '%Y.%m.%d - %H:%M:%S'



# Helper functions
def printJSON(obj):
    logging.info(json.dumps(obj, sort_keys=True, indent=2))

def formatSeconds(seconds):
    time = seconds
    units = 's'

    if time >= 60:
        time /= 60.0
        units = 'm'
    
    if time >= 60:
        time /= 60.0
        units = 'h'

    if time >= 24:
        time /= 24.0
        units = 'd'

    return f'{round(time, 1)} {units}'



# CLASSES
class Commit():

    def __init__(self, hash, date, author):
        self.hash = hash
        self.date = date
        self.author = author

    def __str__(self):
        return f"{self.hash} ({self.date.strftime(DATETIME_FORMAT)}) {self.author}"

    def to_json(self):
        return {
            'hash': self.hash,
            'date': datetime.datetime.strftime(self.date, DATETIME_FORMAT),
            'author': self.author,
        }

    @staticmethod
    def from_json(commit):
        return Commit(commit['hash'], datetime.datetime.strptime(commit['date'], DATETIME_FORMAT), commit['author'])



class Project():

    def __init__(self, project):

        # Compute organization and name of project
        organization, name = project.split('/')
        
        self.organization = organization
        self.name = name
        self.path = f'{REPOS_DIR}/{name}'
        self.commits_path = f'{COMMITS_DIR}/{name}.json'
        self.issues_dir = f'{ISSUES_DIR}/{name}'

        self.repo = None
        self.commits = []
        self.remaining_commits = []
        self.current_commit = None



    def initialize(self):
        logging.info("Initializing project's repository...")

        # Move to data directory
        os.chdir(REPOS_DIR)


        # If project has not already been cloned locally, do it
        if not os.path.exists(self.path):
            self.repo = Repo.clone_from(f'https://github.com/{self.organization}/{self.name}.git', to_path=self.path)
        else:
            self.repo = Repo(self.path)


        # If list of commits hasn't been generated, do it
        if not os.path.exists(self.commits_path):
            self.fetch_commits()
        else:
            self.load_commits()


        # If some commits have already been processed
        self.compute_remaining_commits()



    def fetch_commits(self):
        logging.info('Generating chronological list of commits of repository...')


        # Generate list of commits in master branch in chronological order
        self.commits = []
        
        for commit in self.repo.iter_commits():
            self.commits += [Commit(commit.hexsha, commit.committed_datetime, commit.author.email)]

        self.commits = list(reversed(self.commits))


        # Store commits list to JSON file
        with open(self.commits_path, 'w', encoding='UTF-8') as f:
            json.dump([commit.to_json() for commit in self.commits], f, indent=2)



    def load_commits(self):
        self.commits = []

        with open(self.commits_path, 'r', encoding='UTF-8') as f:
            self.commits = [Commit.from_json(commit) for commit in json.load(f)]



    def compute_remaining_commits(self):
        processed_commit_hashes = []

        if os.path.exists(self.issues_dir):
            for path in os.listdir(self.issues_dir):
                processed_commit_hashes += [path.split('.')[0]]

        self.remaining_commits = list(filter(lambda commit: commit.hash not in processed_commit_hashes, self.commits))

        n_commits = len(self.commits)
        n_remaining_commits = len(self.remaining_commits)
        n_processed_commits = n_commits - n_remaining_commits

        logging.info(f'Commits processed: {n_processed_commits}/{n_commits}')



    def add_properties(self):
        logging.info('Generating SonarQube project properties file...')
        
        with open(f'{self.path}/{SONAR_PROJECT_PROPS_FNAME}', 'w', encoding='UTF-8') as f:
            f.write(
                f'sonar.projectKey={self.name}\n' +
                'sonar.sources=.\n'+
                'sonar.sourceEncoding=UTF-8'
            )



    def checkout(self, commit):
        logging.info('Checking out repository...')

        # Store current commit
        self.current_commit = commit

        self.repo.head.reset(commit.hash, working_tree=True)
        self.repo.git.clean('-xdf')

        # Regenerate SonarQube project properties file
        self.add_properties()



    def scan(self):
        logging.info('Scanning for smells in current revision...')

        # Move to project's directory
        os.chdir(self.path)

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

        path = f'{self.issues_dir}/{self.current_commit.hash}.json'
        
        with open(path, 'w', encoding='UTF-8') as f:
            json.dump(issues, f, sort_keys=True, indent=2)



def process_project(project):
    p = Project(project)

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format=f'%(asctime)s [%(levelname)s] [{p.name}] %(message)s',
        handlers=[logging.FileHandler(f'{LOGS_DIR}/{p.name}.log'), logging.StreamHandler()],
    )

    # Initialize repository
    p.initialize()
    
    remaining_commits = p.remaining_commits
    n_remaining_commits = len(remaining_commits)

    # Initialize counters
    n_done = 0
    n_remaining = n_remaining_commits

    t_0 = datetime.datetime.now()

    # Process every commit
    while n_remaining > 0:
        logging.info(f'Processing commit {n_done + 1}/{n_remaining_commits}')

        commit = remaining_commits[n_done]
        logging.info(commit)

        p.checkout(commit)
        p.scan()
        p.extract_smells()

        t = datetime.datetime.now()

        n_done += 1
        n_remaining -= 1

        remaining_seconds = (t - t_0).total_seconds() / n_done * n_remaining
        
        logging.info(f'Remaining time: {formatSeconds(remaining_seconds)}')






def main():

    """
    NOTE: Please set working directory to where this main file exists for it to work.

    Steps:
    1 - Run a server instance of SonarQube.
    2 - Define a user with 'Browse' permissions on all projects.
    3 - Run this file.
    """

    # Define projects
    js_projects = ['expressjs/express', 'bower/bower', 'less/less.js', 'request/request', 'gruntjs/grunt', 'jquery/jquery', 'vuejs/vue', 'ramda/ramda', 'Leaflet/Leaflet', 'hexojs/hexo', 'chartjs/Chart.js', 'webpack/webpack', 'moment/moment', 'webtorrent/webtorrent', 'riot/riot']
    ts_projects = ['formium/formik']#, 'angular/angular']
    projects = ts_projects + js_projects

    # Generate data and results directories (if they do not already exist)
    for path in [REPOS_DIR, LOGS_DIR, DATA_DIR, COMMITS_DIR, ISSUES_DIR]:
        if not os.path.exists(path):
            os.makedirs(path)

    # Process every project
    with Pool(4) as p:
        p.map(process_project, projects)
    #for project in projects:
    #    process_project(project)






if __name__ == '__main__':
    main()