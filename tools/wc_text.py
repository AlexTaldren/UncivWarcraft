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
