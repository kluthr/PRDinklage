import json
import os
import requests

GITHUB_TOKEN = os.environ['GIT_TOKEN']


class GitHubHandler(object):

    def __init__(self):
        self.token = GITHUB_TOKEN
        self.url_base = 'https://api.github.com/'

    def get_teams(self):
        '''Retrieves a list of Vacasa's teams from github
        '''
        url = '{}orgs/Vacasa/teams?access_token={}'.format(self.url_base,
                                                           self.token)
        response = requests.get(url)
        teams = json.loads(response.text)
        team_list = []

        for team in teams:
            team_list.append(team["name"])

        return team_list

    def get_team_members(self, command):
        '''Finds a team name based on the give command and returns a list of
        members for that team
        '''
        team_data = {}
        team_info = self._get_team_info(command)

        if team_info:
            team_data = self._get_team_members(team_info)

        return team_data

    def get_team_prs(self, command):
        '''Finds a team name based on the given command and returns a list of
        pr data for the teams' members
        '''
        prs = []
        team_data = self.get_team_members(command)
        if team_data:
            repos = self._set_repos()
            prs = self._set_prs(repos, team_data)

        return prs

    def _get_team_info(self, command):
        '''Finds a team name based on the given command and returns a dict
        of the team name and team id
        '''
        url = '{}orgs/Vacasa/teams?access_token={}'.format(self.url_base,
                                                           self.token)
        response = requests.get(url)
        teams = json.loads(response.text)
        command = command.replace('-', ' ').upper()
        info = {}

        for team in teams:
            name = team['name'].upper()

            if name in command:
                info = {'name': team['name'], 'id': team['id']}
                break

        return info

    def _get_team_members(self, team_info):
        '''Retrieves a list of team members based on the team info
        '''
        url = '{}teams/{}/members?access_token={}'.format(self.url_base,
                                                          team_info["id"],
                                                          self.token)
        response = requests.get(url)
        members = json.loads(response.text)

        team_info["team_members"] = []
        for member in members:
            team_info["team_members"].append(member["login"])

        return team_info

    def _set_repos(self):
        '''Returns a list of repos for Vacasa's github account
        '''
        url = '{}orgs/Vacasa/repos?access_token={}'.format(self.url_base,
                                                           self.token)
        response = requests.get(url)
        repos = json.loads(response.text)

        repos_list = []
        for repo in repos:
            repos_list.append(repo['url'])

        return repos_list

    def _set_prs(self, repos, team_info):
        '''Returns a list of dicts representing a team's prs
        '''
        pr_data = []

        for repo in repos:
            response = requests.get(
                '{}/pulls?access_token={}'.format(repo, self.token))
            prs = json.loads(response.text)

            for pr in prs:
                user = pr['user']['login']
                if user in team_info['team_members']:
                    jira_reference = pr['head']['ref'].split('/')[-1]
                    pr_data.append({"user": user,
                                    "pr_url": pr['url'],
                                    "jira_reference": jira_reference,
                                    "reviews": self._set_pr_reviews(pr['url'])
                                    })

        return pr_data

    def _set_pr_reviews(self, url):
        '''Returns a formatted string containing pr approvals for the given pr
        url
        '''
        response = requests.get(
            '{}/reviews?access_token={}'.format(url, self.token))
        reviews = json.loads(response.text)

        reviewers_string = ''
        for reviewer in reviews:
            if reviewer['state'] == 'APPROVED':
                reviewers_string = (
                    '{} {} |'.format(reviewers_string,
                                     reviewer['user']['login']))
        if len(reviewers_string) > 1:
            reviewers_string = "[APPROVED:{}]".format(reviewers_string[:-2])
        else:
            reviewers_string = "[ ]"

        return reviewers_string
