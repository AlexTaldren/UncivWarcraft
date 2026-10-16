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
        for (int t = 25; t <= maxTurns; t += 25) {
            gi.setSimulateMaxTurns(t);
            while (gi.getTurns() < t && gi.getAliveMajorCivs().size() > 1 && gi.getVictoryData() == null)
                gi.nextTurn(null, false);
            report(gi);
            for (Civilization c : gi.getCivilizations()) if (c.getCivName().equals("Humans")) {
                java.util.TreeMap<String,Integer> seen = new java.util.TreeMap<>();
                for (com.unciv.logic.map.mapunit.MapUnit u : kotlin.sequences.SequencesKt.asIterable(c.getUnits().getCivUnits())) seen.merge(u.getName(), 1, Integer::sum);
                System.out.println("   Humans field: " + seen);
            }
            if (gi.getAliveMajorCivs().size() <= 1 || gi.getVictoryData() != null) break;
        }
        System.out.println("VICTORY: " + gi.getVictoryData());
        for (Civilization c : gi.getCivilizations()) {
            if (!c.getCivName().equals("Humans")) continue;
            java.util.TreeMap<String,Integer> seen = new java.util.TreeMap<>();
            for (com.unciv.logic.map.mapunit.MapUnit u : kotlin.sequences.SequencesKt.asIterable(c.getUnits().getCivUnits())) seen.merge(u.getName(), 1, Integer::sum);
            System.out.println("HUMAN UNITS NOW: " + seen);
        }
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
              .append(" | ").append(c.getEra().getName());
        }
        System.out.println(sb);
    }
}
