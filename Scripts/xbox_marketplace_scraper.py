import os
import json
import requests
import time
from bs4 import BeautifulSoup

# Retry mechanism parameters
retry_delay = 5  # seconds

def download_image(url, target_path):
    max_retries = 5
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
            })
            if response.status_code != 200:
                raise requests.exceptions.RequestException(f"Failed to fetch image. Status code: {response.status_code}")
                
            with open(target_path, 'wb') as f:
                f.write(response.content)
            break
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed for titleid: {titleid}. Error: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)  # Wait before retrying
            else:
                print(f"Failed to fetch data for titleid: {titleid} after {max_retries} attempts.")   

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

def scrape_and_download():
    max_retries = 5
    # URL of the JSON file containing game data
    json_url = 'https://raw.githubusercontent.com/xenia-manager/xenia-manager-database/main/Database/xbox_marketplace_games.json'
    for attempt in range(max_retries): 
        try:
            response = requests.get(json_url)
            if response.status_code != 200:
                raise requests.exceptions.RequestException(f"Failed to fetch image. Status code: {response.status_code}")
                
            game_data = response.json()
            download_and_organize_images(game_data)
        except requests.exceptions.RequestException as e:
                print(f"Attempt {attempt + 1} failed for titleid: {titleid}. Error: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)  # Wait before retrying
                else:
                    print(f"Failed to fetch data for titleid: {titleid} after {max_retries} attempts.")

if __name__ == "__main__":
    scrape_and_download()
