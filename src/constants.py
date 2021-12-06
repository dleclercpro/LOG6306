import os
from dotenv import load_dotenv



# Load environment variables
load_dotenv()



# Formats
DATETIME_FORMAT = '%Y.%m.%d - %H:%M:%S'



# Paths
ROOT_DIR = '/Users/david/Projects/LOG6306'
REPOS_DIR = f'{ROOT_DIR}/repos'
LOGS_DIR = f'{ROOT_DIR}/logs'
DATA_DIR = f'{ROOT_DIR}/data'
COMMITS_DIR = f'{DATA_DIR}/commits'
ISSUES_DIR = f'{DATA_DIR}/issues'



# GitHub
GITHUB_API = 'https://api.github.com'
GITHUB_TOKEN = os.environ['GITHUB_TOKEN']

# Sonar
SONAR_API = 'http://localhost:9000/api/issues/search'
SONAR_TOKEN = os.environ['SONAR_TOKEN']
SONAR_USERNAME = os.environ['SONAR_USERNAME']
SONAR_PASSWORD = os.environ['SONAR_PASSWORD']

SONAR_SCANNER = os.environ['SONAR_SCANNER']
SONAR_PROJECT_PROPS_FNAME = 'sonar-project.properties'
SONAR_SCANNER_PROPS_FNAME = 'sonar-scanner.properties'



# Projects
JS_PROJECTS = [
    'expressjs/express',
    'bower/bower',
    'less/less.js',
    'request/request',
    'gruntjs/grunt',
    'jquery/jquery',
    'vuejs/vue',
    'ramda/ramda',
    'Leaflet/Leaflet',
    'hexojs/hexo',
    'chartjs/Chart.js',
    'webpack/webpack',
    'moment/moment',
    'webtorrent/webtorrent',
    'riot/riot',
    'facebook/react',
    'facebook/react-native',
    'vuejs/vue',
    'twbs/bootstrap',
    'd3/d3',
    'axios/axios',
    'atom/atom',
    'lodash/lodash',
]

TS_PROJECTS = [
    'facebook/jest',
    'formium/formik',
    'angular/angular',
    'microsoft/vscode',
    'reduxjs/redux',
    'socketio/socket.io',
    'puppeteer/puppeteer',
    'sveltejs/svelte',
    'nestjs/nest',
    'babel/babel',
    'apollographql/apollo-client',
    'apollographql/apollo-server',
    'tensorflow/tfjs',
    'BabylonJS/Babylon.js',
    'redis/node-redis',
    'sass/sass',
    'signalapp/Signal-Desktop',
    'wechaty/wechaty',
    'storybookjs/storybook',
]