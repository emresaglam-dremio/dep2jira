from dep_parser import Dependencies

# Create a new Dependencies instance
# This will read the configuration from config_test.yaml 
# Hopefully I will change that soon as a parameter.

d = Dependencies()
crits = d.get_crits()
d.issue_prep()
d.push_issues_to_JIRA()

# You can always nuke the issues that you created by running 
# d.nuke_issues(quantity=10)
# This will nuke 10 issues.