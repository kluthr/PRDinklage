<?php

class PRDinklage {

    protected $curl;
    
    public function __construct($git_token, $jira_key) {
        $this->git_token = $git_token;
        $this->jira_key = $jira_key;
        $this->curl = curl_init();
    }

    public function help(){
        $message = "How can I help you? I can:\n\n";
        $message = $message . "`@pr_dinklage show team names`\n";
        $message = $message . "`@pr_dinklage show {team} prs`\n";
        $message = $message . "`@pr_dinklage show {team} users`\n\n";
        return $message;
    }

    private function get_users_from_file($team) {
        $json = file_get_contents('/var/www/html/helpers/teams.json');
        $team_data = json_decode($json, true);   
        $users = [
            'github_users' => $team_data['teams'][$team]['github_users'],
            'jira_users' => $team_data['teams'][$team]['jira_users']
        ];
        return $users;
    }

    public function show_team_members($team) {
        $data = $this->get_users_from_file($team);
        $message = $this->create_team_message($data, $team);
        return $message;
    }

    public function show_team_names() {
        $json = file_get_contents('/var/www/html/helpers/teams.json');
        $team_data = json_decode($json, true); 
        $message = $this->create_team_names_message($team_data);
        return $message;
    }

    public function show_team_prs($team) {
        $users = $this->get_users_from_file($team);   
        $jira_issues = $this->get_jira_issues($users);
        $repos = $this->get_repos();
        $prs = $this->get_prs($repos, $users, $jira_issues);
        $message = $this->create_pr_message($prs);
        curl_close($this->curl);
        return $message;
    }

    private function get_jira_issues($users) {
        $jira_issues = [];
        $header = [
            'Content-Type'=>'application/json'
        ];
        curl_reset($this->curl);
        curl_setopt($this->curl, CURLOPT_USERPWD, $this->jira_key);
        curl_setopt($this->curl, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($this->curl, CURLOPT_HTTPHEADER, $header);
        foreach ($users['jira_users'] as $user) {
            $url = "https://vacasait.atlassian.net/rest/api/2/search?jql=assignee={$user}";
            curl_setopt($this->curl, CURLOPT_URL, $url);
            $results = curl_exec($this->curl);
            $issues = json_decode($results, true);
            foreach ($issues['issues'] as $issue){
                $jira_issues[$issue['key']] = $issue['fields']['status']['name'];
            }
        }
        return $jira_issues;
    }

    private function get_repos() {
        $team_repos;
        $header = [
            'Content-Type'=>'application/json'
        ];
        $url = "https://api.github.com/orgs/Vacasa/repos?access_token={$this->git_token}";
        curl_reset($this->curl);
        curl_setopt($this->curl, CURLOPT_URL, $url);
        curl_setopt($this->curl, CURLOPT_USERAGENT, 'PRDinklage');
        curl_setopt($this->curl, CURLOPT_RETURNTRANSFER, true);
        $results = curl_exec($this->curl);
        $repos = json_decode($results, true);
        foreach ($repos as $repo) {
            $team_repos[] = $repo['url'];
        }
        return $team_repos;
    }

    private function get_prs($repos, $users, $jira_issues) {
        $prs;
        foreach ($repos as $repo) {
            $url = "{$repo}/pulls?access_token={$this->git_token}";
            curl_reset($this->curl);
            curl_setopt($this->curl, CURLOPT_URL, $url);
            curl_setopt($this->curl, CURLOPT_USERAGENT, 'PRDinklage');
            curl_setopt($this->curl, CURLOPT_RETURNTRANSFER, true);
            $repo_prs = json_decode(curl_exec($this->curl), true);
            foreach ($repo_prs as $pr) {
                $reference = $pr['head']['ref'];
                $status = $this->get_jira_status($reference, $jira_issues);
                $user = substr($pr['user']['url'], 29);
                if (in_array($user, $users['github_users'])) {
                    $reviews = $this->get_pr_reviews($pr['url']);
                    $details = [$status, $pr['_links']['html']['href'], $user, $reviews];
                    $prs[] = $details;
                }
            }
        }
        sort($prs);
        return $prs;
    }

    private function get_jira_status($reference, $jira_issues) {
        foreach ($jira_issues as $key => $value) {
            if (strpos($reference, $key)) {
                return $value;
            }
        }
        return 'None';
    }

   private function get_pr_reviews($url) {
        curl_reset($this->curl);
        curl_setopt($this->curl, CURLOPT_URL, "{$url}/reviews?access_token={$this->git_token}");
        curl_setopt($this->curl, CURLOPT_USERAGENT, 'PRDinklage');
        curl_setopt($this->curl, CURLOPT_RETURNTRANSFER, true);
        $results = curl_exec($this->curl);
        $reviews = json_decode($results, true);
        $review_string = '';
        foreach ($reviews as $review) {
            if ($review['state'] == 'APPROVED') {
                $review_string = $review_string . "{$review['user']['login']} | ";
            }
        }
        if (strlen($review_string) > 1) {
            $substring = substr($review_string, 0, -2);
            $review_string = "[ APPROVED:{$substring}]";
        } else {
            $review_string = '[ ]';   
        }
        return $review_string;
    }

    private function create_pr_message($prs) {
        $message = "I have found the following PRs for this team:\n";
        foreach ($prs as $pr) {
            $status_padding = str_repeat(' ', 25 - strlen($pr[0]));
            $url_padding = str_repeat(' ', 60 - strlen($pr[1]));
            $name_padding = str_repeat(' ', 20 - strlen($pr[2]));
            $message = $message . "`{$pr[0]}{$status_padding}{$pr[1]}{$url_padding}{$pr[2]}{$name_padding}{$pr[3]}`\n";
        }
        $message = $message . 'Excellent work team :tada:';
        return $message;
    }

    private function create_team_message($users, $team) {
        $name = strtoupper($team);
        $message = "TEAM {$name}:\nGithub: [\n";
        sort($users['github_users']);
        foreach ($users['github_users'] as $user) {
            $message = $message . "\t`{$user}`\n";
        }
        $message = $message . "]\nJira: [\n";
        sort($users['jira_users']);
        foreach ($users['jira_users'] as $user) {
            $message = $message . "\t`{$user}`\n";
        }
        $message = $message . "]\n";
        return $message;
    }

    private function create_team_names_message($data) {
        $message = "TEAMS: [\n";
        foreach ($data['teams'] as $key => $value) {
            $message = $message . "\t`{$key}`\n";
        }
        $message = $message . "]\n";
        return $message;
    }

    public function edit_team($team, $edit, $type='', $user='') {
        $json = file_get_contents('teams.json');
        $team_data = json_decode($json, true); 
        if ($type == 'jira') {
            $type = 'jira_users';
        } elseif ($type == 'github') {
            $type = 'github_users';
        }
        
        if ($edit == 'add') {
            $this->add_user($team_data, $team, $type, $user);
        } elseif ($edit == 'delete') {
            $this->delete_user($team_data, $team, $type, $user);
        } elseif ($edit == 'new') {
            $this->add_team($team_data, $team);
        }   
    }

    private function add_user($data, $team, $type, $user) {
        $data['teams'][$team][$type][] = $user;
        file_put_contents('teams.json', json_encode($data));
        $this->show_team_members($team);
    }

    private function delete_user($data, $team, $type, $user) {
        if (($key = array_search($user, $data['teams'][$team][$type])) !== false) {
            echo $key;
            unset($data['teams'][$team][$type][$key]);
        }
        file_put_contents('teams.json', json_encode($data));
        $this->show_team_members($team);
    }

    private function add_team($data, $name) {
        $data['teams'][$name]['jira_users'] = [];
        $data['teams'][$name]['github_users'] = [];
        $data['teams'][$name]['slack_channel'] = "";
        ksort($data);
        file_put_contents('teams.json', json_encode($data));
        $this->show_team_members('all');
    }
}

