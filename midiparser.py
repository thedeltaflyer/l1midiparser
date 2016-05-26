#!/usr/bin/env python
# -*- coding: utf-8 -*-
# --------------------------------------- #
#    File name: midiparser.py
#    Author: David Khudaverdyan
#    Date created: 5/22/2016
#    Date last modified: 5/26/2016
#    Python Version: 2.7
# --------------------------------------- #

import midi
import argparse
from os import path
from collections import Counter

__author__ = "David Khudaverdyan"
__copyright__ = "Copyright 2016, David Khudaverdyan"
__credits__ = ["David Khudaverdyan", "Ara Kourchians"]
__license__ = "MIT"
__version__ = "1.0"


class MidiHandler(object):
    def __init__(self, file_path, sample_rate=1, include_pauses=True):
        """MidiHandler
        Handles the conversion from midi to timelines/tracks

        :param file_path: Path to the midi file
        :param sample_rate: sample rate to use for down-sampling (fraction of resolution)
        :param include_pauses: Whether pauses should be included in the generation
        """
        self._midi_file = midi.read_midifile(file_path)
        self.midi_resolution = self._midi_file.resolution  # This is ticks per beat
        self.sample_rate = sample_rate
        self.beat_resolution = self.midi_resolution / self.sample_rate
        self.include_pauses = include_pauses
        self.timelines = []
        self.tracks = []
        self._create_timeline()
        self._convert()

    def _create_timeline(self):
        """_create_timeline
        Generates a timeline of all ticks for all midi tracks

        :return: None
        """
        for track in self._midi_file:
            track_timeline = []
            queued_note = None
            for event in track:
                if isinstance(event, midi.events.NoteOnEvent):
                    queued_note = MidiNote(event.pitch, event.velocity)
                    for tick in range(event.tick):
                        # This is a pause, play no notes!
                        track_timeline.append(MidiNote())
                elif isinstance(event, midi.events.NoteOffEvent):
                    for tick in range(event.tick):
                        track_timeline.append(queued_note or MidiNote())
            if len(track_timeline) > 0:
                self.timelines.append(track_timeline)

    def _convert(self):
        """_convert
        Converts the full timelines into down-sampled tracks

        :return: None
        """
        for timeline in self.timelines:
            track = []
            timeline_length = len(timeline)
            num_beats = timeline_length / self.beat_resolution
            for beat in range(num_beats):
                beat_start = beat * self.beat_resolution
                beat_end = (beat + 1) * self.beat_resolution
                sub_timeline = timeline[beat_start:beat_end]
                winning_note = Counter(sub_timeline).most_common(1)[0][0]
                track.append(winning_note)
            self.tracks.append(track)

    def get_timelines(self):
        """get_timelines
        Generates a list of timelines with notes represented as dictionaries

        :return: A list of lists with timeline dictionaries
        """
        my_timelines = []
        for timeline in self.timelines:
            my_timelines.append({
                "notes": [note.read_note() for note in timeline],
                "velocities": [note.read_velocity() for note in timeline]
            })
        return my_timelines

    def num_tracks(self):
        """num_tracks

        :return: The number of non-empty tracks
        """
        return len(self.tracks)

    def get_tracks(self):
        """get_tracks
        Generates a list of tracks with notes represented as dictionaries

        :return: A list of lists with timeline dictionaries
        """
        my_tracks = []
        for track in self.tracks:
            my_tracks.append({
                "notes": [note.read_note() for note in track],
                "velocities": [note.read_velocity() for note in track]
            })
        return my_tracks

    def get_notes(self, track):
        """get_notes

        :param track: The index of the desired track
        :return: A list of notes (str)
        """
        return [note.read_note() for note in self.tracks[track]]

    def get_velocities(self, track):
        """get_velocities

        :param track: The index of the desired track
        :return: A list of velocities (int)
        """
        return [note.read_velocity() for note in self.tracks[track]]


class MidiNote(object):
    def __init__(self, value=None, velocity=0):
        """MidiNote
        This object contains midi note values and converts them to the desired array values.

        :param value: The midi note value
        :param velocity: The midi velocity
        """
        self.valid_notes = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
        if value is None:
            self.note = "1"
            self.level = ""
        else:
            self.note = self.valid_notes[value % len(self.valid_notes)]
            self.level = str(value / len(self.valid_notes))
        self.velocity = velocity

    def __eq__(self, other):
        return self.note == other.note and self.velocity == other.velocity

    def read_note(self):
        """read_note

        :return: The array value of the note (str)
        """
        return "%s%s" % (self.note, self.level)

    def read_velocity(self):
        """read_velocity

        :return: The velocity of the note (int)
        """
        return self.velocity


def main():
    parser = argparse.ArgumentParser(
        description="This utility converts midi files to the format expected by the LayerOne Demo Board")
    parser.add_argument('midi_file',
                        metavar='MIDI_File',
                        help='The MIDI file to convert')
    parser.add_argument('-s', '--sample_rate',
                        type=int,
                        default=1,
                        metavar='SAMPLE_RATE',
                        help='An integer that represents what fraction of the resolution to sample')
    parser.add_argument('-v', '--velocity',
                        action='store_true',
                        default=False,
                        help='Include velocity in output')
    parser.add_argument('-o', '--output',
                        metavar='OUTPUT_FILE',
                        help='Output to the specified file instead of stdout')
    parser.add_argument('-p', '--prefix',
                        metavar='PREFIX',
                        default='song_ch',
                        help='Specify a prefix for the short name. Default is "song_ch"')
    args = parser.parse_args()

    if not path.isfile(args.midi_file):
        parser.error("There is no file at '%s'" % path.abspath(args.midi_file))

    my_handler = MidiHandler(args.midi_file, args.sample_rate)

    full_output = []

    for i, track in enumerate(my_handler.get_tracks()):
        output = "__prog__ unsigned short %s%if[] __attribute__((space(prog))) = {\n%s\n};\n" % (
            args.prefix, i + 1, ",".join(track["notes"]))
        if args.velocity:
            output += "\n__prog__ unsigned short %s%ia[] __attribute__((space(prog))) = {\n%s\n};\n" % (
                args.prefix, i + 1, ",".join(["%i" % velocity for velocity in track["velocities"]]))
        full_output.append(output)

    if args.output:
        output_path = path.abspath(args.output)
        with open(output_path, 'w') as f:
            f.write("\n".join(full_output))
        print "Output saved to: %s" % output_path
    else:
        print("\n".join(full_output))


if __name__ == "__main__":
    main()
