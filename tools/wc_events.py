"""Random events from Warcraft lore (v0.10).

Each event pops up for the civ it happens to, with a few choices; the AI picks for
itself. They're triggered from GlobalUniques: a small chance every other turn, limited
to the eras the story belongs to. Names here are the mod's own (after renames).
"""

# How often: <every [3] turns> <with [n]% chance> gives about n/3 % per turn per civ.
def _when(chance, *extra):
    return " ".join(["<upon turn start>", "<every [3] turns>", "<with [%d]%% chance>" % chance] + list(extra))


def _need(amount, stat):
    return "Only available <when above [%d] [%s]>" % (amount - 1, stat)


def _mana(n):
    """Spend n Mana (only offered when the stockpile has it)."""
    return ["Instantly consumes [%d] [Mana]" % n, "Only available <when above [%d] [Mana]>" % (n - 1)]


EVENTS = [
    {
        "name": "The Darkmoon Faire",
        "text": "A caravan of striped tents and creaking wagons rolls into view: Silas Darkmoon's Faire "
                "has come to our lands! Games of chance, strange beasts, a fortune-teller named Sayge and "
                "a great many tickets for sale.",
        "trigger": _when(2, "<after turn number [15]>"),
        "choices": [
            ("Host the Faire in our capital (-100 Gold, a short Golden Age)",
             ["Gain [-100] [Gold]", "Empire enters a [3]-turn Golden Age", _need(100, "Gold")]),
            ("Try our luck at the games (-40 Gold, win up to 120)",
             ["Gain [-40] [Gold]", "Gain [0]-[120] [Gold]", _need(40, "Gold")]),
            ("Ask Sayge to read our fortune (+Science)", ["Gain [30] [Science]"]),
        ],
    },
    {
        "name": "Plague of Undeath",
        "text": "Grain from the north has been tainted. Those who ate the bread sicken, die... and rise again. "
                "The Cult of the Damned is spreading the plague of undeath through our granaries, as it "
                "once did in Lordaeron.",
        "trigger": _when(1, "<starting from the [Age of the Third War]>", "<before the [Age of the Cataclysm]>"),
        "choices": [
            ("Ward the granaries with arcane seals (-25 Mana)", _mana(25)),
            ("Burn the infected granaries (-120 Gold)", ["Gain [-120] [Gold]", _need(120, "Gold")]),
            ("Call on the priests to cleanse the grain (-80 Faith)", ["Gain [-80] [Faith]", _need(80, "Faith")]),
            ("Seal the gates and hope (lose population)", ["[-2] population in a random city"]),
        ],
    },
    {
        "name": "Legion Incursion",
        "text": "The sky tears open in a wound of green fire. A fel rift has opened near our lands, and the "
                "demons of the Burning Legion are pouring through!",
        "trigger": _when(1, "<starting from the [Age of the Dark Portal]>"),
        "choices": [
            ("Stand and fight! (demons attack; heroes rise to meet them)",
             ["[2] [Felguard]s rebel <before the [Age of the Lich King]>",
              "[2] [Infernal]s rebel <starting from the [Age of the Lich King]>",
              "Gain [60] [Faith]"]),
            ("Close the rift with a great spell (-35 Mana)", _mana(35)),
            ("Seal the rift with arcane might (-200 Gold)", ["Gain [-200] [Gold]", _need(200, "Gold")]),
        ],
    },
    {
        "name": "A Goblin Offer",
        "text": "A Steamwheedle Cartel zeppelin touches down outside the capital. A goblin in a fine suit "
                "steps out: \"Time is money, friend! Have I got a deal for you...\"",
        "trigger": _when(2, "<after turn number [25]>"),
        "choices": [
            ("Buy the goblin blueprints (-100 Gold, +Science)",
             ["Gain [-100] [Gold]", "Gain [80]-[160] [Science]", _need(100, "Gold")]),
            ("Sell them our surplus grain (+Gold, lose population)",
             ["Gain [60]-[140] [Gold]", "[-1] population in a random city"]),
            ("Send them packing", []),
        ],
    },
    {
        "name": "The Lunar Festival",
        "text": "The Lunar Festival has come, and the spirits of the elders walk among us. Lanterns float "
                "over the rooftops and the people ask how we will honor the old ones.",
        "trigger": _when(1, "<after turn number [10]>"),
        "choices": [
            ("Pay homage to the elders (+Faith)", ["Gain [40] [Faith]"]),
            ("Launch fireworks over the capital (-30 Gold, +Culture)",
             ["Gain [-30] [Gold]", "Gain [50] [Culture]", _need(30, "Gold")]),
        ],
    },
    {
        "name": "Brewfest",
        "text": "Dwarven brewers have rolled their kegs into town for Brewfest. The people are already "
                "singing, and the Dark Iron dwarves are sure to crash the party.",
        "trigger": _when(1, "<after turn number [20]>"),
        "choices": [
            ("Sponsor the festival (-80 Gold, a short Golden Age)",
             ["Gain [-80] [Gold]", "Empire enters a [2]-turn Golden Age", _need(80, "Gold")]),
            ("Tax the kegs (+Gold)", ["Gain [40]-[80] [Gold]"]),
        ],
    },
    {
        "name": "Children's Week",
        "text": "War has left many orphans in our lands. The matrons of the orphanage ask our citizens to "
                "take them in.",
        "trigger": _when(1, "<after turn number [30]>"),
        "choices": [
            ("Take in the orphans (-30 Gold, +1 population)",
             ["Gain [-30] [Gold]", "[1] population in a random city", _need(30, "Gold")]),
            ("Fund the orphanage (+Culture)", ["Gain [25] [Culture]"]),
        ],
    },
    {
        "name": "Gnomish Refugees",
        "text": "Gnomes driven from irradiated Gnomeregan arrive at our gates with nothing but their tools "
                "and a great deal of enthusiasm.",
        "trigger": _when(1, "<after turn number [40]>", "<before the [Age of the Legion]>"),
        "choices": [
            ("Welcome them into our cities (-40 Gold, +2 population)",
             ["Gain [-40] [Gold]", "[2] population in a random city", _need(40, "Gold")]),
            ("Put them to work in our workshops (+Science)", ["Gain [60]-[110] [Science]"]),
            ("Turn them away", []),
        ],
    },
    {
        "name": "A Titan Vault",
        "text": "Explorers' League diggers have broken into a sealed vault of the Titans. Strange machines "
                "hum in the dark, and runes glow on the walls.",
        "trigger": _when(1, "<after turn number [30]>"),
        "choices": [
            ("Tap the vault's power (+40 Mana)", ["Instantly provides [40] [Mana]"]),
            ("Study the Titan relics (+Science)", ["Gain [60]-[150] [Science]"]),
            ("Sell the relics to collectors (+Gold)", ["Gain [80]-[180] [Gold]"]),
            ("Seal it again. Some things are best left buried (+Faith)", ["Gain [40] [Faith]"]),
        ],
    },
    {
        "name": "The Cataclysm",
        "text": "Deathwing the Destroyer has burst from Deepholm. The earth splits, the sea rises and "
                "fire falls from the sky across Azeroth.",
        "trigger": _when(4, "<during the [Age of the Cataclysm]>"),
        "choices": [
            ("Rebuild what was broken (-150 Gold)", ["Gain [-150] [Gold]", _need(150, "Gold")]),
            ("Raise great wards against the fire (-50 Mana)", _mana(50)),
            ("Seek the blessing of the Dragon Aspects (-100 Faith)", ["Gain [-100] [Faith]", _need(100, "Faith")]),
            ("Endure (lose population)", ["[-2] population in a random city"]),
        ],
    },
    {
        "name": "A Wandering Brewmaster",
        "text": "A Pandaren brewmaster with a keg on his back wanders into the capital, looking for a good "
                "brew and a better story.",
        "trigger": _when(1, "<after turn number [20]>"),
        "choices": [
            ("Invite him to stay (-60 Gold, +Culture, +1 population)",
             ["Gain [-60] [Gold]", "Gain [40] [Culture]", "[1] population in a random city", _need(60, "Gold")]),
            ("Listen to his tales of Pandaria (+Science)", ["Gain [35] [Science]"]),
        ],
    },
    {
        "name": "Hallow's End",
        "text": "It is Hallow's End, and the Headless Horseman has been seen riding by moonlight. The "
                "people beg us to light the Wickerman to keep him away.",
        "trigger": _when(1, "<after turn number [15]>"),
        "choices": [
            ("Light the Wickerman (+Culture)", ["Gain [35] [Culture]"]),
            ("Pay the guards to watch the night (-30 Gold, +Faith)",
             ["Gain [-30] [Gold]", "Gain [40] [Faith]", _need(30, "Gold")]),
        ],
    },
    {
        "name": "An Envoy of the Kirin Tor",
        "text": "An envoy from Dalaran offers to train our most gifted children in the arcane arts, for a fee.",
        "trigger": _when(1, "<after turn number [35]>"),
        "choices": [
            ("Pay the Kirin Tor in Mana (-30 Mana, +Science)", _mana(30) + ["Gain [100]-[160] [Science]"]),
            ("Accept the Kirin Tor's offer (-80 Gold, +Science)",
             ["Gain [-80] [Gold]", "Gain [100]-[160] [Science]", _need(80, "Gold")]),
            ("Politely decline", []),
        ],
    },
    {
        "name": "Murloc Raid",
        "text": "\"Mrglglglgl!\" A tribe of murlocs has crawled out of the surf and is raiding our "
                "fishing villages.",
        "trigger": _when(2, "<after turn number [8]>", "<before the [Age of the Dark Portal]>"),
        "choices": [
            ("Drive them back into the sea! (murlocs attack)", ["[2] [Militia]s rebel"]),
            ("Leave them an offering of fish (-25 Gold)", ["Gain [-25] [Gold]", _need(25, "Gold")]),
        ],
    },
    {
        "name": "The Defias Brotherhood",
        "text": "The stonemasons who rebuilt our walls were never paid. Now they wear red masks, and call "
                "themselves the Defias Brotherhood.",
        "trigger": _when(1, "<starting from the [Age of Arathor]>", "<before the [Age of the Lich King]>"),
        "choices": [
            ("Pay the Stonemasons' Guild what it is owed (-150 Gold)", ["Gain [-150] [Gold]", _need(150, "Gold")]),
            ("Crush the Brotherhood! (bandits attack)",
             ["[2] [Pikeman]s rebel <before the [Age of the Third War]>",
              "[2] [Musketeer]s rebel <starting from the [Age of the Third War]>"]),
        ],
    },
]

# ---------------------------------------------------------------- v0.12: world threats, dragonflights, race events
EVENTS += [
    {
        "name": "The Scourge Marches",
        "text": "The Lich King's armies pour out of the north. Ghouls and death knights fall upon our borders, and the dead rise behind them.",
        "trigger": _when(2, "<during the [Age of the Lich King]>"),
        "not_for": ["Scourge"],
        "choices": [
            ("Hold the line! (the Scourge attacks; the faithful rally)",
             ["[2] [Ghoul]s rebel", "A [Death Knight] rebels", "Gain [60] [Faith]"]),
            ("Hold them back with arcane wards (-40 Mana)", _mana(40)),
            ("Burn the dead before they rise (-150 Gold)", ["Gain [-150] [Gold]", _need(150, "Gold")]),
        ],
    },
    {
        "name": "The Legion Invades",
        "text": "This is no mere incursion. Fel meteors rain across Azeroth as the Burning Legion begins its invasion in earnest.",
        "trigger": _when(4, "<during the [Age of the Legion]>"),
        "choices": [
            ("Defend our cities! (Infernals fall; heroes rise)", ["[3] [Infernal]s rebel", "A [Felguard] rebels", "Gain [100] [Faith]"]),
            ("Shield the cities with a great ward (-60 Mana)", _mana(60)),
            ("Raise every ward we have (-300 Gold)", ["Gain [-300] [Gold]", _need(300, "Gold")]),
        ],
    },
    {
        "name": "Whispers of the Old Gods",
        "text": "In the dark, a voice whispers. Scholars dream of tentacles and eyes, and some stop sleeping altogether. The Old Gods are stirring.",
        "trigger": _when(3, "<starting from the [Age of Azerite]>"),
        "choices": [
            ("Seal our minds with arcane wards (-40 Mana)", _mana(40)),
            ("Resist the whispers through prayer (-100 Faith)", ["Gain [-100] [Faith]", _need(100, "Faith")]),
            ("Silence the cultists (lose population)", ["[-1] population in a random city"]),
            ("Listen... (+Science, but madness spreads)", ["Gain [150]-[250] [Science]", "[-2] population in a random city", "Gain [-50] [Culture]"]),
        ],
    },
    {
        "name": "The Gift of Alexstrasza",
        "text": "A great red dragon circles the capital and lands in the fields. Alexstrasza the Life-Binder offers her blessing to our people.",
        "trigger": _when(1, "<after turn number [40]>"),
        "choices": [
            ("Accept the gift of life (+2 population)", ["[2] population in a random city"]),
            ("Ask her to bless our temples (+Faith)", ["Gain [80] [Faith]"]),
        ],
    },
    {
        "name": "The Blue Dragonflight",
        "text": "Kalecgos of the blue dragonflight offers to share the secrets of the arcane, if we promise to use them wisely.",
        "trigger": _when(1, "<after turn number [50]>"),
        "choices": [
            ("Ask him to fill our Mana stores (+50 Mana)", ["Instantly provides [50] [Mana]"]),
            ("Learn from the Spell-Weaver (+Science)", ["Gain [100]-[200] [Science]"]),
            ("Politely decline the dragon's offer", []),
        ],
    },
    {
        "name": "Nozdormu's Warning",
        "text": "A bronze dragon steps out of time itself. Nozdormu the Timeless warns of a future that must not come to pass, and shows us how to change it.",
        "trigger": _when(1, "<after turn number [60]>"),
        "choices": [
            ("Heed the Timeless One (a short Golden Age)", ["Empire enters a [3]-turn Golden Age"]),
            ("Ask to see the paths of time (+Science)", ["Gain [120] [Science]"]),
        ],
    },
    {
        "name": "The Emerald Dream",
        "text": "Our people dream of a green and endless forest. Ysera the Dreamer has touched their sleep with peace.",
        "trigger": _when(1, "<after turn number [30]>"),
        "choices": [
            ("Embrace the Dream (+Culture)", ["Gain [60] [Culture]"]),
            ("Let the druids interpret it (+Faith)", ["Gain [60] [Faith]"]),
        ],
    },
    {
        "name": "Lord Prestor's Offer",
        "text": "A charming nobleman, Lord Daval Prestor, offers gold and counsel to our court. Something about his eyes is not quite right.",
        "trigger": _when(1, "<after turn number [40]>", "<before the [Age of the Cataclysm]>"),
        "choices": [
            ("Accept his generous gift (+300 Gold, but the black dragon's influence spreads)",
             ["Gain [300] [Gold]", "Gain [-80] [Culture]", "[-1] population in a random city"]),
            ("Unmask him! (he flees; the court is grateful)", ["Gain [40] [Culture]"]),
        ],
    },
    {
        "name": "A Bold Experiment",
        "text": "Our tinkers want to test a new device. In theory it will revolutionize gnomish science. In theory.",
        "trigger": _when(3, "<after turn number [20]>"),
        "only": ["Gnomes"],
        "choices": [
            ("Power it with Mana (-20 Mana, a safer gamble)", _mana(20) + ["Gain [80]-[220] [Science]"]),
            ("Fund the experiment (-60 Gold, a gamble on Science)", ["Gain [-60] [Gold]", "Gain [0]-[250] [Science]", _need(60, "Gold")]),
            ("Insist on more safety tests (+Science)", ["Gain [40] [Science]"]),
        ],
    },
    {
        "name": "Explosive Prototype",
        "text": "KA-BOOM! A prototype has exploded in the workshop. Nobody was hurt, probably, but the neighborhood is a crater.",
        "trigger": _when(2, "<after turn number [30]>"),
        "only": ["Gnomes"],
        "choices": [
            ("Study the crater (+Science, lose population)", ["Gain [80]-[160] [Science]", "[-1] population in a random city"]),
            ("Pay for the repairs (-80 Gold)", ["Gain [-80] [Gold]", _need(80, "Gold")]),
        ],
    },
    {
        "name": "The Wandering Isle's Choice",
        "text": "The great turtle Shen-zin Su is wounded, and our people must choose a path. Aysa Cloudsinger and the Tushui would join the Alliance; Ji Firepaw and the Huojin, the Horde.",
        "trigger": None,             # fired by the Pandaren's own unique, upon entering the Age of the Dark Portal
        "only": ["Pandaren"],
        "choices": [
            ("Follow the Tushui and join the Alliance (defense, +10% vs the Horde)", ["Gain a free [Tushui Monastery] [in capital]"]),
            ("Follow the Huojin and join the Horde (attack, +10% vs the Alliance)", ["Gain a free [Huojin Training Hall] [in capital]"]),
            ("Remain neutral and walk the middle path (+Culture)", ["Gain [150] [Culture]"]),
        ],
    },
]


# v0.18 Mana sink: AIs were banking thousands of Mana. Whenever a civ holds 300+, every
# 5 turns the ley lines swell and it can spend the surplus. The AI is steered away from
# hoarding with a choice weight; a human player may always keep the Mana.
EVENTS += [
    {
        "name": "The Ley Lines Swell",
        "text": "Our Mana stores are brimming, and the ley lines beneath our cities hum with power. "
                "Our magi say such a surplus should be put to use before it slips away into the Nether.",
        "trigger": "<upon turn start> <every [5] turns> <when above [299] [Mana]>",
        "choices": [
            ("Channel it into research (-150 Mana, +Science)",
             _mana(150) + ["Gain [150]-[300] [Science]"]),
            ("Hold a festival of arcane lights (-200 Mana, 4-turn Golden Age)",
             _mana(200) + ["Empire enters a [4]-turn Golden Age"]),
            ("Bless the land (-150 Mana, +Culture and Faith)",
             _mana(150) + ["Gain [100] [Culture]", "Gain [100] [Faith]"]),
            ("Keep the Mana in reserve", ["[-90]% weight to this choice for AI decisions"]),
        ],
    },
]


def json_events():
    out = []
    for e in EVENTS:
        out.append({
            "name": e["name"], "text": e["text"], "presentation": "Alert",
            "civilopediaText": [{"text": e["text"]}],
            "choices": [{"text": t, "uniques": u} for t, u in e["choices"]],
        })
    return out


def triggers(race):
    """Trigger uniques for one major civilization."""
    out = []
    for e in EVENTS:
        if not e["trigger"] or race in e.get("not_for", ()) or ("only" in e and race not in e["only"]):
            continue
        out.append("Triggers a [%s] event %s" % (e["name"], e["trigger"]))
    return out
