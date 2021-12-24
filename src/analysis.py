import logging
import numpy as np
import pandas as pd
from scipy import stats
from mlxtend.frequent_patterns import apriori
import matplotlib as mpl
from matplotlib import pyplot as plt
from matplotlib import ticker



# Custom imports
from constants import AXIS_COL, AXIS_ROW, COMMIT_COL, COUNT_COL, DATA_DIR, DECREASED_COL, DELTA_COLS, EPSILON, FILE_COL, FILE_VERSION_COLS, INCREASED_COL, JS, LANGUAGE_NAMES, LANGUAGES, LOC_COL, N_RELEASE_TAGS, PROJECT_COL, RULE_COL, SMELLS_COLS, STATS, SMELLS_PATH, STEADY_COL, TS
from smells import SMELLS, N_SMELLS, SMELLS_DICT
from lib import load_dataframe, ratio_to_percent, store_dataframe



# Useful constants
MIN_COOCCURRENCE = 0.05



# Helper functions
def is_symmetrical(m):
    n_rows = len(m.index)
    n_cols = len(m.columns)

    for i in range(n_rows):
        for j in range(n_cols):
            if m.iloc[i, j] != m.iloc[j, i]:
                return False

    return True



# CLASSES
class Analysis():

    def __init__(self, projects):
        self.projects = projects



    def load_smells(self, language=None):
        smells = load_dataframe(SMELLS_PATH)

        # No language chosen: return all smells
        if language is None:
            return smells

        # Merge smell occurences across all projects of same language
        language_smells = pd.DataFrame({}, columns=SMELLS)

        for p in self.projects:
            if p.language != language:
                continue

            project_smells = smells[smells[PROJECT_COL] == p.name][SMELLS]
            language_smells = language_smells.append(project_smells, ignore_index=True)

        return language_smells



    def merge_stats(self):

        """
        Merge stats of all projects together in one dataframe.
        """
        
        columns = [PROJECT_COL] + STATS

        stats = pd.DataFrame(None, columns=columns)

        for p in self.projects:
            repo_stats = p.repo.stats.to_dict()
            row = {PROJECT_COL: f'{p.owner}/{p.name}', 'language': p.language}

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

        for ratio in ['js_ratio', 'ts_ratio']:
            stats[ratio] = stats[ratio].apply(lambda x: ratio_to_percent(x, 1))

        # Sort according to stars
        stats = stats.sort_values('stargazers_count', axis=AXIS_ROW, ascending=False)

        # Split JS and TS stats
        for language in LANGUAGES:
            split_stats = stats[stats['language'] == language]

            # Drop language column
            split_stats = split_stats.drop(columns=['language'])

            # Store final stats for all projects
            store_dataframe(split_stats, f'{DATA_DIR}/{language}_stats.csv')



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

            # Retrieve considered smells in project
            smells = p.get_smells()

            if smells is None:
                raise RuntimeError(f'Missing smells for project `{p.name}`.')
            

            # Initialize smell deltas dataframe
            smell_deltas_init = np.zeros((1, len(DELTA_COLS)))
            smell_deltas = pd.DataFrame(smell_deltas_init, columns=DELTA_COLS, dtype=int)


            # Compute number of smells at each recent release
            n_smells = np.array([])

            for release in p.get_recent_releases():
                release_smells = smells[smells[COMMIT_COL] == release.commit_hash]
                n_smells = np.append(n_smells, len(release_smells))


            # Compute deltas from one commit to another
            if sum(n_smells) > 0:
                deltas = n_smells[1:] - n_smells[:-1]

                smell_deltas.loc[0, STEADY_COL] = np.sum(deltas == 0)
                smell_deltas.loc[0, INCREASED_COL] = np.sum(deltas > 0)
                smell_deltas.loc[0, DECREASED_COL] = np.sum(deltas < 0)

            # No smell found in any release!
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
            files = p.get_files()

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
                deltas = n_smells[1:] - n_smells[:-1]

                row = smell_deltas[FILE_COL] == smelly_file

                smell_deltas.loc[row, STEADY_COL] = np.sum(deltas == 0)
                smell_deltas.loc[row, INCREASED_COL] = np.sum(deltas > 0)
                smell_deltas.loc[row, DECREASED_COL] = np.sum(deltas < 0)


            # Store smell deltas for current project
            p.store_file_smell_deltas(smell_deltas)



    def compute_smell_deltas_fns(self, smell_deltas):

        """
        Compute five-number summary of smell deltas. 
        """

        # Compute five-number-summary for all files
        fns = pd.DataFrame({}, index=['Min', 'Q1', 'Median', 'Mean', 'Q3', 'Max'], columns=DELTA_COLS)

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



    def compute_fns_app_smell_deltas(self):

        """
        Compute FNS smell deltas for all combined apps of a given language. 
        """

        # For each project language
        for language in LANGUAGES:
            result = pd.DataFrame({}, columns=DELTA_COLS, dtype=float)
            
            logging.info(f'Computing smell deltas on app scale for: {language}')

            n_projects = 0

            for p in self.projects:
                if p.language != language:
                    continue
                else:
                    n_projects += 1

                deltas = p.get_app_smell_deltas()[DELTA_COLS]
                n_deltas = deltas.sum(axis=AXIS_COL)[0]

                # Only consider apps which had smells
                if n_deltas == N_RELEASE_TAGS - 1:
                    result = result.append(deltas, ignore_index=True)

            logging.info(f'Found {len(result)}/{n_projects} projects with smells.')

            # Compute five-number-summary for all files
            fns = self.compute_smell_deltas_fns(result)
            store_dataframe(fns, f'{DATA_DIR}/{language}_fns_app_smell_deltas.csv', index=True)



    def compute_fns_file_smell_deltas(self):

        """
        Compute FNS smell deltas for all combined files of a given language. 
        """

        # For each project language
        for language in LANGUAGES:
            result = pd.DataFrame({}, columns=DELTA_COLS, dtype=float)

            logging.info(f'Computing smell deltas on file scale for: {language}')

            n_files = 0

            for p in self.projects:
                if p.language != language:
                    continue
                else:
                    n_files += len(p.get_files())

                deltas = p.get_file_smell_deltas()[DELTA_COLS]
                n_deltas = deltas.sum(axis=AXIS_COL)

                # Remove files which were deleted at a given release
                deltas = deltas[n_deltas == N_RELEASE_TAGS - 1]

                result = result.append(deltas, ignore_index=True)

            logging.info(f'Found {len(result)}/{n_files} files with smells over {N_RELEASE_TAGS} releases.')

            # Compute five-number-summary for all files
            fns = self.compute_smell_deltas_fns(result)
            store_dataframe(fns, f'{DATA_DIR}/{language}_fns_file_smell_deltas.csv', index=True)



    def compute_occurences_by_smell(self, p):

        """
        Compute occurence for each smell type
        """
        
        smells = self.load_smells()

        project_smells = smells[smells[PROJECT_COL] == p.name].loc[:, SMELLS]

        occurences = project_smells.sum(axis=AXIS_ROW)

        return occurences



    def compute_file_count_by_smell(self, p):

        """
        Compute file count for each smell type
        """
        
        smells = self.load_smells()
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
        result = result.applymap(lambda x: ratio_to_percent(x, 1))

        # Replace rule indices to smell names
        result.index = [SMELLS_DICT[rule]['label'] for rule in result.index]

        # Replace language IDs with their formatted name
        result.columns = [LANGUAGE_NAMES[language] for language in result.columns]

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
        result = result.applymap(lambda x: ratio_to_percent(x, 1))
        
        # Replace rule indices to smell names
        result.index = [SMELLS_DICT[rule]['label'] for rule in result.index]

        # Replace language IDs with their formatted name
        result.columns = [LANGUAGE_NAMES[language] for language in result.columns]

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
                files = p.get_files()
                n_files += len(files)


            # Compute percentage of files affected by each type of smell
            file_frequency_by_smell = file_count_by_smell / n_files
            result.loc[:, language] = file_frequency_by_smell

        # Format output to percentages
        result = result.applymap(lambda x: ratio_to_percent(x, 1))
        
        # Replace rule indices to smell names
        result.index = [SMELLS_DICT[rule]['label'] for rule in result.index]

        # Replace language IDs with their formatted name
        result.columns = [LANGUAGE_NAMES[language] for language in result.columns]

        store_dataframe(result, f'{DATA_DIR}/file_smell_frequencies.csv', index=True)
        print(result)



    def compute_smell_cooccurences(self):
        
        """
        Compute co-occurrence of different smell types in individual files.
        """
        
        # For each project language
        for language in LANGUAGES:
            smells = self.load_smells(language)


            # One-hot encode smell occurences in files
            ohe_smells = smells > 0


            # Compute frequent pairs of smells
            freq_itemsets = apriori(ohe_smells, min_support=EPSILON, max_len=2, use_colnames=True)


            # Compute matrices of co-occurrences between pairs of smells
            cooccurrences = pd.DataFrame(np.zeros((N_SMELLS, N_SMELLS)), index=SMELLS, columns=SMELLS, dtype=float)

            for _, row in freq_itemsets.iterrows():
                smell_set = row['itemsets']
                probability = row['support']

                # Ignore item sets which aren't pairs
                if len(smell_set) != 2:
                    continue

                # Fill co-occurrences matrix with probability of co-occurrence for
                # given pair of smells
                smell_1, smell_2 = smell_set

                if smell_1 in SMELLS and smell_2 in SMELLS:
                    cooccurrences.loc[smell_1, smell_2] = probability
                    cooccurrences.loc[smell_2, smell_1] = probability


            # Make sure matrix is symmetrical
            if not is_symmetrical(cooccurrences):
                raise ArithmeticError('Co-occurence matrix must be symmetrical!')


            # Replace rule indices to smell names
            cooccurrences.index = [SMELLS_DICT[rule]['short_label'] for rule in cooccurrences.index]
            cooccurrences.columns = [SMELLS_DICT[rule]['short_label'] for rule in cooccurrences.columns]


            # Store co-occurence matrices
            store_dataframe(cooccurrences, f'{DATA_DIR}/{language}_smell_cooccurences.csv', index=True)
            store_dataframe(cooccurrences.applymap(lambda x: ratio_to_percent(x, 1)), f'{DATA_DIR}/{language}_clean_smell_cooccurences.csv', index=True)



    def merge_smell_cooccurrences(self):

        """
        Format smell co-occurrences as percentages for each project language. Higher part
        of matrix is dedicated to JS. Lower part is dedicated to TS.
        """

        merged_cooccurrences = pd.DataFrame(np.zeros((N_SMELLS, N_SMELLS)), index=SMELLS, columns=SMELLS, dtype=float)

        for language in LANGUAGES:
            cooccurences = load_dataframe(f'{DATA_DIR}/{language}_smell_cooccurences.csv', index_col=0)
            
            merged_cooccurrences.index = cooccurences.index
            merged_cooccurrences.columns = cooccurences.columns

            for i in range(len(cooccurences.index)):
                for j in range(len(cooccurences.columns)):
                    if (
                        i > j and language == JS or
                        j > i and language == TS or
                        i == j
                    ):
                        continue

                    merged_cooccurrences.iloc[i, j] = cooccurences.iloc[i, j]

        # Co-occurence as percentage
        merged_cooccurrences = merged_cooccurrences.applymap(lambda x: ratio_to_percent(x, 1))
        print(merged_cooccurrences)

        store_dataframe(merged_cooccurrences, f'{DATA_DIR}/merged_smell_cooccurences.csv', index=True)



    def compute_top_smell_cooccurences(self):

        """
        Format and keep only the smell pairs for which the highest co-occurrence probabilities
        have been observed.
        """

        for language in LANGUAGES:
            cooccurences = load_dataframe(f'{DATA_DIR}/{language}_smell_cooccurences.csv', index_col=0)

            # Initialize dataframe for significant co-occurrences (probability of co-occurrence higher
            # than given value)
            significant_cooccurences = pd.DataFrame({}, columns=['Pair', 'Probability'])

            for i in range(len(cooccurences.index)):
                for j in range(len(cooccurences.columns)):
                    if i > j:
                        continue

                    probability = cooccurences.iloc[i, j]

                    # Store JS in 
                    # Keep smells with significant co-occurrence
                    if probability < MIN_COOCCURRENCE:
                        continue
                    
                    significant_cooccurences = significant_cooccurences.append({
                        'Pair': f'({cooccurences.index[i]}, {cooccurences.columns[j]})',
                        'Probability': probability,
                    }, ignore_index=True)

            # Sort by probability
            significant_cooccurences.sort_values('Probability', axis=AXIS_ROW, ascending=False, inplace=True)
            
            # Co-occurence as percentage
            significant_cooccurences['Probability'] = significant_cooccurences['Probability'].apply(lambda x: ratio_to_percent(x, 1))
            print(significant_cooccurences)

            store_dataframe(significant_cooccurences, f'{DATA_DIR}/{language}_smell_cooccurrences_>5%.csv')



    def compute_smell_count_vs_size(self):

        # For each project language
        for language in LANGUAGES:
            smells_vs_size = pd.DataFrame({}, columns=[PROJECT_COL, COMMIT_COL, LOC_COL, COUNT_COL])

            for p in self.projects:
                if p.language != language:
                    continue

                smells = p.get_smells()
                files = p.get_files()

                for release in p.get_recent_releases():
                    n_lines = files[files[COMMIT_COL] == release.commit_hash][LOC_COL].sum()
                    n_smells = len(smells[smells[COMMIT_COL] == release.commit_hash])

                    smells_vs_size = smells_vs_size.append({
                        PROJECT_COL: p.name,
                        COMMIT_COL: release.commit_hash,
                        LOC_COL: n_lines,
                        COUNT_COL: n_smells,
                    }, ignore_index=True)

            store_dataframe(smells_vs_size, f'{DATA_DIR}/{language}_smell_count_vs_size.csv', index=True)



    def plot_smell_count_vs_size(self):

        # Initialize plot
        mpl.rcParams.update({'text.usetex': True, 'font.size': 18})
        _, ax = plt.subplots(figsize = (10, 8))

        # Define plot title and axis labels
        #ax.set_title('Smell Count as a Function of App Size', fontweight = 'bold')
        ax.set_xlabel(r'kLOC')
        ax.set_ylabel(r'Smell Count')

        # Change axes scale
        scale_x = 1_000
        scale_y = 1_000

        ticks_x = ticker.FuncFormatter(lambda x, pos: x / scale_x)
        ax.xaxis.set_major_formatter(ticks_x)

        ticks_y = ticker.FuncFormatter(lambda y, pos: f'{y / scale_y}K')
        ax.yaxis.set_major_formatter(ticks_y)

        # For each project language
        smells_vs_size = {}

        # Define color by language
        colors = {JS: 'red', TS: 'blue'}

        for language in LANGUAGES:
            smells_vs_size[language] = load_dataframe(f'{DATA_DIR}/{language}_smell_count_vs_size.csv')

            x = smells_vs_size[language][LOC_COL].tolist()
            y = smells_vs_size[language][COUNT_COL].tolist()

            m, b, r_value, p_value, std_err = stats.linregress(x, y)

            print(language)
            print(f'Slope: {m}')
            print(f'Intercept: {b}')
            print(f'R^2-Value: {r_value ** 2}')
            print(f'P-Value: {p_value}')
            print(f'STD Error: {std_err}')
            print()

            x_ = np.linspace(0, 185_000, 1_000)

            # Plot points
            ax.plot(x, y, label=LANGUAGE_NAMES[language], ls='', ms=3, marker='o', c=colors[language])

            # Plot linear fits
            ax.plot(x_, m*x_ + b, label=None, ls='--', c=colors[language])

        # Add legend to plot
        ax.legend()

        # Tighten up the whole plot
        plt.tight_layout()

        # Show plot
        plt.show()