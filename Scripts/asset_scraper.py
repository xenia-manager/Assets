import time
import os
import sys
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv
import requests

sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables from the .env file
load_dotenv()

# Globals
# List of all of the games
GAMES_LIST = os.getenv('GAMES_LIST_URL')

# URL template - Used for scraping data from Xbox Marketplace
URL_TEMPLATE = "https://raw.githubusercontent.com/xenia-manager/Database/temp-main/Database/Xbox%20Marketplace/{id}/{id}.json"

# Constants for retrying
MAX_RETRIES = 5  # Number of retry attempts
RETRY_DELAY = 5  # Delay in seconds before retrying

# Different image extensions to support when checking if the URL is valid
MIME_TYPE_TO_EXTENSION = {
    'image/jpeg': '.jpg',
    'image/png': '.png',
    'image/bmp': '.bmp',
    'image/webp': '.webp',
    'image/tiff': '.tiff',
    'image/vnd.microsoft.icon': '.ico'
}

# Functions
def fetch_games_list():
    """
    Fetch games list from the provided URL
    """
    games_list = []
    response = requests.get(GAMES_LIST, timeout=30)
    if response.status_code == 200:
        games_list = response.json()
    else:
        print(f"Failed to fetch JSON data from the URL, status code: {response.status_code}")
        games_list = []
    return games_list

def find_image(image_name, search_dir):
    """
    Checks if the image already exists
    """
    # Define the common image formats/extensions you want to check
    image_formats = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp']

    # Loop through all possible formats and check if the image exists
    for fmt in image_formats:
        image_path = os.path.join(search_dir, image_name + fmt)
        if os.path.isfile(image_path):
            return True  # Return the path if the image exists
    return False

# Fallback check for extension of the image
def fallback_with_pil(image_content, image_name):
    """
    Fallback to detect the image format using PIL if MIME type detection fails.
    """
    try:
        image = Image.open(BytesIO(image_content))
        image_format = image.format.lower()  # Convert format to lowercase for consistency
        extension = f'.{image_format}'
        print(f"Using PIL fallback: Detected image format is {image_format}.")
        return extension
    except Exception as e:
        print(f"Failed to detect image format for {image_name} using PIL. Error: {e}")
        return ''  # If detection fails, return an empty extension

def download_image(url, image_name, target_path):
    """
    Function that downloads the iamge to the target path
    """
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'}, timeout=10, verify=False)
            content_type = response.headers.get('Content-Type', '')
            if "image" in content_type:
                extension = MIME_TYPE_TO_EXTENSION.get(content_type, '')
                if not extension:
                    extension = fallback_with_pil(response.content, image_name)

                if not extension:
                    print(f"Skipping saving {image_name} as no valid image format was detected.")
                    break

                with open(target_path + extension, 'wb') as f:
                    f.write(response.content)
            else:
                print(f"Failed to fetch the {image_name}")
            break
        except requests.exceptions.RequestException:
            print(f"Failed to fetch the {image_name}, status code: {response.status_code} (Attempt {attempt}/{MAX_RETRIES})")
            if attempt < MAX_RETRIES - 1:
                print(f'Retrying in {RETRY_DELAY} seconds...')
                time.sleep(RETRY_DELAY)
    return

def save_game_images(game_data):
    """
    Creates directory to store game assets and downloads all of them
    """
    os.makedirs(f'Artwork/{game_data['id']}', exist_ok=True) # Creates a directory for the game
    # Background
    if game_data['artwork']['background'] is not None and not find_image("background", f'Artwork/{game_data['id']}/'):
        download_image(game_data['artwork']['background'], 'background',f'Artwork/{game_data['id']}/background')
    # Banner
    if game_data['artwork']['banner'] is not None and not find_image("banner", f'Artwork/{game_data['id']}/'):
        download_image(game_data['artwork']['banner'], 'banner',f'Artwork/{game_data['id']}/banner')
    # Boxart
    if game_data['artwork']['boxart'] is not None and not find_image("boxart", f'Artwork/{game_data['id']}/'):
        download_image(game_data['artwork']['boxart'], 'boxart',f'Artwork/{game_data['id']}/boxart')
    # Icon
    if game_data['artwork']['icon'] is not None and not find_image("icon", f'Artwork/{game_data['id']}/'):
        download_image(game_data['artwork']['icon'], 'icon',f'Artwork/{game_data['id']}/icon')
    
    # Slideshow/Gallery
    """if game_data['artwork']['gallery'] is not None and len(game_data['artwork']['gallery']) > 0:
        os.makedirs(f'Artwork/{game_data['id']}/Gallery', exist_ok=True) # Creates a directory for the game's slideshow
        for slideshow_image in game_data['artwork']['gallery']:
            if not os.path.exists(f'Artwork/{game_data['id']}/Gallery/{os.path.basename(slideshow_image)}'):
                download_image(slideshow_image, f'{os.path.basename(slideshow_image)}' ,f'Artwork/{game_data['id']}/Gallery/{os.path.splitext(os.path.basename(slideshow_image))[0]}')"""

def scrape_game_data(title_id,url):
    """
    Grabs game data from database (If that specific title ID has .JSON with it)
    """
    for attempt in range(MAX_RETRIES):
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            game_data = response.json()
            return game_data
        elif response.status_code == 404:
            break
        else:
            print(f"Failed to fetch data for titleid: {title_id}, \
                status code: {response.status_code} (Attempt {attempt}/{MAX_RETRIES})")
            if attempt < MAX_RETRIES - 1:  # Avoid sleeping on the last attempt
                print(f"Retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
    return None


if __name__ == "__main__":
    """
    Goes through every game and calls for scraping of detailed game data and saving the image
    """
    games_list = fetch_games_list()
    for game in games_list:
        print(f"Processing {game['title']} ({game['id']})")
        # Main Title ID scrapping data
        url = URL_TEMPLATE.format(id=game['id'])
        game_data = scrape_game_data(game['id'], url)
        if game_data is not None:
            save_game_images(game_data)
            
        # Alternative ID data scrapping (If it has them)
        if game['alternative_id'] is not None and len(game['alternative_id']) > 0:
            print(f"Processing alternative id's for {game['title']}")
            for title_id in game['alternative_id']:
                print(f"Processing ({title_id})")
                url = URL_TEMPLATE.format(id=title_id)
                game_data = scrape_game_data(title_id, url)
                if game_data is not None:
                    save_game_images(game_data)
