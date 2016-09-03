# Lyric Selector


## Overview

This is a tool to aid inspiration. Running the script will return a single song lyric randomly selected from a database that you build. To build the database, simply enter a song name and artist name, and lyric_selector will retrieve the lyrics online and confirm with you that they are correct. See "Usage" for details.

## Installation

1. Clone or download this repo
2. `cd lyric_selector`
3. `pip install -r requirements.txt`

## Usage
#### Main command
* `python lyric_selector.py`
	* Prints a single song lyric from your database, along with artist name. It will then ask if you would like more context. Enter `y` to see the surrounding lines of the song, or `n` to exit the program.

#### Options
* `--input`
	* For entering song lyrics into the database. It will prompt you for the song name and artist name, then will try to retrieve them from either songLyrics.com or metroLyrics.com. If it finds lyrics, it will show a preview and confirm that they are correct before adding.
* `--songlist`
	* Displays a list of all songs and artists currently in your database. Organized in alphabetical order by artist.
* `--url <url>`
	* For explicit entry of a URL. Only supports songLyrics.com or metroLyrics.com URLs at this time. This can be used in case the lyrics exist at one of these two sites, but were not found by the program using the `--input` flag.

## Compatibility
Compatible with Python versions 2.7 and up.

