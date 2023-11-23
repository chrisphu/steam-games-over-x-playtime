import sys
import urllib.request
import json

steam_web_api_url = 'http://api.steampowered.com/'

def check_for_help_flag():
    if len(sys.argv) == 1:
        return
    if sys.argv[1] in ['-h', '--help']:
        print('\nCommand to run: py steam-games-over-x-playtime.py {steam web api key} {steamid} {x minutes}')
        print('\n- Go to https://steamcommunity.com/dev for Steam Web API Key')
        print('- {steamid} is the account\'s 64 bit SteamID')
        return True
    return False

def check_number_of_arguments():
    if len(sys.argv) != 4:
        quantifier = 'few' if len(sys.argv) < 3 else 'many'
        raise Exception('Too ' + quantifier + ' arguments.')

def check_x_minutes_argument(x_minutes):
    try:
        x_minutes = int(x_minutes)
        return x_minutes
    except Exception as error:
        print(error)
        raise Exception('Could not parse {x minutes} argument as in integer.')

def write_url_argument(parameter, argument, first_argument = False):
    delimiter = '?' if first_argument else '&'
    return delimiter + parameter + '=' + argument

def steam_web_api_GetOwnedGames(arguments):
    url = steam_web_api_url + 'IPlayerService/GetOwnedGames/v0001/' + arguments
    try:
        response = urllib.request.urlopen(url)
        data = json.load(response)['response']
        return data
    except Exception as error:
        print(error)
        raise Exception('Could not load .json data.')

def get_game_count(data):
    return data['game_count']

def get_game_count_with_playtime_equal_to_or_greater_than_x_minutes(data, x_minutes):
    count = 0
    games = data['games']
    for game in games:
        if game['playtime_forever'] >= x_minutes:
            count += 1
    return count

def main():
    if check_for_help_flag():
        return
    check_number_of_arguments()
    x_minutes = check_x_minutes_argument(sys.argv[3])

    steam_web_api_key_argument = write_url_argument('key', sys.argv[1], True)
    steamid_argument = write_url_argument('steamid', sys.argv[2])
    format_argument = write_url_argument('format', 'json')
    arguments = steam_web_api_key_argument + steamid_argument + format_argument

    steam_web_api_GetOwnedGames_data = steam_web_api_GetOwnedGames(arguments)
    game_count = get_game_count(steam_web_api_GetOwnedGames_data)
    game_count_with_playtime_equal_to_or_greater_than_x_minutes = get_game_count_with_playtime_equal_to_or_greater_than_x_minutes(steam_web_api_GetOwnedGames_data, x_minutes)
    
    rounded_percentage_of_games = round((game_count_with_playtime_equal_to_or_greater_than_x_minutes / game_count) * 100, 1)
    print('\n{} of {} games ({}%) with over {} minutes of playtime.'.format(game_count_with_playtime_equal_to_or_greater_than_x_minutes, game_count, rounded_percentage_of_games, x_minutes))

if __name__ == '__main__':
    main()
