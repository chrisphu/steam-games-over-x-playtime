import sys
import urllib.request
import json

steam_web_api_url = 'http://api.steampowered.com/'

def check_for_help_flag():
    if len(sys.argv) == 1:
        raise Exception('No arguments supplied.')
    if sys.argv[1] in ['-h', '--help']:
        print('\nCommand to run: py steam-games-over-x-playtime.py {steam web api key} {steamids} {x minutes}')
        print('\n- Go to https://steamcommunity.com/dev for Steam Web API Key')
        print('- {steamids} are 64 bit SteamIDs separated by commas.')
        return True
    return False

def check_number_of_arguments():
    expected_number_of_arguments = 4
    if len(sys.argv) != expected_number_of_arguments:
        quantifier = 'few' if len(sys.argv) < expected_number_of_arguments else 'many'
        raise Exception('Too ' + quantifier + ' arguments supplied.')

def check_x_minutes_argument(x_minutes):
    try:
        x_minutes = int(x_minutes)
        return x_minutes
    except Exception as error:
        print(error)
        raise Exception('Could not parse {x minutes} argument as an integer.')

def write_url_argument(parameter, argument, first_argument = False):
    delimiter = '?' if first_argument else '&'
    return delimiter + parameter + '=' + argument

def attempt_json_load_from_steam_web_api_url(url):
    try:
        response = urllib.request.urlopen(url)
        data = json.load(response)['response']
        return data
    except Exception as error:
        print(error)
        raise Exception('Could not load .json data.')

def steam_web_api_GetPlayerSummaries(arguments):
    url = steam_web_api_url + 'ISteamUser/GetPlayerSummaries/v0002/' + arguments
    return attempt_json_load_from_steam_web_api_url(url)

def steam_web_api_GetOwnedGames(arguments):
    url = steam_web_api_url + 'IPlayerService/GetOwnedGames/v0001/' + arguments
    return attempt_json_load_from_steam_web_api_url(url)

def get_game_count_over_x_minutes_playtime(data, x_minutes):
    count = 0
    games = data['games']
    for game in games:
        if game['playtime_forever'] > x_minutes:
            count += 1
    return count

def main():
    if check_for_help_flag():
        return
    check_number_of_arguments()
    x_minutes = check_x_minutes_argument(sys.argv[3])

    steam_web_api_key_url_argument = write_url_argument('key', sys.argv[1], True)
    steamids_url_argument = write_url_argument('steamids', sys.argv[2])
    steam_web_api_GetPlayerSummaries_url_arguments = steam_web_api_key_url_argument + steamids_url_argument
    steam_web_api_GetPlayerSummaries_data = steam_web_api_GetPlayerSummaries(steam_web_api_GetPlayerSummaries_url_arguments)

    players = steam_web_api_GetPlayerSummaries_data['players']
    for player in players:
        persona_name = player['personaname']
        steamid = player['steamid']
        steamid_url_argument = write_url_argument('steamid', steamid)
        format_url_argument = write_url_argument('format', 'json')
        steam_web_api_GetOwnedGames_url_arguments = steam_web_api_key_url_argument + steamid_url_argument + format_url_argument
        steam_web_api_GetOwnedGames_data = steam_web_api_GetOwnedGames(steam_web_api_GetOwnedGames_url_arguments)
        game_count = steam_web_api_GetOwnedGames_data['game_count']
        game_count_over_x_minutes_playtime = get_game_count_over_x_minutes_playtime(steam_web_api_GetOwnedGames_data, x_minutes)
        
        rounded_percentage_of_games = round((game_count_over_x_minutes_playtime / game_count) * 100, 1)
        print('{}: {} owns {} of {} games ({}%) with over {} minutes of playtime.'.format(steamid, persona_name, game_count_over_x_minutes_playtime, game_count, rounded_percentage_of_games, x_minutes))

if __name__ == '__main__':
    main()
