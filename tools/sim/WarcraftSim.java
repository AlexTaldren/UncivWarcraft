import com.unciv.Constants;
import com.unciv.UncivGame;
import com.unciv.logic.GameInfo;
import com.unciv.logic.GameStarter;
import com.unciv.logic.civilization.Civilization;
import com.unciv.logic.civilization.PlayerType;
import com.unciv.logic.map.MapParameters;
import com.unciv.logic.map.MapSize;
import com.unciv.models.metadata.GameParameters;
import com.unciv.models.metadata.GameSettings;
import com.unciv.models.metadata.GameSetupInfo;
import com.unciv.models.metadata.Player;
import com.unciv.models.ruleset.RulesetCache;
import com.unciv.models.tilesets.TileSetCache;

import java.util.ArrayList;

/** Plays an all-AI game of the UncivWarcraft ruleset and reports what happened.
 *  Run with the working directory containing jsons/ (from Unciv.jar) and mods/UncivWarcraft. */
public class WarcraftSim {
    static final java.util.TreeMap<String, Integer> SPELLS = new java.util.TreeMap<>();
    public static void main(String[] args) {
        int maxTurns = args.length > 0 ? Integer.parseInt(args[0]) : 300;
        String[] majors = args.length > 1 ? args[1].split(",") : new String[]{"Humans", "Orcs"};
        long seed = args.length > 2 ? Long.parseLong(args[2]) : 1L;

        UncivGame game = new UncivGame(true);
        UncivGame.Companion.setCurrent(game);
        GameSettings settings = new GameSettings();
        settings.setShowTutorials(false);
        game.setSettings(settings);
        RulesetCache.INSTANCE.loadRulesets(true, false);
        TileSetCache.INSTANCE.loadTileSetConfigs(true);
        if (!RulesetCache.INSTANCE.containsKey("UncivWarcraft")) throw new RuntimeException("mod not loaded");

        GameParameters gp = new GameParameters();
        gp.setBaseRuleset("UncivWarcraft");
        gp.setDifficulty("Prince");
        gp.setStartingEra("Age of Tribes");
        gp.setNumberOfCityStates(6);
        ArrayList<Player> players = new ArrayList<>();
        for (String m : majors) players.add(new Player(m, PlayerType.AI, ""));
        players.add(new Player(Constants.spectator, PlayerType.Human, ""));
        gp.setPlayers(players);

        String mapPath = args.length > 3 ? args[3] : null;
        MapParameters mp;
        GameSetupInfo setup;
        if (mapPath != null) {
            com.badlogic.gdx.files.FileHandle fh = new com.badlogic.gdx.files.FileHandle(mapPath);
            mp = com.unciv.logic.files.MapSaver.INSTANCE.loadMapParameters(fh);
            gp.setNumberOfCityStates(12);
            setup = new GameSetupInfo(gp, mp);
            setup.setMapFile(fh);
        } else {
            mp = new MapParameters();
            mp.setMapSize(new MapSize(majors.length > 6 ? "Medium" : "Small"));
            mp.setSeed(seed);
            setup = new GameSetupInfo(gp, mp);
        }

        GameInfo gi = GameStarter.Companion.startNewGame(setup);
        for (Civilization c : gi.getCivilizations()) {
            if (c.isBarbarian() || c.isSpectator()) continue;
            com.unciv.logic.map.mapunit.MapUnit first = null;
            for (com.unciv.logic.map.mapunit.MapUnit u : kotlin.sequences.SequencesKt.asIterable(c.getUnits().getCivUnits())) { first = u; break; }
            System.out.println("START " + c.getCivName() + " @ " + (first == null ? "-" : first.getCurrentTile().getPosition()));
        }
        gi.getGameParameters().setVictoryTypes(new ArrayList<>(gi.getRuleset().getVictories().keySet()));
        game.setGameInfo(gi);
        System.out.println("STARTED: " + gi.getCivilizations().size() + " civs on " + (mapPath != null ? mp.getName() : mp.getMapSize().getName()));

        gi.setSimulateUntilWin(true);
        for (int t = 5; t <= maxTurns; t += 5) {
            gi.setSimulateMaxTurns(t);
            while (gi.getTurns() < t && gi.getAliveMajorCivs().size() > 1 && gi.getVictoryData() == null)
                gi.nextTurn(null, false);
            sampleDiplomacy(gi);
            for (Civilization c : gi.getCivilizations()) for (com.unciv.logic.map.mapunit.MapUnit u : kotlin.sequences.SequencesKt.asIterable(c.getUnits().getCivUnits()))
                for (String st : u.getStatusMap().keySet()) if (st.endsWith(" Cooldown")) SPELLS.merge(st.replace(" Cooldown", ""), 1, Integer::sum);
            for (Civilization c : gi.getCivilizations()) for (com.unciv.logic.civilization.Notification n : c.getNotifications()) {
                String tx = n.getText();
                for (String k : new String[]{"Darkmoon","granar","fel rift","Legion","Steamwheedle","Lunar","Brewfest","orphan","Gnome","Titan","Deathwing","brewmaster","Wickerman","Hallow","Kirin Tor","murloc","Defias","Mrgl","Golden Age","rebel","Onyxia","Hakkar","Ragnaros","C'Thun","Sapphiron","Kil'jaeden","N'Zoth","Raid Trophy","Covenant","Fel","Sunwell"})
                    if (tx.contains(k)) EVENTS.merge(k, 1, Integer::sum);
            }
            if (t % 25 != 0 && gi.getAliveMajorCivs().size() > 1 && gi.getVictoryData() == null) continue;
            report(gi);
            for (Civilization c : gi.getCivilizations()) if (c.getCivName().equals("Humans")) {
                java.util.TreeMap<String,Integer> seen = new java.util.TreeMap<>();
                for (com.unciv.logic.map.mapunit.MapUnit u : kotlin.sequences.SequencesKt.asIterable(c.getUnits().getCivUnits())) seen.merge(u.getName(), 1, Integer::sum);
                System.out.println("   Humans field: " + seen);
            }
            if (gi.getAliveMajorCivs().size() <= 1 || gi.getVictoryData() != null) break;
        }
        System.out.println("VICTORY: " + gi.getVictoryData());
        System.out.println("SPELL COOLDOWNS SEEN (5-turn samples): " + SPELLS);
        for (Civilization c : gi.getCivilizations()) {
            java.util.List<String> gpl = new ArrayList<>();
            java.util.TreeMap<String,Integer> barb = new java.util.TreeMap<>();
            for (com.unciv.logic.map.mapunit.MapUnit u : kotlin.sequences.SequencesKt.asIterable(c.getUnits().getCivUnits())) {
                if (u.getBaseUnit().isGreatPerson()) gpl.add(u.getName() + "=" + u.getInstanceName());
                if (c.isBarbarian()) barb.merge(u.getName(), 1, Integer::sum);
            }
            if (!gpl.isEmpty()) System.out.println("GP " + c.getCivName() + ": " + gpl);
            java.util.TreeMap<String,Integer> uu = new java.util.TreeMap<>();
            for (com.unciv.logic.map.mapunit.MapUnit u : kotlin.sequences.SequencesKt.asIterable(c.getUnits().getCivUnits()))
                if (u.getBaseUnit().getUniqueTo() != null) uu.merge(u.getName(), 1, Integer::sum);
            java.util.List<String> ub = new ArrayList<>();
            for (com.unciv.logic.city.City city : c.getCities()) for (com.unciv.models.ruleset.Building b : gi.getRuleset().getBuildings().values()) if (b.getUniqueTo() != null && city.getCityConstructions().isBuilt(b.getName())) ub.add(b.getName());
            if (!uu.isEmpty() || !ub.isEmpty()) System.out.println("UNIQUE " + c.getCivName() + ": units " + uu + " buildings " + new java.util.TreeSet<>(ub));
            if (c.isMajorCiv()) {
                int plague = 0, deep = 0, promoH = 0;
                for (com.unciv.logic.map.tile.Tile t : gi.getTileMap().getTileList()) { if (t.getOwner() != c) continue;
                    if (t.getTerrainFeatures().contains("Plagued Land")) plague++;
                    if ("Deep Mine".equals(t.getImprovement())) deep++;
                }
                for (com.unciv.logic.map.mapunit.MapUnit u : kotlin.sequences.SequencesKt.asIterable(c.getUnits().getCivUnits()))
                    for (String p : new String[]{"Hearthstone", "Portal Attunement", "Flight Path"}) if (u.getPromotions().getPromotions().contains(p)) promoH++;
                System.out.println("PLAY " + c.getCivName() + ": plagued tiles " + plague + " | deep mines " + deep + " | travel promos " + promoH
                    + " | mana " + c.getResourceAmount("Mana") + " | happiness " + c.getStats().getHappiness()
                    + " | trophies " + c.getResourceAmount("Raid Trophy") + " | choices " + fateful(c));
            }
            if (c.isBarbarian()) System.out.println("BARBARIAN UNITS: " + barb);
        }
        System.out.println("EVENT SEEN: " + EVENTS);
        System.out.println("DIPLOMACY (pair-samples every 5 turns; share of known pairs in each state):");
        for (String k : new String[]{"Alliance-Alliance", "Horde-Horde", "Alliance-Horde", "Neutral-any"}) {
            int[] v = DIPLO.getOrDefault(k, new int[4]);
            if (v[0] == 0) continue;
            System.out.printf("   %-18s samples %5d | friends %5.1f%% | defensive pacts %5.1f%% | at war %5.1f%%%n",
                k, v[0], 100.0 * v[1] / v[0], 100.0 * v[2] / v[0], 100.0 * v[3] / v[0]);
        }
        for (Civilization c : gi.getCivilizations()) {
            if (!c.getCivName().equals("Humans")) continue;
            java.util.TreeMap<String,Integer> seen = new java.util.TreeMap<>();
            for (com.unciv.logic.map.mapunit.MapUnit u : kotlin.sequences.SequencesKt.asIterable(c.getUnits().getCivUnits())) seen.merge(u.getName(), 1, Integer::sum);
            System.out.println("HUMAN UNITS NOW: " + seen);
        }
    }

    static final java.util.Map<String, String> FACTION = new java.util.HashMap<>();
    static {
        for (String n : new String[]{"Humans","Dwarves","Gnomes","Night Elves","Draenei","Worgen","High Elves","Dark Iron Dwarves","Kul Tirans"}) FACTION.put(n, "Alliance");
        for (String n : new String[]{"Orcs","Trolls","Tauren","Forsaken","Blood Elves","Goblins","Zandalari Trolls"}) FACTION.put(n, "Horde");
        FACTION.put("Pandaren", "Neutral"); FACTION.put("Scourge", "Neutral");
    }
    static final java.util.Map<String, Integer> EVENTS = new java.util.TreeMap<>();
    static final java.util.Map<String, int[]> DIPLO = new java.util.TreeMap<>();

    static void sampleDiplomacy(GameInfo gi) {
        java.util.List<Civilization> majors = new ArrayList<>();
        for (Civilization c : gi.getCivilizations()) if (c.isMajorCiv() && c.isAlive()) majors.add(c);
        for (int i = 0; i < majors.size(); i++) for (int j = i + 1; j < majors.size(); j++) {
            Civilization a = majors.get(i), b = majors.get(j);
            com.unciv.logic.civilization.diplomacy.DiplomacyManager dm = a.getDiplomacyManager(b);
            if (dm == null) continue;   // not met yet
            String fa = FACTION.getOrDefault(a.getCivName(), "Neutral"), fb = FACTION.getOrDefault(b.getCivName(), "Neutral");
            String key = fa.equals("Neutral") || fb.equals("Neutral") ? "Neutral-any"
                : fa.equals(fb) ? fa + "-" + fb : "Alliance-Horde";
            int[] v = DIPLO.computeIfAbsent(key, k -> new int[4]);
            v[0]++;
            if (dm.hasFlag(com.unciv.logic.civilization.diplomacy.DiplomacyFlags.DeclarationOfFriendship)) v[1]++;
            if (dm.getDiplomaticStatus() == com.unciv.logic.civilization.diplomacy.DiplomaticStatus.DefensivePact) v[2]++;
            if (dm.getDiplomaticStatus() == com.unciv.logic.civilization.diplomacy.DiplomaticStatus.War) v[3]++;
        }
    }

    static String fateful(Civilization c) {
        java.util.List<String> out = new ArrayList<>();
        for (String p : c.getPolicies().getAdoptedPolicies())
            if (p.contains("Fel") || p.contains("Sunwell") || p.contains("Covenant")) out.add(p);
        return out.toString();
    }

    static void report(GameInfo gi) {
        StringBuilder sb = new StringBuilder("TURN " + gi.getTurns() + ":");
        for (Civilization c : gi.getCivilizations()) {
            if (!c.isMajorCiv()) continue;
            sb.append("\n   ").append(c.getCivName())
              .append(c.isDefeated() ? " [defeated]" : "")
              .append(" | cities ").append(c.getCities().size())
              .append(" | units ").append(c.getUnits().getCivUnitsSize())
              .append(" | techs ").append(c.getTech().getTechsResearched().size())
              .append(" | ").append(c.getEra().getName())
              .append(" | trophies ").append(c.getResourceAmount("Raid Trophy"));
        }
        System.out.println(sb);
    }
}
