import com.unciv.UncivGame;
import com.unciv.logic.GameInfo;
import com.unciv.logic.GameStarter;
import com.unciv.logic.civilization.Civilization;
import com.unciv.logic.civilization.PlayerType;
import com.unciv.logic.map.MapParameters;
import com.unciv.logic.map.MapSize;
import com.unciv.logic.map.mapunit.MapUnit;
import com.unciv.models.metadata.*;
import com.unciv.models.ruleset.*;
import com.unciv.models.ruleset.unique.*;
import com.unciv.models.tilesets.TileSetCache;
import java.util.ArrayList;

/** v0.12 checks: every unique on the named objects parses to a known type (UNKNOWN is
 *  printed otherwise), and faction tags work as unit and civilization filters. */
public class PlayCheck {
    static int unknown = 0;
    static void check(String owner, Iterable<Unique> uniques) {
        for (Unique u : uniques) {
            boolean bad = u.getType() == null;
            for (Unique c : u.getModifiers()) bad |= c.getType() == null;
            if (bad) { unknown++; System.out.println("  UNKNOWN " + owner + " | " + u.getText()); }
        }
    }
    public static void main(String[] args) {
        UncivGame game = new UncivGame(true);
        UncivGame.Companion.setCurrent(game);
        game.setSettings(new GameSettings());
        RulesetCache.INSTANCE.loadRulesets(true, false);
        TileSetCache.INSTANCE.loadTileSetConfigs(true);
        Ruleset r = RulesetCache.INSTANCE.get("UncivWarcraft");
        for (var n : r.getNations().values()) check("nation " + n.getName(), n.getUniqueObjects());
        for (var n : r.getUnits().values()) check("unit " + n.getName(), n.getUniqueObjects());
        for (var n : r.getBuildings().values()) check("building " + n.getName(), n.getUniqueObjects());
        for (var n : r.getTileImprovements().values()) check("improvement " + n.getName(), n.getUniqueObjects());
        for (var n : r.getUnitPromotions().values()) check("promotion " + n.getName(), n.getUniqueObjects());
        for (var n : r.getEvents().values()) for (var ch : n.getChoices()) check("event " + n.getName(), ch.getUniqueObjects());
        for (var n : r.getRuinRewards().values()) check("ruin " + n.getName(), n.getUniqueObjects());
        for (var n : r.getTileResources().values()) check("resource " + n.getName(), n.getUniqueObjects());
        System.out.println("UNKNOWN uniques (untyped tags excepted): " + unknown);

        GameParameters gp = new GameParameters();
        gp.setBaseRuleset("UncivWarcraft");
        gp.setNumberOfCityStates(0);
        ArrayList<Player> players = new ArrayList<>();
        for (String s : new String[]{"Humans", "Orcs", "Scourge", "Pandaren"}) players.add(new Player(s, PlayerType.AI, ""));
        players.add(new Player(com.unciv.Constants.spectator, PlayerType.Human, ""));
        gp.setPlayers(players);
        MapParameters mp = new MapParameters();
        mp.setMapSize(new MapSize("Tiny"));
        GameInfo gi = GameStarter.Companion.startNewGame(new GameSetupInfo(gp, mp));
        for (Civilization c : gi.getCivilizations()) {
            if (!c.isMajorCiv()) continue;
            StringBuilder sb = new StringBuilder("CIV " + c.getCivName() + ":");
            for (String f : new String[]{"Alliance", "Horde", "Undead", "Major"})
                sb.append(" ").append(f).append("=").append(c.matchesFilter(f, null, true));
            for (MapUnit u : kotlin.sequences.SequencesKt.asIterable(c.getUnits().getCivUnits())) {
                sb.append(" | unit ").append(u.getName()).append(" vs[Horde]=").append(u.matchesFilter("Horde", true, new GameContext(u)));
                break;
            }
            System.out.println(sb);
        }
    }
}
