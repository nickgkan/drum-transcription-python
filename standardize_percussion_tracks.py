"""
Additional functions for PyGuitarPro.

This function standardizes the way the tabs are written and
handles cases where a tab is ergonomically impossible to play,
e.g. when it demands more than two hands to hit all notes.

The function handles the most commonly used notes:
notation = {
    35: Bass Drum 2
    36: Bass Drum 1
    37: Side Stick/Rimshot
    38: Snare Drum 1
    39: Hand Clap
    40: Snare Drum 2
    41: Low Tom 2
    42: Closed Hi-hat
    43: Low Tom 1
    44: Pedal Hi-hat
    45: Mid Tom 2
    46: Open Hi-hat
    47: Mid Tom 1
    48: High Tom 2
    49: Crash Cymbal 1
    50: High Tom 1
    51: Ride Cymbal 1
    52: Chinese Cymbal
    53: Ride Bell
    54: Tambourine
    55: Splash Cymbal
    56: Cowbell
    57: Crash Cymbal 2
    59: Ride Cymbal 2
}

Basic rules (string enumeration: 1 - 6 starting from top):
    * Keep only 38 as snare drum.
    * Keep only 36 as bass drum.
    * Keep only 51 as ride cymbal.
    * Main cymbal on string 1.
    * Secondary cymbal (if any) on string 2.
    * Snare drum on string 3.
    * Toms on strings 3 and 4.
    * Bass drum on string 5.
    * Pedal hi-hat on string 6.
    * When more than 2 notes are to be played with hands,
        prioritize snare drum, then crash cymbals and then
        cymbal - tom pairs.
"""
import argparse

import guitarpro


TOMS = set([38, 40, 37, 41, 43, 45, 47, 48, 50])
CYMBALS = set([49, 57, 52, 55, 51, 53, 54, 56, 59, 42, 44, 46])
HAND_NOTES = TOMS.union(CYMBALS)


def parse_args():
    """Parse input arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--input_file', dest='input_file', help='Input file name',
        type=str, required=True
    )
    parser.add_argument(
        '--output_file', dest='output_file', help='Output file name',
        type=str, required=True
    )
    return parser.parse_args()


def _simplify_note(note):
    """Unify references to bass drum, snare drum or ride cymbal."""
    if note.value == 35:  # Bass Drum 1 -> Bass Drum 2
        note.value = 36
    elif note.value == 40:  # Snare Drum 2 -> Snare Drum 1
        note.value = 38
    elif note.value == 59:  # Ride Cymbal 2 -> Ride CYmbal 1
        note.value = 51
    return note


def _place_note(note, note_values):
    """Place note on a string depending on other notes' values."""
    if note.value == 36:  # Bass drum on string 5
        note.string = 5
    elif note.value == 38:  # Snare drum on string 3
        note.string = 3
    elif note.value == 44:  # Pedal Hi-hat on string 6
        note.string = 6
    elif note.value == 49:  # Crash Cymbal 1 on string 1
        note.string = 1
    elif note.value in CYMBALS:
        if any(  # Another cymbal occupies string 1
                value in CYMBALS and (value < note.value or value == 49)
                for value in note_values
        ):
            note.string = 2
        else:  # Main cymbal on string 3
            note.string = 1
    elif note.value in TOMS:
        if any(
                value in TOMS and (value < note.value or value == 38)
                for value in note_values
        ):
            note.string = 4  # Another tom occupies string 3
        else:
            note.string = 3  # First tom found for this beat on string 3
    return note


def _trim_note_values(notes):
    """Trim notes so as maximum 2 are played with the hands."""
    note_values = set(note.value for note in notes)
    hand_values = note_values.intersection(HAND_NOTES)
    if len(hand_values) > 2:
        return_values = set()
        if 38 in note_values:  # Snare Drum is prioritized
            return_values.add(38)
        if 49 in note_values:  # Crash Cymbal 1
            return_values.add(49)
        if len(return_values) < 2 and 57 in note_values:  # Crash Cymbal 1
            return_values.add(49)
        while len(return_values) < 2:
            if any(  # Try to append a cymbal
                    value in CYMBALS and value not in return_values
                    for value in note_values
            ):
                return_values.add(next(
                    value
                    for value in note_values
                    if value in CYMBALS and value not in return_values
                ))
            if len(return_values) < 2 and any(  # Try to append a tom
                    value in TOMS and value not in return_values
                    for value in note_values
            ):
                return_values.add(next(
                    value
                    for value in note_values
                    if value in TOMS and value not in return_values
                ))
        return_values = set(return_values)
    else:
        return_values = hand_values
    return_values.update(note_values.difference(HAND_NOTES))
    return [note for note in notes if note.value in return_values]


def standardize_track(track):
    """Standardize tab format and clean unplayable parts."""
    for measure in track.measures:
        for voice in measure.voices:
            for beat in voice.beats:
                if not any(beat.notes):
                    continue
                beat.notes = list({
                    note.value: note
                    for note in [_simplify_note(note) for note in beat.notes]
                }.values())
                beat.notes = _trim_note_values(beat.notes)
                note_values = set(note.value for note in beat.notes)
                beat.notes = [
                    _place_note(note, note_values) for note in beat.notes
                ]
    return track


def standardize(input_filename, output_filename):
    """Read a gp file 'input_filename', write to 'output_filename'."""
    song = guitarpro.parse(input_filename)
    song.tracks = [
        standardize_track(track) if track.isPercussionTrack
        else track
        for track in song.tracks
    ]
    guitarpro.write(song, output_filename)


def main():
    """Score standardization pipeline."""
    args = parse_args()
    standardize(args.input_file, args.output_file)

if __name__ == "__main__":
    main()
