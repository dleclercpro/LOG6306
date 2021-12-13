import os
from dotenv import load_dotenv



# Load environment variables
load_dotenv()



# Formats
DATETIME_FORMAT = '%Y.%m.%d - %H:%M:%S'

PROJECT_COL = 'project'
COMMIT_COL = 'commit_hash'
FILE_COL = 'file_name'



# AXES
AXIS_ROW = 0
AXIS_COL = 1



# Paths
ROOT_DIR = '/Users/david/Projects/LOG6306'

REPOS_DIR = f'{ROOT_DIR}/repos'
LOGS_DIR = f'{ROOT_DIR}/logs'
DATA_DIR = f'{ROOT_DIR}/data'

STATS_DIR = f'{DATA_DIR}/stats'
TAGS_DIR = f'{DATA_DIR}/tags'
RELEASES_DIR = f'{DATA_DIR}/releases'
ISSUES_DIR = f'{DATA_DIR}/issues'
SMELLS_DIR = f'{DATA_DIR}/smells'
FILES_DIR = f'{DATA_DIR}/files'

DIRS = [REPOS_DIR, LOGS_DIR, STATS_DIR, TAGS_DIR, RELEASES_DIR, ISSUES_DIR, SMELLS_DIR, FILES_DIR]

STATS_PATH = f'{DATA_DIR}/stats.csv'
SMELLS_PATH = f'{DATA_DIR}/smells.csv'
GENERIC_RULES_PATH = f'{DATA_DIR}/generic_rules.csv'
SPECIFIC_RULES_PATH = f'{DATA_DIR}/specific_rules.csv'

LOG_PATH = f'{LOGS_DIR}/root.log'



# GitHub
GITHUB_API = 'https://api.github.com'
GITHUB_TOKEN = os.environ['GITHUB_TOKEN']

# Sonar
SONAR_API = 'http://localhost:9000/api'
SONAR_TOKEN = os.environ['SONAR_TOKEN']
SONAR_USERNAME = os.environ['SONAR_USERNAME']
SONAR_PASSWORD = os.environ['SONAR_PASSWORD']

SONAR_SCANNER = os.environ['SONAR_SCANNER']
SONAR_PROJECT_PROPS_FNAME = 'sonar-project.properties'
SONAR_SCANNER_PROPS_FNAME = 'sonar-scanner.properties'



# Stats
STATS = [
    'created_at',
    'forks_count',
    'stargazers_count',
    'watchers_count',
    'open_issues_count',
    'commits_count',
    'contributors_count',
    'releases_count',
    'js_proportion',
    'ts_proportion',
]



# Projects
JS_PROJECTS = [
    'expressjs/express',
    'bower/bower',
    'request/request',
    'jquery/jquery',
    'ramda/ramda',
    'hexojs/hexo',
    'chartjs/Chart.js',
    'webtorrent/webtorrent',
    'riot/riot',
    'd3/d3',
    'axios/axios',
    'yarnpkg/yarn',
    'serverless/serverless',
    'tailwindlabs/tailwindcss',
    'typicode/json-server',

    # DO NOT WORK
    #'gruntjs/grunt',
    #'strapi/strapi',
    #'meteor/meteor',
    #'nodejs/node',
    #'mrdoob/three.js',
    #'h5bp/html5-boilerplate',
    #'Leaflet/Leaflet',
    #'less/less.js',
    #'vuejs/vue',
    #'webpack/webpack',
    #'moment/moment',
    #'facebook/react',
    #'facebook/react-native',
    #'vuejs/vue',
    #'twbs/bootstrap',
    #'atom/atom',
    #'FortAwesome/Font-Awesome',
    #'hakimel/reveal.js',
    #'mui-org/material-ui',
    #'lodash/lodash',
    #'prettier/prettier',
    #'gatsbyjs/gatsby',
]

TS_PROJECTS = [
    'formium/formik',
    'socketio/socket.io',
    'apollographql/apollo-client',
    'redis/node-redis',
    'ionic-team/ionic-framework',
    'vercel/hyper',
    'nativefier/nativefier',
    'facebook/docusaurus',
    'cheeriojs/cheerio',
    'tannerlinsley/react-query',
    'akveo/ngx-admin',
    'reduxjs/react-redux',
    'graphql/graphql-js',
    'railsware/upterm',
    'balena-io/etcher',

    # DO NOT WORK
    #'facebook/jest',
    #'ant-design/ant-design',
    ##'angular/angular',
    #'typeorm/typeorm',
    ##'microsoft/vscode',
    #'vercel/next.js',
    #'reduxjs/redux',
    ##'sass/sass',
    #'NativeScript/NativeScript',
    #'nestjs/nest',
    #'puppeteer/puppeteer',
    #'sveltejs/svelte',
    #'babel/babel',
    ##'signalapp/Signal-Desktop',
    #'wechaty/wechaty',
    ##'storybookjs/storybook',
    #'apollographql/apollo-server',
    #'tensorflow/tfjs',
    ##'BabylonJS/Babylon.js',
    ###'cdr/code-server',
    ##'apache/superset',
    ##'pixijs/pixijs',
    ##'vitejs/vite',
    ##'vuetifyjs/vuetify',
    ###'immutable-js/immutable-js'
    ##'apache/echarts',
    ##'postcss/postcss',
    ##'laurent22/joplin',
    ##'angular/angular-cli',
    ##'niklasvh/html2canvas',
    ##'mobxjs/mobx',
    ##'supabase/supabase',
    ##'chakra-ui/chakra-ui',
    ##'angular/components',
    ##'doczjs/docz',
    #'t4t5/sweetalert',
    ##'vuejs/devtools',
    #'ianstormtaylor/slate',
    ##'Eugeny/tabby',
    #'prisma/prisma',
    ###'elastic/kibana',
    #'GoogleChromeLabs/squoosh',
    #'recharts/recharts',
    #'jquense/yup',
    #'grafana/grafana',
    #'excalidraw/excalidraw',
    #'conwnet/github1s',
    #'codex-team/editor.js',
    #'notable/notable',
    #'lensapp/lens',
]