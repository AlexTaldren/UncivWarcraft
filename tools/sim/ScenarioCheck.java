import com.unciv.UncivGame;
import com.unciv.logic.GameInfo;
import com.unciv.logic.civilization.*;
import com.unciv.models.metadata.GameSettings;
import com.unciv.models.ruleset.RulesetCache;
import com.unciv.models.tilesets.TileSetCache;

/** Loads each scenario the way New Game > Scenario does (spectator removed, all computer players)
 *  and plays some turns.  args: scenario files...  (last arg: turns) */
public class ScenarioCheck {
    public static void main(String[] args) throws Exception {
        UncivGame game = new UncivGame(true);
        UncivGame.Companion.setCurrent(game);
        GameSettings s = new GameSettings(); s.setShowTutorials(false); game.setSettings(s);
        RulesetCache.INSTANCE.loadRulesets(true, false);
        TileSetCache.INSTANCE.loadTileSetConfigs(true);
        int turns = Integer.parseInt(args[args.length - 1]);
        for (int i = 0; i < args.length - 1; i++) {
            String text = new String(java.nio.file.Files.readAllBytes(java.nio.file.Paths.get(args[i])), "UTF-8");
            GameInfo gi = com.unciv.logic.files.UncivFiles.Companion.gameInfoFromString(text);
            gi.getCivilizations().removeIf(c -> c.getCivID().equals("Spectator"));
            for (Civilization c : gi.getCivilizations()) c.getDiplomacy().remove("Spectator");
            gi.getGameParameters().getPlayers().removeIf(p -> p.getChosenCiv().equals("Spectator"));
            if (gi.getCurrentPlayer().equals("Spectator")) gi.setCurrentPlayer("");
            game.setGameInfo(gi);
            gi.setSimulateUntilWin(true);
            gi.setSimulateMaxTurns(gi.getTurns() + turns);
            int t0 = gi.getTurns();
            while (gi.getTurns() < t0 + turns && gi.getVictoryData() == null) {
                gi.nextTurn(null, false);
            }
            StringBuilder sb = new StringBuilder();
            for (Civilization c : gi.getCivilizations()) if (c.isMajorCiv())
                sb.append(c.getCivName()).append(c.isDefeated() ? "(dead)" : "").append(":").append(c.getCities().size()).append(" ");
            int wars = 0;
            for (Civilization c : gi.getCivilizations()) for (Civilization o : gi.getCivilizations()) if (c.isMajorCiv() && o.isMajorCiv() && c.isAtWarWith(o)) wars++;
            System.out.println("PLAYED " + args[i] + " turns " + t0 + "->" + gi.getTurns() + " era " + gi.getCivilizations().get(0).getEra().getName()
                    + " | wars " + wars / 2 + " | " + sb);
        }
    }
}
