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
# the band comes in on film beat 8, stops dead at 24 (the song's own break), and comes back on 26 at a later Gm bar, the
# chord that would have come next anyway, then plays straight through to the song's real ending.
MUSIC = {
    "file": "cinematic_corporate_alexmorgan_556231.mp3",
    "bpm": 110.02,
    "first_beat": 0.0,
    # (first film beat, first song beat, how many beats)
    "parts": [(0, 32, 24), (24, 74, 2), (26, 100, 20)],
    "lifts": [8, 26],
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
    # the band comes in on the materials, then how it's done, step by step, in close-up
    dict(key="mats", clip="IMG_8675", start=18, beats=3, speed=0.85, zoom=(1.05, 1.0), center=(0.76, 0.5), punch=0.05),
    dict(key="poke", clip="IMG_8687", start=34, beats=2, speed=0.8, zoom=(1.6, 1.52), pan=((0.54, 0.74), (0.53, 0.47)), whip=1),
    dict(key="legs", clip="IMG_8690", start=8, beats=2, speed=0.9, zoom=(1.7, 1.62), pan=((0.43, 0.55), (0.41, 0.41)), whip=-1),
    # the payoff: he opens his hand, the tower stays up, and the picture holds on it while the title lands
    dict(key="stand", clip="IMG_8691", start=31, beats=6, speed=[(0, 0.6), (2, 0.45), (3, 0.35), (3.4, 0.02), (6, 0.02)],
         zoom=(1.46, 1.54), pan=((0.335, 0.68), (0.31, 0.68)), whip=1),
    # three plates, three pairs of hands, and no faces in shot
    dict(key="class", clip="IMG_8675", start=0, beats=3, speed=0.6, zoom=(1.04, 1.0), pan=((0.36, 0.5), (0.42, 0.5)), whip=-1),
    # the song stops: the last frame holds while paint spreads across it
    dict(key="breath", kind="hold", beats=2, of="class"),
    # it comes back bigger, straight down onto the paint table
    dict(key="slide", clip="IMG_8583", start=0, beats=2, speed=1.1, zoom=(1.08, 1.08), center=(0.5, 0.5), punch=0.06, steady=8),
    dict(key="art", clip="IMG_8592", start=20, beats=2, speed=0.85, zoom=(1.16, 1.24), center=(0.55, 0.42), steady=10, whip=1),
    dict(key="table", clip="IMG_8588", start=0, beats=1, speed=1.0, zoom=(1.14, 1.08), center=(0.5, 0.6), steady=6, whip=-1),
    # the whole room, the window, the point
    dict(key="room", kind="photo", photo="IMG_8597", beats=4, zoom=(1.36, 1.3), pan=((0.54, 0.62), (0.54, 0.39))),
    dict(key="end", kind="end", beats=11),
]

# at: how many beats into its shot the chapter title starts
CHAPTERS = {
    "stand": {"kicker": "MARSHMALLOW TOWERS", "real": "Engineering.", "at": 3.0, "beats": 3.0},
    "slide": {"kicker": "WASHABLE PAINT", "real": "Fine art.", "at": 0.0, "beats": 4.0},
}

# what's happening, in plain words. b0, b1: the beats within the shot it's on screen; y: where it sits, clear of the action
STEPS = [
    dict(shot="mats", b0=0.2, b1=3.0, y=1330, kick="THE CHALLENGE", lines=["Marshmallows + spaghetti.", "Build a tower."]),
    dict(shot="poke", b0=0.1, b1=2.0, y=1400, kick="STEP 1", lines=["Push the spaghetti in."]),
    dict(shot="legs", b0=0.1, b1=2.0, y=1400, kick="STEP 2", lines=["Add more legs."]),
    dict(shot="stand", b0=0.2, b1=2.9, y=430, kick="STEP 3", lines=["Now let go…"]),
    dict(shot="class", b0=0.1, b1=3.0, y=1240, kick=None, lines=["Every child", "built their own."]),
]

# (shot it starts in, beat within that shot, text, x, y)
PILLS = [
    ("class", 0.3, "FINE MOTOR SKILLS", 540, 1465),
    ("class", 1.1, "PROBLEM SOLVING", 372, 1547),
    ("class", 1.9, "PATIENCE", 810, 1547),
    ("art", 0.1, "COLOUR", 540, 1250),
    ("art", 0.7, "FOCUS", 540, 1332),
    ("art", 1.3, "SELF-EXPRESSION", 540, 1414),
]

BREATH = "Then, the paint."
ROOM = ["Nothing.", "Just growing up."]

END = {
    "line1": "Little stars today,",
    "line2": "bright futures tomorrow.",
    "pill": "NOW ENROLLING",
    "rows": [("phone", "(780) 230-1599"), ("pin", "10629 West Side Drive, Grande Prairie"), ("globe", "tinystars.ca  ·  @tinystarsgp")],
    "hit": 7,  # beats into the closing card: the song's last hit
}
