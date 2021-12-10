import requests
import json
from bs4 import BeautifulSoup
import re
import sqlite3
import os

def itunes_search(searchterm):   
    base_url = "https://itunes.apple.com/search"
    response = requests.get(base_url, params = {"term": searchterm, "media": "music", "entity": "musicTrack", "limit": 25})
    data = json.loads(response.text)
    return data["results"]

def get_all_artists():
    lines_list = []
    full_path = os.path.join(os.path.dirname(__file__), 'tiktok_songs.html')
    with open(full_path) as f:
        content = f.read()
        soup = BeautifulSoup(content, 'html.parser')
        name = soup.find()
        container = soup.find('div', class_="article-body-content standard-body-content")
        lines = container.find_all('h4',class_="body-h4")
        regex = "(?:by |— |- |—)(.+)"
        for line in lines:
            name = line.text
            match = re.findall(regex, name)
            name = match[0].strip()
            if name not in lines_list:
                lines_list.append(name)
    return lines_list

def get_artists_cleaned(l):
    regex= '(.+)(?:\s+ft\..+)'
    artists = []
    for line in l:
        if "ft." not in line:
            artists.append(line)
        else:
            match = re.findall(regex, line)
            for word in match:
                artists.append(word)
    artists.remove('5ifty3')
    return artists

def get_top_5_tracks(artist):
    results = itunes_search(artist)
    tracks = []
    names = []
    rank = 0
    for d in results:
        if d['trackName'].upper() not in names:
            rank += 1
            names.append(d['trackName'].upper())
            tracks.append((d['trackName'], artist, rank))
    return tracks[:5]

def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def set_up_itunes_table(artist_list, cur, conn):
    cur.execute("CREATE TABLE IF NOT EXISTS iTunes (track_name TEXT, artist_id INTEGER, search_rank INTEGER)")
    cur.execute("SELECT COUNT(track_name) From iTunes")
    count = cur.fetchone()[0] // 25 * 5
    for artist in artist_list[count: count + 5]:
        tracks = get_top_5_tracks(artist)
        artist_id = 0
        for track in tracks:
            track_name = track[0]
            rank = track[2]
            cur.execute("SELECT artist_id, artist_name FROM iTunes_artists")
            artist_ids = cur.fetchall()
            for tup in artist_ids:
                if tup[1] == artist:
                    artist_id = tup[0]
                    cur.execute("INSERT INTO iTunes (track_name, artist_id, search_rank) VALUES (?, ?, ?)", (track_name, int(artist_id), rank, ))
    print('done')
    conn.commit()



def set_up_itunes_artist_table(artist_list, cur, conn):
    cur.execute("CREATE TABLE IF NOT EXISTS iTunes_artists (artist_id INTEGER, artist_name TEXT UNIQUE)")
    artist_id = 0
    for artist in artist_list:
        artist_id += 1
        cur.execute('INSERT OR IGNORE INTO iTunes_artists (artist_id, artist_name) VALUES (?, ?)', (artist_id, artist, ))
    conn.commit()

def main():
    artist_list = get_artists_cleaned(get_all_artists())
    cur, conn = setUpDatabase('itunes.db')
    set_up_itunes_artist_table(artist_list, cur, conn)
    set_up_itunes_table(artist_list, cur, conn)

if __name__ == "__main__":
    main()