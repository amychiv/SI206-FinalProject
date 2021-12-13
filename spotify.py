import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from bs4 import BeautifulSoup
import re
import os
import sqlite3
import json

cid = '2538d38c8fce42bb87ca53261ed1d899'
secret = 'd69ee735e89d4e2ca9097ae108368843'
client_credentials_manager = SpotifyClientCredentials(client_id = cid, client_secret= secret)
sp = spotipy.Spotify(client_credentials_manager
=
client_credentials_manager)

def get_all_artists():
     '''Takes no parameters. Returns list of unique artists from the Seventeen website using BeautifulSoup. Uses regex to ensure only the artist name
    is in the returned list.'''
    lines_list = []
    with open('tiktok_songs.html') as f:
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
    '''Takes in list of artists that get_all_artists() returns. Returns the same list of artists, but without the '(feat. featured_artist)'
    part of the artist name to be used in our search queries.'''
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

def get_track_data(artist_list):
     '''Takes in a list of artists from get_artists_cleaned(). Iterates through each artist in this list and uses the artist name as a search query with the Spotify API. 
     Returns a list of tuples in the format: (track name, track id, artist name, track popularity)'''
    track_data = []
    for artist in artist_list:
        for i in range(0,10,2):
            track_results = sp.search(q='artist:'+ artist, type='track', limit=1,offset=i)
            for i, t in enumerate(track_results['tracks']['items']):
                if "(feat. " in t['name']:
                    beg_name = t['name'].split("(feat. ")
                    name = beg_name[0]
                    if name not in track_data:
                        track_data.append((t['name'], t['id'], t['artists'][0]['name'], t['popularity']))
                    else: 
                        continue
                else: 
                    if t['name'] not in track_data:
                        track_data.append((t['name'], t['id'], t['artists'][0]['name'], t['popularity']))
                    else: 
                        continue
    unique_track_data = []
    for i in range(len(track_data) - 2):
        name = track_data[i][0]
        if name != track_data[i + 1][0] and name != track_data[i + 2][0]:
            unique_track_data.append(track_data[i])
    return unique_track_data


def get_audio_features(track_id):
  
    audio_features = sp.audio_features(track_id)
    danceability = audio_features[0]['danceability']
    energy = audio_features[0]['energy']
    liveness = audio_features[0]['liveness']
    tempo = audio_features[0]['tempo']
    return (danceability, energy, liveness, tempo)


def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def setUpSpotifyTable(artist_list, cur, conn):
    cur.execute("CREATE TABLE IF NOT EXISTS Spotify_Data (track_name TEXT, track_id TEXT, artist_id INTEGER, popularity INTEGER, danceability NUMBER, energy NUMBER, liveness NUMBER, tempo NUMBER)")
    track_data = get_track_data(artist_list)
    cur.execute("SELECT COUNT(*) FROM Spotify_Data")
    count = cur.fetchone()
    for i in range(count[0], count[0] + 25):
        track_name = track_data[i][0]
        track_id = track_data[i][1]
        artist_name = track_data[i][2]
        popularity = track_data[i][3]
        danceability = get_audio_features(track_id)[0]
        energy = get_audio_features(track_id)[1]
        liveness = get_audio_features(track_id)[2]
        tempo = get_audio_features(track_id)[3]
        cur.execute('SELECT artist_id, artist_name FROM Spotify_Artists')
        artist_ids = cur.fetchall()
        for artist_tup in artist_ids:
            if artist_tup[1] == artist_name:
                artist = artist_tup[0]
                cur.execute("INSERT INTO Spotify_Data (track_name, track_id, artist_id, popularity, danceability, energy, liveness, tempo) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (track_name, track_id, int(artist), popularity, danceability, energy, liveness, tempo, ))
    conn.commit()
    print("Done")
    

def setUpArtistTable(artist_list, cur, conn):
    cur.execute("CREATE TABLE IF NOT EXISTS Spotify_Artists (artist_id INTEGER, artist_name TEXT UNIQUE)")
    artist_id = 0
    for artist in artist_list:
        artist_id += 1
        cur.execute("INSERT OR IGNORE INTO Spotify_Artists (artist_id, artist_name) VALUES (?,?)", (artist_id, artist, ))
    conn.commit()



def main():
    '''Takes in no parameters and calls all of the functions above.'''
    artist_cleaned = (get_artists_cleaned(get_all_artists()))
    artist_list = get_all_artists()
    cur, conn = setUpDatabase('Music.db')
    setUpArtistTable(artist_cleaned, cur, conn)
    setUpSpotifyTable(artist_cleaned, cur, conn)
    


if __name__ == "__main__":
    main()



    






