# LayerOne Demoscene MIDI Parser

This is a command-line MIDI file parser that converts most MIDI files into note arrays for use on the LayerOne Demoscene Board.

## Installation
To use this tool, clone this repo (or just download midiparser.py)

This tool requires the python `midi` library. This can be installed via pip:
```bash
>> pip install python-midi
```

Or manually from [the python-midi github](https://github.com/vishnubob/python-midi)

> I always recommend using a `virtualenv` to contain python project libraries [(Guide)](http://docs.python-guide.org/en/latest/dev/virtualenvs/)

## Basic Usage
### Basic output
To output an array of notes to stdout:
```bash
>> python midiparser.py /path/to/midi/file.mid
__prog__ unsigned short song_ch1f[] __attribute__((space(prog))) = {
1,1,1,E3,E3,E3,Ab3,Ab3,Ab3,Ab3...};
```

### Sample rate
In this context "sample rate" refers to the fidelity of the exported array. By default the tool downsamples the MIDI data so that there is 1 note per "beat" where a "beat" is defined by the MIDI file's resolution. By setting an integer "sample rate" using the `-s` flag sets what fraction of the resolution constitutes a note.

For example, a value of 2 will output one note for every half-beat in the MIDI file.

As you increase this value, the number of notes produced by the same MIDI file increases. I recommend that you set this as low as possible for the quality of music you desire.

I have found that values of 4-16 work well for most files.

```bash
>> ./midiparser.py /path/to/midi/file.mid -s 1
__prog__ unsigned short song_ch1f[] __attribute__((space(prog))) = {
1,1,1,E3,E3,E3,Ab3,Ab3,Ab3,Ab3...};
>> ./midiparser.py /path/to/midi/file.mid -s 2
__prog__ unsigned short song_ch1f[] __attribute__((space(prog))) = {
1,1,1,1,1,1,E3,E3,E3,E3,E3,E3,Ab3,Ab3,Ab3,Ab3,Ab3,Ab3,Ab3,Ab3...};
```

### Saving to a file
To have the data saved to a file use the `-o` flag:
```bash
>> ./midiparser.py /path/to/midi/file.mid -o output_file.h
Output saved to: /path/to/cwd/output_file.h
```

### Including vector data
To include MIDI vector data in addition to notes, use the `-v` flag:
```bash
>> ./midiparser.py /path/to/midi/file.mid -v
__prog__ unsigned short song_ch1f[] __attribute__((space(prog))) = {
1,1,1,E3,E3,E3,Ab3,Ab3,Ab3,Ab3...};

__prog__ unsigned short song_ch1a[] __attribute__((space(prog))) = {
0,0,0,95,95,95,95,95,95,95...};
```
Note: For now, notes and vectors are all MIDI features this parser supports. For most LayerOne Demoscene Board applications, you will only need notes.

### Custom variable prefix
The default output uses the variable name _song_ch_ as the "prefix". To set a custom prefix, use the `-p` flag:
```bash
>> ./midiparser.py /path/to/midi/file.mid -p my_prefix
__prog__ unsigned short my_prefix1f[] __attribute__((space(prog))) = {
1,1,1,E3,E3,E3,Ab3,Ab3,Ab3,Ab3...};
```

## Credits
### Links
* [LayerOne](http://www.layerone.org)
* [L1 Demo Party](http://l1demo.org/)

### People
* [Arko](https://github.com/arkorobotics)

### Inspiration
This project was inspired by [mr1337357](https://github.com/mr1337357) who created a parser for their [2015 Demo](https://github.com/mr1337357/layerone-demo).
