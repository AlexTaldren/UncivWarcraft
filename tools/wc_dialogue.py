"""Leader dialogue, written in each faction's own voice (Oct 2026 pass).

Unciv gives every leader one line per situation: declaring war, being attacked, being
defeated, the first meeting, a neutral and a hostile greeting, and a trade offer.
build.py applies these over the lines in wc_factions. The opening narration
(startIntroPart1/2) stays in wc_factions.

Voices: Anduin's reluctant idealism, Thrall's blunt honour and Orcish, Tyrande's
ancient sternness and Darnassian, the Dwarves' and Dark Irons' brogue, Gnomish
technobabble, Cairne's calm, Darkspear and Zandalari troll speech and loa, Blood Elf
pride, High Elf aloofness, Pandaren proverbs, Sylvanas's cold menace, Velen's
prophecy, Goblin salesmanship, Gilnean grit, the Lich King's dominion and Kul Tiran
sea-talk. All lines are original; only in-world words (Lok'tar, Ishnu-alah, Bal'a
dash...) come from the setting.
"""

FIELDS = ("declaringWar", "attacked", "defeated", "introduction", "neutralHello", "hateHello", "tradeRequest")


def _d(war, attacked, defeated, intro, hello, hate, trade):
    return dict(zip(FIELDS, (war, attacked, defeated, intro, hello, hate, trade)))


DIALOGUE = {
    "Humans": _d(
        "I hoped it would never come to this. For Stormwind, and for the Light, we march.",
        "You mistake mercy for weakness. The Lion of Stormwind still has teeth.",
        "Then let the Light judge between us... Stormwind yields.",
        "I am Anduin Wrynn, High King of Stormwind. I would sooner build bridges than walls. Shall we?",
        "Well met, and may the Light keep you.",
        "I am trying to see the good in you. You make it very difficult.",
        "The markets of Stormwind are full to bursting. Let us both prosper."),
    "Orcs": _d(
        "Lok'tar ogar! The drums of the Horde beat for war!",
        "You strike at the Horde? Then you will face it, blade to blade.",
        "Our strength is spent... but the spirits will sing of how we fell.",
        "I am Thrall, son of Durotan, Warchief of the Horde. Speak plainly. Orcs have no patience for honeyed words.",
        "Throm-ka. The Horde sees you.",
        "Kagh! You test the patience of the Horde.",
        "Durotar's soil is harsh, but its hands are strong. Trade with us, and trade honestly."),
    "Night Elves": _d(
        "Elune guide my arrows. The Sentinels ride against you.",
        "You spill blood beneath the boughs of Ashenvale? Elune's wrath will find you.",
        "The groves fall silent... Elune, receive your children.",
        "I am Tyrande Whisperwind, High Priestess of Elune. These forests are older than your kingdoms. Tread lightly.",
        "Ishnu-alah, stranger.",
        "You are not welcome beneath these boughs.",
        "The Kaldorei have moonwell water and moonglow ink. What would you offer for them?"),
    "Dwarves": _d(
        "Right, that's done it! Sound the horns, lads, Ironforge marches!",
        "Ye've picked a fight wi' the wrong mountain, laddie!",
        "Ach... the forges go cold. Ironforge is yours. Treat her well.",
        "Magni Bronzebeard, King o' Ironforge! Pull up a stool, the ale's on me.",
        "Well met, friend! Ye look like ye could use a pint.",
        "Ach, you again. Say yer piece an' be gone.",
        "Our forges never sleep an' our kegs are never dry. Fancy a trade?"),
    "Gnomes": _d(
        "Engaging battle protocols! Mechanostriders, forward! For Gnomeregan!",
        "A flagrant violation of every safety regulation! You'll pay for that!",
        "Catastrophic... systems... failure. Back to the drawing board.",
        "High Tinker Gelbin Mekkatorque, delighted! Mind the gears, and don't touch anything that ticks.",
        "Salutations! Lovely day for an experiment, isn't it?",
        "Oh. You. My calculations predicted this would be unpleasant.",
        "I've a brand-new gizmo you simply must have. Only slightly explodey. Shall we trade?"),
    "Tauren": _d(
        "The drums of Thunder Bluff call us to war. May the Earth Mother forgive what we must do.",
        "You draw blood on sacred ground? The Earth Mother will not forgive it.",
        "Our hooves grow still... we return to the earth that bore us.",
        "I am Cairne Bloodhoof, High Chieftain of the tauren. Sit, traveler. The winds of Mulgore welcome all who come in peace.",
        "Walk with the Earth Mother, friend.",
        "The spirits grow restless when you are near.",
        "The plains of Mulgore are generous: kodo hide, plainstrider feathers. What do you bring in return?"),
    "Trolls": _d(
        "Da Darkspear be comin' for ya, mon. Da loa already know how dis ends.",
        "Ya made a big mistake, mon. Da Darkspear never forget.",
        "Bwonsamdi be waitin'... tell him Vol'jin be comin' soon.",
        "I be Vol'jin, chieftain of da Darkspear. Speak true, mon. Da spirits be listenin'.",
        "Da loa be smilin' on ya today, mon.",
        "Ya be testin' Vol'jin's patience. Careful now.",
        "Got spices from Stranglethorn an' charms from da Echo Isles. Wanna make a deal, mon?"),
    "Blood Elves": _d(
        "Silvermoon has endured worse than you. Magisters, Blood Knights: to war.",
        "You strike at Quel'Thalas? We have buried greater foes than you.",
        "Silvermoon falls... again. Perhaps this time no one will be left to remember.",
        "Lor'themar Theron, Regent Lord of Quel'Thalas. You may speak.",
        "Bal'a dash, malanore.",
        "Must I endure you again? Be brief.",
        "Silvermoon's enchanters sell only the finest. Can you afford it?"),
    "High Elves": _d(
        "The rangers of Eversong will see you fall. Quel'Thalas stands alone, as it always has.",
        "You dare assail the eternal kingdom? Foolish, short-lived thing.",
        "The runestones fail... the light of Quel'Thalas dims.",
        "I am Anasterian Sunstrider, King of Quel'Thalas. We have little need of outsiders, but I will hear you.",
        "Shorel'aran. State your purpose.",
        "Your presence offends the light of the Sunwell.",
        "Our artisans may part with a few treasures, if your coin is worthy of them."),
    "Pandaren": _d(
        "When balance cannot be kept with an open hand, it must be kept with a closed fist.",
        "You stir the waters of a still pool. Do not be surprised when the mud rises.",
        "The mists close... may the Celestials guide what remains.",
        "I am Shaohao, Emperor of Pandaria. Sit, share a cup of tea, and let us speak without haste.",
        "Peace, friend. The tea is warm.",
        "Hmm. Some guests are like rain on a festival day.",
        "Our brewmasters have opened a fine new barrel. Shall we trade, and share it?"),
    "Forsaken": _d(
        "The Forsaken have no fear of death. You will learn to.",
        "Your mistake. We will add your dead to our ranks.",
        "Darkness again... I know it well.",
        "I am Sylvanas Windrunner, the Banshee Queen. Choose your words carefully, living one.",
        "Speak. My patience is not as endless as my years.",
        "Leave me, mortal, before I decide you are more useful dead.",
        "The apothecaries have need of certain... materials. What can you offer the Forsaken?"),
    "Draenei": _d(
        "The Light has shown me this path, and I grieve to walk it. The Vindicators march.",
        "You have chosen the darkness. The Naaru's light will answer.",
        "We have fled before... we will endure. We always have.",
        "I am Velen, Prophet of the draenei. I have seen your coming in visions. Be welcome.",
        "May the Naaru light your path.",
        "I sense shadow in your heart.",
        "The Exodar can spare crystals of rare purity. Shall we trade?"),
    "Goblins": _d(
        "Nothin' personal, pal. Business is business, and business says WAR!",
        "Oh, you're gonna pay for that. With interest. Compounded daily!",
        "Worst... investment... ever.",
        "Trade Prince Jastor Gallywix! Pleasure doin' business with ya. Probably.",
        "Time is money, friend. Whaddya want?",
        "You again? You're bad for business.",
        "Have I got a deal for you! Limited time offer, act now!"),
    "Worgen": _d(
        "Gilneas will have its vengeance! Let the beasts run free!",
        "You'll feel the fury of the worgen, man and wolf alike!",
        "Gilneas... I have failed you a second time.",
        "I am Genn Greymane, King of Gilneas. Mind your manners. Some of my people bite.",
        "Good day. Keep your torches lowered, if you please.",
        "You again. The wolf in me would like a word with you.",
        "Gilneas is open for trade, for now. Do not make me regret it."),
    "Scourge": _d(
        "The dead rise at my command. None will be spared.",
        "You strike at the Lich King? Then you will serve him in death.",
        "The throne... is cold... so cold...",
        "I am Arthas, the Lich King. Kneel, or be raised to kneel.",
        "The Lich King sees you. For now, that is all.",
        "Your soul will make a fine addition to my army.",
        "The Scourge needs nothing from the living. But it may amuse me to deal."),
    "Dark Iron Dwarves": _d(
        "The forges o' Shadowforge burn for war now. Ye brought this on yerselves.",
        "Ye'll burn for that! Every last one o' ye!",
        "Shadowforge falls dark... but Dark Iron doesnae break. It only cools.",
        "Moira Thaurissan, Queen o' the Dark Irons and voice o' the Council o' Three Hammers. Mind who ye're addressin'.",
        "Aye, well met. Don't dawdle.",
        "Hmph. You. Speak yer piece an' be gone.",
        "Black iron an' fire-forged steel, finest under the mountain. What's yer offer?"),
    "Kul Tirans": _d(
        "The Admiralty has made its decision. Raise the anchors and run out the guns!",
        "You'll regret crossing Kul Tiras. The sea remembers every slight.",
        "The tide goes out on Kul Tiras... but it always comes back in.",
        "I am Jaina Proudmoore, Lord Admiral of Kul Tiras. Our ships sail everywhere. Let's see if yours are welcome.",
        "Fair winds and following seas.",
        "State your business. The tide won't wait, and neither will I.",
        "Boralus has holds full of cargo. Name your price, and let's not haggle all day."),
    "Zandalari Trolls": _d(
        "The Golden Empire marches! Your blood will feed the loa!",
        "You strike at Zandalar? Rezan will see you torn apart.",
        "Dazar'alor falls... Bwonsamdi, you will have your due.",
        "I am Talanji, Queen of the Zandalari Empire. Bow, and we may speak as equals... almost.",
        "The Zandalari acknowledge you.",
        "You again. The loa turn their faces from you, and so do I.",
        "The treasuries of Dazar'alor are deep. What could you possibly offer us?"),
}


def apply(nations):
    """Overwrite the leader lines of each major nation dict (by nation name)."""
    for n in nations:
        n.update(DIALOGUE.get(n["name"], {}))
    return nations
