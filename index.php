<?php
require 'vendor/autoload.php';
require 'helpers/config.php';
require 'helpers/PRDinklage.php';

use React\EventLoop\Factory;
use BotMan\BotMan\BotManFactory;
use BotMan\BotMan\Drivers\DriverManager;
use BotMan\Drivers\Slack\SlackRTMDriver;

DriverManager::loadDriver(SlackRTMDriver::class);

$git_token = '';
$jira_key = '';
$loop = Factory::create();
$botman = BotManFactory::createForRTM([
    'slack' => [
        'token' => '',
    ],
], $loop);

$botman->hears('<@U7X8J1LCA>', function($bot) {
    $bot->reply('How may I serve you? :crown:');
});

$botman->hears('<@U7X8J1LCA> help', function($bot) {
    $dinkle = new PRDinklage('', '');
    $message = $dinkle->help();
    $bot->reply($message);
});

$botman->hears('<@U7X8J1LCA> show {team} users', function($bot, $team) {
    $dinkle = new PRDinklage('', '');
    $message = $dinkle->show_team_members($team);
    $bot->reply($message);
});

$botman->hears('<@U7X8J1LCA> show {team} prs', function($bot, $team) {
    $git_token = '';
    $jira_key = '';    
    echo $git_token;
    echo $jira_key;
    $bot->reply("Gathering information...");
    $dinkle = new PRDinklage($git_token, $jira_key);
    $message = $dinkle->show_team_prs($team);
    $bot->reply($message);
});

$botman->hears('<@U7X8J1LCA> show team names', function($bot) {
    $dinkle = new PRDinklage('', '');
    $message = $dinkle->show_team_names();
    $bot->reply($message);
});

$botman->hears('Thank you <@U7X8J1LCA>', function($bot) {
    $bot->reply('You are most welcome.');
});

$botman->hears('<@U7X8J1LCA> party!', function($bot) {
    $bot->reply(":partyparrot: :parrotbeer: :ice-cream-parrot: :aussie-reverse-conga-parrot: :aussie-conga-parrot: :aussie-reverse-conga-parrot: :parrotsleep:\n:parrotwave1: :parrotwave2: :parrotwave3: :parrotwave4: :parrotwave5: :parrotwave6: :parrotwave7:");
});

$loop->run();

