import os

import requests
from dotenv import load_dotenv

from database import Database
from game import Game

load_dotenv()

API_KEY = os.getenv("API_KEY")
STEAM_ID = os.getenv("STEAM_ID")


def get_owned_games_data(api_key, steam_id):
    url = "https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
    params = {
        'key': api_key,
        'steamid': steam_id,
        'include_appinfo': True,
        'include_played_free_games': True,
        'format': 'json'
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get('response', {}).get('games', [])

    print(f"Error while fetching games: {response.status_code}")
    return []


def get_achievement_schema(api_key, app_id) -> dict:
    url = "https://api.steampowered.com/ISteamUserStats/GetSchemaForGame/v2/"
    params = {
        'key': api_key,
        'appid': app_id,
        'l': 'english',
        'format': 'json'
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        achievements = response.json().get('game', {}).get('availableGameStats', {}).get('achievements', [])
        return {achievement['name']: achievement for achievement in achievements}
    return {}


def get_game_data(api_key, steam_id, app_id) -> None | Game:
    url = "https://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/"
    params = {
        'key': api_key,
        'steamid': steam_id,
        'appid': app_id,
        'format': 'json'
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json().get('playerstats', {})
        return Game(
            app_id=app_id,
            game_name=data.get('gameName', '-'),
            achievements=data.get('achievements', []),
            schema_loader=lambda app_id: get_achievement_schema(api_key, app_id),
        )
    return None


def find_perfect_games():
    print("Fetching game list from Steam...")
    owned_games = get_owned_games_data(API_KEY, STEAM_ID)
    games_ids = [str(game['appid']) for game in owned_games if game.get('playtime_forever', 0) > 5]

    if not games_ids:
        print("No games found, or the profile is private.")
        return

    print(f"Found {len(owned_games)} games, including {len(games_ids)} played.\n")
    print("Checking achievements...")
    perfect_games = []
    perfect_games_ids_before = Database.get_perfect_games_ids()

    for game_id in games_ids:
        game = get_game_data(API_KEY, STEAM_ID, game_id)
        if game is None:
            continue

        if game.perfect:
            if game.app_id not in perfect_games_ids_before:
                print(f"[NEW 100%] Game {game.game_name} has been added to the 100% list!")
                Database.add_perfect_game(game.app_id)

            perfect_games.append(game)
        elif game.app_id in perfect_games_ids_before:
            not_unlocked_achievements = game.get_not_unlocked_achievements()

            print(f"[REMOVED] Game {game.game_name} has been removed from the 100% list, missing {len(not_unlocked_achievements)} achievements")
            print("Not unlocked achievements:")
            for achievement in not_unlocked_achievements:
                print(f"- {achievement.name}: {achievement.description}")
            Database.remove_perfect_game(game.app_id)

    print(f"Total games at 100%: {len(perfect_games)}")


if __name__ == "__main__":
    find_perfect_games()
