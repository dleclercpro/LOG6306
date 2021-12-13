import os
import logging
import numpy as np
import pandas as pd



# Custom imports
from constants import AXIS_ROW, DATA_DIR, EPSILON, STATS, SMELLS_DIR, STATS_PATH, GENERIC_RULES_PATH, SPECIFIC_RULES_PATH, SMELLS_PATH
from lib import load_json, load_dataframe, store_dataframe, store_series
from issue import Issue



# Useful constants
PROJECT_COL = 'project'
COMMIT_COL = 'commit_hash'
FILE_COL = 'file_name'
RULE_COL = 'rule'
TYPE_COL = 'type'
SEVERITY_COL = 'severity'
TAGS_COL = 'tags'

FILE_INSTANCE_COLS = [PROJECT_COL, COMMIT_COL, FILE_COL]
SMELLS_COLS = FILE_INSTANCE_COLS + [RULE_COL]

STEADY_COL = 'Steady'
INCREASED_COL = 'Increased'
DECREASED_COL = 'Decreased'

DELTAS = [STEADY_COL, INCREASED_COL, DECREASED_COL]

SMELLS = ['S1067', 'S1143', 'S1186', 'S1192', 'S121', 'S126', 'S131', 'S134', 'S1539', 'S1541', 'S1821', 'S1994', 'S2208', 'S2310', 'S2871', 'S3353', 'S3504', 'S3523', 'S3525', 'S3735', 'S3776', 'S3972', 'S3973', 'S4123', 'S4524', 'S930']
N_SMELLS = len(SMELLS)



# CLASSES
class Analysis():

    def __init__(self, projects):
        self.projects = projects



    def merge_stats(self):

        """
        Merge stats of all projects together in one dataframe.
        """
        
        columns = [PROJECT_COL] + STATS

        stats = pd.DataFrame(None, columns=columns)

        for p in self.projects:
            row = {PROJECT_COL: p.name, **p.repo.stats.to_dict()}
            stats = stats.append(row, ignore_index=True)

        store_dataframe(stats, STATS_PATH)



    def find_rules(self):
        
        """
        Find rules shared between JS and TS using all issues found in projects.

        NOTE: Needs all issues to be extracted from SonarQube before it can be run.
        """
        
        languages = set([])
        rulesets = {'common-js': set([]), 'common-ts': set([]), 'javascript': set([]), 'typescript': set([])}
        
        # Loop on all projects
        for p in self.projects:
            files = os.listdir(p.issues_dir)

            logging.info(f'Processing {len(files)} files of issues for: {p.name}')

            # Loop on all files
            for file in files:
                file_issues = load_json(f'{p.issues_dir}/{file}')
                    
                # Loop on all issues
                for file_issue in file_issues:
                    language, rule = file_issue['rule'].split(':')

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
        
        rules = {'generic': generic_rules, 'specific': specific_rules}
        n_rules = len(rules['generic']) + len(rules['specific'])

        logging.info(f'Found {n_rules} common rules between {len(self.projects)} JavaScript/TypeScript projects.')
        logging.info(f'Found languages: {languages}')

        store_series(rules['generic'], GENERIC_RULES_PATH)
        store_series(rules['specific'], SPECIFIC_RULES_PATH)



    def get_project_issues(self, p):

        """
        Extract shared JS/TS issues from project's issues files.
        """

        issues = []

        # Loop on all files
        for file in os.listdir(p.issues_dir):
            commit_hash = file.split('.json')[0]

            # Load project issues file
            file_issues = load_json(f'{p.issues_dir}/{file}')
            
            # Loop on every issue
            for file_issue in file_issues:
                file_name = file_issue['component'].split(':')[-1]
                language, rule = file_issue['rule'].split(':')
                type = file_issue['type']
                severity = file_issue['severity']
                tags = file_issue['tags']

                # Determine which type of rule it is
                is_specific = language in ['javascript', 'typescript']

                # Determine whether it is a test file
                is_test_file = 'test' in file_name

                # Skip generic and uncommon rules
                if is_specific and not is_test_file:
                    issues += [Issue(
                        p.name,
                        commit_hash,
                        file_name,
                        language,
                        rule,
                        type,
                        severity,
                        tags,
                    )]

        return issues



    def list_files(self):

        """
        List files for all recent releases.
        """

        for p in self.projects:
            logging.info(f'Generating list of files for every recent release in `{p.name}`...')

            files = pd.DataFrame([], columns=[PROJECT_COL, COMMIT_COL, FILE_COL])
            
            for release in p.get_recent_releases():
                p.checkout(release, add_properties=False)

                for root, _, filenames in os.walk(p.dir):
                    for filename in filenames:
                        path = os.path.join(root, filename)
                        path = os.path.relpath(path, p.dir)

                        if path[-3:] == '.js' or path[-3:] == 'ts':
                            row = {
                                PROJECT_COL: p.name,
                                COMMIT_COL: release.commit_hash,
                                FILE_COL: path,
                            }
                            files = files.append(row, ignore_index=True)

            store_dataframe(files, p.files_fname)



    def list_smells(self):

        """
        List all individual smells from all projects together into one single dataframe.
        """

        # Loop on all projects
        for p in self.projects:

            # Read issues
            issues = self.get_project_issues(p)
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
                    logging.info(f'Processing `{issue.project}` issue: {i + 1}/{n_issues}')

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
            store_dataframe(smells, p.smells_fname)



    def count_smells(self):

        """
        Count smells in every single combination of project, commit and file.
        """
        
        # Merge all project smells together
        smells = pd.DataFrame({}, columns=SMELLS_COLS)
        rules = np.array([])

        for p in self.projects:
            new_smells = load_dataframe(p.smells_fname)

            if new_smells is None:
                raise RuntimeError(f'Missing smells for project `{p.name}`.')

            # Only keep critical smells
            new_smells = new_smells[new_smells[SEVERITY_COL] == 'CRITICAL']
            
            smells = pd.concat([smells, new_smells], ignore_index=True, sort=False)
            rules = np.append(rules, new_smells[RULE_COL].to_numpy())

        # Extract set of unique rules from data
        rules = np.unique(rules)
        n_rules = len(rules)
        logging.info(f'Found {n_rules} critical rules in all projects.')


        # Extract unique pairs of project, commit ID and file name
        file_versions = smells.loc[:, FILE_INSTANCE_COLS].drop_duplicates().values
        n_file_versions = len(file_versions)
        logging.info(f'Found {n_file_versions} unique file versions in all projects.')


        # Define columns of merged smells dataframe
        cols = np.append(FILE_INSTANCE_COLS, rules)

        # Initialize the entire dataframe with all smell counts to zero
        merged_smells_init = np.hstack((file_versions, np.zeros((n_file_versions, n_rules))))
        merged_smells = pd.DataFrame(merged_smells_init, columns=cols)

        # Cast types
        for rule in rules:
            merged_smells = merged_smells.astype({ rule: int })


        # Initialize smell counter
        i = 0

        # Fill dataframe
        for project, commit_hash, file_name in file_versions:

            # Show progress
            if i == 0 or i % 100 == 0:
                logging.info(f'Processing unique file commit combination: {i + 1}/{n_file_versions}')
            
            # Define function to grab row associated with a combination of commit and file
            get_indices = lambda df: (
                (df[PROJECT_COL] == project) &
                (df[COMMIT_COL] == commit_hash) &
                (df[FILE_COL] == file_name)
            )

            # Compute dataframe indices for current pair of commit and file
            indices = get_indices(smells)
            merged_indices = get_indices(merged_smells)

            # Get test smells in current pair
            rules = smells[indices][RULE_COL].tolist()

            # Increment their count
            for rule in rules:
                merged_smells.loc[merged_indices, rule] += 1

            # Increment smell counter
            i += 1
        
        store_dataframe(merged_smells, SMELLS_PATH)



    def count_smell_deltas(self):

        """
        Count deltas in number of smells present in every single
        combination of project, commit and file.
        """
        
        for p in self.projects:
            logging.info(f'Computing smell deltas for: {p.name}')

            smells = load_dataframe()

            if smells is None:
                raise RuntimeError(f'Missing smells for project `{p.name}`.')
            
            # Read files present in commits
            files = np.unique(smells[FILE_COL])
            n_files = len(files)

            # Initialize smell deltas dataframe
            smell_deltas_init = np.hstack((np.reshape(files, (n_files, 1)), np.zeros((n_files, len(DELTAS)))))
            smell_deltas = pd.DataFrame(smell_deltas_init, columns=[FILE_COL] + DELTAS)

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

                # Compute number of smells at each recent release
                for release in p.get_recent_releases():
                    files = load_dataframe(p.files_fname)
                    file_exists = file in files[files[COMMIT_COL] == release.commit_hash][FILE_COL].tolist()

                    # Only consider a delta if the file exists in current release
                    if file_exists:
                        new_smells = smells[(smells[FILE_COL] == file) & (smells[COMMIT_COL] == release.commit_hash)]
                        n_smells = np.append(n_smells, len(new_smells))

                # Compute deltas for current file from one commit to another
                deltas = n_smells[1:] - n_smells[:-1]

                smell_deltas.loc[smell_deltas[FILE_COL] == file, STEADY_COL] = np.sum(deltas == 0)
                smell_deltas.loc[smell_deltas[FILE_COL] == file, INCREASED_COL] = np.sum(deltas > 0)
                smell_deltas.loc[smell_deltas[FILE_COL] == file, DECREASED_COL] = np.sum(deltas < 0)

                # Increment file counter
                i += 1

            deltas_avg = smell_deltas[DELTAS].mean(axis=AXIS_ROW).to_numpy()
            deltas_avg = np.reshape(deltas_avg, (len(deltas_avg), 1))

            deltas_std = smell_deltas[DELTAS].std(axis=AXIS_ROW).to_numpy()
            deltas_std = np.reshape(deltas_std, (len(deltas_std), 1))

            deltas_stats = pd.DataFrame(np.hstack((deltas_avg, deltas_std)), index=DELTAS, columns=['AVG', 'STD'])

            print(deltas_stats)
            print()



    def compute_occurences_by_smell(self, p):

        """
        Compute occurence for each smell type
        """
        
        smells = load_dataframe(SMELLS_PATH)
        smells = smells[smells[PROJECT_COL] == p.name].loc[:, SMELLS]

        occurences = smells.sum(axis=AXIS_ROW)

        return occurences



    def compute_file_count_by_smell(self, p):

        """
        Compute file count for each smell type
        """
        
        smells = load_dataframe(SMELLS_PATH)
        smells = smells[smells[PROJECT_COL] == p.name].loc[:, SMELLS]

        file_count = (smells > 0).sum(axis=AXIS_ROW)

        return file_count



    def compute_overall_distribution_smells(self):

        """
        ...
        """
        
        # For each project type
        for language in ['js', 'ts']:
        
            # Compute occurence for each smell and corresponding distribution
            occurences_by_app = {}

            for p in self.projects:
                if p.language != language:
                    continue
                
                occurences_by_app[p.name] = self.compute_occurences_by_smell(p)


            # Compute distribution of smells across all apps
            distribution = pd.Series(np.zeros(N_SMELLS), index = SMELLS)

            for occurences in occurences_by_app.values():
                distribution = distribution.add(occurences)

            n_total_occurences = np.sum(distribution)

            distribution /= n_total_occurences

            store_series(distribution, f'{DATA_DIR}/{language}_smells_distribution_overall.csv')

            print(distribution)
            print()



    def compute_app_smell_frequencies(self):

        # For each project type
        for language in ['js', 'ts']:
            n_apps = 0

            # Compute app count by smell type
            app_count_by_smell = pd.Series(np.zeros(N_SMELLS), index = SMELLS)

            for p in self.projects:
                if p.language != language:
                    continue

                # Compute occurences by smell type in current app
                occurences = self.compute_occurences_by_smell(p)

                # Increment number of apps as well as app count where each type of smell is displayed
                n_apps += 1
                app_count_by_smell.loc[occurences > 0] += 1


            # Compute percentage of apps affected by each type of smell
            app_frequency_by_smell = app_count_by_smell / n_apps
            
            store_series(app_frequency_by_smell, f'{DATA_DIR}/{language}_smells_distribution_by_app.csv')

            logging.info('# apps: {0}'.format(n_apps))
            print(app_frequency_by_smell)



    # def compute_file_smell_frequencies(self):
    #     n_files = 0

    #     # Compute file count by smell type
    #     file_count_by_smell = pd.Series(np.zeros(N_SMELLS), index = SMELLS)

    #     for p in self.projects:

    #         # Compute file count for each smell type in current app
    #         file_count_by_smell = file_count_by_smell.add(self.compute_file_count_by_smell(p))

    #         # Add number of files considered in current app
    #         files = load_dataframe('{0}/{1}'.format(directory, TESTS_FILENAME))
    #         n_files += len(files)


    #     # Compute percentage of files affected by each type of smell
    #     file_frequency_by_smell = file_count_by_smell / n_files
        
    #     store_series(file_frequency_by_smell, SMELL_TEST_FILE_FREQUENCY_PATH)

    #     logging.info('# test files: {0}'.format(n_files))
    #     print(file_frequency_by_smell)



    # def compute_smell_cooccurences_in_files(self):
    #     smells = pd.DataFrame([], columns = SMELLS)

    #     for directory, _, filenames in os.walk(SMELLS_DIR):
    #         if SMELLS_FILENAME not in filenames:
    #             continue

    #         # Merge smell occurences across all apps
    #         app_smells = load_dataframe('{0}/{1}'.format(directory, SMELLS_FILENAME))[SMELLS]
    #         smells = smells.append(app_smells, ignore_index = True)
        
    #     # One-hot encode smell occurences in test files
    #     ohe_smells = smells > 0

    #     # Compute co-occurences between all combinations of smells
    #     cooccurences = apriori(ohe_smells, min_support = EPSILON)

    #     # Compute matrices of co-occurences between pairs of test smells as well as pairs of classic and test smells
    #     cooccurences_smell_pairs = pd.DataFrame(np.full((N_SMELLS, N_SMELLS), '0%'), index = SMELLS, columns = SMELLS)

    #     for _, row in cooccurences.iterrows():
    #         cooccurence = '{0}%'.format(round(row['support'] * 100)) # Co-occurence as percentage
    #         smell_set = row['itemsets']

    #         # Only consider pairs
    #         if len(smell_set) == 2:
    #             smell_1, smell_2 = [SMELLS[smell] for smell in smell_set]

    #             if smell_1 in SMELLS and smell_2 in SMELLS:
    #                 cooccurences_smell_pairs.loc[smell_1, smell_2] = cooccurence

    #     print(cooccurences_smell_pairs)
    #     store_dataframe(cooccurences_smell_pairs, SMELL_COOCCURENCES)