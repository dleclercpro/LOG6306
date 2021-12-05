import os
import datetime
import logging
from multiprocessing import Pool



# Custom libs
from constants import COMMITS_DIR, DATA_DIR, ISSUES_DIR, LOGS_DIR, REPOS_DIR
from lib import formatSeconds
from project import Project



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
    
    n_commits = len(p.repo.commits)
    n_remaining_commits = len(p.remaining_commits)

    # Initialize counters
    n = 0
    n_remaining = n_remaining_commits

    t_0 = datetime.datetime.now()

    # Process every commit
    while n_remaining > 0:
        logging.info(f'Processing commit {n_commits - n_remaining_commits + 1}/{n_commits}')

        commit = p.remaining_commits[n]
        logging.info(commit)

        p.checkout(commit)
        p.scan()
        p.extract_smells()

        t = datetime.datetime.now()

        n += 1
        n_remaining -= 1

        remaining_seconds = (t - t_0).total_seconds() / n * n_remaining
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
    ts_projects = ['formium/formik']
    projects = ts_projects + js_projects

    # Generate data and results directories (if they do not already exist)
    for dir in [REPOS_DIR, LOGS_DIR, DATA_DIR, COMMITS_DIR, ISSUES_DIR]:
        if not os.path.exists(dir):
            os.makedirs(dir)

    # Process every project
    with Pool(4) as p:
        p.map(process_project, projects)
    #for project in projects:
    #    process_project(project)






if __name__ == '__main__':
    main()