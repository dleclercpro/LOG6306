import os
import time
import datetime
import logging
from multiprocessing import Pool



# Custom libs
from constants import TS_PROJECTS, JS_PROJECTS, STATS_DIR, COMMITS_DIR, ISSUES_DIR, LOGS_DIR, REPOS_DIR
from lib import formatSeconds
from project import Project



def process_project(project):
    p = Project(project)

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format=f'%(asctime)s [%(levelname)s] %(message)s',
        handlers=[logging.FileHandler(f'{LOGS_DIR}/root.log'), logging.StreamHandler()],
    )

    # Initialize repository
    p.initialize()

    # Grab remaining commits to process
    n_commits = len(p.repo.commits)
    n_remaining_commits = len(p.remaining_commits)

    # Initialize counters
    n = n_remaining_commits
    i = 0

    t_0 = datetime.datetime.now()

    # Process every commit
    while n > 0:
        logging.info(f'Processing commit {n_commits - n + 1}/{n_commits}')

        commit = p.remaining_commits[i]
        logging.info(commit)

        p.checkout(commit)
        p.scan()

        # Give some time to SonarQube server to process new issues before
        # fetching them
        time.sleep(5)
        
        p.extract_smells()

        t = datetime.datetime.now()

        i += 1
        n -= 1

        remaining_seconds = (t - t_0).total_seconds() / i * n
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
    projects = TS_PROJECTS + JS_PROJECTS

    # Generate data and results directories (if they do not already exist)
    for dir in [REPOS_DIR, LOGS_DIR, STATS_DIR, COMMITS_DIR, ISSUES_DIR]:
        if not os.path.exists(dir):
            os.makedirs(dir)

    # Process every project
    multi = False

    if multi:
        with Pool(4) as p:
            p.map(process_project, projects)
    else:
        for project in projects:
            print()
            process_project(project)






if __name__ == '__main__':
    main()