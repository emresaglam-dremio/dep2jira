import csv
import json
from jira import JIRA
from yaml import safe_dump, safe_load

class Dependencies:

    def __init__(self):
        self.config_file="config_test.yaml"
        with open(self.config_file, 'r') as configfile:
            self.config = safe_load(configfile)
        self.filename = self.config["jira"]["filename"]
        self.server = self.config["jira"]["server"]
        self.username = self.config["jira"]["username"]
        self.api_token = self.config["jira"]["api_token"]
        self.project = self.config["jira"]["project"]
        self.issuetype={'name': 'Bug'}
        self.components = [{"name": "Security"}]
        self.j = JIRA(server=self.server, basic_auth=(self.username, self.api_token))
        self.crits = []
        self.jira_issues = []
    
    def get_crits(self):
        '''
        This function parses the CSV file and gets only the CRITICALs from the report.
        TODO: Parse all in the future
        '''
        with open(self.filename) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row["CVSSv3_BaseSeverity"] == "CRITICAL":
        #        if row["CVSSv3_BaseSeverity"] == "":
        #           row["CVSSv3_BaseSeverity"] = "MEDIUM"
                    self.crits.append(row)
                    #print ("{}\n|\n⌙-->{}: {} \n".format(row["Identifiers"], row["CVSSv3_BaseSeverity"], row["Vulnerability"]))
        return self.crits
        #print (json.dumps(self.crits))

    def issue_prep(self):
        '''
        This function prepares the issues to be pushed to JIRA. It doesn't push them!
        In order to push the issues, you need to run push_issues_to_JIRA() function
        '''
        for crit in self.crits:
            issue_summary = "[CRITICAL] This is a 3rd party library vulnerability "
            issue_summary = issue_summary + "for {}".format(crit["DependencyName"])
            issue_description = "*Please upgrade the library to the latest version. Or if the product is not impacted by this vulnerability, please create a suppression.* \n\n"
            issue_description = issue_description + "Description: {}\n{}\n\n".format(crit["Description"], crit["Vulnerability"])
            for key, value in crit.items():
                if "CVE" in value:
                    value = "[{}|https://cve.mitre.org/cgi-bin/cvename.cgi?name={}]".format(value, value)
                issue_description = issue_description + "{}: {}\n".format(key, value)
            #print("{}\n{}".format(issue_summary, issue_description))
            issue_details = {
                'project': {'key': self.project},
                'summary': issue_summary,
                'description': issue_description,
                'issuetype': self.issuetype,
                'components': self.components
            }
            self.jira_issues.append(issue_details)
            #new_issue = j.create_issue(fields=issue_details)
            #print(new_issue)
            issue_description = ""


    def push_issues_to_JIRA(self, quantity=1):
        '''
        This will push the issues parsed in issue_prep() to JIRA. It has a "brake" functionality as the quantity parameter.
        quantity is there to prevent flooding accidentally our JIRA with a ton of stuff. Please check the size of the 
        self.jira_issues list (len(self.jira_issues)) and give that as a parameter to the quantity for production!
        '''
        counter = 0
        if self.jira_issues:
            for jira_issue in self.jira_issues:
                if counter < quantity:
                    new_issue = self.j.create_issue(fields=jira_issue)
                    print(new_issue)
                    counter += 1
        else:
            raise Exception("JIRA issues are empty, you might want to check if you ran issue_prep() before this")


    def nuke_issues(self):
        warning = input("This is a destructive operation on this JIRA account: {} \nIt will nuke all the issues in this project: {}\nAre you sure?! (Yes/No)> ".format(self.server, self.project))
        if warning == "Yes":
            issues = self.j.search_issues('project={}'.format(self.project))
            #print(issues)
            for issue in issues:
                print("{} deleted...".format(issue))
                issue.delete()
        else:
            print("Skipping the nuke...")