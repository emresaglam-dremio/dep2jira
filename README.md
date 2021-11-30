Created a python class to parse the OWASP Dependency Check CSV report and create JIRA tickets for the CRITICALs.


## TODO
- Parametrize the config file.
- Parametrize the `issuetype` and the `component`
- Maybe don't return anything in get_crits()?
- Add HIGHs, not just CRITICALs
- More error handling