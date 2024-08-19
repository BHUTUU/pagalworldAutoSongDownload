import requests
import bs4
import re, os, time
url = "https://www.pagalworld.com.sb/"
songPath = os.path.join(os.getcwd(), "songs")
songHtml = os.path.join(os.getcwd(), "songsHtml")
for i in [songPath, songHtml]:
    if not os.path.exists(i):
        os.makedirs(i)
thisSongPath = lambda x: os.path.join(songPath, x)
thisSongHtmlPath = lambda x: os.path.join(songHtml, x)
resp = requests.get(url)
fl = open("test.html", "w", encoding="utf-8")
fl.write(resp.text)
fl.close()

soup = bs4.BeautifulSoup(open("test.html"), "html.parser")

# Extracting all the links

links = []
for link in soup.find_all('a'):
    href = link.get('href')
    if href and href.startswith("https://www.pagalworld.com.sb/"):
        links.append(href)
songLinks = []
songNames=[]
for i in links:
    if str(i).endswith("-mp3-song-download.html"):
        songLinks.append(i)
        songNames.append(i.split("/")[-1].replace("-mp3-song-download.html", ".mp3"))
# open the download page:

for i in range(len(songLinks)):
    # print(f"Downloading {songNames[i]}...")
    resp = requests.get(songLinks[i])
    fl = open(thisSongHtmlPath(songNames[i]+".html"), "wb")
    fl.write(resp.content)
    fl.close()
    # Parse the downloaded HTML:
    maxTry = 10
    trycount = 0
    if os.path.exists(thisSongPath(songNames[i])):
        print(f"song: {songNames[i]} : Already downloaded.. skipping..")
        continue
    while True:
        try:
            print(f"Trying to download {songNames[i]}...")
            soup = bs4.BeautifulSoup(open(thisSongHtmlPath(songNames[i]+".html"),encoding="utf-8"), "html.parser")
            stat = True
            break
        except Exception as e:
            print(str(e))
            if trycount == maxTry:
                stat=False
                break
            time.sleep(1)
            trycount += 1
            continue
    if stat is False:
        continue
    song320links = []

    # Extract the download link:
    for link in soup.find_all("a"):
        href = link.get('href')
        if href and href.startswith("https://www.pagalworld.com.bz/dl/"):
            if href.endswith(songNames[i][:-4]+"-mp3-song-download/320"):
                song320links.append(href)
                os.remove(thisSongHtmlPath(songNames[i]+".html"))
    if len(song320links) == 0:
        print(f"Failed to find 320kbps download link for {songNames[i]}!")
        continue
    # Download song final page:
    resp = requests.get(song320links[0])
    print("creating file html")
    fl = open(thisSongHtmlPath(songNames[i]+".html"), "wb")
    fl.write(resp.content)
    fl.close()
    # Parse the downloadlink in downloaded HTML:
    maxTry = 10
    trycount = 0
    while True:
        try:
            soup = bs4.BeautifulSoup(open(thisSongHtmlPath(songNames[i]+".html"), encoding="utf-8"), "html.parser")
            for link in soup.find_all("a"):
                href = link.get('href')
                if href and href.startswith("https://www.pagalworld.com.sb/files/download/type/320/id/"):
                    songLink = href
                    stat=True
                    break
            break
        except Exception as e:
            if trycount == maxTry:
                stat=False
                break
            print(str(e))
            print(f"Failed to find download link for {songNames[i]}!")
            continue
    if stat is False:
        continue
    # Download the song:
    print(f"Downloading {songNames[i]}...")
    resp = requests.get(songLink)
    fl = open(thisSongPath(songNames[i]), "wb")
    fl.write(resp.content)
    fl.close()
    os.remove(thisSongHtmlPath(songNames[i]+".html"))
    time.sleep(5)
    print(f"{songNames[i]} downloaded successfully")
