# LOG6306: Patrons pour la compréhension de programme

### Project Title
Impact of Typing on Code Smells: A Comparison Between Javascript and Typescript Projects

### Smell Detectors
- SonarQube
- JSNose

## Validity Threats
- Not using a compiler may be compensated by increasingly intelligent IDEs, which can provide static code analysis on-the-fly.
- Code smells may be a symptom of a hidden variable (e.g. community smells), which is responsible for fault-proneness of code.

## Questions
- Does SonarQube analyze the entire commit history? If so, does it keep track of issues which existed at some point, but were then removed?
- Which code smells can SonarQube identify?
- What is the detection performance of SonarQube?
- Can I add a custom set of rules allowing SonarQube to detect more smells? How to determine performance then?