"""Victory and defeat screens, and the city-state messages Unciv writes itself (Oct 2026).

Two parts:
  VICTORY  - per victory type: the header, the victory text and the defeat text
             (VictoryTypes.json fields). build.py applies them with apply_victories().
  ENGLISH  - English text for strings that are built into Unciv rather than read from the
             ruleset: the victory/defeat banners, city-state notifications and the city-states'
             replies to tribute demands. A mod's jsons/translations/English.properties replaces
             these for English players while the mod is in play (tested with the game's own
             Translations class). Keys must match Unciv's template exactly, placeholders included.
City-states have no greeting lines of their own beyond the four per nation in wc_factions
(introduction, declaringWar, attacked, defeated); Unciv uses neutralHello/hateHello only for
major civilizations, so the shared messages below are where city-states speak otherwise.
All text is original.
"""
import os

VICTORY = {
    "Scientific": (
        "Build the Titan Ascension Project and assemble the Titan vessel to win!",
        "The Titan vessel rises on a column of arcane fire, and Azeroth watches in silence. Your "
        "artificers and magi have unlocked what the makers left behind, and your people sail beyond "
        "the Great Dark to stand among the stars. The bards will need new songs; the old ones are too small.",
        "Another people's vessel has climbed into the sky, carrying the secrets of the Titans with it. "
        "Your workshops fall quiet and your scholars burn their notes. Yet the stars are patient, and "
        "so are your people. One day they will build again, and follow."),
    "Cultural": (
        "Complete 5 policy branches and restore the Well of Eternity to win!",
        "The Well of Eternity shines again, and its light carries your name to every corner of Azeroth. "
        "Your poets, priests and loremasters have done what no army could: the world now sings your songs, "
        "keeps your holy days and tells your histories as its own.",
        "The Well of Eternity has been restored, but not by your hand. Your songs are fading from the "
        "taverns and your libraries gather dust. Still, a story is never truly lost while one keeper "
        "remembers it. Your people will tell it again."),
    "Domination": (
        "Capture all enemy Capitals to win!",
        "The banners of every rival capital lie torn at your feet. From the frozen wastes of Northrend to "
        "the sands of Tanaris, one power rules Azeroth, and it is yours. Let the war drums fall silent. "
        "There is no one left to answer them.",
        "Your capital has fallen and your banners burn. Your armies are scattered across Azeroth, and "
        "the conquerors write the histories now. But in hidden valleys and forgotten caves, your people "
        "sharpen their blades and wait for the day of reckoning."),
    "Diplomatic": (
        "Build the Grand Council of Azeroth and be voted its leader to win!",
        "The Grand Council of Azeroth has spoken, and every banner in the hall dips toward yours. Alliance, "
        "Horde and all who stand between have chosen you to lead them. You have won the world without a "
        "single siege, and your enemies are left wondering when they lost.",
        "The Grand Council of Azeroth has chosen another to lead. Your envoys return home with empty "
        "hands and bitter words. But councils change their minds, and alliances are never made of stone. "
        "Your people will be heard again."),
    "Time": (
        None,
        "The ages have turned, and when the sands of time settle, your people stand tallest. No "
        "dragonflight, no prophet and no conqueror can deny it: this era of Azeroth belongs to you.",
        "The ages have turned, and the chronicles of Azeroth name another people as the greatest of this "
        "era. Your people endure, and the Timeways are long. Their hour will come."),
}


def apply_victories(victory_types):
    for v in victory_types:
        if v["name"] not in VICTORY:
            continue
        header, win, lose = VICTORY[v["name"]]
        if header:
            v["victoryScreenHeader"] = header
        v["victoryString"] = win
        v["defeatString"] = lose
    return victory_types


ENGLISH = {
    # ---- victory screen
    "You have won a [victoryType] Victory!": "Azeroth is yours! A [victoryType] Victory!",
    "[civilization] has won a [victoryType] Victory!": "[civilization] has claimed Azeroth with a [victoryType] Victory!",
    "Your civilization stands above all others! The exploits of your people shall be remembered until the end of civilization itself!":
        "Your people stand above all others! Their deeds will be sung in every hall and longhouse until the last sun sets on Azeroth!",
    "You have been defeated. Your civilization has been overwhelmed by its many foes. But your people do not despair, for they know that one day you shall return - and lead them forward to victory!":
        "You have been defeated. Your people have been overwhelmed by their many foes. But they do not despair, for they know that one day you shall return, and lead them forward to victory!",
    # ---- meeting and losing city-states
    "We have encountered the City-State of [name]!": "Our scouts have reached the free city of [name]!",
    "The City-State of [name] has been destroyed!": "The free city of [name] has been razed! Only ash and ruin remain.",
    "[cityStateName] gave us a [unitName] as a gift!": "[cityStateName] has sent us a [unitName] in token of friendship!",
    "[civName] gave us a [unitName] as gift near [cityName]!": "[civName] has sent us a [unitName], now waiting near [cityName]!",
    # ---- city-states answering a demand for tribute
    "We will comply, but our consent is given grudgingly.": "Take it, then. But we will remember who held the knife.",
    "Your demands are in poor taste. We shall decide this matter on our own.": "You speak to us like a warlord to a village. We will decide this ourselves.",
    "Did you really expect us to bend to such brazen demands?": "Bend the knee to you? Our walls have outlasted greater bullies.",
    # ---- city-states asking for help, and thanking you
    "[cityState] is being attacked by [civName] and asks all major civilizations to help them out by gifting them military units.":
        "[cityState] is under siege by [civName]! Their envoys beg the great powers of Azeroth to send soldiers.",
    "[cityState] is being invaded by Barbarians! Destroy Barbarians near their territory to earn Influence.":
        "Raiders are overrunning the lands of [cityState]! Drive the Barbarians from their borders to earn their favor.",
    "[cityState] is grateful that you killed a Barbarian that was threatening them!":
        "[cityState] raises a cup in your name: the raiders at their gates are slain!",
    "[cityState] is being attacked by [civName]! Kill [amount] of the attacker's military units and they will be immensely grateful.":
        "[cityState] is under attack by [civName]! Slay [amount] of the attacker's soldiers and they will not forget it.",
    "[cityState] is deeply grateful for your assistance in the war against [civName]!":
        "[cityState] will sing of your aid in the war against [civName] for generations!",
    "[cityState] no longer needs your assistance against [civName].":
        "[cityState] has made its peace with [civName]. Your blades are no longer needed there.",
    "[cityState] cancelled the quests they had given you because you demanded tribute from them.":
        "[cityState] has torn up the tasks they gave you. Their trust left with the tribute you took.",
    "We need you to help us defend against [civName]. Killing [amount] of their military units would slow their offensive.":
        "Stand with us against [civName]! Slay [amount] of their soldiers and their assault will falter.",
    # ---- quests
    "[civName] assigned you a new quest: [questName].": "[civName] seeks a champion: [questName].",
    "[civName] rewarded you with [influence] influence for completing the [questName] quest.":
        "[civName] honors you with [influence] influence for completing [questName].",
    "[civName] no longer needs your help with the [questName] quest.": "[civName] no longer needs a champion for [questName].",
    "The [questName] quest for [civName] has ended. It was won by [civNames].":
        "The contest of [questName] for [civName] is over. The honor goes to [civNames].",
    # ---- protection and its breaking
    "You have broken your Pledge to Protect [civName]!": "You have broken your oath to protect [civName]! Word of it spreads quickly.",
    "City-States grow wary of your aggression. The resting point for Influence has decreased by [amount] for [civName].":
        "The free cities whisper of the warmongering of [civName]. The regard they settle back to falls by [amount].",
    "[civName] is upset that you demanded tribute from [cityState], whom they have pledged to protect!":
        "[civName] is angered that you extorted [cityState], a city sworn to their protection!",
    "[civName] is upset that you attacked [cityState], whom they have pledged to protect!":
        "[civName] is angered that you attacked [cityState], a city sworn to their protection!",
    "[civName] is upset that you attacked [cityState], whom they are allied with!":
        "[civName] is angered that you attacked [cityState], their sworn ally!",
    "[civName] is outraged that you destroyed [cityState], whom they had pledged to protect!":
        "[civName] swears vengeance: you destroyed [cityState], a city sworn to their protection!",
    "[civName] has destroyed [cityState], whom you had pledged to protect!":
        "[civName] has destroyed [cityState], a city you swore to protect!",
    "We have married into the ruling family of [civName], bringing them under our control.":
        "A royal wedding binds the house of [civName] to ours. Their city now flies our banner.",
    "[civName] has married into the ruling family of [civName2], bringing them under their control.":
        "[civName] has wed into the ruling house of [civName2]. That city now flies their banner.",
}


def write_english(jsons_dir):
    """Write jsons/translations/English.properties (Unciv's key = value format)."""
    out = os.path.join(jsons_dir, "translations")
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, "English.properties")
    with open(path, "w", encoding="utf-8") as f:
        f.write("# UncivWarcraft: Warcraft wording for messages built into Unciv (English players)\n")
        for k, v in ENGLISH.items():
            f.write("%s = %s\n" % (k, v))
    return len(ENGLISH)
