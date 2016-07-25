import argparse
import sys
import csv
import random

import requests
from bs4 import BeautifulSoup


def main():
    parser = argparse.ArgumentParser(description='Return a random lyric from song database.')
    parser.add_argument('--input', dest='entering_song', nargs='?', const=True, default=False)

    args = parser.parse_args()

    if args.entering_song:
        song_entry()
    else:
        lyric_gen()


def song_entry():
    song_name = raw_input('Song name: ').strip()
    artist_name = raw_input('Artist name: ').strip()

    # Web-scrape for lyrics
    sys.stdout.write('Searching for lyrics...\n')
    songlyrics_search = False

    # Search on MetroLyrics
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

    url = 'http://www.metrolyrics.com/' + fixed_song_name + '-lyrics-' + fixed_artist_name + '.html'
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")

    text = soup.find('div', {'id' : 'lyrics-body-text'})

    if text is not None:
        lyrics = ''
        paragraphs = text.find_all('p')
        for para in paragraphs:
            lyrics = lyrics + str(para.text) + '\n'
        try:
            write_lyrics_to_file(lyrics, song_name=song_name, artist_name=artist_name)
        except Exception:
            sys.stdout.write('Whoops. Lyrics were found but something went wrong.\n')
            return

        sys.stdout.write('Lyrics added successfully!\n')
        return
    else:
        songlyrics_search = True

    if songlyrics_search:
        sys.stdout.write('Trying on SongLyrics now...\n')

        url = 'http://www.songlyrics.com/' + fixed_artist_name + '/' + fixed_song_name + '-lyrics/'
        resp = requests.get(url)
        soup = BeautifulSoup(resp.text, "html.parser")

        lyrics_section = soup.find('p', {'id' : 'songLyricsDiv'})
        if lyrics_section is None:
            sys.stdout.write('No lyrics were found. Sorry :(\n')
            return
        else:
            lyrics = str(lyrics_section.text)
            try:
                write_lyrics_to_file(lyrics, song_name=song_name, artist_name=artist_name)
            except Exception:
                sys.stdout.write('Whoops. Lyrics were found but something went wrong.\n')
                return

            sys.stdout.write('Lyrics added successfully!\n')
            return


def write_lyrics_to_file(lyrics, song_name, artist_name):
    split_lyrics = lyrics.split('\n')
    full_row = [song_name, artist_name]
    for line in split_lyrics:
        if line != '':
            full_row.append(line)

    with open('lyrics.txt', 'a') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        writer.writerow(full_row)


def lyric_gen():
    line = ''
    song = ''
    artist = ''
    context = []

    with open('lyrics.txt', 'r') as file:
        reader = csv.reader(file, delimiter = ';')
        data = list(reader)
        row_count = len(data)
        file.seek(0)

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
                upper = total_cols - 1

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
