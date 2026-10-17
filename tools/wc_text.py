"""Warcraft wording for ancient ruins rewards, city-state quests, city-state types and
specialists (v0.10). Bracketed placeholders ([cityName], [techName] ...) are filled in by
the game and must stay exactly as they are.
"""

RUINS = {   # Ruins.json name -> notification
    "discover cultural artifacts": "Among the ruins we find carved tablets of a forgotten people. Our scholars will study them for years! (+20 culture)",
    "squatters willing to work for you": "A [Peasant] sheltering in the ruins offers to work for us!",
    "squatters wishing to settle under your rule": "Refugees in the ruins ask to found a town under our banner. A [Settler] has joined us!",
    "your exploring unit receives training": "The spirits of fallen warriors haunting the ruins teach our explorer their ways of battle!",
    "survivors (adds population to a city)": "We have found survivors of a fallen village in the ruins. They make their home in [cityName].",
    "discover a lost technology": "Titan-forged machinery in the ruins reveals the lost secrets of [techName]!",
    "advanced weaponry for your explorer": "Our explorer finds a cache of old weapons hidden in the ruins!",
    "reveal nearby Barbarian camps": "Red bandanas and murloc tracks: there are raiders nearby. Their camps are revealed!",
    "find a crudely-drawn map": "We have found a crumpled map of the region, signed by an Explorers' League surveyor!",
    "discover holy symbols": "Ancient holy symbols in the ruins deepen our understanding of the faith! (+[faithAmount] Faith)",
    "an ancient prophecy": "A prophecy carved in the ruins speaks of our people's destiny, and stirs their faith! (+[faithAmount] Faith)",
}

QUESTS = {   # Quests.json name -> description
    "Route": "Build a road to connect your capital to our city, so that caravans may travel safely between us.",
    "Clear Barbarian Camp": "Raiders have made camp near our city: Defias, gnolls or worse. Please drive them out.",
    "Connect Resource": "To make our peoples stronger, connect [tileResource] to your trade network.",
    "Construct Wonder": "Build [wonder], and let all of Azeroth see the strength of your people.",
    "Acquire Great Person": "Heroes change the course of history! You will be rewarded for gaining a new [greatPerson].",
    "Conquer City State": "The city of [cityState] has wronged us for the last time. Wipe them from the map and you will be well rewarded.",
    "Find Player": "We have not yet found where [civName] built their cities. You will be rewarded for finding their lands.",
    "Find Natural Wonder": "Send your best explorers into the wilds. Nobody has yet found [naturalWonder].",
    "Give Gold": "Raiders sent by [civName] have plundered our coffers. Unless we receive some Gold, our city will not survive.",
    "Pledge to Protect": "We need your protection against the aggression of [civName]. Pledge to protect us and seal the bond between our peoples.",
    "Contest Culture": "The people whose culture grows the most will receive a reward.",
    "Contest Faith": "The people whose faith grows the most will receive a reward.",
    "Contest Technologies": "The people who make the most new discoveries will receive a reward.",
    "Invest": "The Darkmoon Faire has come to our city, and coin is flowing! For a while, any Gold donation will yield [50]% extra Influence.",
    "Bully City State": "We are tired of the airs of [cityState]. Whoever puts them in their place by demanding tribute will be rewarded.",
    "Denounce Civilization": "We have been forced to pay tribute to [civName]! Tell all of Azeroth of their misdeeds.",
    "Spread Religion": "We have heard the teachings of [religionName] and are curious. Will you send missionaries to teach us?",
}

# City-state types. "Militaristic" and "Mercantile" are kept: Unciv's own rule texts name
# them ("Militaristic City-States grant units...", "Can only be created by Mercantile
# City-States"), so renaming them would make those lines wrong.
CS_TYPES = {
    "Cultured": "Lorekeeper",
    "Maritime": "Harbor",
    "Religious": "Sacred",
}

SPECIALISTS = {
    "Scientist": "Arcanist",
    "Merchant": "Trader",
    "Artist": "Bard",
    "Engineer": "Tinker",
}

CS_TYPE_TEXT = {
    "Lorekeeper": "Cities of scholars and storytellers, like the Lorewalkers of Pandaria. Friends gain Culture.",
    "Harbor": "Port cities living from the sea, like Ratchet and Booty Bay. Friends gain Food.",
    "Mercantile": "Trading cities of goblins and merchant princes. Friends gain Happiness, and they trade rare luxuries.",
    "Militaristic": "Fortress cities and mercenary companies. Friends receive troops.",
    "Sacred": "Holy cities and pilgrim sites. Friends gain Faith.",
}

# City-state voices: (declaring war, attacked, defeated, introduction)
CS_DIALOGUE = {
    "Dalaran": ("The Kirin Tor have judged you a threat. The Violet Citadel goes to war.",
                "You dare raise a hand against Dalaran? The archmagi will remember this.",
                "Dalaran has fallen before... and it always rises again.",
                "Greetings from the Kirin Tor. Dalaran's doors are open to all who seek knowledge."),
    "Theramore": ("Jaina's patience has run out. Theramore's guard marches against you.",
                  "Theramore was built for peace, but it will defend itself.",
                  "Theramore's towers burn... again.",
                  "Welcome to Theramore, where Alliance and Horde may yet find peace."),
    "Stromgarde": ("By the blood of Thoradin, Stromgarde will see you broken!",
                   "Stromgarde has held these highlands for a thousand years. We will not yield.",
                   "Arathor's last kingdom falls silent.",
                   "Stromgarde greets you. We are the heirs of Arathor, the first kingdom of men."),
    "Gadgetzan": ("Bad for business, friend. Real bad. The Water Barons are coming for you.",
                  "Hey! Attacking a neutral town? There'll be a bill for this.",
                  "The bank's closed. Permanently.",
                  "Welcome to Gadgetzan! Everything's for sale, and the bruisers keep the peace."),
    "Booty Bay": ("The Blackwater Raiders are hoisting the black flag. Run while you can!",
                  "You'll be swimming with the sharks for this, landlubber!",
                  "The bay is yours. Watch out for the sharks.",
                  "Ahoy! Welcome to Booty Bay. Mind your purse and your back."),
    "Ratchet": ("Ratchet's pulling its contracts. Expect the bruisers.",
                "You hit our docks? You're paying for the repairs!",
                "Ratchet's docks go quiet.",
                "Ratchet welcomes you! Best port on the Barrens coast, and the only one."),
    "Everlook": ("Everlook is closing its gates to you, and opening its armories.",
                 "Out here the cold kills fools. So do we.",
                 "The snows of Winterspring cover Everlook.",
                 "Everlook greets you. Warm drinks, fair prices, and the only fire for miles."),
    "Steamwheedle Port": ("The Cartel has voted. You're a liability.",
                          "An attack on Steamwheedle Port is an attack on the whole Cartel!",
                          "The Cartel cuts its losses.",
                          "Steamwheedle Port, open for business! Neutral ground, as long as you pay."),
    "Light's Hope Chapel": ("The Light will judge you. The Argent Dawn rides.",
                            "We stood against the Scourge. We will stand against you.",
                            "Even now, the Light endures.",
                            "Be welcome at Light's Hope Chapel, last bastion against the Scourge."),
    "Cenarion Hold": ("The Cenarion Circle will defend the balance of nature against you.",
                      "You bring blood to sacred ground. The druids will answer.",
                      "The Hold falls, but the Circle endures.",
                      "Cenarion Hold greets you. We watch the gates of Ahn'Qiraj so that others may sleep."),
    "Argent Vanguard": ("The Argent Crusade marches against you!",
                        "We came north to fight the Lich King, not you. But we will.",
                        "The Vanguard's banners fall in the snow.",
                        "The Argent Vanguard stands at the gates of Icecrown. Will you join the crusade?"),
    "Feathermoon Stronghold": ("The Sentinels of Feathermoon nock their arrows. You are their target.",
                               "Elune guide our arrows against you.",
                               "Feathermoon falls under the shadow of the moon.",
                               "Ishnu-alah. Feathermoon Stronghold watches over the wilds of Feralas."),
    "The Earthen Ring": ("The elements are out of balance, and you are the cause. The Earthen Ring will set it right.",
                         "Fire, earth, wind and water rise against you!",
                         "The elements fall silent... for now.",
                         "The Earthen Ring greets you. We are the shamans who keep the elements in balance."),
    "Knights of the Ebon Blade": ("Death knights do not forgive. The Ebon Blade rides against you.",
                                  "You would cross runeblades with the Ebon Blade? So be it.",
                                  "Even death knights can die twice.",
                                  "We are the Knights of the Ebon Blade, free of the Lich King's will. State your purpose."),
    "Explorers' League": ("Ye've wrecked yer last dig site. The League's coming for ye!",
                          "Hands off the artifacts!",
                          "The digs are buried... we'll be back.",
                          "Welcome to the Explorers' League! Mind the rope and don't touch anything old."),
    "Thorium Brotherhood": ("The Brotherhood is done with ye. Our forges now make weapons for yer enemies.",
                            "Strike the Brotherhood and ye strike the hottest forges in Azeroth!",
                            "Thorium Point's fires go out.",
                            "The Thorium Brotherhood welcomes ye. We're the finest smiths outside Blackrock, and we left them for good reason."),
}
