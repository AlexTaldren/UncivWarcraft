"""Per-faction scorecard from WarcraftSim logs.

usage: python3 scorecard.py log1 [log2 ...]
For each race: cities at turns 100/200/last (mean over logs), how often it was alive at
the end, mean techs at the end, wins, and the cities it lost to / took from others.
"""
import re, sys
from collections import defaultdict

ROW = re.compile(r"^   (.+?)( \[defeated\])? \| cities (\d+) \| units (\d+) \| techs (\d+) \|")


def parse(path):
    turns, cur = {}, None
    win, held = None, {}
    for line in open(path, errors="replace"):
        if line.startswith("TURN "):
            cur = int(line.split()[1].rstrip(":"))
            turns[cur] = {}
        m = ROW.match(line)
        if m and cur is not None:
            turns[cur][m.group(1)] = dict(dead=bool(m.group(2)), cities=int(m.group(3)), techs=int(m.group(5)))
        if line.startswith("VICTORY:"):
            m2 = re.search(r"winningCiv=([^,]+), victoryType=(\w+), victoryTurn=(\d+)", line)
            if m2:
                win = (m2.group(1), m2.group(2), int(m2.group(3)))
        if line.startswith("CITIES HELD BY CONQUERORS"):
            for a, b, n in re.findall(r"([^{,]+?) -> ([^=]+)=(\d+)", line.split(":", 1)[1]):
                held[(a.strip(), b.strip())] = int(n)
    return turns, win, held


def nearest(turns, t):
    ks = [k for k in turns if k <= t]
    return turns[max(ks)] if ks else {}


def main(paths):
    games = [parse(p) for p in paths]
    races = sorted({r for t, _, _ in games for snap in t.values() for r in snap})
    print("%-20s %6s %6s %6s %6s %6s %5s %5s %5s" % ("race", "c@100", "c@200", "c@end", "alive", "techs", "wins", "lost", "took"))
    for r in races:
        c100 = [nearest(t, 100).get(r, {}).get("cities", 0) for t, _, _ in games]
        c200 = [nearest(t, 200).get(r, {}).get("cities", 0) for t, _, _ in games]
        last = [t[max(t)].get(r, {}) for t, _, _ in games if t]
        cend = [x.get("cities", 0) for x in last]
        alive = sum(1 for x in last if x and not x["dead"])
        techs = [x.get("techs", 0) for x in last]
        wins = sum(1 for _, w, _ in games if w and w[0] == r)
        lost = sum(n for _, _, h in games for (a, b), n in h.items() if a == r)
        took = sum(n for _, _, h in games for (a, b), n in h.items() if b == r)
        avg = lambda v: sum(v) / len(v) if v else 0
        print("%-20s %6.1f %6.1f %6.1f %4d/%d %6.0f %5d %5d %5d" % (r, avg(c100), avg(c200), avg(cend), alive, len(last),
                                                              avg(techs), wins, lost, took))
    print()
    for p, (t, w, h) in zip(paths, games):
        print(p, "| victory:", w, "| last turn:", max(t) if t else None)


if __name__ == "__main__":
    main(sys.argv[1:])
