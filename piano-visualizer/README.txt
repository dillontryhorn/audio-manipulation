This project converts piano music MIDI files to MP3 files and visualizes them on a virtualized piano

I used conda with python 3.12.9 for this project. I exported my environment to the ../env/ folder. I also generated a requirements.txt if you want to use pip instead. You can run the first command for conda or the second for just pip.
1. conda env create -f conda_environment.yml
OR
2. pip install -r requirements.txt

If you don't already have fluidsynth installed, run the install_fluidsynth.py script. Or run it anyways to verify it's all there. The script also installs a soundfont file needed for converting MIDI to MP3. Then add the "C:\tools\fluidsynth\bin" folder to your local PATH. Here is the proper usage below
python install_fluidsynth.py

Next, execute the MIDI_to_mp3 program, which takes a MIDI file as input and outputs the MP3. Here is some proper usage below.
1. python MIDI_to_mp3.py my_song.mid          # Outputs to out.mp3
OR
2. python MIDI_to_mp3.py my_song.mid custom.mp3  # Outputs to custom.mp3

Finally, to visualize, you just execute the piano_visualizer.py script, providing the MIDI and the MP3. Proper usage below.
python piano_visualizer.py my_song.mid out.mp3

When the visualizer launches, go to "Controls" in the menu bar and select "Start" to start playback. Simply exit when you're finished.

I received the "example_song.mid" file from this YouTube link: https://www.youtube.com/watch?v=ehB2YdMyVV0

Cheers,
Dillon