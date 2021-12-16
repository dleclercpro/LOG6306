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

RULES = {
    "BLOCKER": {
        "S128": "Switch cases should end with an unconditional 'break' statement",
        "S1219": "'switch' statements should not contain non-case labels",
        "S1314": "Octal values should not be used",
        "S1526": "Variables declared with 'var' should be declared before they are used",
    },
    "CRITICAL": {
        "S131": "'switch' statements should have 'default' clauses",
        "S134": "Control flow statements 'if', 'for', 'while', 'switch' and 'try' should not be nested too deeply", # Too complex
        "S888": "Equality operators should not be used in 'for' loop termination conditions",
        "S1067": "Expressions should not be too complex", # Too complex
        "S1186": "Functions should not be empty", # Useless, confusing
        "S1192": "String literals should not be duplicated", # Useless
        "S1541": "Cyclomatic Complexity of functions should not be too high", #
        "S1821": "'switch' statements should not be nested",
        "S1994": "'for' loop increment clauses should modify the loops' counters",
        "S2871": "A compare function should be provided when using 'Array.prototype.sort()'",
        "S3353": "Unchanged variables should be marked 'const'",
        "S3735": "'void' should not be used",
        "S3776": "Cognitive Complexity of functions should not be too high", # Too complex
        #"S3973": "A conditionally executed single line should be denoted by indentation",
        "S4123": "'await' should only be used with promises",
    },
    "MAJOR": {
        "S104": "Files should not have too many lines of code", # Too long
        "S107": "Functions should not have too many parameters", # Too long, too complex
        "S108": "Nested blocks of code should not be left empty", # Useless, confusing
        "S109": "Magic numbers should not be used", # Confusing
        "S138": "Functions should not have too many lines of code", # Too long
        "S905": "Non-empty statements should change control flow or have at least one side-effect", # Useless, confusing
        "S1117": "Variables should not be shadowed", # Error
        "S1121": "Assignments should not be made from within sub-expressions",
        "S1440": "'===' and '!==' should be used instead of '==' and '!='", # Typing
        "S1479": "'switch' statements should not have too many 'case' clauses", #
        "S1763": "All code should be reachable", #
        "S1788": "Function parameters with default values should be last",
        "S1871": "Two branches in a conditional structure should not have exactly the same implementation", # Useless, confusing
        "S1862": "Related 'if/else if' statements should not have the same condition", # Useless, confusing
        "S2137": "Special identifiers should not be bound or assigned", # Types
        "S2392": "Variables should be used in the blocks where they are declared", # Error
        "S2424": "Built-in objects should not be overridden",
        "S2589": "Boolean expressions should not be gratuitous",
        "S2814": "Variables and functions should not be redeclared", # Error
        "S3531": "Generators should 'yield' something", # Types
        "S3579": "Array indexes should be numeric", # Types
        "S3696": "Literals should not be thrown", # Types
        "S3800": "Functions should always return the same type", ### Types
        "S3801": "Functions should use 'return' consistently", # Types, confusing
        "S3984": "Errors should not be created without being thrown", # Useless
        "S4030": "Collection and array contents should be used",
        "S4140": "Sparse arrays should not be declared", # Types
        "S4143": "Collection elements should not be replaced unconditionally",
        "S4144": "Functions should not have identical implementations", # Useless, confusing
        "S5843": "Regular expressions should not be too complicated", # Too complex
    },
    "MINOR": {
        "S2990": "The global 'this' object should not be used", # Maintainability
        "S3402": "Strings and non-strings should not be added", # Types
    },
    "INFO": {
    },
}



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
STATS_PATH = f'{DATA_DIR}/stats.csv'
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
    'forks_count',
    'stargazers_count',
    'watchers_count',
    'open_issues_count',
    'commits_count',
    'contributors_count',
    'tags_count',
    'releases_count',
    'filtered_releases_count',
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