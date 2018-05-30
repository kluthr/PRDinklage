import json
from pr_dinklage import PRDinklage


with open('teams.json') as teams_file:
    teams = json.load(teams_file)

    for team, members in teams.items():
        dinkle = PRDinklage('ABDCEFG',
                            '<@U7X8J1LCA> show {} users'.format(team))
        dinkle.parse_command()
        print('')

        dinkle2 = PRDinklage('ABDCEFG',
                             '<@U7X8J1LCA> show {} prs'.format(team))
        dinkle2.parse_command()
        print('')
