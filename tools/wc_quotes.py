"""Tech quotes in Warcraft voices (content pass, Oct 2026).

Unciv shows a technology's "quote" when it is researched. Every line is original, written
in the voice of a Warcraft figure or people; none is copied from the games.
"""

QUOTES = {
    "Farming": "Feed the village first. Glory can wait until the harvest is in. — a Westfall farmer",
    "Pottery": "A clay jar holds more than grain. It holds the winter we survived. — Tauren saying",
    "Beast Taming": "The wolf is not your servant. It is your brother, and it will judge you. — Durotan",
    "Archery": "Breathe out. Let the moon guide the arrow. — Sentinel training lesson",
    "Mining": "Dig deep enough and the mountain tells you its secrets. Dig too deep and it tells you something else. — Ironforge miner",
    "Sailing": "The sea gives, and the sea takes. Respect her, and she gives a little more. — Kul Tiran tidesage",
    "Herbalism": "Peacebloom for the body, silverleaf for the mind, and patience for everything else. — Cenarion herbalist",
    "Runic Script": "The titans wrote the world in runes. We are only learning to read. — Brann Bronzebeard",
    "Skinning": "Waste nothing the hunt gives you. The Earth Mother is watching. — Tauren hunter",
    "The Wheel": "Round, it rolls. Square, it does not. This is the whole of engineering. — Gnomish primer, first page",
    "Masonry": "A wall is only as strong as the hands that laid it and the hearts that guard it. — Stromgarde stonemason",
    "Bronze Working": "Copper and tin, fire and hammer. From such humble things, kingdoms are made. — Dwarven smith",
    "Optics": "Look further, and you will see your enemy before he sees you. — Farstrider proverb",
    "Riding": "A good mount will carry you through fire. A bad one will carry you into it. — Stormwind stablemaster",
    "Mathematics": "Numbers do not lie. Accountants, however... — Goblin trade prince",
    "Construction": "Build it to last a thousand years, and it might survive the next war. — Alliance engineer",
    "Philosophy": "Before you can command the arcane, you must first command yourself. — Archmage Antonidas",
    "Bardic Lore": "Sing of the fallen, so that the living remember why they fight. — Darnassian lorekeeper",
    "Coinage": "Gold is the only language every race speaks fluently. — Steamwheedle Cartel motto",
    "Engineering": "If it explodes, it was a learning experience. If it doesn't, it was a success. — Gelbin Mekkatorque",
    "Iron Forged Swords": "Iron does not care who swings it. Make sure it is you. — Orc blademaster",
    "Priesthood": "The Light asks only that we remain steadfast. It is enough, and it is everything. — Northshire priest",
    "Arathi Law": "A kingdom of laws outlives any king. — Thoradin, first King of Arathor",
    "Trade Guilds": "One merchant is a target. A hundred merchants are a guild, and guilds have guards. — Stormwind trade charter",
    "Blacksmithing": "Strike while the iron is hot, and strike again while it is cooling. — Thorium Brotherhood smith",
    "Seafaring": "Beyond the horizon lie new lands, old enemies and better fishing. — Booty Bay captain",
    "Scholarship": "Knowledge hoarded is knowledge lost. Share it, and it multiplies. — Lorewalker Cho",
    "Animal War Training": "The kodo does not fear the arrow, so neither should its rider. — Tauren war chief",
    "Clockwork": "Wind it up, set it down, and stand well back. — Gnomish tinker",
    "Siege Engineering": "Every wall has a weakness. Usually it is the gate. — Horde siege master",
    "Steel Forged Swords": "Steel holds an edge. So must the warrior who carries it. — Varian Wrynn",
    "Astronomy": "The stars are the oldest map of all. The night elves have been reading it for ten thousand years. — Tyrande Whisperwind",
    "Choral Hymns": "When a thousand voices sing to the Light, even the dead stop to listen. — Cathedral of Light chorister",
    "Banking": "Deposit your gold with us and sleep soundly. We certainly will. — Gadgetzan banker",
    "Inscription": "A glyph is a spell that waits patiently. — Dalaran scribe",
    "Blackpowder": "Point the loud end at the enemy. — Ironforge rifle drill, lesson one",
    "Navigation": "A Kul Tiran never gets lost. We simply discover new places we did not intend to visit. — Daelin Proudmoore",
    "Architecture": "Build a spire high enough and the gods themselves will notice. — Quel'Thalas architect",
    "Auctioneering": "Going once, going twice... sold to the goblin in the back with too much gold! — Auction House barker",
    "Mithril Forged Swords": "Mithril is light as a feather and hard as a dragon's scale. It is also very expensive. — Dwarven armorer",
    "Alchemy": "Every potion is a question. Some answer it. Some explode. — Royal Apothecary Society",
    "Archaeology": "Every ruin is a letter from the past. Most are complaints. — Harrison Jones",
    "Arcane Science": "Magic is not a mystery. It is a discipline. — Jaina Proudmoore",
    "Steamworks": "Steam, gears and a little bit of fire. What could possibly go wrong? — Goblin engineer",
    "Long Rifles": "Aim small, miss small. — Gilnean marksman",
    "War Doctrine": "Plans survive until the first arrow flies. Prepare anyway. — Anduin Lothar",
    "Soil Enrichment": "Feed the land, and the land feeds you. Poison it, and you starve together. — Cenarion druid",
    "Natural Lore": "The forest remembers every footstep. Walk lightly. — Malfurion Stormrage",
    "Storm Hammers": "Throw the hammer. Call it back. Throw it again. Repeat until the enemy stops. — Muradin Bronzebeard",
    "Steam Power": "The kettle sings, and the engine roars. — Gnomeregan workshop sign",
    "Seaforium": "Handle with care. Then handle with more care. Then run. — Goblin demolitions crew",
    "Frost Enchantment": "Cold is patient. Cold always wins. — Frostwolf shaman",
    "Communication Crystals": "Speak into the crystal. Clearly. No, the other end. — Kirin Tor apprentice",
    "Gnomish Gearworks": "Small gears turn big wheels. Small gnomes build big machines. — Gnomish engineering motto",
    "Gnomish Flight": "Up is the easy part. Down is where we need more work. — Gnomish test pilot",
    "Tramways": "The Deeprun Tram: because tunnelling under the sea seemed sensible at the time. — Ironforge engineer",
    "Arcanite Alloys": "Arcanite is what happens when you ask the arcane to hold still. — Thorium Brotherhood smith",
    "Arcane Conduits": "Channel the ley lines, and a city never sleeps. — Silvermoon magister",
    "Fragmentation Shards": "It is not the explosion that gets you. It is all the little pieces. — Dark Iron demolitionist",
    "Liquid Fire": "Burn the field, and the enemy has nowhere to stand. — Blood Elf battlemage",
    "Elixir Mastery": "Drink this. Do not ask what is in it. — Goblin alchemist",
    "Mana Theory": "Mana is the blood of magic. Spill too much, and something hungry will come to drink it. — Khadgar",
    "Scrying": "Peer into the orb and see what the enemy plans. Try not to let it see you back. — Dalaran seer",
    "Battle Formations": "A line of shields is a wall that walks. — Alliance drill sergeant",
    "Nature's Blessing": "Ask the trees for help, and they will answer. Slowly. — Keeper of the Grove",
    "Unstable Mana": "Never store it near anything you would miss. — Mana Bomb project notes",
    "Demolition": "If you can't go through it, blow it up. If you can go through it, blow it up anyway. — Goblin sapper",
    "Titan Logic": "The titans built the world as a machine. Now we are learning how to repair it. — Keeper Loken's records",
    "Portal Networks": "Step through a portal in Stormwind, step out in Dalaran. Keep your arms and legs inside. — Portal trainer",
    "War Drums": "When the drums beat, every orc remembers who he is. — Thrall",
    "Siege Barrage": "Bring every cannon. Then bring more. — Horde siege commander",
    "Eye of Kilrogg": "What the eye sees, the warlock knows. — Gul'dan",
    "Mechagnomics": "Flesh is weak. Gears are forever. — King Mechagon",
    "Focused Arcana": "A single beam of focused will can split a mountain. Please do not split our mountain. — Kirin Tor lecturer",
    "Azerothian Unity": "Alliance and Horde, standing together. Who would have believed it? — Baine Bloodhoof",
    "Azerite Refinement": "Azeroth bleeds Azerite. We must decide what to do with her blood. — Magni Bronzebeard",
    "Titanforging": "Forge as the titans forged, and what you make will outlast the stars. — Keeper of Ulduar",
    "Ethereal Technology": "Everything has a price, even the impossible. — Consortium broker",
    "Invisibility": "You cannot strike what you cannot see. That is the whole point. — Ravenholdt master",
    "Secrets of the Void": "Gaze into the Void, and it gazes back, and whispers your name. — Xal'atath",
}


def apply(techs):
    """Set the quote of every tech that has one here; return how many."""
    n = 0
    for col in techs:
        for t in col.get("techs", []):
            if t["name"] in QUOTES:
                t["quote"] = QUOTES[t["name"]]
                n += 1
    return n
