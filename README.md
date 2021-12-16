# LOG6306: Patrons pour la compréhension de programme

### Impact of Typing on Code Smells: A Comparison Between Javascript and Typescript Projects

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

## Instructions
- Change the ROOT_DIR variable in 'constants.py' for the directory where you extracted this project to
## Questions
- Does SonarQube analyze the entire commit history? If so, does it keep track of issues which existed at some point, but were then removed?
    - It seems as though SonarQube only reports issues present in the current state of a project. It also informs the user wrt. when said issues were introduced in their current form.
    - The problem is: those issues could have been introduced earlier, yet the last modification involving it is identified as the time where it was introduced.
    - Another problem is: if an issue existed at some point, but was removed, it never shows up in SonarQube's analysis.
    - Another problem is: how to follow evolution of code smells over time?
- Which code smells can SonarQube identify?
- What is the detection performance of SonarQube?
- Can I add a custom set of rules allowing SonarQube to detect more smells? How to determine performance then?