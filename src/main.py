import os
import logging
from multiprocessing import Pool



# Custom libs
from constants import DIRS, JS, TS, TS_PROJECTS, JS_PROJECTS, LOG_PATH
from project import Project
from analysis import Analysis



def process_projects(projects):
    for name, language in projects:
        p = Project(name, language)

        # Initialize project
        p.initialize()

        # Scan project for issues
        p.find_issues()

        # List project's valid JS/TS files
        p.list_valid_files()

        # List project's smells
        p.list_smells()



def analyze_projects(projects):
    p_s = []

    for name, language in projects:
        p = Project(name, language)

        # Initialize project
        p.initialize()

        # Keep project in memory
        p_s += [p]

    # Execute analysis for all projects
    analysis = Analysis(p_s)
    analysis.merge_stats()
    
    #analysis.count_smells()
    #analysis.count_smell_deltas_by_project()

    analysis.compute_overall_smells_distribution()
    analysis.compute_app_smell_frequencies()
    analysis.compute_file_smell_frequencies()
    analysis.compute_smell_cooccurences_in_files()






def main():

    """
    NOTE: Please set working directory to where this main file exists for it to work.

    Steps:
    1 - Run a server instance of SonarQube.
    2 - Define a user with 'Browse' permissions on all projects.
    3 - Run this file.
    """

    # Generate data and results directories (if they do not already exist)
    for dir in DIRS:
        if not os.path.exists(dir):
            os.makedirs(dir)

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format=f'%(asctime)s [%(levelname)s] %(message)s',
        handlers=[logging.FileHandler(LOG_PATH), logging.StreamHandler()],
    )

    # Define projects
    projects = [(name, JS) for name in JS_PROJECTS] + [(name, TS) for name in TS_PROJECTS]

    # Process every project
    process_projects(projects)

    # Analyze every project
    analyze_projects(projects)






if __name__ == '__main__':
    main()