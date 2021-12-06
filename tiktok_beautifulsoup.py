from bs4 import BeautifulSoup
import re

def get_all_artists():
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
    regex= '(.+)(?:\s+ft\..+)'
    artists = []
    for line in l:
        if "ft." not in line:
            artists.append(line)
        else:
            match = re.findall(regex, line)
            for word in match:
                artists.append(word)
    return artists
    
print(get_artists_cleaned(get_all_artists()))
