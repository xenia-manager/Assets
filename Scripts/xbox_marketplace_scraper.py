import os
import json
import requests
from bs4 import BeautifulSoup

def download_image(url, target_path):
    response = requests.get(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
    })
    with open(target_path, 'wb') as f:
        f.write(response.content)

def scrape_and_download():
    # URL of the JSON file containing game data
    json_url = 'https://raw.githubusercontent.com/xenia-manager/xenia-manager-database/main/Database/xbox_marketplace_games.json'
    try:
        response = requests.get(json_url)
        if response.status_code == 200:
            game_data = response.json()
            download_and_organize_images(game_data)
        else:
            print(f"Failed to fetch JSON data. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch JSON data. Exception: {e}")

def download_and_organize_images(game_data):
    for game in game_data:
        url = game["Box art"]
        if url:
            image_name = f"{game['ID']}.jpg"
            folder_path = os.path.join("Assets","Marketplace","Boxart")
            os.makedirs(folder_path, exist_ok=True)
            file_path = os.path.join(folder_path, image_name)
            download_image(url, file_path)
            print(f"Downloaded: {file_path}")

        else:
            print(f"No image found for {game['Title']}.")

if __name__ == "__main__":
    scrape_and_download()
