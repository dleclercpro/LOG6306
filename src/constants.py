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

STATS_DIR = f'{DATA_DIR}/stats'
TAGS_DIR = f'{DATA_DIR}/tags'
RELEASES_DIR = f'{DATA_DIR}/releases'
ISSUES_DIR = f'{DATA_DIR}/issues'
SMELLS_DIR = f'{DATA_DIR}/smells'

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
    'Leaflet/Leaflet',
    'hexojs/hexo',
    'chartjs/Chart.js',
    'webtorrent/webtorrent',
    'riot/riot',
    'd3/d3',
    'axios/axios',
    'lodash/lodash',
    'prettier/prettier',
    'mui-org/material-ui'

    # DO NOT WORK
    #'gruntjs/grunt',
    #'nodejs/node',
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
]

TS_PROJECTS = [
    'formium/formik',
    'socketio/socket.io',
    'nestjs/nest',
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
    'youzan/vant',
    ###'ianstormtaylor/slate',
    ###'lensapp/lens',
    
    # DO NOT WORK
    #'facebook/jest',
    ##'angular/angular',
    ##'microsoft/vscode',
    #'reduxjs/redux',
    ##'sass/sass',
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
]