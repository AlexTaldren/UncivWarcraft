"""Sprites and icons for the roster units (roster_data.py): every unit gets a loadout that fits its
bucket, tier and name, drawn on its faction's own body (unit_art_races.py). A shared unit gets one
sprite per faction that fields it ("<unit>-<faction>"), so a Troll crew does not look like an Orc one.

Interim art, to be replaced by dedicated designs: heavy beasts are the faction's mount without a rider,
giants are an oversized warrior of the race, machines reuse the shared war machines, and ships reuse
each faction's earlier ship art. Air units are not drawn on the map.
"""
import os
import shutil

import unit_art as UA
import unit_art_humans as UH
import unit_art_machines as UM
import unit_art_races as UR
import roster_data as RD
import wc_roster
from unit_art import lit, line, TINT, STEEL, LEATHER, TAN, WOOD, IRON, HAIR, FY
from unit_art_humans import CLOTHD

HUMANS = UR.Race("Humans")
GIANT = UR.Race("giant", rows=(("dup", 6), ("dup", 13), ("dup", 16)), cols=(("dup", 4), ("dup", -4)))


# ---------------------------------------------------------------- extra loadouts
def stalker(cv, cx=UA.MIL_X - 2, fy=FY):
    """Ambusher: hood and long cloak in the faction's colour, a dagger in each hand."""
    cv.shadow(cx, 8)
    UH.cape(cv, cx, fy, 2, length=11)
    b = cv.part()
    cv.rect(b, cx - 9, fy - 17, cx - 9, fy - 13, STEEL[0])
    UH.back_grip(cv, cx, fy, LEATHER)
    UH.base(cv, cx, fy, legs_r=CLOTHD, torso_r=LEATHER, belt_r=IRON)
    UH.hood(cv, cx, fy - 23, 2)
    tx = cx + 8
    d = cv.part()
    cv.rect(d, tx, fy - 18, tx, fy - 13, STEEL[0])
    UH.front_reach(cv, cx, fy, LEATHER, tx)


def assassin(cv, cx=UA.MIL_X - 2, fy=FY):
    """Master of ambush: masked, two long blades, a cloak with the inner colour on its edge."""
    cv.shadow(cx, 8)
    UH.cape(cv, cx, fy, 2, length=12)
    t = cv.part(1, sep=False)
    cv.rect(t, cx - 6, fy - 4, cx - 3, fy - 4, TINT[1])
    UH.sword_up(cv, cx - 9, fy - 24, fy - 13, guard=0, guard_ramp=IRON)
    UH.back_grip(cv, cx, fy, CLOTHD)
    UH.base(cv, cx, fy, legs_r=CLOTHD, torso_r=CLOTHD, belt_r=LEATHER)
    s = cv.part(1, sep=False)
    cv.pix(s, line(cx - 4, fy - 15, cx + 4, fy - 9), TINT[0])
    UH.hood(cv, cx, fy - 23, 0, ramp=CLOTHD)
    m = cv.part(sep=False)
    cv.rect(m, cx - 1, fy - 19, cx + 3, fy - 18, CLOTHD[2])
    tx = cx + 8
    d = cv.part()
    cv.rect(d, tx, fy - 24, tx + 1, fy - 13, lit(STEEL, dark_from=tx + 1))
    UH.front_reach(cv, cx, fy, CLOTHD, tx + 1)


def thrower(cv, cx=UA.MIL_X - 4, fy=FY):
    """Thrower: one javelin raised to throw, more in a case on the back, a small shield."""
    cv.shadow(cx, 8)
    q = cv.part()
    cv.rect(q, cx - 8, fy - 18, cx - 6, fy - 11, lit(LEATHER, dark_from=cx - 6))
    sp = cv.part()
    cv.pix(sp, [(cx - 8, fy - 21), (cx - 8, fy - 20), (cx - 8, fy - 19), (cx - 6, fy - 20), (cx - 6, fy - 19)], WOOD[0])
    UH.hang(cv, cx - 6, fy, TAN)
    UH.base(cv, cx, fy, legs_r=LEATHER, torso_r=TINT, layer=2)
    UA.head(cv, cx, fy - 23)
    UH.hair(cv, cx, fy - 23, HAIR)
    y = fy - 24
    j = cv.part()                                                          # javelin over the shoulder, point forward
    cv.rect(j, cx - 6, y, cx + 12, y, WOOD[1])
    cv.rect(j, cx + 13, y - 1, cx + 14, y + 1, STEEL[0])
    cv.put(j, cx + 15, y, STEEL[0])
    sl = cv.part(2)
    cv.rect(sl, cx + 4, fy - 20, cx + 6, fy - 14, lit(TINT, dark_from=cx + 6))
    UA.fist(cv, cx + 4, y - 1)


def apprentice(cv, cx=UA.MIL_X - 5, fy=FY):
    """Novice caster: plain robe with a coloured mantle, a short staff with a small glow."""
    cv.shadow(cx, 8)
    UH.robe(cv, cx, fy, TAN)
    UH.robe_trim(cv, cx, fy, 1, stole=False)
    UA.arm(cv, cx - 6, fy - 14, TAN, length=5)
    UH.mantle(cv, cx, fy, 2)
    UA.head(cv, cx, fy - 23)
    UH.hair(cv, cx, fy - 23, HAIR)
    tx = cx + 9
    UH.pole(cv, tx, fy - 21, fy)
    g = cv.part()
    cv.rows(g, [(fy - 24, tx, tx), (fy - 23, tx - 1, tx + 1), (fy - 22, tx, tx)], UH.ARCANE[1])
    UH.front_reach(cv, cx, fy, TAN, tx)


def beast_only(cv, cx=UA.MID_X - 2, fy=FY):
    """A war beast: the faction's great animal with a pack saddle in its colours."""
    cv.shadow(cx + 1, 14)
    back = UA.horse(cv, cx, fy)
    UH.blanket(cv, cx, back)
    p = cv.part()
    cv.rect(p, cx - 5, back - 3, cx + 2, back - 1, lit(LEATHER, dark_from=cx + 1, light_to=cx - 3, light_rows=back - 3))
    d = cv.part(1, sep=False)
    cv.rect(d, cx - 5, back - 2, cx + 2, back - 2, TINT[1])


GUN = ("rifle", "gunner", "marksman", "sharpshooter", "death ray", "crossbow")
THROW = ("thrower", "harpoon", "tosser", "spitter", "trident", "slingshot", "snap dragon")
BEAST = ("kodo", "bear", "beast", "turtle", "brutosaur", "hound", "charger", "couatl")
MACHINE = ("golem", "construct", "warframe", "shredder", "lumberjack", "colossus", "reaver", "machine", "armor", "statue")


def loadout(name, b, t):
    """(function, rule) for a roster unit. rule: 'mount' / 'machine' (no body rebuild), 'giant', or ''."""
    import unit_art_beasts as UB
    if name in UB.SPECIAL:
        return UB.SPECIAL[name]
    n = name.lower()
    has = lambda words: any(w in n for w in words)
    if b == "aggressive":
        if has(("berserker", "reaver", "ravager", "bruiser", "deathbringer")):
            return UH.gladiator, ""
        return [UH.militia, UR.footman_r, UH.vanquisher if "champion" in n else UH.man_at_arms][t], ""
    if b == "defensive":
        if "halberd" in n:
            return UH.halberdier, ""
        return [UH.spearman, UH.pikeman, UH.royal_guard][t], ""
    if b == "scout":
        return [UH.scout, stalker, assassin][t], ""
    if b == "ranged":
        if has(THROW):
            return thrower, ""
        if has(GUN):
            return [UH.rifleman, UH.rifleman, UH.sharpshooter][t], ""
        return [UR.archer_r, UH.ranger, UH.ranger_captain][t], ""
    if b == "magic":
        return [apprentice, UH.magus, UH.archmage][t], ""
    if b == "mounted":
        if name == "Paladin":
            return UH.paladin, "mount"
        if "archer" in n:
            return UH.mounted_archer, "mount"
        if "lancer" in n:
            return UH.lancer, "mount"
        if "knight" in n and t == 2:
            return UH.silver_hand, "mount"
        return [UH.outrider, UR.knight_r, UH.war_rider][t], "mount"
    if b == "heavy":
        special = {"Steam Tank": UH.steam_tank, "Siege Engine": UM.siege_engine, "Mechano-Tank": UM.mechano_tank, "Spider Tank": UM.mechano_tank}
        if name in special:
            return special[name], "machine"
        if "rider" in n:
            return UR.knight_r, "mount"
        if has(BEAST):
            return beast_only, "mount"
        if has(MACHINE):
            return (UM.iron_colossus if t == 2 else UM.war_golem), "machine"
        return (UH.vanquisher if t == 2 else UH.gladiator), "giant"
    if b == "siege":
        if "demolisher" in n:
            return UM.demolisher, "machine"
        if has(("beast", "caller", "guardian")):
            return beast_only, "mount"
        return [UA.catapult, UH.ballista, UH.mortar_team][t], "machine"
    if b == "naval":
        if has(("dreadnought", "battleship", "juggernaught", "flagship", "man-o'-war")):
            return UM.juggernaught, "machine"
        return [UM.longboat, UM.war_galley, UM.frigate][t], "machine"
    if b == "healer":
        return [UH.cleric, UR.priest_r, UH.great_prophet][t], ""
    return None, ""


def render(name, b, t, nation):
    fn, rule = loadout(name, b, t)
    race = UR.RACES.get(nation, HUMANS)
    if fn is None:
        return None
    if rule in ("mount", "machine", "air"):
        return UR.render(fn, race, "Knight" if rule == "mount" else "Catapult")
    if rule == "giant":
        return UR.render(fn, race, "", after=GIANT)
    return UR.render(fn, race, "")


OLD_SHIP = ["Longboat", "War Galley", "Frigate"]


def write_all(image_dirs, unit_dir="TileSets/AbsoluteUnits/Units/"):
    folder = os.path.join(image_dirs[0], unit_dir)
    icons = os.path.join(os.path.dirname(os.path.normpath(image_dirs[0])), "Images", "UnitIcons")
    count = 0

    def save(stem, layers):
        for suf, im in zip(("", "-1", "-2"), layers):
            im.save(os.path.join(folder, stem + suf + ".png"))

    def old_ship(stem, t, nation):
        src = os.path.join(folder, "%s-%s" % (OLD_SHIP[t], nation))
        if not os.path.exists(src + ".png"):
            return False
        for suf in ("", "-1", "-2"):
            if os.path.exists(src + suf + ".png"):
                shutil.copyfile(src + suf + ".png", os.path.join(folder, stem + suf + ".png"))
        return True

    import unit_art_beasts as UB
    for name, (b, t, users) in RD.slots().items():
        first = "Humans" if "Humans" in users else users[0]
        made = None
        for stem, nation in [(name, first)] + [("%s-%s" % (name, n), n) for n in users]:
            if b == "naval" and (nation in UB.SHIP_STYLE or name in UB.HORDE_SHIPS):
                style = "horde" if name in UB.HORDE_SHIPS else UB.SHIP_STYLE[nation]
                layers = UR.render(UB.ship(style, t), UR.RACES.get(nation, HUMANS), "Catapult")
            else:
                layers = render(name, b, t, nation)
            if layers is None:
                continue
            save(stem, layers)
            made = made or layers
            count += 1
        if made is not None and os.path.isdir(icons):                    # every roster unit gets its own icon, cut from its sprite
            ic = UB.icon(made)
            if ic is not None:
                ic.save(os.path.join(icons, name + ".png"))
    return count


_prev_write = UA.write_all


def _write_everything(image_dirs, unit_dir="TileSets/AbsoluteUnits/Units/"):
    n = _prev_write(image_dirs, unit_dir)
    m = write_all(image_dirs, unit_dir)
    print("roster unit sprites:", m)
    return n + m


UA.write_all = _write_everything
