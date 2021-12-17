# Impact of Typing on Code Smells: An Empirical Comparison Between Javascript and Typescript Projects in the Open-Source Community

## Smell Detector
- SonarQube

## Validity Threats
- Not using a compiler may be compensated by increasingly intelligent IDEs, which can provide static code analysis on-the-fly.
- Code smells may be a symptom of a hidden variable (e.g. community smells), which is responsible for fault-proneness of code.
- Max number of issues that can be fetched from the SonarQube server: 10,000
- Selection of releases only (X.X.X) using tags, manual filtering
- Minimum 25 patch-level releases
- Ignored files with 'test' in their path
- Some projects may have converted from JS to TS recently
- Ignoring files which aren't present in all recent releases when computing smell deltas on file scale

## Instructions
- Change the ROOT_DIR variable in 'constants.py' for the directory where you extracted this project to
- Rename '.env.dummy' to '.env' and fill it with your own credentials

## Questions
- Does SonarQube analyze the entire commit history? If so, does it keep track of issues which existed at some point, but were then removed?
    - It seems as though SonarQube only reports issues present in the current state of a project. It also informs the user wrt. when said issues were introduced in their current form.
    - The problem is: those issues could have been introduced earlier, yet the last modification involving it is identified as the time where it was introduced.
    - Another problem is: if an issue existed at some point, but was removed, it never shows up in SonarQube's analysis.
    - Another problem is: how to follow evolution of code smells over time?
- Which code smells can SonarQube identify?
- What is the detection performance of SonarQube?
- Can I add a custom set of rules allowing SonarQube to detect more smells? How to determine performance then?

## Incompatible JS Projects
- gruntjs/grunt
- strapi/strapi
- meteor/meteor
- nodejs/node
- mrdoob/three.js
- h5bp/html5-boilerplate
- Leaflet/Leaflet
- less/less.js
- vuejs/vue
- webpack/webpack
- moment/moment
- facebook/react
- facebook/react-native
- vuejs/vue
- twbs/bootstrap
- atom/atom
- FortAwesome/Font-Awesome
- hakimel/reveal.js
- mui-org/material-ui
- lodash/lodash
- prettier/prettier
- gatsbyjs/gatsby

## Incompatible TS Projects
- facebook/jest
- ant-design/ant-design
- angular/angular
- cheeriojs/cheerio
- typeorm/typeorm
- fingerprintjs/fingerprintjs
- microsoft/vscode
- neoclide/coc.nvim
- reduxjs/react-redux
- reduxjs/redux-thunk
- vercel/next.js
- GeekyAnts/NativeBase
- redis/node-redis
- reduxjs/redux
- sass/sass
- NativeScript/NativeScript
- nestjs/nest
- puppeteer/puppeteer
- sveltejs/svelte
- babel/babel
- signalapp/Signal-Desktop
- wechaty/wechaty
- storybookjs/storybook
- apollographql/apollo-server
- tensorflow/tfjs
- BabylonJS/Babylon.js
- cdr/code-server
- apache/superset
- pixijs/pixijs
- vitejs/vite
- vuetifyjs/vuetify
- immutable-js/immutable-js
- apache/echarts
- postcss/postcss
- laurent22/joplin
- angular/angular-cli
- niklasvh/html2canvas
- mobxjs/mobx
- supabase/supabase
- chakra-ui/chakra-ui
- angular/components
- doczjs/docz
- t4t5/sweetalert
- vuejs/devtools
- ianstormtaylor/slate
- Eugeny/tabby
- prisma/prisma
- elastic/kibana
- GoogleChromeLabs/squoosh
- recharts/recharts
- jquense/yup
- grafana/grafana
- excalidraw/excalidraw
- conwnet/github1s
- codex-team/editor.js
- notable/notable
- lensapp/lens