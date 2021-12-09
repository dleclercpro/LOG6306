import os
import logging
import numpy as np
import pandas as pd



# Custom imports
from constants import STATS, DATA_DIR, SMELLS_DIR, STATS_PATH, GENERIC_RULES_PATH, SPECIFIC_RULES_PATH, SMELLS_PATH
from lib import load_json, load_dataframe, load_series, store_dataframe, store_series
from issue import Issue



# Useful constants
PROJECT_COL = 'project'
COMMIT_COL = 'commit_hash'
FILE_COL = 'file_name'
RULE_COL = 'rule'

FILE_INSTANCE_COLS = [PROJECT_COL, COMMIT_COL, FILE_COL]
RAW_SMELLS_COLS = FILE_INSTANCE_COLS + [RULE_COL]

STEADY_COL = 'steady'
INCREASED_COL = 'increased'
DECREASED_COL = 'decreased'

DELTAS = [STEADY_COL, INCREASED_COL, DECREASED_COL]
DELTA_COLS = [FILE_COL] + DELTAS



# CLASSES
class Analysis():

    def __init__(self, projects):
        self.projects = projects
        self.rules = load_series(f'{DATA_DIR}/specific_rules.csv').tolist()



    def extract_common_rules(self):
        languages = set([])
        rulesets = {'common-js': set([]), 'common-ts': set([]), 'javascript': set([]), 'typescript': set([])}
        
        # Loop on all projects
        for p in self.projects:
            files = os.listdir(p.issues_dir)

            logging.info(f'Processing {len(files)} files of issues for: {p.name}')

            # Loop on all files
            for file in files:
                issues = None

                issues = load_json(f'{p.issues_dir}/{file}')
                    
                # Loop on all issues
                for issue in issues:
                    language, rule = issue['rule'].split(':')

                    # Store language
                    languages.add(language)

                    # Store rule in corresponding ruleset
                    for ruleset_language in rulesets.keys():
                        if ruleset_language == language:
                            rulesets[language].add(rule)
                            break

        # Compute common rules between JavaScript and TypeScript
        generic_rules = pd.Series(list(rulesets['common-js'].intersection(rulesets['common-ts'])))
        specific_rules = pd.Series(list(rulesets['javascript'].intersection(rulesets['typescript'])))
        
        common_rules = {'generic': generic_rules, 'specific': specific_rules}
        n_common_rules = len(common_rules['generic']) + len(common_rules['specific'])

        logging.info(f'Found {n_common_rules} common rules between {len(self.projects)} JavaScript/TypeScript projects.')
        logging.info(f'Found languages: {languages}')

        store_series(common_rules['generic'], GENERIC_RULES_PATH)
        store_series(common_rules['specific'], SPECIFIC_RULES_PATH)



    def merge_stats(self):
        columns = [PROJECT_COL] + STATS

        stats = pd.DataFrame(None, columns=columns)

        for p in self.projects:
            row = {PROJECT_COL: p.name, **p.repo.stats.to_dict()}
            stats = stats.append(row, ignore_index=True)

        store_dataframe(stats, STATS_PATH)



    def get_common_issues(self, p):
        common_issues = []

        # Loop on all files
        for file in os.listdir(p.issues_dir):
            commit_hash = file.split('.json')[0]

            # Load project issues file
            issues = load_json(f'{p.issues_dir}/{file}')
            
            # Loop on every issue
            for issue in issues:
                language, rule = issue['rule'].split(':')
                file_name = issue['component'].split(':')[-1]

                # Determine which type of rule it is
                is_specific = any([language.startswith(l) for l in ['javascript', 'typescript']])

                # Skip generic and uncommon rules
                if rule in self.rules and is_specific:
                    common_issues += [Issue(p.name, commit_hash, file_name, language, rule)]

        return common_issues



    def list_raw_smells(self):

        # Loop on all projects
        for p in self.projects:

            # Read common issues
            issues = self.get_common_issues(p)
            n_issues = len(issues)

            # Initialize smell counter
            i = 0

            # Initialize results dataframe
            raw_smells_init = np.zeros((n_issues, len(RAW_SMELLS_COLS)))
            raw_smells = pd.DataFrame(raw_smells_init, columns=RAW_SMELLS_COLS)

            # Loop on all issues
            for issue in issues:

                # Show progress
                if i == 0 or i % 100 == 0:
                    logging.info(f'Processing `{issue.project}` issue: {i + 1}/{n_issues}')

                # Add new rule to dataframe
                raw_smells.loc[i, PROJECT_COL] = issue.project
                raw_smells.loc[i, COMMIT_COL] = issue.commit_hash
                raw_smells.loc[i, FILE_COL] = issue.file_name
                raw_smells.loc[i, RULE_COL] = issue.rule

                # Increment smell counter
                i += 1

            # Store raw smells for current project
            store_dataframe(raw_smells, f'{SMELLS_DIR}/{p.name}.csv')



    def merge_raw_smells(self):
        
        # Merge all raw smells together
        raw_smells = pd.DataFrame({}, columns=RAW_SMELLS_COLS)

        for p in self.projects:
            new_smells = load_dataframe(f'{SMELLS_DIR}/{p.name}.csv')

            if new_smells is not None:
                raw_smells = pd.concat([raw_smells, new_smells], ignore_index=True, sort=False)

        # Extract unique pairs of project, commit ID and file name
        file_instances = raw_smells.loc[:, FILE_INSTANCE_COLS].drop_duplicates().values
        n_file_instances = len(file_instances)


        # Define columns of merged smells dataframe
        cols = FILE_INSTANCE_COLS + self.rules

        # Initialize the entire dataframe with all smell counts to zero
        smells_init = np.hstack((file_instances, np.zeros((n_file_instances, len(self.rules)))))
        smells = pd.DataFrame(smells_init, columns=cols)

        # Cast types
        for rule in self.rules:
            smells = smells.astype({ rule: int })


        # Initialize smell counter
        i = 0

        # Fill dataframe
        for project, commit_hash, file_name in file_instances:

            # Show progress
            if i == 0 or i % 100 == 0:
                logging.info(f'Processing unique file commit combination: {i + 1}/{n_file_instances}')
            
            # Define function to grab row associated with a combination of commit and file
            get_indices = lambda df: (
                (df[PROJECT_COL] == project) &
                (df[COMMIT_COL] == commit_hash) &
                (df[FILE_COL] == file_name)
            )

            # Compute dataframe indices for current pair of commit and file
            raw_indices = get_indices(raw_smells)
            indices = get_indices(smells)

            # Get test smells in current pair
            rules = raw_smells[raw_indices][RULE_COL].tolist()

            # Increment their count
            for rule in rules:
                smells.loc[indices, rule] += 1

            # Increment smell counter
            i += 1
        
        store_dataframe(smells, SMELLS_PATH)



    def count_smell_deltas(self, p):
        smells = load_dataframe(f'{SMELLS_DIR}/{p.name}.csv')
        
        # Read files present in commits
        files = np.unique(smells[FILE_COL])
        n_files = len(files)

        # Initialize smell deltas dataframe
        smell_deltas_init = np.hstack((np.reshape(files, (n_files, 1)), np.zeros((n_files, len(DELTAS)))))
        smell_deltas = pd.DataFrame(smell_deltas_init, columns=DELTA_COLS)

        # Cast types
        for delta in DELTAS:
            smell_deltas = smell_deltas.astype({ delta: int })


        # Initialize file counter
        i = 0

        # Compute smell deltas for each file
        for file in files:
            n_smells = np.array([])

            # Show progress
            if i == 0 or i % 10 == 0:
                logging.info(f'Processing file: {i + 1}/{n_files}')

            # Compute number of smells at each commit
            for commit in p.get_recent_commits():
                n_smells_in_commit = len(smells[(smells[FILE_COL] == file) & (smells[COMMIT_COL] == commit.hash)])
                n_smells = np.append(n_smells, n_smells_in_commit)

                if file == 'docs/src/lib/notion/createTable.js':
                    print(file)
                    print(commit.hash)
                    print(n_smells_in_commit)
                    print()

            # Compute deltas for current file from one commit to another
            deltas = n_smells[1:] - n_smells[:-1]

            smell_deltas.loc[smell_deltas[FILE_COL] == file, STEADY_COL] = np.sum(deltas == 0)
            smell_deltas.loc[smell_deltas[FILE_COL] == file, INCREASED_COL] = np.sum(deltas > 0)
            smell_deltas.loc[smell_deltas[FILE_COL] == file, DECREASED_COL] = np.sum(deltas < 0)

            # Increment file counter
            i += 1

        print(smell_deltas)