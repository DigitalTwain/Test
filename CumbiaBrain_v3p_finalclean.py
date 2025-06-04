
import os
import random
from mido import Message, MidiFile, MidiTrack, MetaMessage, bpm2tempo

# === CONFIG ===
tempo_bpm = int(random.triangular(80, 110, 95))
ticks_per_beat = 480
steps_per_beat = 4
ticks_per_step = ticks_per_beat // steps_per_beat
steps_per_measure = 16
total_measures = int(random.randint(60, 90) / (60 / tempo_bpm * 4))

# === KEY SETUP ===
scale_types = {
    'major': [0, 2, 4, 5, 7, 9, 11],
    'minor': [0, 2, 3, 5, 7, 8, 10]
}
scale_type = random.choice(['major', 'minor'])
scale_intervals = scale_types[scale_type]
key_root = random.choice(range(48, 60))


def enforce_scale(note):
    direction = random.choice([-1, 1])
    while (note - key_root) % 12 not in scale_intervals:
        note += direction
    return note

# === DRUM PATTERNS & FILLS ===
drum_patterns = [
    [36, None, 70, 70, 38, None, 70, 70, 36, None, 70, 70, 38, None, 70, 70],
    [56, None, 38, 42, 36, None, 41, 42, 56, None, 38, 42, 36, 42, 41, 42],
    [70, None, 70, 70, 70, None, 70, 70, 70, None, 70, 70, 70, None, 70, 70],
    [36, None, 56, 56, 56, None, 56, 56, 36, None, 56, 56, 56, None, 56, 56],
    [36, None, 42, None, 38, None, 42, None, 36, None, 42, 56, 38, 56, 42, 56],
    [36, None, None, None, 36, None, None, None, 36, None, None, None, 36, None, None, None]
]

fill_pool = [
    [38, 38, 38, 38],
    [49, 42, 56, 56],
    [41, 41, 36, None],
    [49, None, None, None],
    [41, 45, 41, 45],
    [51, 46, 51, 46]
]

def generate_drum_sequence(measures):
    sequence = []
    while len(sequence) < measures:
        block = random.choice(drum_patterns)
        repeat = random.choice([2, 4])
        for _ in range(repeat):
            new_block = block.copy()
            if random.random() < 0.5:
                fill = random.choice(fill_pool)
                new_block[-4:] = fill
            sequence.append(new_block)
    return sequence[:measures]

drum_sequence = generate_drum_sequence(total_measures)

# === INSTRUMENT POOLS ===
primary_instruments = [21, 28, 1, 65, 81, 19]
support_instruments = [81, 82, 83, 88, 89, 65, 57, 21, 1, 19, 25, 30]
bass_instruments = [33, 38, 39, 5, 1]

# === MOTIF LIBRARY (TRUNCATED EXAMPLE) ===
motif_library = [
    [0, 2, 4, 5, 4, 2, 0, 2, 4, 7, 5, 4, 2, 1, 0, 1],
    [0, 0, 2, 2, 4, 4, 5, 5, 4, 4, 2, 2, 0, 0, -1, -1],
    [0, 3, 5, 7, 5, 3, 0, 2, 4, 6, 4, 2, 0, -2, -4, -5],
    [0, 1, 0, 2, 3, 2, 4, 5, 4, 5, 4, 2, 3, 2, 1, 0]
] * 10  # 40 motifs (for simplicity)

# === OUTPUT FILE ===
output_folder = "cumbia_output"
os.makedirs(output_folder, exist_ok=True)
existing = [f for f in os.listdir(output_folder) if f.startswith("cumbia_song_") and f.endswith(".mid")]
existing_numbers = [int(f.split("_")[-1].split(".")[0]) for f in existing if f.split("_")[-1].split(".")[0].isdigit()]
next_number = max(existing_numbers + [0]) + 1
output_file = os.path.join(output_folder, f"cumbia_song_{next_number:03}.mid")

# === MIDI FILE ===
mid = MidiFile(ticks_per_beat=ticks_per_beat)
meta = MidiTrack()
meta.append(MetaMessage('set_tempo', tempo=bpm2tempo(tempo_bpm)))
meta.append(MetaMessage('time_signature', numerator=4, denominator=4))
mid.tracks.append(meta)

# === MOTIF STRUCTURE ===
# Select 3–10 motifs from the global library, weighted towards 5
motif_count = random.choices(list(range(3, 11)), weights=[1, 3, 6, 8, 6, 4, 2, 1])[0]
chosen_motifs = random.sample(motif_library, k=motif_count)

motif_sequence = []
for i in range(total_measures):
    base_motif = random.choice(chosen_motifs)
    motif_sequence.append(base_motif)

# === TRACK BUILDERS ===
def build_track(channel, instrument, octave, sequence):
    track = MidiTrack()
    track.append(Message('program_change', program=instrument, time=0, channel=channel))
    for m in range(total_measures):
        motif = sequence[m]
        step_cursor = 0
        if channel == 2:
            behavior = random.choice(["parallel", "octave_swap", "double_rhythm", "ambient_pad", "stab_harmony"])
            if behavior == "octave_swap":
                octave_shift = random.choice([-1, 1])
                for s in range(steps_per_measure):
                    degree = motif[s % len(motif)]
                    note = enforce_scale(key_root + degree + (12 * (octave + octave_shift)))
                    track.append(Message('note_on', note=note, velocity=70, time=0, channel=channel))
                    track.append(Message('note_off', note=note, velocity=60, time=ticks_per_step, channel=channel))
            elif behavior == "double_rhythm":
                for s in range(steps_per_measure * 2):
                    degree = motif[(s // 2) % len(motif)]
                    note = enforce_scale(key_root + degree + (12 * octave))
                    track.append(Message('note_on', note=note, velocity=60, time=0, channel=channel))
                    track.append(Message('note_off', note=note, velocity=50, time=ticks_per_step // 2, channel=channel))
            elif behavior == "ambient_pad":
                interval = random.choice([0, 2, 4])
                pad_note = enforce_scale(key_root + scale_intervals[interval] + (12 * octave))
                pad_duration = random.choice([8, 16]) * ticks_per_step
                track.append(Message('note_on', note=pad_note, velocity=42, time=0, channel=channel))
                track.append(Message('note_off', note=pad_note, velocity=35, time=pad_duration, channel=channel))
            elif behavior == "stepping_pad":
                intervals = random.sample([0, 2, 4], 2)
                first_note = enforce_scale(key_root + scale_intervals[intervals[0]] + (12 * octave))
                second_note = enforce_scale(key_root + scale_intervals[intervals[1]] + (12 * octave))
                track.append(Message('note_on', note=first_note, velocity=42, time=0, channel=channel))
                track.append(Message('note_off', note=first_note, velocity=35, time=(ticks_per_step * 8), channel=channel))
                track.append(Message('note_on', note=second_note, velocity=42, time=0, channel=channel))
                track.append(Message('note_off', note=second_note, velocity=35, time=(ticks_per_step * 8), channel=channel))
            elif behavior == "stab_harmony":
                pattern = random.choice([
                    [0, 4, 8, 12], [1, 5, 9, 13], [0, 3, 5, 7, 10, 12]
                ])
                time = 0
                for step in range(steps_per_measure):
                    if step in pattern:
                        degree = motif[step % len(motif)]
                        note = enforce_scale(key_root + degree + (12 * octave))
                        track.append(Message('note_on', note=note, velocity=70, time=time, channel=channel))
                        track.append(Message('note_off', note=note, velocity=60, time=ticks_per_step, channel=channel))
                        time = 0
                    else:
                        time += ticks_per_step
                if time > 0:
                    track.append(Message('note_off', note=0, velocity=0, time=time, channel=channel))
            else:
                for s in range(steps_per_measure):
                    degree = motif[s % len(motif)]
                    note = enforce_scale(key_root + degree + (12 * octave))
                    track.append(Message('note_on', note=note, velocity=75, time=0, channel=channel))
                    track.append(Message('note_off', note=note, velocity=60, time=ticks_per_step, channel=channel))
        elif channel == 1:
            behavior = random.choices(["full", "groove", "simple", "burst"], weights=[50, 20, 15, 15])[0]
            if behavior == "groove":
                beats = [0, 4, 8, 12]
            elif behavior == "burst":
                beats = [0, 8] if random.random() < 0.5 else [0, 8, 12]
            elif behavior == "simple":
                beats = [0]
            else:
                beats = list(range(16))
            support_behaviors = ["ambient_pad", "stepping_pad", "stab_harmony", "octave_swap", "double_rhythm"]
            primary_behavior = random.choices(["rhythm", "support_style"], weights=[60, 40])[0]
            if primary_behavior == "support_style":
                chosen = random.choice(support_behaviors)
                if chosen == "ambient_pad":
                    interval = random.choice([0, 2, 4])
                    pad_note = enforce_scale(key_root + scale_intervals[interval] + (12 * octave))
                    pad_duration = steps_per_measure * ticks_per_step
                    track.append(Message('note_on', note=pad_note, velocity=42, time=0, channel=channel))
                    track.append(Message('note_off', note=pad_note, velocity=35, time=pad_duration, channel=channel))
                    continue
                elif chosen == "stepping_pad":
                    intervals = random.sample([0, 2, 4], 2)
                    first_note = enforce_scale(key_root + scale_intervals[intervals[0]] + (12 * octave))
                    second_note = enforce_scale(key_root + scale_intervals[intervals[1]] + (12 * octave))
                    track.append(Message('note_on', note=first_note, velocity=42, time=0, channel=channel))
                    track.append(Message('note_off', note=first_note, velocity=35, time=(ticks_per_step * 8), channel=channel))
                    track.append(Message('note_on', note=second_note, velocity=42, time=0, channel=channel))
                    track.append(Message('note_off', note=second_note, velocity=35, time=(ticks_per_step * 8), channel=channel))
                    continue
                elif chosen == "stab_harmony":
                    pattern = [0, 4, 8, 12]
                    time = 0
                    for step in range(steps_per_measure):
                        if step in pattern:
                            degree = motif[step % len(motif)]
                            note = enforce_scale(key_root + degree + (12 * octave))
                            track.append(Message('note_on', note=note, velocity=75, time=time, channel=channel))
                            track.append(Message('note_off', note=note, velocity=60, time=ticks_per_step, channel=channel))
                            time = 0
                        else:
                            time += ticks_per_step
                    if time > 0:
                        track.append(Message('note_off', note=0, velocity=0, time=time, channel=channel))
                    continue
                elif chosen == "octave_swap":
                    shift = random.choice([-1, 1])
                    for s in range(steps_per_measure):
                        degree = motif[s % len(motif)]
                        note = enforce_scale(key_root + degree + (12 * (octave + shift)))
                        track.append(Message('note_on', note=note, velocity=80, time=0, channel=channel))
                        track.append(Message('note_off', note=note, velocity=60, time=ticks_per_step, channel=channel))
                    continue
                elif chosen == "double_rhythm":
                    for s in range(steps_per_measure * 2):
                        degree = motif[(s // 2) % len(motif)]
                        note = enforce_scale(key_root + degree + (12 * octave))
                        track.append(Message('note_on', note=note, velocity=70, time=0, channel=channel))
                        track.append(Message('note_off', note=note, velocity=60, time=ticks_per_step // 2, channel=channel))
                    continue
            for beat in beats:
                rest = beat - step_cursor
                if rest > 0:
                    track.append(Message('note_off', note=0, velocity=0, time=rest * ticks_per_step, channel=channel))
                step_cursor = beat
                degree = motif[step_cursor % len(motif)]
                note = enforce_scale(key_root + degree + (12 * octave))
                track.append(Message('note_on', note=note, velocity=80, time=0, channel=channel))
                track.append(Message('note_off', note=note, velocity=60, time=ticks_per_step, channel=channel))
                step_cursor += 1
            remaining = steps_per_measure - step_cursor
            if remaining > 0:
                track.append(Message('note_off', note=0, velocity=0, time=remaining * ticks_per_step, channel=channel))
        else:
            for s in range(steps_per_measure):
                degree = motif[s % len(motif)]
                note = enforce_scale(key_root + degree + (12 * octave))
                track.append(Message('note_on', note=note, velocity=80, time=0, channel=channel))
                track.append(Message('note_off', note=note, velocity=60, time=ticks_per_step, channel=channel))
    return track
    return track
    return track

def build_bass_track(instrument, sequence):
    track = MidiTrack()
    track.append(Message('program_change', program=instrument, time=0, channel=0))
    for m in range(total_measures):
        motif = sequence[m]
        behavior = random.choices(["burst", "dense", "simple", "groove"], weights=[30, 35, 10, 25])[0]
        if behavior == "burst":
            beats = [0, 8] if random.random() < 0.5 else [0, 8, 12]
        elif behavior == "dense":
            beats = list(range(0, 16, 2))
        elif behavior == "groove":
            beats = [0, 4, 8, 12]
        else:
            beats = [0]

        step_cursor = 0
        for beat in beats:
            rest = beat - step_cursor
            if rest > 0:
                track.append(Message('note_off', note=0, velocity=0, time=rest * ticks_per_step, channel=0))
            step_cursor = beat
            degree = motif[step_cursor % len(motif)]
            note = enforce_scale(key_root + degree - 12)
            track.append(Message('note_on', note=note, velocity=90, time=0, channel=0))
            track.append(Message('note_off', note=note, velocity=60, time=ticks_per_step, channel=0))
            step_cursor += 1
        remaining = steps_per_measure - step_cursor
        if remaining > 0:
            track.append(Message('note_off', note=0, velocity=0, time=remaining * ticks_per_step, channel=0))
    return track

def build_drum_track():
    track = MidiTrack()
    for pattern in drum_sequence:
        time = 0
        for note in pattern:
            if note:
                track.append(Message('note_on', note=note, velocity=100, time=time, channel=9))
                track.append(Message('note_off', note=note, velocity=80, time=ticks_per_step, channel=9))
                time = 0
            else:
                time += ticks_per_step
        if time > 0:
            track.append(Message('note_off', note=0, velocity=0, time=time, channel=9))
    return track

bass = build_bass_track(random.choice(bass_instruments), motif_sequence)
primary = build_track(1, random.choice(primary_instruments), 1, motif_sequence)
support = build_track(2, random.choice(support_instruments), 1, motif_sequence)
drums = build_drum_track()

mid.tracks.extend([bass, primary, support, drums])
mid.save(output_file)
print(f"✅ MIDI saved: {output_file}")
