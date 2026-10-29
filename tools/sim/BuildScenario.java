import com.unciv.UncivGame;
import com.unciv.logic.GameInfo;
import com.unciv.logic.GameStarter;
import com.unciv.logic.civilization.*;
import com.unciv.logic.civilization.diplomacy.*;
import com.unciv.logic.map.mapunit.MapUnit;
import com.unciv.logic.map.tile.Tile;
import com.unciv.models.metadata.*;
import com.unciv.models.ruleset.*;
import com.unciv.models.ruleset.unique.*;
import com.unciv.models.tilesets.TileSetCache;

import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;

/** Builds the mod's scenarios (saved games in the mod's scenarios/ folder, offered under New Game > Scenario).
 *  Run with the working directory containing jsons/ (from Unciv.jar) and mods/UncivWarcraft (with its maps).
 *  args: out_dir   (writes "The Third War", "The Cataclysm", "Battle for Azeroth", "Alliance versus Horde",
 *                   "The Legion Invasion", "Mists of Pandaria", "Wrath of the Lich King")
 *  Each scenario: a lore moment on the Azeroth map, in its age, every capital already founded,
 *  lore armies, the wars of the time, and an opening message for every faction. The player picks
 *  which faction to play in the New Game screen; the rest are computer players. */
public class BuildScenario {
    static final String[] ALLIANCE = {"Humans", "Night Elves", "Dwarves", "Gnomes", "High Elves", "Draenei", "Worgen", "Dark Iron Dwarves", "Kul Tirans"};
    static final String[] HORDE = {"Orcs", "Tauren", "Trolls", "Blood Elves", "Forsaken", "Goblins", "Zandalari Trolls"};
    static final String[] HORDE_ALL = {"Orcs", "Tauren", "Trolls", "Blood Elves", "Forsaken", "Goblins", "Zandalari Trolls",
            "Nightborne", "Highmountain Tauren"};

    static GameInfo gi;

    static Civilization civ(String name) {
        for (Civilization c : gi.getCivilizations()) if (c.getCivName().equals(name)) return c;
        return null;
    }

    static List<MapUnit> units(Civilization c) {
        List<MapUnit> l = new ArrayList<>();
        for (MapUnit u : kotlin.sequences.SequencesKt.asIterable(c.getUnits().getCivUnits())) l.add(u);
        return l;
    }

    static void foundCapitals() {
        for (Civilization c : gi.getCivilizations()) {
            if (c.isBarbarian() || c.isSpectator()) continue;
            for (MapUnit u : units(c)) if (u.getName().equals("Settler")) {
                com.unciv.logic.map.mapunit.actions.UnitActions.INSTANCE.invokeUnitAction(u, com.unciv.models.UnitActionType.FoundCity);
                break;
            }
        }
    }

    static void give(String civName, String... unitNames) {
        Civilization c = civ(civName);
        if (c == null || c.getCities().isEmpty()) return;
        for (String n : unitNames) c.getUnits().placeUnitNearTile(c.getCapital(false).getLocation(), n);
    }

    static void meetAll() {
        List<Civilization> majors = new ArrayList<>();
        for (Civilization c : gi.getCivilizations()) if (c.isMajorCiv() && !c.isSpectator()) majors.add(c);
        for (Civilization a : majors) for (Civilization b : majors) if (a != b && !a.knows(b))
            a.getDiplomacyFunctions().makeCivilizationsMeet(b, false);
    }

    static void war(String a, String b) {
        Civilization ca = civ(a), cb = civ(b);
        if (ca == null || cb == null) return;
        if (!ca.knows(cb)) ca.getDiplomacyFunctions().makeCivilizationsMeet(cb, false);
        DiplomacyManager dm = ca.getDiplomacy().get(b);
        if (!ca.isAtWarWith(cb)) dm.declareWar(new DeclareWarReason(WarType.DirectWar, null));
        // the wars of the moment last: neither side's AI offers peace for the first 30 turns
        dm.setFlag(DiplomacyFlags.DeclinedPeace, 30, false);
        cb.getDiplomacy().get(a).setFlag(DiplomacyFlags.DeclinedPeace, 30, false);
    }

    static void friends(String a, String b) {
        Civilization ca = civ(a), cb = civ(b);
        if (ca == null || cb == null || ca.isAtWarWith(cb)) return;
        if (!ca.knows(cb)) ca.getDiplomacyFunctions().makeCivilizationsMeet(cb, false);
        ca.getDiplomacy().get(b).signDeclarationOfFriendship();
    }

    static void plague(String civName, int radius, int max) {
        Civilization c = civ(civName);
        if (c == null || c.getCities().isEmpty()) return;
        int n = 0;
        for (Tile t : kotlin.sequences.SequencesKt.asIterable(c.getCapital(false).getCenterTile().getTilesInDistance(radius))) {
            if (n >= max || t.isCityCenter() || t.isWater() || t.isImpassible() || t.getNaturalWonder() != null) continue;
            String base = baseOf(t);
            if (!(base.equals("Grassland") || base.equals("Plains") || base.equals("Tundra") || base.equals("Snow"))) continue;
            List<String> feats = new ArrayList<>();
            for (String f : t.getTerrainFeatures()) if (f.equals("Hill")) feats.add(f);
            feats.add("Plagued Land");
            t.setTerrainFeatures(feats);
            n++;
        }
    }

    static String baseOf(Tile t) {
        try { java.lang.reflect.Field f = Tile.class.getDeclaredField("baseTerrain"); f.setAccessible(true); return (String) f.get(t); }
        catch (Exception e) { throw new RuntimeException(e); }
    }

    static void tell(String text) {
        for (Civilization c : gi.getCivilizations()) if (c.isMajorCiv())
            c.addNotification(text, Notification.NotificationCategory.General, "OtherIcons/Star");
    }

    static void tellCiv(String civName, String text) {
        Civilization c = civ(civName);
        if (c != null) c.addNotification(text, Notification.NotificationCategory.General, "OtherIcons/Star");
    }

    static void spawnNear(String civName, String unit) {
        Civilization c = civ(civName);
        if (c == null) return;
        UniqueTriggerActivation.INSTANCE.triggerUnique(new Unique("A [" + unit + "] rebels", UniqueTarget.Triggerable, "scenario"),
                c, null, null, null, null, null);
    }

    static GameInfo start(String map, String era, String[] majors, int cityStates) {
        GameParameters gp = new GameParameters();
        gp.setBaseRuleset("UncivWarcraft");
        gp.setDifficulty("Prince");
        gp.setStartingEra(era);
        gp.setNumberOfCityStates(cityStates);
        ArrayList<Player> players = new ArrayList<>();
        for (String m : majors) players.add(new Player(m, PlayerType.AI, ""));
        players.add(new Player(com.unciv.Constants.spectator, PlayerType.Human, ""));
        gp.setPlayers(players);
        com.badlogic.gdx.files.FileHandle fh = new com.badlogic.gdx.files.FileHandle("mods/UncivWarcraft/maps/" + map);
        com.unciv.logic.map.MapParameters mp = com.unciv.logic.files.MapSaver.INSTANCE.loadMapParameters(fh);
        GameSetupInfo setup = new GameSetupInfo(gp, mp);
        setup.setMapFile(fh);
        GameInfo g = GameStarter.Companion.startNewGame(setup);
        g.getGameParameters().setVictoryTypes(new ArrayList<>(g.getRuleset().getVictories().keySet()));
        UncivGame.Companion.getCurrent().setGameInfo(g);
        return g;
    }

    static void save(String outDir, String name) throws Exception {
        String s = com.unciv.logic.files.UncivFiles.Companion.gameInfoToString(gi, true, false);
        Files.createDirectories(Paths.get(outDir));
        Files.write(Paths.get(outDir, name), s.getBytes(StandardCharsets.UTF_8));
        int cities = 0, units = 0;
        for (Civilization c : gi.getCivilizations()) { cities += c.getCities().size(); units += units(c).size(); }
        int wars = 0;
        for (Civilization c : gi.getCivilizations()) for (Civilization o : gi.getCivilizations()) if (c.isMajorCiv() && o.isMajorCiv() && c.isAtWarWith(o)) wars++;
        System.out.println("SCENARIO OK: " + name + " | wars " + wars / 2 + " | " + gi.getCivilizations().size() + " civs, " + cities + " cities, "
                + units + " units, " + s.length() / 1024 + " KB");
    }

    public static void main(String[] args) throws Exception {
        String out = args[0];
        UncivGame game = new UncivGame(true);
        UncivGame.Companion.setCurrent(game);
        GameSettings settings = new GameSettings();
        settings.setShowTutorials(false);
        game.setSettings(settings);
        RulesetCache.INSTANCE.loadRulesets(true, false);
        TileSetCache.INSTANCE.loadTileSetConfigs(true);

        // ------------------------------------------------------------ The Third War
        gi = start("Azeroth", "Age of the Third War",
                new String[]{"Humans", "High Elves", "Dwarves", "Kul Tirans", "Scourge", "Orcs", "Trolls", "Tauren", "Night Elves"}, 12);
        foundCapitals();
        plague("Scourge", 2, 8);
        give("Scourge", "Kel'Thuzad", "Ghoul", "Ghoul", "Ghoul", "Crypt Fiend", "Death Knight", "Acolyte");
        give("Humans", "Uther the Lightbringer", "Footman", "Paladin");
        give("High Elves", "Alleria Windrunner", "Farstrider");
        give("Orcs", "Grom Hellscream", "Grunt", "Grunt");
        give("Night Elves", "Malfurion Stormrage", "Huntress");
        give("Trolls", "Rokhan");
        give("Tauren", "Baine Bloodhoof");
        meetAll();
        war("Scourge", "Humans"); war("Scourge", "High Elves"); war("Scourge", "Dwarves");
        war("Night Elves", "Orcs");
        friends("Humans", "High Elves"); friends("Humans", "Dwarves"); friends("Humans", "Kul Tirans");
        friends("Orcs", "Trolls"); friends("Orcs", "Tauren"); friends("Trolls", "Tauren");
        tell("The Third War: the plague of undeath spreads from Northrend, and the Scourge marches on Lordaeron and Quel'Thalas. "
                + "Across the sea, the Horde lands in Kalimdor and clashes with the night elves of Ashenvale. "
                + "Behind it all, the Burning Legion waits.");
        tellCiv("Scourge", "The Lich King commands: break Lordaeron and Quel'Thalas, and spread the plague.");
        save(out, "The Third War");

        // ------------------------------------------------------------ The Cataclysm
        String[] all = {"Humans", "Orcs", "Night Elves", "Dwarves", "Gnomes", "Tauren", "Trolls", "Blood Elves", "High Elves", "Pandaren",
                "Forsaken", "Draenei", "Goblins", "Worgen", "Scourge", "Dark Iron Dwarves", "Kul Tirans", "Zandalari Trolls"};
        gi = start("Azeroth Large", "Age of the Cataclysm", all, 16);
        foundCapitals();
        meetAll();
        spawnNear("Humans", "Deathwing the Destroyer");
        spawnNear("Orcs", "Twilight Doomcaller");
        spawnNear("Night Elves", "Twilight Doomcaller");
        war("Orcs", "Night Elves");      // Garrosh's push into Ashenvale
        war("Forsaken", "Worgen");       // the battle for Gilneas
        war("Goblins", "Night Elves");   // Azshara
        tell("The Cataclysm: Deathwing has burst from Deepholm and the world is torn apart. The Twilight's Hammer gathers for the end "
                + "of days, while the Horde and the Alliance fight over the ruins: Ashenvale burns, and Gilneas falls to the Forsaken.");
        save(out, "The Cataclysm");

        // ------------------------------------------------------------ Battle for Azeroth
        String[] bfa = {"Humans", "Night Elves", "Dwarves", "Gnomes", "Draenei", "Worgen", "Dark Iron Dwarves", "Kul Tirans", "High Elves",
                "Orcs", "Tauren", "Trolls", "Blood Elves", "Forsaken", "Goblins", "Zandalari Trolls", "Pandaren"};
        gi = start("Azeroth Large", "Age of Azerite", bfa, 14);
        foundCapitals();
        meetAll();
        for (String a : ALLIANCE) for (String h : HORDE) war(h, a);
        for (int i = 0; i < ALLIANCE.length; i++) for (int j = i + 1; j < ALLIANCE.length; j++) friends(ALLIANCE[i], ALLIANCE[j]);
        for (int i = 0; i < HORDE.length; i++) for (int j = i + 1; j < HORDE.length; j++) friends(HORDE[i], HORDE[j]);
        give("Kul Tirans", "Daelin Proudmoore");
        give("Zandalari Trolls", "Rastakhan");
        give("Forsaken", "Nathanos Blightcaller");
        tell("Battle for Azeroth: the sword of Sargeras has wounded the world, and Azerite bleeds from the earth. Teldrassil has burned "
                + "and Lordaeron lies in ruins. The Alliance and the Horde are at war on every front, and Kul Tiras and Zandalar "
                + "choose their sides. The Pandaren stand apart, for now.");
        save(out, "Battle for Azeroth");

        // ------------------------------------------------------------ Alliance versus Horde (content pass, Oct 2026)
        String[] avh = {"Humans", "Night Elves", "Dwarves", "Gnomes", "Draenei", "Worgen", "High Elves", "Kul Tirans",
                "Orcs", "Tauren", "Trolls", "Blood Elves", "Forsaken", "Goblins", "Nightborne", "Highmountain Tauren"};
        gi = start("Azeroth Huge", "Age of the Dark Portal", avh, 16);
        foundCapitals();
        meetAll();
        String[] avhA = {"Humans", "Night Elves", "Dwarves", "Gnomes", "Draenei", "Worgen", "High Elves", "Kul Tirans"};
        String[] avhH = {"Orcs", "Tauren", "Trolls", "Blood Elves", "Forsaken", "Goblins", "Nightborne", "Highmountain Tauren"};
        for (String a : avhA) for (String h : avhH) war(h, a);
        for (int i = 0; i < avhA.length; i++) for (int j = i + 1; j < avhA.length; j++) friends(avhA[i], avhA[j]);
        for (int i = 0; i < avhH.length; i++) for (int j = i + 1; j < avhH.length; j++) friends(avhH[i], avhH[j]);
        give("Humans", "Uther the Lightbringer", "Footman", "Footman");
        give("Orcs", "Grom Hellscream", "Grunt", "Grunt");
        give("Dwarves", "Muradin Bronzebeard");
        give("Tauren", "Baine Bloodhoof");
        tell("Alliance versus Horde: the old war returns to every corner of Azeroth. Eight peoples stand under the lion of the Alliance "
                + "and eight under the banner of the Horde. Nobody else is coming. Win it.");
        save(out, "Alliance versus Horde");

        // ------------------------------------------------------------ The Legion Invasion
        gi = start("Broken Isles", "Age of the Legion",
                new String[]{"Nightborne", "Highmountain Tauren", "Humans", "Night Elves", "Orcs", "Draenei", "Blood Elves"}, 2);
        foundCapitals();
        meetAll();
        for (String a : new String[]{"Humans", "Night Elves", "Draenei"}) for (String h : new String[]{"Orcs", "Blood Elves"}) friends(a, h);
        friends("Nightborne", "Highmountain Tauren");
        give("Nightborne", "Grand Magistrix Elisande", "Spellblade");
        give("Highmountain Tauren", "Huln Highmountain", "Highmountain Warbrave");
        give("Draenei", "Maraad", "Vindicator");
        give("Humans", "Paladin");
        give("Orcs", "Grom Hellscream");
        spawnNear("Draenei", "Gul'dan the Destroyer");
        spawnNear("Nightborne", "Felguard");
        spawnNear("Night Elves", "Infernal");
        spawnNear("Humans", "Felguard");
        tell("The Legion Invasion: Gul'dan has broken open the Tomb of Sargeras and the Burning Legion pours onto the Broken Shore. "
                + "The Alliance and the Horde have set aside their war to stand with the Nightborne of Suramar and the tribes of Highmountain. "
                + "Hold the isles, or Azeroth falls.");
        save(out, "The Legion Invasion");

        // ------------------------------------------------------------ Mists of Pandaria
        gi = start("Pandaria", "Age of the Cataclysm", new String[]{"Pandaren", "Humans", "Orcs", "Dwarves", "Trolls", "Night Elves"}, 4);
        foundCapitals();
        meetAll();
        war("Orcs", "Humans");        // the landings in Krasarang
        war("Trolls", "Dwarves");
        war("Orcs", "Night Elves");
        friends("Humans", "Dwarves"); friends("Humans", "Night Elves"); friends("Orcs", "Trolls");
        give("Pandaren", "Chen Stormstout", "Shado-Pan Monk");
        give("Humans", "Footman", "Footman");
        give("Orcs", "Grunt", "Grunt");
        tell("Mists of Pandaria: the mists have parted, and the Alliance and the Horde have carried their war to the shores of Pandaria. "
                + "Every battle wakes the sha, the dark echoes of anger and fear buried beneath the land. The Pandaren must choose: "
                + "keep the peace, or join the fight.");
        save(out, "Mists of Pandaria");

        // ------------------------------------------------------------ Wrath of the Lich King
        gi = start("Northrend", "Age of the Lich King", new String[]{"Scourge", "Humans", "Orcs", "Tauren", "Trolls", "Dwarves", "Forsaken"}, 4);
        foundCapitals();
        meetAll();
        plague("Scourge", 2, 8);
        for (String o : new String[]{"Humans", "Orcs", "Tauren", "Trolls", "Dwarves", "Forsaken"}) war("Scourge", o);
        friends("Humans", "Dwarves"); friends("Orcs", "Tauren"); friends("Orcs", "Trolls"); friends("Tauren", "Trolls"); friends("Orcs", "Forsaken");
        give("Scourge", "Kel'Thuzad", "Death Knight", "Death Knight", "Ghoul", "Ghoul", "Crypt Fiend");
        give("Humans", "Uther the Lightbringer");
        give("Orcs", "Grom Hellscream");
        give("Dwarves", "Muradin Bronzebeard");
        give("Forsaken", "Nathanos Blightcaller");
        spawnNear("Dwarves", "Sapphiron");
        tell("Wrath of the Lich King: the Lich King stirs on his frozen throne, and his Scourge spills across Northrend. The Alliance "
                + "lands at Valiance Keep and Valgarde, the Horde at Warsong Hold and Vengeance Landing. Icecrown Citadel waits.");
        tellCiv("Scourge", "The Lich King commands: drive the living from Northrend, and raise their dead to serve.");
        save(out, "Wrath of the Lich King");
    }
}
