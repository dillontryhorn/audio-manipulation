import mido
from mido import MidiFile, tick2second
import pygame
import tkinter as tk
from tkinter import Menu
from threading import Thread, Event
import time
import argparse

# Reduce audio latency
pygame.mixer.pre_init(44100, -16, 2, 512)

# --- 1) NOTE MAPPINGS ------------------------------------------------------
note_to_name = {
    21: 'A0', 22: 'A#0', 23: 'B0', 24: 'C1', 25: 'C#1', 26: 'D1', 27: 'D#1', 28: 'E1',
    29: 'F1', 30: 'F#1', 31: 'G1', 32: 'G#1', 33: 'A1', 34: 'A#1', 35: 'B1', 36: 'C2',
    37: 'C#2', 38: 'D2', 39: 'D#2', 40: 'E2', 41: 'F2', 42: 'F#2', 43: 'G2', 44: 'G#2',
    45: 'A2', 46: 'A#2', 47: 'B2', 48: 'C3', 49: 'C#3', 50: 'D3', 51: 'D#3', 52: 'E3',
    53: 'F3', 54: 'F#3', 55: 'G3', 56: 'G#3', 57: 'A3', 58: 'A#3', 59: 'B3', 60: 'C4',
    61: 'C#4', 62: 'D4', 63: 'D#4', 64: 'E4', 65: 'F4', 66: 'F#4', 67: 'G4', 68: 'G#4',
    69: 'A4', 70: 'A#4', 71: 'B4', 72: 'C5', 73: 'C#5', 74: 'D5', 75: 'D#5', 76: 'E5',
    77: 'F5', 78: 'F#5', 79: 'G5', 80: 'G#5', 81: 'A5', 82: 'A#5', 83: 'B5', 84: 'C6',
    85: 'C#6', 86: 'D6', 87: 'D#6', 88: 'E6', 89: 'F6', 90: 'F#6', 91: 'G6', 92: 'G#6',
    93: 'A6', 94: 'A#6', 95: 'B6', 96: 'C7', 97: 'C#7', 98: 'D7', 99: 'D#7', 100: 'E7',
    101: 'F7', 102: 'F#7', 103: 'G7', 104: 'G#7', 105: 'A7', 106: 'A#7', 107: 'B7', 108: 'C8'
}
is_black = {note: ('#' in name) for note, name in note_to_name.items()}

# --- 2) PARSE MIDI WITH TEMPO ----------------------------------------------
def process_midi(midi_path):
    mid = MidiFile(midi_path)
    tempo = 500000  # default µs per beat
    merged = mido.merge_tracks(mid.tracks)
    abs_ticks = 0
    events = []

    first_note_tick = None
    first_note_time = None

    for msg in merged:
        abs_ticks += msg.time
        if msg.type == 'set_tempo':
            tempo = msg.tempo
        elif msg.type == 'note_on' and msg.velocity > 0:
            t = tick2second(abs_ticks, mid.ticks_per_beat, tempo)
            if first_note_time is None:
                first_note_tick = abs_ticks
                first_note_time = t
            events.append(('on', msg.note, t))
        elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
            t = tick2second(abs_ticks, mid.ticks_per_beat, tempo)
            events.append(('off', msg.note, t))

    # Normalize events so first note_on is at t=0
    events = [(a, n, t - first_note_time) for a, n, t in events]
    return events, first_note_time + (first_note_tick/1000)  # seconds delay before first note

# --- 3) DRAW KEYBOARD ON CANVAS --------------------------------------------
def draw_keyboard(canvas, key_w=20, key_h=150):
    white_ids, black_ids = {}, {}
    idx = 0
    # White keys
    for midi in range(21, 109):
        if not is_black[midi]:
            x = idx * key_w
            rid = canvas.create_rectangle(x, 0, x + key_w, key_h,
                                          fill='white', outline='black')
            canvas.create_text(x + key_w/2, key_h - 10,
                               text=note_to_name[midi], font=('Arial', 6))
            white_ids[midi] = rid
            idx += 1
    # Black keys
    idx = 0
    for midi in range(21, 109):
        if not is_black[midi]:
            x = idx * key_w
            if (midi + 1 in is_black) and is_black[midi + 1]:
                bx = x + key_w * 0.75
                br = canvas.create_rectangle(bx, 0, bx + key_w * 0.5, key_h * 0.6,
                                             fill='black', outline='black')
                black_ids[midi + 1] = br
            idx += 1
    return white_ids, black_ids

# --- 4) PLAY AUDIO & VISUALIZE IN SYNC -------------------------------------
def play_and_visualize(events, canvas, white_ids, black_ids, stop_ev, visual_offset, start_time):
    pygame.mixer.music.play()
    for action, note, t in events:
        if stop_ev.is_set():
            break
        target = t + visual_offset
        delay = target - (time.time() - start_time)
        if delay > 0:
            time.sleep(delay)
        rid = black_ids.get(note) if is_black[note] else white_ids.get(note)
        if rid is None:
            continue
        color = 'yellow' if action == 'on' else ('black' if is_black[note] else 'white')
        canvas.itemconfig(rid, fill=color)

# --- 5) MAIN GUI & MENU ----------------------------------------------------
def run_visualizer(midi_path, mp3_path, user_offset):
    events, true_first_note_delay = process_midi(midi_path)
    visual_offset = user_offset + true_first_note_delay

    pygame.mixer.init()
    pygame.mixer.music.load(mp3_path)

    stop_ev = Event()
    thread = None

    root = tk.Tk()
    root.title(f"Piano Visualizer")

    cw, ch = 52 * 20, 150
    canvas = tk.Canvas(root, width=cw, height=ch)
    canvas.pack()

    white_ids, black_ids = draw_keyboard(canvas)

    def start_playback():
        nonlocal thread
        stop_ev.clear()
        pygame.mixer.music.stop()
        pygame.mixer.music.play()
        start_time = time.time()
        thread = Thread(
            target=play_and_visualize,
            args=(events, canvas, white_ids, black_ids, stop_ev, visual_offset, start_time),
            daemon=True
        )
        thread.start()

    def stop_playback():
        stop_ev.set()
        pygame.mixer.music.stop()

        def reset_keys():
            for note, rid in white_ids.items():
                canvas.itemconfig(rid, fill='white')
            for note, rid in black_ids.items():
                canvas.itemconfig(rid, fill='black')

        # Delay key reset slightly to allow thread to exit
        root.after(100, reset_keys)


    def on_close():
        stop_playback()
        root.destroy()

    # Menu
    menubar = Menu(root)
    control_menu = Menu(menubar, tearoff=0)
    control_menu.add_command(label="Start", command=start_playback)
    control_menu.add_command(label="Stop", command=stop_playback)
    menubar.add_cascade(label="Controls", menu=control_menu)
    root.config(menu=menubar)

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()

# --- 6) ENTRY POINT --------------------------------------------------------
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Piano Visualizer")
    parser.add_argument("midi", help="Path to MIDI file")
    parser.add_argument("mp3", help="Path to MP3 file")
    parser.add_argument("--offset", type=float, default=0.0,
                        help="Optional visual offset in seconds if necessary (default: 0.0)") 
    args = parser.parse_args()

    run_visualizer(args.midi, args.mp3, args.offset)
