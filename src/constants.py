import os
from dotenv import load_dotenv



# Load environment variables
load_dotenv()



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

DELTAS = [STEADY_COL, INCREASED_COL, DECREASED_COL]

SMELLS_DICT = {
    "S103": "Lines should not be too long", # Lengthy lines
    "S107": "Functions should not have too many parameters", # Long parameter list
    "S134": "Control flow statements 'if', 'for', 'while', 'switch' and 'try' should not be nested too deeply", # Depth
    "S138": "Functions should not have too many lines of code", # Long method
    "S1121": "Assignments should not be made from within sub-expressions", # Assignment in conditional statement
    "S1541": "Cyclomatic Complexity of functions should not be too high", # Complex code
    "S4327": "'this' should not be assigned to variables", # This-assign

    # Additions
    "S104": "Files should not have too many lines of code", # Lengthy file
    "S109": "Magic numbers should not be used", # Magic number
    "S125": "Sections of code should not be commented out", # Dead code
    "S1067": "Expressions should not be too complex", # Complex expression
    "S1117": "Variables should not be shadowed", # Shadowed variable
    "S1186": "Functions should not be empty", # Empty function
    "S1192": "String literals should not be duplicated", # Duplicated strings
    "S1440": "'===' and '!==' should be used instead of '==' and '!='", # Weak equality
    "S1763": "All code should be reachable", # Unreachable code
    "S1854": "Unused assignments should be removed", # Useless assignment
    "S2424": "Built-in objects should not be overridden", # Overwritten built-ins
    "S2814": "Variables and functions should not be redeclared", # Overwritten variable/function
    "S3003": "Comparison operators should not be used with strings", # String ordinal comparison
    "S3516": "Function returns should not be invariant", # Invariant function
    "S3696": "Literals should not be thrown", # Invalid errors
    "S3699": "The output of functions that don't return anything should not be used", # Useless output
    "S3801": "Functions should use 'return' consistently", # Inconsistent function type
    "S4144": "Functions should not have identical implementations", # Duplicated function

    # Missing
    "S1479": "'switch' statements should not have too many 'case' clauses", # Complex switch

    # Missing additions
    "S1862": "Related 'if/else if' statements should not have the same condition", # Duplicated conditional statement
    "S2688": "'NaN' should not be used in comparisons", # NaN comparison
    "S3531": "Generators should 'yield' something", # Useless generator
    "S3984": "Errors should not be created without being thrown", # Useless error
}

SMELLS = ['S103','S104','S107','S109','S125','S134','S138','S1067','S1117','S1121','S1186','S1192','S1440','S1541','S1763','S1854','S2424','S2814','S3003','S3516','S3696','S3699','S3801','S4144','S4327',]
N_SMELLS = len(SMELLS)



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
STATS = [
    'created_at',
    'stargazers_count',
    #'watchers_count',
    'forks_count',
    'contributors_count',
    #'open_issues_count',
    'commits_count',
    'tags_count',
    #'releases_count',
    #'filtered_releases_count',
    'js_ratio',
    'ts_ratio',
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

    # DO NOT WORK
    #'facebook/jest',
    #'ant-design/ant-design',
    ##'angular/angular',
    #'cheeriojs/cheerio',
    #'typeorm/typeorm',
    #'fingerprintjs/fingerprintjs',
    ##'microsoft/vscode',
    #'neoclide/coc.nvim',
    #'reduxjs/react-redux',
    #'reduxjs/redux-thunk',
    #'vercel/next.js',
    #'GeekyAnts/NativeBase',
    #'redis/node-redis',
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