import os



# Formats
DATETIME_FORMAT = '%Y.%m.%d - %H:%M:%S'

# Useful constants
EPSILON = 1e-9

# Pandas axes
AXIS_ROW = 'index'
AXIS_COL = 'columns'

# Languages
JS = 'javascript'
TS = 'typescript'
LANGUAGES = [JS, TS]

# Releases
N_RELEASE_TAGS = 25

# File extensions
JS_EXTENSIONS = ['.js', '.jsx', '.mjs']
TS_EXTENSIONS = ['.ts', '.tsx']



# Dataframe column labels
PROJECT_COL = 'project'
COMMIT_COL = 'commit_hash'
FILE_COL = 'file_name'
LANGUAGE_COL = 'language'
RULE_COL = 'rule'
TYPE_COL = 'type'
SEVERITY_COL = 'severity'
TAGS_COL = 'tags'

FILE_VERSION_COLS = [PROJECT_COL, COMMIT_COL, FILE_COL]
SMELLS_COLS = FILE_VERSION_COLS + [RULE_COL]

SEVERITIES = ['BLOCKER', 'CRITICAL', 'MAJOR']

STEADY_COL = 'steady'
INCREASED_COL = 'increased'
DECREASED_COL = 'decreased'

DELTA_COLS = [STEADY_COL, INCREASED_COL, DECREASED_COL]



# Paths
ROOT_DIR = '/Users/david/Projects/LOG6306'
#ROOT_DIR = 'C:/Projects/LOG6306'

REPOS_DIR = f'{ROOT_DIR}/repos'
LOGS_DIR = f'{ROOT_DIR}/logs'
DATA_DIR = f'{ROOT_DIR}/data'

STATS_DIR = f'{DATA_DIR}/stats'
TAGS_DIR = f'{DATA_DIR}/tags'
RELEASES_DIR = f'{DATA_DIR}/releases'
ISSUES_DIR = f'{DATA_DIR}/issues'
SMELLS_DIR = f'{DATA_DIR}/smells'
DELTAS_DIR = f'{DATA_DIR}/deltas'
FILES_DIR = f'{DATA_DIR}/files'

DIRS = [REPOS_DIR, LOGS_DIR, STATS_DIR, TAGS_DIR, RELEASES_DIR, ISSUES_DIR, SMELLS_DIR, DELTAS_DIR, FILES_DIR]

LOG_PATH = f'{LOGS_DIR}/root.log'
JS_STATS_PATH = f'{DATA_DIR}/js_stats.csv'
TS_STATS_PATH = f'{DATA_DIR}/ts_stats.csv'
SMELLS_PATH = f'{DATA_DIR}/smells.csv'



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
STATS = ['created_at', 'stargazers_count', 'forks_count', 'contributors_count', 'commits_count', 'tags_count', 'js_ratio', 'ts_ratio']



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

    'facebook/create-react-app',
    'mermaid-js/mermaid',
    'nuxt/nuxt.js',
    'Dogfalo/materialize',
    'nwjs/nw.js',
    'iamkun/dayjs',
    'kenwheeler/slick',
    'GitSquared/edex-ui',
    'alvarotrigo/fullPage.js',
    'koajs/koa',
    'quilljs/quill',
    'zenorocha/clipboard.js',
    'lerna/lerna',
    'preactjs/preact',
    'nolimits4web/swiper',
    'carbon-app/carbon',
    'jashkenas/backbone',
]

TS_PROJECTS = [
    'formium/formik',
    'socketio/socket.io',
    'apollographql/apollo-client',
    'statelyai/xstate',
    'palantir/blueprint',
    'pmndrs/react-three-fiber',
    'ionic-team/ionic-framework',
    'vercel/hyper',
    'nativefier/nativefier',
    'facebook/docusaurus',
    'tannerlinsley/react-query',
    'akveo/ngx-admin',
    'graphql/graphql-js',
    'railsware/upterm',
    'balena-io/etcher',

    'marmelab/react-admin',
    'react-dnd/react-dnd',
    'floating-ui/floating-ui',
    'youzan/vant',
    'reduxjs/reselect',
    'pubkey/rxdb',
    'wulkano/Kap',    
    'fingerprintjs/fingerprintjs',
    'react-navigation/react-navigation',
    'ustbhuangyi/better-scroll',
    'pmndrs/react-spring',
    'streamich/react-use',
    'JedWatson/react-select',
    'remix-run/react-router',
    'oldj/SwitchHosts',
    'flatpickr/flatpickr',
]