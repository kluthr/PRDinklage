import os
from slackclient import SlackClient
from random import randrange
from github_handler import GitHubHandler
from jira_handler import JiraHandler

SLACK_TOKEN = os.environ['SLACK_TOKEN']
DINKLAGE_ID = os.environ['DINKLAGE_ID']
QUOTES = [
    'Never forget what you are, the rest of the world will not. Wear it like '
    'armor and it can never be used to hurt you.',
    'Death is so final, yet life is full of possibilities.',
    'A mind needs books like a sword needs a whetstone.',
    'It\'s hard to put a leash on a dog once you\'ve put a crown on its head.',
    'I try to know as many people as I can. You never know which one you\'ll '
    'need.',
    'It\'s not easy being drunk all the time. If it were easy, everyone would '
    'do it.',
    'Every time we deal with an enemy, we create two more.',
    'In my experience eloquent men are right every bit as often as imbeciles.',
    'It\'s easy to confuse "what is" with "what ought to be,"" especially when'
    ' "what is" has worked out in your favor.'
    ]


class PRDinklage(object):

    def __init__(self, channel_id, command):
        self.slack_client = SlackClient(SLACK_TOKEN)
        self.channel_id = channel_id
        self.command = command.upper()

    def parse_command(self):
        '''
        Parses the event command and routes it accordingly. Sends the returned
        message to slack
        '''
        terms = self.command.split()
        if self.command == DINKLAGE_ID:
            message = 'How may I serve you? :crown:'
        elif 'HELP' in terms:
            message = self._show_help_message()
        else:
            gh_handler = GitHubHandler()
            if 'TEAMS' in terms:
                message = self._show_teams(gh_handler)
            elif 'USERS' in terms:
                message = self._show_team_users(gh_handler)
            elif 'PRS' in terms:
                message = self._show_team_prs(gh_handler)
            else:
                self._send_slack_message('I\'m not sure what you mean, but a '
                                         'word of advice:')
                message = QUOTES[randrange(0, len(QUOTES), 1)]

        self._send_slack_message(message)
        return True

    def _send_slack_message(self, message):
        '''Sends a message to slack via the slackbot
        '''
        self.slack_client.api_call(
            'chat.postMessage',
            channel=self.channel_id,
            text=message,
        )

    def _show_help_message(self):
        '''Returns a message containing help info to send to slack
        '''
        message = ('How can I help? I can:\n\n`@pr_dinklage show teams`\n'
                   '`@pr_dinklage show {team} prs`\n`@pr_dinklage show {team}'
                   ' users`\n\n')
        return message

    def _show_teams(self, gh_handler):
        '''Retrieves team names from Github and returns as a message to send
        to slack
        '''
        teams = gh_handler.get_teams()
        message = 'TEAMS:\n'

        for team in teams:
            message = '{}{}\n'.format(message, team)

        return message

    def _show_team_users(self, gh_handler):
        '''Gets a list of github users for a team given in the command and
        returns as a formatted message
        '''
        team_data = gh_handler.get_team_members(self.command)
        if 'name' in team_data and 'id' in team_data:
            if team_data['team_members']:
                github_users = team_data['team_members']

                jira_handler = JiraHandler()
                jira_users = jira_handler.get_team_members(team_data['name'])

                message = '{}:\nGithub Users:\n'.format(
                    team_data['name'].upper())

                for user in github_users:
                    message = '{}{}\n'.format(message, user)

                message = '{}\nJira Users:\n'.format(message)

                for user in jira_users:
                    message = '{}{}\n'.format(message, user)
            else:
                message = 'No users found for this team.'
        else:
            message = 'Team not found. Please try again.'

        return message

    def _show_team_prs(self, gh_handler):
        '''Takes a command to show team prs and identifies the team name,
        gets the team prs and their relevant jira statuses, formats the prs
        into a message, and returns a message of pr details to send to slack
        '''
        self._send_slack_message('Gathering information...')

        prs = gh_handler.get_team_prs(self.command)
        if prs:
            filled_prs = self._add_jira_statuses(prs)
            message = self._build_pr_message(filled_prs)
        else:
            message = 'No prs found for this team.'

        return message

    def _add_jira_statuses(self, prs):
        '''Takes a list of pr dicts and adds the related jira status for the
        pr to the dict
        '''
        jira_handler = JiraHandler()
        filled_prs = jira_handler.add_jira_statuses(prs, self.command)
        return filled_prs

    def _build_pr_message(self, prs):
        '''Takes a list of pr dicts and builds a formatted message of their
        details
        '''
        message = 'I have found the following PRs for this team:\n'
        for pr in prs:
            name_padding = 18 - len(pr['user'])
            url_padding = 65 - len(pr['pr_url'])
            status_padding = 23 - len(pr['status'])
            message = '{}`{}{}{}{}{}{}{}`\n'.format(message,
                                                    pr['user'],
                                                    ' ' * name_padding,
                                                    pr['pr_url'],
                                                    ' ' * url_padding,
                                                    pr['status'],
                                                    ' ' * status_padding,
                                                    pr['reviews'])
        message = '{}Excellent work :tada:'.format(message)
        return message
