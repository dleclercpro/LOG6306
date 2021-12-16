import os
import logging
import datetime
import numpy as np
import pandas as pd



# Custom imports
from constants import COMMIT_COL, DELTAS_DIR, FILE_COL, FILE_VERSION_COLS, FILES_DIR, ISSUES_DIR, JS, LANGUAGES, PROJECT_COL, REPOS_DIR, RULE_COL, SEVERITY_COL, SMELLS_COLS, SMELLS_DIR, STATS_DIR, TAGS_COL, TS, TYPE_COL
from issue import Issue
from repository import Repo
from lib import formatSeconds, is_js_file, is_test_file, is_ts_file, load_dataframe, load_json, store_dataframe
from smells import SMELLS_DICT
from sonar import Sonar



# CLASSES
class Project():

    def __init__(self, project, language):

        # Compute owner and name of project
        owner, name = project.split('/')

        self.owner = owner
        self.name = name
        self.language = language

        self.repo = None
        self.remaining_releases = []

        self.dir = f'{REPOS_DIR}/{name}'
        self.stats_fname = f'{STATS_DIR}/{name}.csv'
        self.files_fname = f'{FILES_DIR}/{name}.csv'
        self.smells_fname = f'{SMELLS_DIR}/{name}.csv'
        self.deltas_fname = f'{DELTAS_DIR}/{name}.csv'
        self.issues_dir = f'{ISSUES_DIR}/{name}'

        # Define SonarQube server instance
        self.sonar = Sonar(self)



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

        # Load repo's list of release tags
        self.repo.load_releases()

        # Load repo's stats
        self.repo.load_stats()

        # If some releases have already been processed
        self.compute_remaining_releases()



    def checkout(self, release):
        self.repo.checkout(release)



    def get_smells(self):
        smells = load_dataframe(self.smells_fname)
        return smells[smells[RULE_COL].isin(SMELLS_DICT)] if smells is not None else None

    def store_smells(self, smells):
        store_dataframe(smells, self.smells_fname)



    def get_smell_deltas(self):
        return load_dataframe(self.deltas_fname)

    def store_smell_deltas(self, smells):
        store_dataframe(smells, self.deltas_fname)



    def should_skip_file(self, file):
        
        # Neither JS nor TS file
        if not is_js_file(file) and not is_ts_file(file):
            return True
        
        # JS project, but not JS file
        if is_js_file(file) and self.language != JS:
            return True

        # TS project, but not TS file
        if is_ts_file(file) and self.language != TS:
            return True

        # Ignore test files
        if is_test_file(file):
            return True

        return False



    def get_valid_files(self):
        return load_dataframe(self.files_fname)

    def store_valid_files(self, files):
        store_dataframe(files, self.files_fname)



    def get_recent_releases(self, to_compute=25):
        return self.repo.releases[-to_compute:]



    def compute_remaining_releases(self):
        logging.info('Computing remaining releases to process for project...')
        
        # Compute list of releases which have already been processed
        hashes = []
        
        if os.path.exists(self.issues_dir):
            for fname in os.listdir(self.issues_dir):
                hashes += [fname.split('.')[0]]

        # Only consider the last X releases [time constraint]
        recent_releases = self.get_recent_releases()

        # Compute the releases that are not yet processed
        self.remaining_releases = list(filter(lambda t: t.commit_hash not in hashes, recent_releases))
        logging.info(f'Releases remaining to process: {len(self.remaining_releases)}/{len(recent_releases)}')



    def find_issues(self):

        # Grab remaining releases to process
        n_releases = len(self.repo.releases)

        # Initialize counters
        n = len(self.remaining_releases)
        i = 0

        t_0 = datetime.datetime.now()

        # Process every release
        while n > 0:
            logging.info(f'Processing release: {n_releases - n + 1}/{n_releases}')

            release = self.remaining_releases[i]

            self.checkout(release)

            self.sonar.delete()
            self.sonar.scan()
            self.sonar.poll_issues(f'{self.issues_dir}/{self.repo.get_hash()}.json')

            t = datetime.datetime.now()

            i += 1
            n -= 1

            remaining_seconds = (t - t_0).total_seconds() / i * n
            logging.info(f'Remaining time: {formatSeconds(remaining_seconds)}')



    def list_valid_files(self):

        """
        List production JS/TS files for all recent releases of all projects.
        """

        if self.get_valid_files() is not None:
            return

        files = pd.DataFrame([], columns=FILE_VERSION_COLS)
        
        # List files in each recent release of project
        for release in self.get_recent_releases():
            logging.info(f'Generating list of files of `{self.name}` in release: {release.name}')
            
            # Checkout current release
            self.checkout(release)

            # For all files in current release
            for root_dir, _, file_names in os.walk(self.dir):
                for file_name in file_names:
                    path = os.path.join(root_dir, file_name)
                    path = os.path.relpath(path, self.dir)

                    # Skip invalid files
                    if self.should_skip_file(path):
                        continue
                    
                    # Store file version
                    files = files.append({
                        PROJECT_COL: self.name,
                        COMMIT_COL: release.commit_hash,
                        FILE_COL: path.replace('\\', '/'),
                    }, ignore_index=True)

        self.store_valid_files(files)



    def list_smells(self):

        """
        List all individual smells from all projects together into one single dataframe.
        """

        if self.get_smells() is not None:
            return

        # Read issues
        issues = self.get_issues()
        n_issues = len(issues)

        # Initialize smell counter
        i = 0

        # Initialize results dataframe
        smells_init = np.zeros((n_issues, len(SMELLS_COLS)))
        smells = pd.DataFrame(smells_init, columns=SMELLS_COLS)

        # Loop on all issues
        for issue in issues:

            # Show progress
            if i == 0 or i % 100 == 0:
                logging.info(f'Processing `{self.name}` issue: {i + 1}/{n_issues}')

            # Add new rule to dataframe
            smells.loc[i, PROJECT_COL] = issue.project
            smells.loc[i, COMMIT_COL] = issue.commit_hash
            smells.loc[i, FILE_COL] = issue.file_name
            smells.loc[i, RULE_COL] = issue.rule
            smells.loc[i, TYPE_COL] = issue.type
            smells.loc[i, SEVERITY_COL] = issue.severity
            smells.loc[i, TAGS_COL] = '|'.join(issue.tags)

            # Increment smell counter
            i += 1

        # Store raw smells for current project
        self.store_smells(smells)



    def get_issues(self):

        """
        Extract production code issues common to both JS and TS from project's issues files.
        """

        issues = []

        # Loop on all files
        for file in os.listdir(self.issues_dir):
            commit_hash, _ = file.split('.json')

            # Load project issues file
            file_issues = load_json(f'{self.issues_dir}/{file}')
            
            # Loop on every issue
            for file_issue in file_issues:
                file_name = file_issue['component'].split(':')[-1]
                language, rule = file_issue['rule'].split(':')
                type = file_issue['type']
                severity = file_issue['severity']
                tags = file_issue['tags']

                # Skip rules in invalid files
                if self.should_skip_file(file_name):
                    continue

                # Skip unspecific rules
                if language not in LANGUAGES:
                    continue

                # Store issue
                issues += [Issue(
                    self.name,
                    commit_hash,
                    file_name,
                    language,
                    rule,
                    type,
                    severity,
                    tags,
                )]

        return issues