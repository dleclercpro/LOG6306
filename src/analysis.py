import logging
import numpy as np
import pandas as pd
from mlxtend.frequent_patterns import apriori



# Custom imports
from constants import AXIS_COL, AXIS_ROW, COMMIT_COL, DATA_DIR, DECREASED_COL, DELTA_COLS, EPSILON, FILE_COL, FILE_VERSION_COLS, INCREASED_COL, JS, JS_STATS_PATH, LANGUAGES, N_RELEASE_TAGS, PROJECT_COL, RULE_COL, SMELLS_COLS, STATS, SMELLS_PATH, STEADY_COL, TS, TS_STATS_PATH
from smells import SMELLS, N_SMELLS, MISSING_SMELL_COOCCURENCES, SMELLS_DICT
from lib import load_dataframe, store_dataframe



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
            repo_stats = p.repo.stats.to_dict()
            row = {PROJECT_COL: p.name, 'language': p.language}

            for stat in STATS:
                row[stat] = repo_stats[stat]
            
            stats = stats.append(row, ignore_index=True)

        # Cast types
        stats = stats.astype({
            'stargazers_count': int,
            'forks_count': int,
            'contributors_count': int,
            'commits_count': int,
            'tags_count': int,
            'js_ratio': float,
            'ts_ratio': float,
        })

        # Keep creation year only
        stats['created_at'] = stats['created_at'].apply(lambda x: x[:4])

        # Format big numbers
        for col in ['stargazers_count', 'forks_count', 'commits_count']:
            stats[col] = stats[col].apply(lambda x: f'{round(x / 1000.0, 1)}k')

        # Convert JS/TS ratios to percentages
        def ratio_to_percent(ratio):
            percent = round(ratio * 100.0, 1)

            if percent == 0:
                return '-'
            else:
                return f'{percent}%'

        for ratio in ['js_ratio', 'ts_ratio']:
            stats[ratio] = stats[ratio].apply(ratio_to_percent)

        # Sort according to stars
        stats = stats.sort_values('stargazers_count', axis=AXIS_ROW, ascending=False)

        # Split JS and TS stats
        js_stats = stats[stats['language'] == JS]
        ts_stats = stats[stats['language'] == TS]

        # Drop language column
        js_stats = js_stats.drop(columns=['language'])
        ts_stats = ts_stats.drop(columns=['language'])

        # Store final stats for all projects
        store_dataframe(js_stats, JS_STATS_PATH)
        store_dataframe(ts_stats, TS_STATS_PATH)



    def count_smells(self):

        """
        Count smells in every single combination of project, commit and file.
        """
        
        # Merge all project smells together
        smells = pd.DataFrame({}, columns=SMELLS_COLS)

        for p in self.projects:
            project_smells = p.get_smells()

            if project_smells is None:
                raise RuntimeError(f'Missing smells for project `{p.name}`.')

            smells = pd.concat([smells, project_smells], ignore_index=True, sort=False)


        # Extract set of unique rules from data
        rules = np.unique(smells[RULE_COL].tolist())
        n_rules = len(rules)


        # Extract unique pairs of project, commit ID and file name
        file_versions = smells.loc[:, FILE_VERSION_COLS].drop_duplicates().values
        n_file_versions = len(file_versions)
        logging.info(f'Found {n_file_versions} unique file versions in all projects.')


        # Initialize the entire dataframe with all smell counts to zero
        merged_smells_init = np.hstack((file_versions, np.zeros((n_file_versions, n_rules))))
        merged_smells = pd.DataFrame(merged_smells_init, columns=np.append(FILE_VERSION_COLS, rules))

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



    def count_app_smell_deltas(self):

        """
        Count deltas in number of smells present in every single app.
        """
        
        # Compute smell deltas for each file of each project
        for p in self.projects:
            logging.info(f'Computing smell deltas on app scale for: {p.name}')

            smells = p.get_smells()

            if smells is None:
                raise RuntimeError(f'Missing smells for project `{p.name}`.')
            

            # Initialize smell deltas dataframe
            smell_deltas_init = np.zeros((1, len(DELTA_COLS)))
            smell_deltas = pd.DataFrame(smell_deltas_init, columns=DELTA_COLS)

            # Cast types
            for delta in DELTA_COLS:
                smell_deltas = smell_deltas.astype({ delta: int })


            # Compute number of smells at each recent release
            n_smells = np.array([])

            for release in p.get_recent_releases():
                release_smells = smells[smells[COMMIT_COL] == release.commit_hash]
                n_smells = np.append(n_smells, len(release_smells))


            # Compute deltas from one commit to another
            if np.sum(n_smells) > 0:
                deltas = n_smells[1:] - n_smells[:-1]

                smell_deltas.loc[0, STEADY_COL] = np.sum(deltas == 0)
                smell_deltas.loc[0, INCREASED_COL] = np.sum(deltas > 0)
                smell_deltas.loc[0, DECREASED_COL] = np.sum(deltas < 0)

            else:
                logging.warn(f'None of the considered smells detected in all recent releases of project: {p.name}')


            # Store smell deltas for current project
            p.store_app_smell_deltas(smell_deltas)



    def count_file_smell_deltas(self):

        """
        Count deltas in number of smells present in every single
        combination of project, commit and file.
        """
        
        # Compute smell deltas for each file of each project
        for p in self.projects:
            logging.info(f'Computing smell deltas on file scale for: {p.name}')

            smells = p.get_smells()
            files = p.get_valid_files()

            if smells is None:
                raise RuntimeError(f'Missing smells for project `{p.name}`.')
            

            # Read smelly files
            smelly_files = np.unique(smells[FILE_COL])
            n_smelly_files = len(smelly_files)


            # Initialize smell deltas dataframe
            smell_deltas_init = np.hstack((np.reshape(smelly_files, (n_smelly_files, 1)), np.zeros((n_smelly_files, len(DELTA_COLS)))))
            smell_deltas = pd.DataFrame(smell_deltas_init, columns=[FILE_COL] + DELTA_COLS)

            # Cast types
            for delta in DELTA_COLS:
                smell_deltas = smell_deltas.astype({ delta: int })


            # Compute smell deltas for each smelly file
            for smelly_file in smelly_files:
                n_smells = np.array([])

                # Compute number of smells at each recent release
                for release in p.get_recent_releases():
                    release_files = files[files[COMMIT_COL] == release.commit_hash][FILE_COL].tolist()

                    # Only consider a delta if the smelly file exists in current release
                    if smelly_file in release_files:
                        release_smells = smells[(smells[FILE_COL] == smelly_file) & (smells[COMMIT_COL] == release.commit_hash)]
                        n_smells = np.append(n_smells, len(release_smells))


                # Compute deltas for current file from one commit to another
                if np.sum(n_smells) > 0:
                    deltas = n_smells[1:] - n_smells[:-1]

                    row = smell_deltas[FILE_COL] == smelly_file

                    smell_deltas.loc[row, STEADY_COL] = np.sum(deltas == 0)
                    smell_deltas.loc[row, INCREASED_COL] = np.sum(deltas > 0)
                    smell_deltas.loc[row, DECREASED_COL] = np.sum(deltas < 0)

                else:
                    logging.warn(f'None of the considered smells detected in all recent releases of project `{p.name}` in file: {smelly_file}')


            # Store smell deltas for current project
            p.store_file_smell_deltas(smell_deltas)



    def compute_smell_deltas_fns(self, smell_deltas):

        """
        Compute five-number summary of smell deltas. 
        """

        n = len(smell_deltas)

        # Remove files which aren't present in all releases
        invalid = smell_deltas[smell_deltas.sum(axis=AXIS_COL) != N_RELEASE_TAGS - 1].index
        smell_deltas = smell_deltas.drop(index=invalid)
        n_valid = len(smell_deltas)

        # Compute five-number-summary for all files
        fns = pd.DataFrame({}, index=['Min', 'Q1', 'Median', 'Mean', 'Q3', 'Max'], columns=DELTA_COLS)

        logging.info(f'Computing five-number summary of smell deltas on {n_valid}/{n} entries.')

        fns.loc['Min', :] = smell_deltas.min(axis=AXIS_ROW)
        fns.loc['Q1', :] = smell_deltas.quantile(0.25, axis=AXIS_ROW)
        fns.loc['Median', :] = smell_deltas.median(axis=AXIS_ROW)
        fns.loc['Mean', :] = smell_deltas.mean(axis=AXIS_ROW)
        fns.loc['Q3', :] = smell_deltas.quantile(0.75, axis=AXIS_ROW)
        fns.loc['Max', :] = smell_deltas.max(axis=AXIS_ROW)

        # Format FNS
        fns = fns.transpose()
        fns = fns.applymap(lambda x: f'{round(x, 1)}')
        
        return fns



    def compute_smell_deltas_on_app_scale(self):

        """
        Compute smell deltas for all combined apps of a given language. 
        """

        # For each project language
        for language in LANGUAGES:
            result = pd.DataFrame({}, columns=DELTA_COLS, dtype=float)
            
            logging.info(f'Computing smell deltas on app scale for: {language}')

            for p in self.projects:
                if p.language != language:
                    continue

                deltas = p.get_app_smell_deltas()[DELTA_COLS]

                if len(deltas) > 0:
                    result = result.append(deltas, ignore_index=True)

            # Compute five-number-summary for all files
            fns = self.compute_smell_deltas_fns(result)
            print(fns)



    def compute_smell_deltas_on_file_scale(self):

        """
        Compute smell deltas for all combined files of a given language. 
        """

        # For each project language
        for language in LANGUAGES:
            result = pd.DataFrame({}, columns=DELTA_COLS, dtype=float)

            logging.info(f'Computing smell deltas on file scale for: {language}')

            for p in self.projects:
                if p.language != language:
                    continue

                deltas = p.get_file_smell_deltas()[DELTA_COLS]

                if len(deltas) > 0:
                    result = result.append(deltas, ignore_index=True)

            # Compute five-number-summary for all files
            fns = self.compute_smell_deltas_fns(result)
            print(fns)



    def compute_occurences_by_smell(self, p):

        """
        Compute occurence for each smell type
        """
        
        smells = load_dataframe(SMELLS_PATH)

        project_smells = smells[smells[PROJECT_COL] == p.name].loc[:, SMELLS]

        occurences = project_smells.sum(axis=AXIS_ROW)

        return occurences



    def compute_file_count_by_smell(self, p):

        """
        Compute file count for each smell type
        """
        
        smells = load_dataframe(SMELLS_PATH)
        project_smells = smells[smells[PROJECT_COL] == p.name].loc[:, SMELLS]

        file_count = (project_smells > 0).sum(axis=AXIS_ROW)

        return file_count



    def compute_overall_smells_distribution(self):
        result = pd.DataFrame({}, index=SMELLS, columns=LANGUAGES)

        # For each project language
        for language in LANGUAGES:
            occurences_by_app = {}

            for p in self.projects:
                if p.language != language:
                    continue
                
                occurences_by_app[p.name] = self.compute_occurences_by_smell(p)

            # Compute distribution of smells across all apps
            occurences = pd.Series(np.zeros(N_SMELLS), index=SMELLS)

            # Sum occurences of all apps by smell type
            for app_occurences in occurences_by_app.values():
                occurences = occurences.add(app_occurences)

            n_total_occurences = np.sum(occurences)

            occurences /= n_total_occurences
            result.loc[:, language] = occurences

        # Format output to percentages
        result = result.applymap(lambda x: f'{round(x * 100, 1)}%')

        # Replace rule indices to smell names
        result.index = list(map(lambda i: SMELLS_DICT[i]['label'], result.index))

        store_dataframe(result, f'{DATA_DIR}/overall_smells_distribution.csv', index=True)
        print(result)



    def compute_app_smell_frequencies(self):
        result = pd.DataFrame({}, index=SMELLS, columns=LANGUAGES)
        
        # For each project language
        for language in LANGUAGES:
            n_apps = 0

            # Compute app count by smell type
            app_count_by_smell = pd.Series(np.zeros(N_SMELLS), index = SMELLS)

            for p in self.projects:
                if p.language != language:
                    continue

                # Compute occurences by smell type in current app
                occurences = self.compute_occurences_by_smell(p)

                # Increment number of apps as well as app count where each
                # type of smell is displayed
                app_count_by_smell.loc[occurences > 0] += 1
                n_apps += 1

            # Compute percentage of apps affected by each type of smell
            app_frequency_by_smell = app_count_by_smell / n_apps
            result.loc[:, language] = app_frequency_by_smell

        # Format output to percentages
        result = result.applymap(lambda x: f'{round(x * 100, 1)}%')
        
        # Replace rule indices to smell names
        result.index = list(map(lambda i: SMELLS_DICT[i]['label'], result.index))

        store_dataframe(result, f'{DATA_DIR}/app_smell_frequencies.csv', index=True)
        print(result)



    def compute_file_smell_frequencies(self):
        result = pd.DataFrame({}, index=SMELLS, columns=LANGUAGES)
        
        # For each project language
        for language in LANGUAGES:
            n_files = 0

            # Compute file count by smell type
            file_count_by_smell = pd.Series(np.zeros(N_SMELLS), index = SMELLS)

            for p in self.projects:
                if p.language != language:
                    continue

                # Compute file count for each smell type in current app
                file_count_by_smell = file_count_by_smell.add(self.compute_file_count_by_smell(p))

                # Add number of files considered in current app
                files = p.get_valid_files()
                n_files += len(files)


            # Compute percentage of files affected by each type of smell
            file_frequency_by_smell = file_count_by_smell / n_files
            result.loc[:, language] = file_frequency_by_smell

        # Format output to percentages
        result = result.applymap(lambda x: f'{round(x * 100, 1)}%')
        
        # Replace rule indices to smell names
        result.index = list(map(lambda i: SMELLS_DICT[i]['label'], result.index))

        store_dataframe(result, f'{DATA_DIR}/file_smell_frequencies.csv', index=True)
        print(result)



    def compute_smell_cooccurences_in_files(self):
        smells = load_dataframe(SMELLS_PATH)

        # For each project language
        for language in LANGUAGES:
            smells_by_language = pd.DataFrame({}, columns=SMELLS)

            for p in self.projects:
                if p.language != language:
                    continue

                # Merge smell occurences across all projects of same language
                project_smells = smells[smells[PROJECT_COL] == p.name][SMELLS]
                smells_by_language = smells_by_language.append(project_smells, ignore_index=True)
            
            # One-hot encode smell occurences in files
            ohe_smells = smells_by_language > 0

            # Compute co-occurences between all combinations of smells
            cooccurences = apriori(ohe_smells, min_support=EPSILON)

            # Compute matrices of co-occurences between pairs of smells
            cooccurences_smell_pairs = pd.DataFrame(np.full((N_SMELLS, N_SMELLS), '0%'), index=SMELLS, columns=SMELLS)

            for _, row in cooccurences.iterrows():
                cooccurence = '{0}%'.format(round(row['support'] * 100)) # Co-occurence as percentage
                smell_set = row['itemsets']

                # Only consider pairs
                if len(smell_set) == 2:
                    smell_1, smell_2 = [SMELLS[smell] for smell in smell_set]

                    if smell_1 in SMELLS and smell_2 in SMELLS:
                        cooccurences_smell_pairs.loc[smell_1, smell_2] = cooccurence

            # Replace rule indices to smell names
            cooccurences_smell_pairs.index = list(map(lambda i: SMELLS_DICT[i]['short_label'], cooccurences_smell_pairs.index))
            cooccurences_smell_pairs.columns = list(map(lambda i: SMELLS_DICT[i]['short_label'], cooccurences_smell_pairs.columns))

            store_dataframe(cooccurences_smell_pairs, f'{DATA_DIR}/{language}_smell_cooccurences.csv', index=True)
            print(cooccurences_smell_pairs)



    def clean_smell_cooccurences(self):

        """
        Remove smells for which no co-occurence is detected, neither in JS nor in TS projects.
        """

        for language in LANGUAGES:
            cooccurences = load_dataframe(f'{DATA_DIR}/{language}_smell_cooccurences.csv', index_col=0)

            cooccurences = cooccurences.drop(columns=MISSING_SMELL_COOCCURENCES).drop(index=MISSING_SMELL_COOCCURENCES)

            store_dataframe(cooccurences, f'{DATA_DIR}/{language}_clean_smell_cooccurences.csv', index=True)
            print(cooccurences)