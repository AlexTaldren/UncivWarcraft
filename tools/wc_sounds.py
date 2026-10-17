"""Original attack sounds for UncivWarcraft (v0.16), synthesised from scratch in code.

No recorded or sampled audio is used: every sound is built from noise, oscillators,
filters and envelopes, so the results can ship in the public mod. They replace the
modern Unciv attack sounds (machine guns, tank shots, jets, missiles, nukes, modern rifle shots) with
Warcraft-flavoured ones: steam cannons, gyrocopter guns, gnomish mortars, goblin
rockets and bombs, arcane blasts, titan lightning, and the cries of the beasts
(frost wyrm, gryphon, bat, worgen, infernal).

Files are written as <name>.ogg in the mod's sounds/ folder; units refer to them by
name in "attackSound".
"""
import os, subprocess, tempfile, wave
import numpy as np
from scipy import signal

SR = 44100
RNG = np.random.default_rng(1234)          # fixed seed: rebuilds give identical files


# ------------------------------------------------------------------ building blocks
def t(dur):
    return np.arange(int(dur * SR)) / SR


def noise(dur, kind="white"):
    n = RNG.standard_normal(int(dur * SR))
    if kind == "brown":
        n = np.cumsum(n); n -= np.linspace(n[0], n[-1], len(n)); n /= np.abs(n).max() + 1e-9
    elif kind == "pink":
        b, a = [0.049922035, -0.095993537, 0.050612699, -0.004408786], [1, -2.494956002, 2.017265875, -0.522189400]
        n = signal.lfilter(b, a, n)
    return n / (np.abs(n).max() + 1e-9)


def lp(x, f, order=2):
    return signal.sosfilt(signal.butter(order, min(f, SR / 2.1), "low", fs=SR, output="sos"), x)


def hp(x, f, order=2):
    return signal.sosfilt(signal.butter(order, f, "high", fs=SR, output="sos"), x)


def bp(x, lo, hi, order=2):
    return signal.sosfilt(signal.butter(order, [lo, min(hi, SR / 2.1)], "band", fs=SR, output="sos"), x)


def sweep_lp(x, f0, f1, curve=2.0):
    """A low-pass whose cutoff glides from f0 to f1 (block-wise)."""
    out = np.zeros_like(x)
    n = len(x); blk = 512
    zi = None
    for i in range(0, n, blk):
        k = (i / max(1, n - 1)) ** curve
        f = f0 + (f1 - f0) * k
        sos = signal.butter(2, max(40, min(f, SR / 2.1)), "low", fs=SR, output="sos")
        if zi is None:
            zi = signal.sosfilt_zi(sos) * 0
        out[i:i + blk], zi = signal.sosfilt(sos, x[i:i + blk], zi=zi)
    return out


def env(dur, attack=0.003, decay=0.2, curve=4.0, hold=0.0):
    tt = t(dur)
    e = np.where(tt < attack, tt / max(attack, 1e-6), 1.0)
    d = np.clip((tt - attack - hold) / max(decay, 1e-6), 0, None)
    return e * np.exp(-curve * d) * (tt >= 0)


def adsr(dur, a, d, s, r):
    tt = t(dur); e = np.zeros_like(tt)
    e = np.where(tt < a, tt / a, e)
    e = np.where((tt >= a) & (tt < a + d), 1 - (1 - s) * (tt - a) / d, e)
    e = np.where((tt >= a + d) & (tt < dur - r), s, e)
    e = np.where(tt >= dur - r, s * np.clip((dur - tt) / r, 0, 1), e)
    return e


def osc(freq, dur, shape="sine", phase=0.0):
    """freq may be a number or an array (a glide)."""
    n = int(dur * SR)
    f = np.full(n, float(freq)) if np.isscalar(freq) else np.asarray(freq)[:n]
    ph = 2 * np.pi * np.cumsum(f) / SR + phase
    if shape == "sine":
        return np.sin(ph)
    if shape == "saw":
        return 2 * ((ph / (2 * np.pi)) % 1) - 1
    if shape == "square":
        return np.sign(np.sin(ph))
    if shape == "tri":
        return 2 * np.abs(2 * ((ph / (2 * np.pi)) % 1) - 1) - 1


def glide(f0, f1, dur, curve=1.0):
    k = np.linspace(0, 1, int(dur * SR)) ** curve
    return f0 * (f1 / f0) ** k


def mix(*xs):
    """Sum arrays of different lengths (shorter ones are padded with silence)."""
    n = max(len(x) for x in xs)
    out = np.zeros(n)
    for x in xs:
        out[:len(x)] += x
    return out


def place(total, *parts):
    """Mix (offset_seconds, samples) parts into one buffer of `total` seconds."""
    out = np.zeros(int(total * SR))
    for off, x in parts:
        i = int(off * SR)
        j = min(len(out), i + len(x))
        if j > i:
            out[i:j] += x[:j - i]
    return out


def reverb(x, room=0.25, mix=0.25, damp=3000):
    """A small feedback-delay reverb for space (not a convolution with any recording)."""
    out = x.copy()
    for d, g in ((0.029, 0.6), (0.037, 0.55), (0.041, 0.5), (0.053, 0.45)):
        k = int(d * SR * (1 + room))
        y = np.zeros(len(x) + k * 6)
        y[:len(x)] = x
        for i in range(1, 6):
            y[i * k:i * k + len(x)] += x * (g ** i)
        out = out + lp(y[:len(x)], damp) * mix / 4
    return out


def drive(x, amt=2.0):
    return np.tanh(x * amt) / np.tanh(amt)


def finish(x, loud=0.13, fade=0.02):
    """Even out loudness across sounds (RMS of the loud part), with a soft limiter."""
    x = x - np.mean(x)
    n = int(fade * SR)
    if n and len(x) > n:
        x[-n:] *= np.linspace(1, 0, n)
    x[:64] *= np.linspace(0, 1, 64)
    w = int(0.05 * SR)
    frames = np.sqrt(np.convolve(x ** 2, np.ones(w) / w, "valid"))
    level = np.percentile(frames, 90) if len(frames) else np.abs(x).max()
    x = x * (loud / max(level, 1e-6))
    return np.tanh(x / 0.95) * 0.95 if np.abs(x).max() > 0.9 else x


# ------------------------------------------------------------------ element sounds
def boom(dur=1.0, low=55, body=120, crack=1.0, tail=0.35):
    """A powder blast: a sharp crack, a falling low thump and a noisy rumble."""
    c = hp(noise(0.05), 1500) * env(0.05, 0.0005, 0.012) * crack
    th = osc(glide(body, low, 0.4, 0.5), 0.4) * env(0.4, 0.002, 0.12, 3)
    r = sweep_lp(noise(dur, "brown"), 1800, 120) * env(dur, 0.004, tail, 3)
    return place(dur, (0, c * 0.9), (0, th * 1.0), (0.002, r * 0.8))


def clank(freqs=(410, 683, 1121, 1790), dur=0.35, decay=0.08):
    """Struck metal: inharmonic partials with fast decay."""
    x = sum(osc(f, dur) * env(dur, 0.0005, decay * (1.4 - i * 0.25), 4) / (i + 1) for i, f in enumerate(freqs))
    return x + hp(noise(dur), 3000) * env(dur, 0.0005, 0.01) * 0.6


def hiss(dur=0.5, lo=2500, hi=9000, attack=0.02, decay=0.3):
    return bp(noise(dur), lo, hi) * env(dur, attack, decay, 3)


def growl_voice(dur, f0, f1, formants, rough=0.35, vib=6.0, breath=0.25):
    """A beast voice: a rough, buzzing source shaped by vocal-tract formants."""
    tt = t(dur)
    f = glide(f0, f1, dur, 0.8) * (1 + 0.03 * np.sin(2 * np.pi * vib * tt))
    f = f * (1 + rough * 0.08 * lp(noise(dur), 60) * 3)               # jitter
    src = osc(f, dur, "saw") * (1 + rough * lp(noise(dur), 40) * 2)    # amplitude roughness
    src = src + noise(dur) * breath
    v = sum(bp(src, fc * 0.82, fc * 1.18) * g for fc, g in formants)
    return v


def screech_voice(dur, f0, f1, f2=None, harsh=0.5):
    """A bird/bat cry: a bright, fast-gliding tone with noise and growl."""
    k = int(dur * SR)
    fr = glide(f0, f1, dur, 0.6) if f2 is None else np.concatenate(
        [glide(f0, f1, dur * 0.35, 0.7), glide(f1, f2, dur - dur * 0.35, 1.2)])
    fr = np.interp(np.linspace(0, len(fr) - 1, k), np.arange(len(fr)), fr)
    fr = fr * (1 + 0.02 * np.sin(2 * np.pi * 28 * t(dur)))
    x = osc(fr, dur, "saw") * 0.6 + osc(fr * 2.01, dur, "sine") * 0.3
    x = bp(x, 900, 7000) + bp(noise(dur), 2500, 8000) * harsh * 0.5
    return drive(x, 2.5)


def flap(dur=0.18, f=180):
    """One wing beat: a soft, low whump of air."""
    return mix(lp(noise(dur, "pink"), f * 6) * env(dur, 0.03, 0.06, 4), osc(f, dur) * env(dur, 0.02, 0.05, 5) * 0.4)


# ------------------------------------------------------------------ the sounds
def wc_rifle():
    """A dwarven long rifle: black-powder crack, short boom and a little ring."""
    b = boom(0.7, low=70, body=180, crack=1.2, tail=0.18)
    ring = clank((1900, 2870, 4100), 0.4, 0.05) * 0.25
    return reverb(place(0.75, (0, b), (0.004, ring)), mix=0.3)


def wc_steam_cannon():
    """Steam tanks and golems: a pneumatic chuff, a heavy cannon thud and metal clank."""
    chuff = hiss(0.35, 1500, 7000, 0.005, 0.12) * 0.7
    b = boom(1.4, low=40, body=95, crack=0.7, tail=0.45)
    k = clank((260, 433, 715, 1150), 0.5, 0.12) * 0.55
    vent = hiss(0.9, 2500, 9000, 0.12, 0.45) * 0.35
    return reverb(place(1.6, (0, chuff), (0.06, b), (0.08, k), (0.35, vent)), mix=0.3)


def wc_mortar():
    """A gnomish mortar: a hollow 'thoomp' launch, a whistle, then a distant blast."""
    launch = mix(osc(glide(140, 60, 0.25), 0.25) * env(0.25, 0.002, 0.08, 3), lp(noise(0.2), 600) * env(0.2, 0.001, 0.05) * 0.6)
    whistle = osc(glide(2400, 900, 0.7, 1.4), 0.7) * adsr(0.7, 0.1, 0.2, 0.6, 0.15) * 0.12
    blast = boom(1.1, low=38, body=80, crack=0.5, tail=0.5) * 0.85
    return reverb(place(2.0, (0, launch), (0.15, whistle), (0.85, blast)), room=0.5, mix=0.35)


def wc_gyro_guns():
    """Gyrocopter and dwarven repeating guns: a clattering burst over a rotor whir."""
    dur = 1.0
    shots = []
    for i in range(9):
        s = mix(hp(noise(0.06), 900) * env(0.06, 0.0005, 0.012, 4), osc(glide(320, 140, 0.05), 0.05) * env(0.05, 0.001, 0.015) * 0.6)
        shots.append((0.02 + i * 0.075 + RNG.uniform(-0.006, 0.006), s * RNG.uniform(0.75, 1.0)))
    rot = osc(18, dur, "square") * 0.5 + 0.5
    whir = bp(noise(dur), 300, 1500) * lp(rot, 30) * adsr(dur, 0.08, 0.2, 0.7, 0.25) * 0.35
    tick = clank((2200, 3300), 0.08, 0.02) * 0.18
    return reverb(place(dur, (0, whir), *shots, (0.72, tick)), mix=0.2)


def wc_bomb():
    """A dropped goblin bomb: fuse fizz, a short whistle down and a big blast."""
    fizz = hiss(0.35, 3000, 9000, 0.01, 0.3) * (1 + 0.5 * np.sin(2 * np.pi * 37 * t(0.35))) * 0.25
    fall = osc(glide(1600, 500, 0.4, 1.2), 0.4) * adsr(0.4, 0.05, 0.1, 0.7, 0.05) * 0.12
    b = boom(1.4, low=34, body=85, crack=0.9, tail=0.6)
    debris = bp(noise(0.6), 1500, 6000) * env(0.6, 0.05, 0.25, 3) * 0.2
    return reverb(place(2.0, (0, fizz), (0.25, fall), (0.62, b), (0.75, debris)), room=0.4, mix=0.3)


def wc_rocket():
    """A goblin rocket: sputtering ignition, a rising whoosh and a pop-bang."""
    ign = hp(noise(0.12), 800) * env(0.12, 0.001, 0.04) * 0.7
    roar = sweep_lp(noise(0.6, "pink"), 600, 5000, 0.6) * adsr(0.6, 0.04, 0.2, 0.6, 0.2)
    roar *= 1 + 0.4 * np.sin(2 * np.pi * 23 * t(0.6))
    b = boom(0.9, low=60, body=150, crack=1.0, tail=0.3) * 0.8
    return reverb(place(1.5, (0, ign), (0.04, roar * 0.7), (0.62, b)), mix=0.3)


def wc_arcane_blast():
    """A mage's bolt: a shimmering charge that bursts into a bright, ringing zap."""
    d = 0.9
    tt = t(d)
    charge = sum(osc(glide(f, f * 2.2, 0.35, 1.5), 0.35, "sine") for f in (330, 495, 742)) / 3
    charge *= adsr(0.35, 0.25, 0.05, 0.9, 0.05) * 0.5
    zap_f = glide(1800, 220, 0.5, 0.5)
    zap = osc(zap_f, 0.5, "saw") * env(0.5, 0.002, 0.18, 3)
    zap = bp(zap, 200, 6000) * 0.6 + hp(noise(0.5), 4000) * env(0.5, 0.001, 0.05) * 0.4
    sparkle = sum(osc(f, d - 0.3) * env(d - 0.3, 0.005, 0.3, 4) / 3 for f in (1975, 2637, 3520))
    sparkle *= 1 + 0.5 * np.sin(2 * np.pi * 11 * t(d - 0.3))
    return reverb(place(d, (0, charge), (0.3, zap), (0.3, sparkle * 0.25)), room=0.4, mix=0.4, damp=7000)


def wc_mana_bomb():
    """A mana bomb: a rising arcane drone, a sudden hush, then a vast violet blast."""
    d = 3.2
    rise = sum(osc(glide(f, f * 3, 1.2, 2.0), 1.2, "saw") for f in (55, 82.5, 110)) / 3
    rise = sweep_lp(rise, 300, 4000, 2.0) * adsr(1.2, 1.0, 0.1, 0.9, 0.1) * 0.45
    b = boom(2.0, low=28, body=70, crack=1.0, tail=1.0)
    shim = sum(osc(f, 1.8) * env(1.8, 0.02, 0.9, 3) for f in (440, 660, 990, 1320)) / 4
    shim *= 1 + 0.6 * np.sin(2 * np.pi * 7 * t(1.8))
    wind = sweep_lp(noise(2.0, "pink"), 3000, 200) * env(2.0, 0.05, 1.0, 2.5) * 0.4
    return reverb(place(d, (0, rise), (1.25, b), (1.25, shim * 0.35), (1.3, wind)), room=0.8, mix=0.45)


def wc_ship_cannon():
    """A steam warship's broadside: three deep cannon booms rolling over the water."""
    parts = [(0.0, boom(1.6, 36, 90, 0.8, 0.6)), (0.16, boom(1.6, 40, 100, 0.7, 0.6) * 0.8),
             (0.29, boom(1.6, 34, 85, 0.6, 0.7) * 0.75)]
    return reverb(place(2.0, *parts), room=0.9, mix=0.4, damp=2000)


def wc_lightning():
    """Titan lightning (Iron Colossus, Sky Golem): electric crackle, a whip-crack and thunder."""
    d = 2.2
    buzz = osc(glide(90, 120, 0.3), 0.3, "square") * hp(noise(0.3), 200) * adsr(0.3, 0.2, 0.05, 0.8, 0.05) * 0.25
    crack = hp(noise(0.12), 2000) * env(0.12, 0.0005, 0.03, 3)
    crackle = np.zeros(int(0.5 * SR))
    for _ in range(40):
        i = RNG.integers(0, len(crackle) - 200)
        crackle[i:i + 120] += hp(noise(0.004), 3000)[:120] * RNG.uniform(0.2, 1.0) * np.exp(-i / len(crackle) * 3)
    thunder = sweep_lp(noise(1.8, "brown"), 1200, 80) * adsr(1.8, 0.08, 0.3, 0.5, 1.2) * 0.9
    return reverb(place(d, (0, buzz), (0.25, crack), (0.25, crackle * 0.6), (0.33, thunder)), room=0.7, mix=0.4)


# --- beasts
def wc_wyrm():
    """A frost wyrm: a deep, grinding dragon roar with an icy breath hiss behind it."""
    d = 2.0
    roar = growl_voice(1.6, 95, 70, ((380, 1.0), (900, 0.6), (2300, 0.25)), rough=0.6, vib=5)
    roar = drive(roar * adsr(1.6, 0.12, 0.3, 0.8, 0.5), 2.5)
    sub = osc(glide(48, 38, 1.6), 1.6) * adsr(1.6, 0.15, 0.3, 0.7, 0.5) * 0.5
    breath = hiss(1.4, 2500, 10000, 0.25, 0.8) * 0.4
    ice = sum(osc(f, 1.2) * env(1.2, 0.3, 0.6, 3) for f in (3136, 3951, 4699)) / 3 * 0.06
    return reverb(place(d, (0, roar), (0, sub), (0.35, breath), (0.45, ice)), room=0.8, mix=0.35)


def wc_gryphon():
    """A gryphon rider's attack: wing beats, an eagle screech and a storm hammer's thunder."""
    d = 1.7
    flaps = [(i * 0.17, flap(0.2, 150)) for i in range(2)]
    cry = screech_voice(0.55, 2100, 2900, 1500, harsh=0.4) * adsr(0.55, 0.02, 0.15, 0.7, 0.2) * 0.6
    ham = boom(1.1, low=50, body=130, crack=1.0, tail=0.4) * 0.7
    zap = hp(noise(0.08), 3000) * env(0.08, 0.0005, 0.02) * 0.5
    return reverb(place(d, *flaps, (0.22, cry), (0.75, zap), (0.76, ham)), room=0.5, mix=0.3)


def wc_bat():
    """A batrider: leathery wing flutter, a shrill bat shriek, and a thrown fire bomb."""
    d = 1.6
    flaps = [(i * 0.09, flap(0.11, 260) * 0.8) for i in range(4)]
    shriek = screech_voice(0.35, 3800, 5200, 3000, harsh=0.7) * adsr(0.35, 0.01, 0.1, 0.6, 0.15) * 0.45
    fire = sweep_lp(noise(0.9, "pink"), 4000, 500) * env(0.9, 0.02, 0.4, 2.5) * 0.6
    pop = boom(0.8, low=70, body=160, crack=0.8, tail=0.25) * 0.55
    return reverb(place(d, *flaps, (0.12, shriek), (0.55, pop), (0.56, fire)), room=0.4, mix=0.3)


def wc_snarl():
    """Worgen, ghouls and other beasts: a snarling growl and a slashing bite."""
    d = 0.9
    g = growl_voice(0.55, 150, 115, ((500, 1.0), (1200, 0.7), (2600, 0.3)), rough=0.8, vib=9, breath=0.4)
    g = drive(g * adsr(0.55, 0.04, 0.15, 0.7, 0.2), 3.0) * 0.8
    slash = bp(noise(0.12), 2500, 9000) * env(0.12, 0.005, 0.04, 3) * 0.6
    bite = mix(clank((700, 1350), 0.1, 0.02) * 0.2, lp(noise(0.08), 900) * env(0.08, 0.001, 0.02) * 0.6)
    return reverb(place(d, (0, g), (0.45, slash), (0.5, bite)), mix=0.25)


def wc_rock_smash():
    """An infernal: a grinding boulder impact, a fel-fire roar and falling rubble."""
    d = 1.6
    hit = osc(glide(110, 45, 0.3), 0.3) * env(0.3, 0.002, 0.1, 3) + lp(noise(0.3, "brown"), 400) * env(0.3, 0.001, 0.12)
    grind = bp(noise(0.8, "brown"), 120, 900) * adsr(0.8, 0.02, 0.2, 0.5, 0.4) * 0.6
    fire = sweep_lp(noise(1.2, "pink"), 3500, 400) * env(1.2, 0.05, 0.6, 2.5) * 0.45
    rubble = np.zeros(int(0.9 * SR))
    for _ in range(25):
        i = RNG.integers(0, len(rubble) - 800)
        rubble[i:i + 800] += bp(noise(0.02), 600, 4000)[:800] * env(0.02, 0.0005, 0.006)[:800] * RNG.uniform(0.2, 0.7)
    return reverb(place(d, (0, hit), (0, grind), (0.05, fire), (0.3, rubble * 0.5)), room=0.5, mix=0.3)


SOUNDS = {
    "wc_rifle": wc_rifle, "wc_steam_cannon": wc_steam_cannon, "wc_mortar": wc_mortar,
    "wc_gyro_guns": wc_gyro_guns, "wc_bomb": wc_bomb, "wc_rocket": wc_rocket,
    "wc_arcane_blast": wc_arcane_blast, "wc_mana_bomb": wc_mana_bomb, "wc_ship_cannon": wc_ship_cannon,
    "wc_lightning": wc_lightning, "wc_wyrm": wc_wyrm, "wc_gryphon": wc_gryphon, "wc_bat": wc_bat,
    "wc_snarl": wc_snarl, "wc_rock_smash": wc_rock_smash,
}

# unit -> sound (replaces the modern stock sounds; black powder, bows and blades keep theirs)
UNIT_SOUNDS = {
    # black-powder rifles
    "Musketeer": "wc_rifle", "Rifleman": "wc_rifle", "Fusilier": "wc_rifle", "Shock Trooper": "wc_rifle",
    "Kul Tiran Marine": "wc_rifle", "Skyguard": "wc_rifle", "Ironforge Rifleman": "wc_rifle",
    "Gilnean Rifleman": "wc_rifle",
    # gnomish and dwarven guns, gyrocopters
    "Gyrocopter": "wc_gyro_guns", "Flying Machine": "wc_gyro_guns", "Flak Cannon": "wc_gyro_guns",
    "Mountaineer": "wc_gyro_guns", "Siegebreaker": "wc_steam_cannon",
    # steam machines
    "War Golem": "wc_steam_cannon", "Siege Engine": "wc_steam_cannon", "Mechano-Tank": "wc_steam_cannon",
    "Mechagnome Trooper": "wc_steam_cannon",
    # mortars and siege
    "Mortar Team": "wc_mortar", "Demolisher": "wc_mortar", "Gnomish Bombardier": "wc_mortar",
    # bombs and rockets
    "Grenadier": "wc_bomb", "Bomber Zeppelin": "wc_bomb", "War Zeppelin": "wc_bomb", "Void Bomber": "wc_bomb",
    "Flak Wagon": "wc_rocket",
    # magic
    "Mage": "wc_arcane_blast", "Arcane Missile": "wc_arcane_blast", "Kael'thas Sunstrider": "wc_arcane_blast",
    "Kel'Thuzad": "wc_arcane_blast", "Malfurion Stormrage": "wc_arcane_blast",
    "Mana Bomb": "wc_mana_bomb", "Arcane Annihilator": "wc_mana_bomb",
    # warships and titans
    "Ironclad": "wc_ship_cannon", "Destroyer": "wc_ship_cannon", "Dreadnought": "wc_ship_cannon",
    "Juggernaught": "wc_ship_cannon",
    "Iron Colossus": "wc_lightning", "Sky Golem": "wc_lightning",
    # beasts
    "Frost Wyrm": "wc_wyrm", "Gryphon Rider": "wc_gryphon", "Batrider": "wc_bat",
    "Worgen Ravager": "wc_snarl", "Worgen Stalker": "wc_snarl", "Ghoul": "wc_snarl",
    "Infernal": "wc_rock_smash",
}


def _write_ogg(x, path):
    pcm = (np.clip(x, -1, 1) * 32767).astype(np.int16)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        tmp = f.name
    with wave.open(tmp, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
    subprocess.run(["ffmpeg", "-v", "quiet", "-y", "-i", tmp, "-c:a", "libvorbis", "-q:a", "5",
                    "-fflags", "+bitexact", "-flags:a", "+bitexact", path], check=True)
    os.remove(tmp)


def render_all():
    return {name: finish(fn()) for name, fn in SOUNDS.items()}


def write_all(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    for name, x in render_all().items():
        _write_ogg(x, os.path.join(out_dir, name + ".ogg"))
    return len(SOUNDS)
