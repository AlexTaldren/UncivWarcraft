import com.unciv.UncivGame;
import com.unciv.logic.GameInfo;
import com.unciv.logic.GameStarter;
import com.unciv.logic.civilization.Civilization;
import com.unciv.logic.civilization.PlayerType;
import com.unciv.logic.map.MapParameters;
import com.unciv.logic.map.MapSize;
import com.unciv.logic.map.mapunit.MapUnit;
import com.unciv.models.metadata.GameParameters;
import com.unciv.models.metadata.GameSettings;
import com.unciv.models.metadata.GameSetupInfo;
import com.unciv.models.metadata.Player;
import com.unciv.models.ruleset.Ruleset;
import com.unciv.models.ruleset.RulesetCache;
import com.unciv.models.ruleset.unique.Unique;
import com.unciv.models.tilesets.TileSetCache;
import java.util.ArrayList;

/** Checks that the Humans' uniques parse to known unique types, and that a unit filter
 *  naming a civilization ("Forsaken") matches that civilization's units. */
public class UniqueCheck {
    static void check(String owner, Iterable<Unique> uniques) {
        for (Unique u : uniques) {
            String t = u.getType() == null ? "UNKNOWN" : u.getType().name();
            System.out.println("  " + owner + " | " + u.getText() + " -> " + t);
            for (Unique c : u.getModifiers())
                System.out.println("      <" + c.getText() + "> -> " + (c.getType() == null ? "UNKNOWN" : c.getType().name()));
        }
    }

    public static void main(String[] args) {
        UncivGame game = new UncivGame(true);
        UncivGame.Companion.setCurrent(game);
        GameSettings settings = new GameSettings();
        game.setSettings(settings);
        RulesetCache.INSTANCE.loadRulesets(true, false);
        TileSetCache.INSTANCE.loadTileSetConfigs(true);
        Ruleset r = RulesetCache.INSTANCE.get("UncivWarcraft");
        check("Humans", r.getNations().get("Humans").getUniqueObjects());
        for (String n : args[0].split(","))
            if (r.getUnits().containsKey(n)) check(n, r.getUnits().get(n).getUniqueObjects());
            else check(n, r.getBuildings().get(n).getUniqueObjects());

        GameParameters gp = new GameParameters();
        gp.setBaseRuleset("UncivWarcraft");
        gp.setStartingEra("Age of Tribes");
        gp.setNumberOfCityStates(0);
        ArrayList<Player> players = new ArrayList<>();
        players.add(new Player("Humans", PlayerType.AI, ""));
        players.add(new Player("Forsaken", PlayerType.AI, ""));
        players.add(new Player(com.unciv.Constants.spectator, PlayerType.Human, ""));
        gp.setPlayers(players);
        MapParameters mp = new MapParameters();
        mp.setMapSize(new MapSize("Tiny"));
        GameInfo gi = GameStarter.Companion.startNewGame(new GameSetupInfo(gp, mp));
        for (Civilization c : gi.getCivilizations()) {
            if (!c.isMajorCiv()) continue;
            for (MapUnit u : kotlin.sequences.SequencesKt.asIterable(c.getUnits().getCivUnits()))
                System.out.println("FILTER " + c.getCivName() + " " + u.getName() + " matches [Forsaken]: " + u.matchesFilter("Forsaken", true, new com.unciv.models.ruleset.unique.GameContext(u)));
        }
    }
}
