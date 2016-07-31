import argparse
import sys
import csv
import random

import requests
from bs4 import BeautifulSoup


def main():
    parser = argparse.ArgumentParser(description='Return a random lyric from song database.')
    parser.add_argument('--input', dest='entering_song', nargs='?', const=True, default=False)
    parser.add_argument('--songlist', dest='show_songlist', nargs='?', const=True, default=False)
    parser.add_argument('--url', dest='url', nargs='?', const='', default=None)

    args = parser.parse_args()

    if args.entering_song:
        song_entry()
    elif args.show_songlist:
        list_songs()
    elif args.url is not None:
        url = args.url
        url_song_entry(url)
    else:
        lyric_gen()


def song_entry():
    song_name = raw_input('Song name: ').strip()
    artist_name = raw_input('Artist name: ').strip()

    # Web-scrape for lyrics
    sys.stdout.write('Searching for lyrics...\n')
    lyrics = metrolyrics_search(song_name=song_name, artist_name=artist_name)

    if lyrics is not None:
        try:
            written = write_lyrics_to_file(lyrics, song_name=song_name, artist_name=artist_name, first_try=True)
        except Exception:
            sys.stdout.write('Whoops. Lyrics were found but something went wrong.\n')
            return
        if written:
            return

    lyrics = songlyrics_search(song_name=song_name, artist_name=artist_name)

    if lyrics is not None:
        try:
            written = write_lyrics_to_file(lyrics, song_name=song_name, artist_name=artist_name)
        except Exception:
            sys.stdout.write('Whoops. Lyrics were found but something went wrong.\n')
            return
        if written:
            return


def url_song_entry(url):
    song_name = raw_input('Song name: ').strip()
    artist_name = raw_input('Artist name: ').strip()

    if url == '':
        sys.stdout.write('Please enter a URL after the --url flag.')
        return

    if 'metro' in url:
        lyrics = metrolyrics_search(song_name=song_name, artist_name=artist_name, user_url=url)
    elif 'songlyrics' in url:
        lyrics = songlyrics_search(song_name=song_name, artist_name=artist_name, user_url=url)
    else:
        sys.stdout.write('URL must be from either songLyrics or metroLyrics. Other sites unsupported at this time.\n')
        return

    write_lyrics_to_file(lyrics=lyrics, song_name=song_name, artist_name=artist_name)


def metrolyrics_search(song_name, artist_name, user_url=None):
    # Search on MetroLyrics
    (fixed_song_name, fixed_artist_name) = format_names(song_name=song_name, artist_name=artist_name)

    if user_url is not None:
        url = user_url
    else:
        url = 'http://www.metrolyrics.com/' + fixed_song_name + '-lyrics-' + fixed_artist_name + '.html'

    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")

    text = soup.find('div', {'id' : 'lyrics-body-text'})

    lyrics = None
    if text is not None:
        lyrics = ''
        paragraphs = text.find_all('p')
        for para in paragraphs:
            try:
                stanza = str(para.text)
            except UnicodeEncodeError:
                stanza = para.text.encode('ascii', 'ignore')

            lyrics = lyrics + stanza + '\n'

    return lyrics


def songlyrics_search(artist_name, song_name, user_url=None):
    sys.stdout.write('Trying on SongLyrics now...\n')

    (fixed_artist_name, fixed_song_name) = format_names(song_name=song_name, artist_name=artist_name)

    if user_url is not None:
        url = user_url
    else:
        url = 'http://www.songlyrics.com/' + fixed_artist_name + '/' + fixed_song_name + '-lyrics/'

    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")

    lyrics_section = soup.find('p', {'id' : 'songLyricsDiv'})
    if lyrics_section is None:
        sys.stdout.write('No lyrics were found. Sorry :(\n')
        return None
    else:
        try:
            lyrics = str(lyrics_section.text)
        except UnicodeEncodeError:
            lyrics = lyrics_section.text.encode('ascii', 'ignore')

        if "Sorry, we have no" in lyrics:
            sys.stdout.write('No lyrics were found. Sorry :(\n')
            return None

    return lyrics


def format_names(song_name, artist_name):
    new_song_name = song_name.lower().replace(' ', '-')
    new_artist_name = artist_name.lower().replace(' ', '-')

    fixed_song_name = ''
    fixed_artist_name = ''
    for x in new_artist_name:
        if x.isalpha() or x == '-':
            fixed_artist_name = fixed_artist_name + x
    for y in new_song_name:
        if y.isalpha() or y == '-':
            fixed_song_name = fixed_song_name + y

    fixed_song_name = fixed_song_name.replace('--', '-')
    fixed_artist_name = fixed_artist_name.replace('--', '-')

    return fixed_song_name, fixed_artist_name


def write_lyrics_to_file(lyrics, song_name, artist_name, first_try=False):
    split_lyrics = lyrics.split('\n')

    first_few_lines = split_lyrics[:6]
    sys.stdout.write('\n')
    for line in first_few_lines:
        sys.stdout.write(line + '\n')
    sys.stdout.write('\n' + 'These are the first few lyrics we found.\n')
    response = str(raw_input('Are these correct? (y/n): '))

    if response == 'n':
        if first_try:
            return False
        else:
            sys.stdout.write('Lyrics were not added.\n')
            return False

    sys.stdout.write('\n')

    full_row = [song_name, artist_name]
    for line in split_lyrics:
        if line != '':
            line = line.replace('\n', '')
            full_row.append(line)

    with open('lyrics.txt', 'a') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        writer.writerow(full_row)

    sys.stdout.write('Lyrics added successfully!\n')
    return True


def list_songs():
    with open('lyrics.txt', 'rU') as csvfile:
        reader = csv.reader(csvfile, delimiter = ';')
        songs = []
        for row in reader:
            song = (row[1], row[0])
            songs.append(song)
        songs = sorted(songs, key=lambda song: song[0])
        sys.stdout.write('\n')
        for song in songs:
            sys.stdout.write('Artist: ' + song[0] + ', Song: ' + song[1] + '\n')
    return


def lyric_gen():
    line = ''
    song = ''
    artist = ''
    context = []

    with open('lyrics.txt', 'rU') as csvfile:
        reader = csv.reader(csvfile, delimiter = ';')
        data = list(reader)
        row_count = len(data)
        csvfile.seek(0)

        random_row = random.randint(0, row_count-1)

        counter = 0
        for row in reader:
            if counter != random_row:
                counter += 1
                continue

            total_cols = len(row)
            song = row[0]
            artist = row[1]

            colnum = random.randint(2, total_cols-1)
            line = row[colnum]

            lower = colnum - 2
            upper = colnum + 3
            if lower <= 1:
                lower = 2
            if upper >= total_cols:
                upper = total_cols

            context = row[lower:upper]

            if counter == random_row:
                break

    sys.stdout.write('Lyric: \n')
    sys.stdout.write(line + '\n\n')
    sys.stdout.write('From the song ' + song + '\n')
    sys.stdout.write('By ' + artist + '\n\n')

    response = str(raw_input('Need more context for the line? (y/n): '))
    sys.stdout.write('\n')

    if response == 'y':
        for lyric in context:
            sys.stdout.write(lyric + '\n')
        sys.stdout.write('\n')
        return
    else:
        return


if __name__ == "__main__":
    main()
