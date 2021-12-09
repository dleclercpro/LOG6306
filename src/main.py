import os
import datetime
import logging
from multiprocessing import Pool



# Custom libs
from constants import TS_PROJECTS, JS_PROJECTS, RELEASES_DIR, SMELLS_DIR, LOGS_DIR, STATS_DIR, TAGS_DIR, ISSUES_DIR, LOGS_DIR, REPOS_DIR, LOG_PATH
from lib import formatSeconds
from project import Project
from analysis import Analysis



def process_projects(projects):
    for project in projects:
        p = Project(project)
        p.initialize()

        # Grab remaining releases to process
        n_releases = len(p.repo.releases)
        n_remaining_releases = len(p.remaining_releases)

        # Initialize counters
        n = n_remaining_releases
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

    for project in projects:
        p = Project(project)
        p.initialize()

        if project == 'formium/formik':
            formik = p

        # Keep project in memory
        p_s += [p]

    analysis = Analysis(p_s)
    #analysis.merge_stats()
    analysis.find_common_rules()
    #analysis.load_common_rules()
    #analysis.list_raw_smells()
    #analysis.merge_raw_smells()
    #analysis.count_smell_deltas(formik)






def main():

    """
    NOTE: Please set working directory to where this main file exists for it to work.

    Steps:
    1 - Run a server instance of SonarQube.
    2 - Define a user with 'Browse' permissions on all projects.
    3 - Run this file.
    """

    # Generate data and results directories (if they do not already exist)
    for dir in [REPOS_DIR, LOGS_DIR, STATS_DIR, TAGS_DIR, RELEASES_DIR, ISSUES_DIR, SMELLS_DIR]:
        if not os.path.exists(dir):
            os.makedirs(dir)

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format=f'%(asctime)s [%(levelname)s] %(message)s',
        handlers=[logging.FileHandler(LOG_PATH), logging.StreamHandler()],
    )

    # Define projects
    projects = TS_PROJECTS + JS_PROJECTS

    # Process every project
    process_projects(projects)

    # Analyze every project
    #analyze_projects(projects)






if __name__ == '__main__':
    main()