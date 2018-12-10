# Python Utilities for Drums Transcription

This repository offers some tools to facilitate music transcription, especially drums transcription. Since most of the sites for song tabs are guitar-oriented, drums tabs (if available) are often poorly written and/or unreadable. This project looks to transform drums tabs to a standard format that maximizes readability by tackling the following issues:

- [x] Removal of unnecessary rests
- [x] Standardization of score format
- [ ] Merge of multiple drum tracks into a single one

This version does not alter the notes, except for their duration, unless there are parts that can not be played (e.g. hit two crash cymbals and a snare simultaneously), where some notes are prioritized against others.

## Requirements
* Python 2 or 3 (tested with 3.5)
* pyguitarpro (install with pip)

## Examples:

* Run
```
python3 clear_percussion_tracks.py --input_file="examples/Scorpions - Alien Nation Drum.gp4" --output_file="examples/Alien Nation.gp5"
```
to clean useless rests.

* Run
```
python3 standardize_percussion_tracks.py --input_file="examples/Alien Nation.gp5" --output_file="examples/Alien Nation.gp5"
```
to transform the scores into a standardized format that increases readability and ensures all notes are ergonomically possible to play.
