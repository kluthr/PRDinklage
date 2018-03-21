import json
import os
from requests import get, auth

JIRA_KEY = os.environ['JIRA_KEY']


class JiraHandler(object):

    def __init__(self):
        self.key = JIRA_KEY
        self.username = JIRA_KEY.split(":")[0]
        self.password = JIRA_KEY.split(":")[1]

    def add_jira_statuses(self, prs, command):
        '''Adds correlated jira statuses to a list of pr dicts, or 'None' if no
        jira status is found
        '''
        team_members = self.get_team_members(command)
        jira_issues = self._get_jira_issues(team_members)

        for pr in prs:
            pr['status'] = self._get_jira_status(pr['jira_reference'],
                                                 jira_issues)

        return prs

    def get_team_members(self, command):
        '''Retrieves team members from the teams.json file of jira users
        '''
        command = command.replace('-', ' ').upper()
        team_members = []

        with open('teams.json') as teams_file:
            teams = json.load(teams_file)

            for team_name, team_members in teams.items():
                if team_name.upper() in command:
                    members = team_members

        return members

    def _get_jira_issues(self, users):
        '''Retrieves each user's jira issues as key:status pairs and adds them
        to a list
        '''
        jira_issues = []

        for user in users:
            url = ('https://vacasait.atlassian.net/rest/api/2/'
                   'search?jql=assignee={}'.format(user))
            r = get(url, auth=auth.HTTPBasicAuth(self.username, self.password))
            issues = json.loads(r.text)
            for issue in issues['issues']:
                jira_issues.append((issue['key'],
                                    issue['fields']['status']['name']))
        return jira_issues

    def _get_jira_status(self, reference, jira_issues):
        '''Searches a list of jira_issues for the given reference and returns
        the jira status of the reference, or 'None' if not found
        '''
        terms = reference.split('-')
        reference_title = '{}{}'.format(terms[0], terms[1]).upper()

        for issue in jira_issues:
            title_terms = issue[0].split('-')
            title = '{}{}'.format(title_terms[0], title_terms[1]).upper()
            if reference_title in title:
                return issue[1]

        return 'None'
