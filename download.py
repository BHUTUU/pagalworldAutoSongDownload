import requests, bs4, os, time, threading, sys
from tqdm import tqdm
sys.stdout.reconfigure(encoding='utf-8')
ENCODED_URL = "aHR0cHM6Ly9wYWFnYWx3b3JsZC5jb20uc2Uv".encode()
import base64
URL = base64.b64decode(ENCODED_URL).decode()
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
BASE_DIR = os.getcwd()
SONG_PATH = os.path.join(BASE_DIR, "songs")
SONG_HTML_PATH = os.path.join(BASE_DIR, "songsHtml")
for path in [SONG_PATH, SONG_HTML_PATH]:
    os.makedirs(path, exist_ok=True)
def this_song_path(filename):
    return os.path.join(SONG_PATH, filename)
def this_song_html_path(filename):
    return os.path.join(SONG_HTML_PATH, filename)
def fetch_main_page():
    """Fetch and save the main website page."""
    try:
        resp = requests.get(URL, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        with open("test.html", "w", encoding="utf-8") as fl:
            fl.write(resp.text)
        return True
    except requests.RequestException as e:
        tqdm.write(f"❌ Failed to fetch main page: {e}")
        return False
def extract_song_links():
    """Extract song links from the main page."""
    soup = bs4.BeautifulSoup(open("test.html", "r", encoding="utf-8"), "html.parser")
    song_links = []
    song_names = []
    for link in soup.find_all('a', href=True):
        href = link.get('href')
        if href.endswith("-mp3-song-download.html"):
            song_links.append(href)
            song_names.append(href.split("/")[-1].replace("-mp3-song-download.html", ".mp3"))
    return list(zip(song_links, song_names))
def fetch_song_page(song_link, song_name):
    """Download and save the HTML page for a specific song."""
    try:
        resp = requests.get(song_link, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        file_path = this_song_html_path(song_name + ".html")
        with open(file_path, "wb") as fl:
            fl.write(resp.content)
        return file_path
    except requests.RequestException as e:
        tqdm.write(f"❌ Failed to fetch song page for {song_name}: {e}")
        return None
def extract_download_link(song_html_path):
    """Extract the 320kbps download link from the song page."""
    try:
        soup = bs4.BeautifulSoup(open(song_html_path, "r", encoding="utf-8"), "html.parser")
        for link in soup.find_all("a", href=True):
            if link['href'].startswith(f"{URL[:-1]}/download"):
                return link['href']
    except Exception as e:
        tqdm.write(f"❌ Error extracting download link: {e}")
    return None
def download_song(song_name, song_url, position):
    """Download the song with progress bar."""
    if os.path.exists(this_song_path(song_name)):
        tqdm.write(f"✅ Skipping {song_name}, already downloaded.")
        return
    try:
        resp = requests.get(song_url, headers=HEADERS, timeout=30, stream=True)
        resp.raise_for_status()
        total_size = int(resp.headers.get('content-length', 0))

        with open(this_song_path(song_name), "wb") as file, tqdm(
            desc=song_name, total=total_size, unit='B', unit_scale=True, unit_divisor=1024,
            position=position, leave=True, dynamic_ncols=True
        ) as bar:
            for chunk in resp.iter_content(1024):
                file.write(chunk)
                bar.update(len(chunk))
        tqdm.write(f"✅ {song_name} downloaded successfully!")
    except requests.RequestException as e:
        tqdm.write(f"❌ Failed to download {song_name}: {e}")
def process_song(song_link, song_name, position):
    """Process song: fetch HTML, extract download link, and download."""
    song_html_path = fetch_song_page(song_link, song_name)
    if not song_html_path:
        return
    song_url = extract_download_link(song_html_path)
    if not song_url:
        tqdm.write(f"❌ Failed to find 320kbps link for {song_name}")
        return
    download_song(song_name, song_url, position)
def main():
    if not fetch_main_page():
        return
    songs = extract_song_links()
    if not songs:
        tqdm.write("⚠️ No songs found.")
        return
    tqdm.write(f"🎶 Found {len(songs)} songs. Starting downloads...")
    threads = []
    for index, (song_link, song_name) in enumerate(songs):
        t = threading.Thread(target=process_song, args=(song_link, song_name, index + 1))
        t.start()
        threads.append(t)
        time.sleep(1)
    for t in threads:
        t.join()
    tqdm.write("🎉 All downloads complete.")
if __name__ == "__main__":
    main()
    try:
        os.remove("test.html")
        for files in os.listdir(SONG_HTML_PATH):
            os.remove(os.path.join(SONG_HTML_PATH, files))
        os.rmdir(SONG_HTML_PATH)
    except Exception as e:
        tqdm.write(f"�� Error cleaning up used Files: {e}")
