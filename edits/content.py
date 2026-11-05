"""Everything this film says and shows: the song, the shots, their timing in beats, the words on screen.

Durations are in beats of the music (110 BPM, one beat = 0.545 s), so every cut lands on the beat. 46 beats = 25 s.

A shot: clip (a blurred working copy), start (first frame), beats, speed (1 = real time; a list of (beat, speed) ramps it),
turn (quarter turns clockwise, for clips filmed from above whose rotation tag came out wrong), zoom (start, end),
center (x, y as fractions of the frame) or pan ((x0, y0), (x1, y1)), steady (how hard to smooth the camera's shake),
dim (0 bright .. 1 low-key), punch (a small push on the cut), whip (the shot arrives on a whip pan, 1 or -1 for the
direction).
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "source" / "2026-11-04_raw"

# "Cinematic Corporate" by alex-morgan (Pixabay). Its chords run Gm Eb Bb F, four beats each. It builds under the opening,
# the band comes in on film beat 8, stops dead at 20 (the song's own break), and comes back on 22 at a later F bar, the
# chord that would have come next anyway, then plays straight through to the song's real ending.
MUSIC = {
    "file": "cinematic_corporate_alexmorgan_556231.mp3",
    "bpm": 110.02,
    "first_beat": 0.0,
    # (first film beat, first song beat, how many beats)
    "parts": [(0, 32, 20), (20, 74, 2), (22, 96, 24)],
    "lifts": [8, 22],
}

HOOK = {"ask": ["“What did you do", "at daycare today?”"], "answer": "“Nothing.”",
        "card": ["Here's what", "nothing", "looks like."]}

SHOTS = [
    # the question, over the quietest shot: a hand and a brush
    dict(key="ask", clip="IMG_8582", start=0, beats=3, speed=0.68, zoom=(1.2, 1.12), center=(0.44, 0.42), dim=0.55, steady=6),
    # the answer: a boy in a police costume turns round and looks straight at the camera
    dict(key="answer", clip="IMG_8589", start=58, beats=2, speed=0.9, zoom=(1.5, 1.42), center=(0.6, 0.66), dim=0.4, steady=8,
         whip=1),
    dict(key="card", kind="card", beats=3),
    # the band comes in, the camera rises off the table to show the whole room at work
    dict(key="crane", clip="IMG_8666", start=12, beats=3, speed=1.04, turn=2, zoom=(1.0, 1.0), center=(0.52, 0.5), punch=0.05),
    dict(key="hands", clip="IMG_8687", start=22, beats=2, speed=1.0, zoom=(1.3, 1.22), center=(0.56, 0.62), steady=8, whip=1),
    dict(key="build", clip="IMG_8690", start=8, beats=2, speed=0.9, zoom=(1.18, 1.08), center=(0.46, 0.5), steady=8, whip=-1),
    dict(key="hero", clip="IMG_8691", start=10, beats=3, speed=0.82, zoom=(1.04, 1.12), pan=((0.51, 0.6), (0.36, 0.6)), steady=10, whip=1),
    dict(key="fist", clip="IMG_8694", start=70, beats=2, speed=1.0, zoom=(1.38, 1.42), pan=((0.225, 1.0), (0.34, 1.0)), steady=8, whip=-1),  # framed low: names are on the wall above
    # the song stops: the last frame holds while paint spreads across it
    dict(key="breath", kind="hold", beats=2, of="fist"),
    # it comes back bigger, straight down onto the paint table
    dict(key="slide", clip="IMG_8583", start=0, beats=3, speed=1.1, zoom=(1.08, 1.08), center=(0.5, 0.5), punch=0.06, steady=8),
    dict(key="brush", clip="IMG_8586", start=18, beats=2, speed=1.0, zoom=(1.28, 1.2), center=(0.48, 0.42), steady=8, whip=1),
    dict(key="art", clip="IMG_8592", start=20, beats=2, speed=0.85, zoom=(1.16, 1.24), center=(0.55, 0.42), steady=10, whip=-1),
    dict(key="table", clip="IMG_8588", start=0, beats=1, speed=1.0, zoom=(1.14, 1.08), center=(0.5, 0.6), steady=6, whip=1),
    # the whole room, the window, the point
    dict(key="room", kind="photo", photo="IMG_8597", beats=4, zoom=(1.36, 1.3), pan=((0.54, 0.62), (0.54, 0.39))),
    dict(key="end", kind="end", beats=12),
]

CHAPTERS = {
    "crane": {"kicker": "MARSHMALLOW TOWERS", "real": "Engineering.", "beats": 5.0},
    "slide": {"kicker": "WASHABLE PAINT", "real": "Fine art.", "beats": 5.0},
}

# (shot it starts in, beat within that shot, text)
PILLS = [
    ("hero", 0.2, "FINE MOTOR SKILLS"),
    ("hero", 1.2, "PROBLEM SOLVING"),
    ("hero", 2.2, "PATIENCE"),
    ("art", 0.1, "COLOUR"),
    ("art", 0.7, "FOCUS"),
    ("art", 1.3, "SELF-EXPRESSION"),
]

BREATH = "Then, the paint."
ROOM = ["Nothing.", "Just growing up."]

END = {
    "line1": "Little stars today,",
    "line2": "bright futures tomorrow.",
    "pill": "NOW ENROLLING",
    "rows": [("phone", "(780) 230-1599"), ("pin", "10629 West Side Drive, Grande Prairie"), ("globe", "tinystars.ca  ·  @tinystarsgp")],
    "hit": 8,  # beats into the closing card: the song's last hit
}
