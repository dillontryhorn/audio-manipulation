import os
import sys
import subprocess

def midi_to_wav(midi_file, wav_file):
    """Convert MIDI file to WAV using FluidSynth command line."""
    command = [
        "fluidsynth",
        "-F", wav_file,  # Output WAV file
        midi_file,       # Input MIDI file
    ]
    subprocess.run(command)
    print(f"Converted {midi_file} to {wav_file}")

def wav_to_mp3(wav_file, mp3_file):
    """Convert WAV file to MP3 using pydub."""
    from pydub import AudioSegment
    audio = AudioSegment.from_wav(wav_file)
    audio.export(mp3_file, format="mp3")
    print(f"Converted {wav_file} to {mp3_file}")

def midi_to_mp3(midi_file, mp3_file):
    """Convert MIDI file directly to MP3 by first converting to WAV."""
    wav_file = midi_file.replace('.midi', '.wav').replace('.mid', '.wav')
    midi_to_wav(midi_file, wav_file)
    wav_to_mp3(wav_file, mp3_file)
    os.remove(wav_file)  # Cleanup the temporary WAV file
    print(f"Conversion complete: {mp3_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python MIDI_to_mp3.py <input_file.mid> [output_file.mp3]")
        sys.exit(1)

    midi_file = sys.argv[1]
    mp3_file = sys.argv[2] if len(sys.argv) > 2 else "out.mp3"

    if not os.path.exists(midi_file):
        print(f"Error: File not found - {midi_file}")
        sys.exit(1)

    midi_to_mp3(midi_file, mp3_file)
