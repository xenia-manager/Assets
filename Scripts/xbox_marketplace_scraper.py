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
    json_url = 'https://gist.githubusercontent.com/shazzaam7/f5d16a46a0c16dd1b926af2ace3b9155/raw/92bc31a447b81907af70963b0ebc8bf21ea8334b/test.json'
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
    box_art_env = os.getenv('BOX_ART_ENV', None)
    icon_env = os.getenv('ICON_ENV', None)
    
    if not box_art_env and not icon_env:
        print("Error: No environment variable for box art or icon specified.")
        return
    
    for game in game_data:
        if box_art_env:
            box_art_url = game.get(box_art_env)
            if box_art_url:
                image_name = f"{game['ID']}.jpg"
                folder_path = os.path.join("Assets", "Marketplace", "Boxart")
                os.makedirs(folder_path, exist_ok=True)
                file_path = os.path.join(folder_path, image_name)
                download_image(box_art_url, file_path)
                print(f"Downloaded box art: {file_path}")
            else:
                print(f"No box art found for {game['Title']}.")

        if icon_env:
            icon_url = game.get(icon_env)
            if icon_url:
                image_name = f"{game['ID']}.jpg"
                folder_path = os.path.join("Assets", "Marketplace", "Icons")
                os.makedirs(folder_path, exist_ok=True)
                file_path = os.path.join(folder_path, image_name)
                download_image(icon_url, file_path)
                print(f"Downloaded icon: {file_path}")
            else:
                print(f"No icon found for {game['Title']}.")

if __name__ == "__main__":
    scrape_and_download()
