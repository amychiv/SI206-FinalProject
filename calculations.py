import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from bs4 import BeautifulSoup
import re
import os
import sqlite3
import json
import csv
import matplotlib.pyplot as plt
import pandas as pd

def get_top_10_artists_ids_and_popularity(cur, conn):
    '''Takes in cur and conn, and returns a list of the 10 highest average popularities. 
    Selects all of the artist_ids from the Spotify_Data table and then loops through these ids in order to get the popularity of each of the artist's songs. 
    The popularities are then averaged for each artist, appended to a list, and sorted in descending order.'''
    cur.execute("SELECT artist_id FROM Spotify_Data")
    ids = cur.fetchall()
    popularities = []
    averages = []
    for tup in ids:
        cur.execute("SELECT popularity FROM Spotify_Data WHERE artist_id = " + str(tup[0])) 
        popularity = cur.fetchall()
        if (tup[0], popularity) not in popularities:
            popularities.append((tup[0], popularity))
    for item in popularities:
        total = 0
        for pop in item[1]:
            total += pop[0]
        avg = total / len(item[1])
        averages.append((item[0], avg))
    sorted_averages = sorted(averages, key = lambda x:x[1], reverse = True)
    return sorted_averages[0:10]
        
def get_top_track(artist_id, cur, conn):
    '''Takes in artist_id, cur, conn, and returns a tuple of the artist_id and the corresponding artist's top track.'''
    cur.execute("SELECT track_name, popularity FROM Spotify_Data WHERE artist_id = " + str(artist_id))
    tracks = cur.fetchall()
    sorted_tracks = sorted(tracks, key = lambda x:x[1], reverse = True)
    return (artist_id, sorted_tracks[0][0])

def join_artists(tup, cur, conn):
    cur.execute(f"SELECT Spotify_Artists.artist_name FROM Spotify_Artists JOIN Spotify_Data ON Spotify_Data.artist_id = Spotify_Artists.artist_id WHERE Spotify_Data.artist_id = '{str(tup[0])}' AND Spotify_Data.track_name = '{tup[1]}'")
    artists = cur.fetchall()
    return (artists[0][0], tup[1])

def compare_with_itunes(l2, cur, conn):
    cur.execute("SELECT itunes_track_name FROM iTunes")
    songs = cur.fetchall()
    count = 0
    common_list = []
    for i in range(len(songs)):
        for item in l2:
            if "(feat." in item[1] and songs[i][0][:4] == item[1][:4]:
                count+= 1
                common_list.append(songs[i][0])
            elif songs[i][0] == item[1]:
                count += 1
                common_list.append(songs[i][0])
    return common_list

def get_top_10_artist_names_and_pop(l, cur, conn):
    names = []
    for tup in l:
        cur.execute(f"SELECT Spotify_Artists.artist_name FROM Spotify_Artists JOIN Spotify_Data ON Spotify_Data.artist_id = Spotify_Artists.artist_id WHERE Spotify_Data.artist_id = '{str(tup[0])}'")
        name = cur.fetchone()
        names.append((name[0], tup[1]))
    return names

def get_itunes_songs_and_artists(l, cur, conn):
    info = []
    for item in l:
        cur.execute(f"SELECT iTunes_artists.artist_name FROM iTunes_artists JOIN iTunes ON iTunes.artist_id = iTunes_artists.artist_id WHERE iTunes.itunes_track_name = '{str(item)}'")
        artists = cur.fetchone()
        info.append((item, artists[0]))
    return info


def itunes_csv_out(l, file_name, cur, conn):
    with open(file_name, "w", newline="") as fileout:
        title = fileout.write("SONGS THAT APPEAR IN BOTH SPOTIFY AND ITUNES SEARCHES\n")
        header = fileout.write("Song Name,Artist Name\n")
        writer = csv.writer(fileout)
        info = get_itunes_songs_and_artists(l, cur, conn)
        for item in info:
            row = item
            writer.writerow(row)
        count = len(info)
        line = fileout.write("Number of songs that appear in both: " + str(count))



def csv_out(l, file_name, cur, conn):
     with open(file_name, "w", newline="") as fileout:
        title = fileout.write("TOP TEN TIKTOK ARTISTS AND AVERAGE POPULARITY ON SPOTIFY\n")
        header = fileout.write("Artist Name,Average Popularity\n")
        writer = csv.writer(fileout)
        info = get_top_10_artist_names_and_pop(l, cur, conn)
        for item in info:
            row = item
            writer.writerow(row)

def bar_chart_visualization(l, cur, conn):
    fig = plt.figure(figsize=(80,5))
    ax1 = fig.add_subplot(111)
    artists = []
    average_pop = []
    info = get_top_10_artist_names_and_pop(l, cur, conn)
    for item in info:
        artists.append(item[0])
        average_pop.append(item[1])
    plt.xlabel("Artist Names")
    plt.ylabel("Average Popularity")
    plt.title("TOP 10 TIKTOK ARTISTS AND THEIR AVERAGE POPULARITY ON SPOTIFY")
    plt.xticks(rotation=20)
    plt.xticks(fontsize=8)
    ax1.bar(artists, average_pop)
    plt.show()

def scatterplot_visualization(cur, conn):
    cur.execute("SELECT danceability FROM Spotify_Data")
    danceability = cur.fetchall()
    danceability_list = []
    for item in danceability:
        danceability_list.append(item[0])
    cur.execute("SELECT popularity FROM Spotify_Data")
    popularity = cur.fetchall()
    popularity_list = []
    for pop in popularity:
        popularity_list.append(pop[0])
    cur.execute("SELECT track_name FROM Spotify_Data")
    track_name = cur.fetchall()
    track_list = []
    for track in track_name:
        track_list.append(track[0])
    fig = plt.figure(figsize=(80,5))
    ax1 = fig.add_subplot(111)
    plt.xlabel("Popularity")
    plt.ylabel("Danceability")
    plt.title("Popularity vs. Danceability")
    plt.scatter(popularity_list, danceability_list)
    for i, label in enumerate(track_list):
        ax1.annotate(label, (popularity_list[i], danceability_list[i]), fontsize = 5)
    plt.show()
    x = pd.Series(popularity_list)
    y = pd.Series(danceability_list)
    value = y.corr(x)
    return value


def scatterplot_energy_visualization(cur, conn):
    cur.execute("SELECT energy FROM Spotify_Data")
    energy = cur.fetchall()
    energy_list = []
    for item in energy:
        energy_list.append(item[0])
    cur.execute("SELECT popularity FROM Spotify_Data")
    popularity = cur.fetchall()
    popularity_list = []
    for pop in popularity:
        popularity_list.append(pop[0])
    cur.execute("SELECT track_name FROM Spotify_Data")
    track_name = cur.fetchall()
    track_list = []
    for track in track_name:
        track_list.append(track[0])
    fig = plt.figure(figsize=(80,5))
    ax1 = fig.add_subplot(111)
    plt.xlabel("Popularity")
    plt.ylabel("Energy")
    plt.title("Popularity vs. Energy")
    plt.scatter(popularity_list, energy_list)
    for i, label in enumerate(track_list):
        ax1.annotate(label, (popularity_list[i], energy_list[i]), fontsize = 5)
    plt.show()
    x = pd.Series(popularity_list)
    y = pd.Series(energy_list)
    value = y.corr(x)
    return value

def scatterplot_liveness_visualization(cur, conn):
    cur.execute("SELECT liveness FROM Spotify_Data")
    liveness = cur.fetchall()
    liveness_list = []
    for item in liveness:
        liveness_list.append(item[0])
    cur.execute("SELECT popularity FROM Spotify_Data")
    popularity = cur.fetchall()
    popularity_list = []
    for pop in popularity:
        popularity_list.append(pop[0])
    cur.execute("SELECT track_name FROM Spotify_Data")
    track_name = cur.fetchall()
    track_list = []
    for track in track_name:
        track_list.append(track[0])
    fig = plt.figure(figsize=(80,5))
    ax1 = fig.add_subplot(111)
    plt.xlabel("Popularity")
    plt.ylabel("Liveness")
    plt.title("Popularity vs. Liveness")
    plt.scatter(popularity_list, liveness_list)
    for i, label in enumerate(track_list):
        ax1.annotate(label, (popularity_list[i], liveness_list[i]), fontsize = 5)
    plt.show()
    x = pd.Series(popularity_list)
    y = pd.Series(liveness_list)
    value = y.corr(x)
    return value

def scatterplot_tempo_visualization(cur, conn):
    cur.execute("SELECT tempo FROM Spotify_Data")
    tempo = cur.fetchall()
    tempo_list = []
    for item in tempo:
        tempo_list.append(item[0])
    cur.execute("SELECT popularity FROM Spotify_Data")
    popularity = cur.fetchall()
    popularity_list = []
    for pop in popularity:
        popularity_list.append(pop[0])
    cur.execute("SELECT track_name FROM Spotify_Data")
    track_name = cur.fetchall()
    track_list = []
    for track in track_name:
        track_list.append(track[0])
    fig = plt.figure(figsize=(80,5))
    ax1 = fig.add_subplot(111)
    plt.xlabel("Popularity")
    plt.ylabel("Tempo")
    plt.title("Popularity vs. Tempo")
    plt.scatter(popularity_list, tempo_list)
    for i, label in enumerate(track_list):
        ax1.annotate(label, (popularity_list[i], tempo_list[i]), fontsize = 5)
    plt.show()
    x = pd.Series(popularity_list)
    y = pd.Series(tempo_list)
    value = y.corr(x)
    return value

def write_correlations(filename, cur, conn):
    with open(filename, "w", newline="") as fileout:
        fileout.write("CORRELATION COEFFICIENTS\n")
        dance_value = scatterplot_visualization(cur,conn)
        fileout.write("Popularity vs. Danceability: " + str(dance_value) + "\n")
        energy_value = scatterplot_energy_visualization(cur,conn)
        fileout.write("Popularity vs. Energy: " + str(energy_value) + "\n")
        live_value = scatterplot_liveness_visualization(cur,conn)
        fileout.write("Popularity vs. Liveness: " + str(live_value) + "\n")
        tempo_value = scatterplot_tempo_visualization(cur,conn)
        fileout.write("Popularity vs. Tempo: " + str(tempo_value) + "\n")
    


        

def main():
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/Music.db')
    cur = conn.cursor()
    top_10_artist_ids_and_pop = get_top_10_artists_ids_and_popularity(cur,conn)
    top_10_artists_ids = []
    l2 = []
    for tup in  top_10_artist_ids_and_pop:
        top_10_artists_ids.append(tup[0])
    for id in top_10_artists_ids:
        l2.append(get_top_track(id, cur, conn))
    common_list = compare_with_itunes(l2, cur, conn)
    csv_out(top_10_artist_ids_and_pop, "average_popularity.csv", cur, conn)
    itunes_csv_out(common_list, "common_songs.csv", cur, conn)
    bar_chart_visualization(top_10_artist_ids_and_pop, cur, conn)
    write_correlations("correlations.txt", cur, conn)




if __name__ == "__main__":
    main()
