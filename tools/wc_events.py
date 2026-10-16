"""Random events from Warcraft lore (v0.10).

Each event pops up for the civ it happens to, with a few choices; the AI picks for
itself. They're triggered from GlobalUniques: a small chance every other turn, limited
to the eras the story belongs to. Names here are the mod's own (after renames).
"""

# How often: <every [2] turns> <with [n]% chance> gives about n/2 % per turn per civ.
def _when(chance, *extra):
    return " ".join(["<upon turn start>", "<every [2] turns>", "<with [%d]%% chance>" % chance] + list(extra))


def _need(amount, stat):
    return "Only available <when above [%d] [%s]>" % (amount - 1, stat)


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


def json_events():
    out = []
    for e in EVENTS:
        out.append({
            "name": e["name"], "text": e["text"], "presentation": "Alert",
            "civilopediaText": [{"text": e["text"]}],
            "choices": [{"text": t, "uniques": u} for t, u in e["choices"]],
        })
    return out


def triggers():
    return ["Triggers a [%s] event %s" % (e["name"], e["trigger"]) for e in EVENTS]
