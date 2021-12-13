import os
import datetime
import logging
from multiprocessing import Pool



# Custom libs
from constants import DIRS, TS_PROJECTS, JS_PROJECTS, LOG_PATH
from lib import formatSeconds
from project import Project
from analysis import Analysis



def process_projects(projects):
    for name, language in projects:
        p = Project(name, language)
        p.initialize()


        # Grab remaining releases to process
        n_releases = len(p.repo.releases)

        # Initialize counters
        n = len(p.remaining_releases)
        i = 0

        t_0 = datetime.datetime.now()

        # Process every release
        while n > 0:
            logging.info(f'Processing release: {n_releases - n + 1}/{n_releases}')

            release = p.remaining_releases[i]

            p.checkout(release)
            p.delete()
            p.scan()
            p.extract_issues()

            t = datetime.datetime.now()

            i += 1
            n -= 1

            remaining_seconds = (t - t_0).total_seconds() / i * n
            logging.info(f'Remaining time: {formatSeconds(remaining_seconds)}')



def analyze_projects(projects):
    p_s = []

    for name, language in projects:
        p = Project(name, language)
        p.initialize()

        # Keep project in memory
        p_s += [p]

    analysis = Analysis(p_s)
    #analysis.merge_stats()
    #analysis.find_rules()
    #analysis.load_rules()
    #analysis.list_files()
    #analysis.list_smells()
    #analysis.count_smells()
    #analysis.count_smell_deltas()
    analysis.compute_overall_distribution_smells()
    analysis.compute_app_smell_frequencies()






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
    projects = [(name, 'js') for name in JS_PROJECTS] + [(name, 'ts') for name in TS_PROJECTS]

    # Process every project
    #process_projects(projects)

    # Analyze every project
    analyze_projects(projects)






if __name__ == '__main__':
    main()