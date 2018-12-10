"""
Additional functions for PyGuitarPro.

This function clears all percussion tracks, removing rests.
Note that not all rests are removed, but rather those that
are unnecessary.
"""
import argparse

import guitarpro


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


def remove_rests(input_filename, output_filename):
    """Read a gp file 'input_filename', write to 'output_filename'."""
    song = guitarpro.parse(input_filename)
    song.tracks = [
        remove_rests_from_track(track) if track.isPercussionTrack
        else track
        for track in song.tracks
    ]
    guitarpro.write(song, output_filename)


def remove_rests_from_track(track):
    """
    Remove rests from a given percussion track.

    This function also works for other types of tracks as well.
    """
    for measure in track.measures:
        for voice in measure.voices:
            last = None
            newbeats = []
            for beat in voice.beats:
                if beat.notes:
                    last = beat
                    newbeats.append(beat)
                elif last is not None:
                    try:
                        last.duration = guitarpro.Duration.fromTime(
                            last.duration.time + beat.duration.time
                        )
                    except ValueError:
                        last = beat
                        newbeats.append(beat)
                else:
                    newbeats.append(beat)
            voice.beats = newbeats
    return track


def main():
    """Rest removal pipeline."""
    args = parse_args()
    remove_rests(args.input_file, args.output_file)
    remove_rests(args.output_file, args.output_file)

if __name__ == "__main__":
    main()
