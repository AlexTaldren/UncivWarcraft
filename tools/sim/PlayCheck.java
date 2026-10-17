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
        // portal: found a city, give a unit Portal Adept and Mana, open the portal
        {
            Civilization h = null;
            for (Civilization c : gi.getCivilizations()) if (c.getCivName().equals("Humans")) h = c;
            MapUnit settler = null;
            for (MapUnit u : kotlin.sequences.SequencesKt.asIterable(h.getUnits().getCivUnits())) if (u.getName().equals("Settler")) settler = u;
            com.unciv.logic.map.mapunit.actions.UnitActions.INSTANCE.invokeUnitAction(settler, com.unciv.models.UnitActionType.FoundCity);
            var city = h.getCities().get(0);
            MapUnit m = h.getUnits().placeUnitNearTile(city.getCenterTile().getPosition(), "Militia");
            for (MapUnit o : kotlin.collections.CollectionsKt.toList(kotlin.sequences.SequencesKt.asIterable(city.getCenterTile().getUnits()))) if (o.isMilitary()) o.destroy(false);
            m.removeFromTile(); m.putInTile(city.getCenterTile());
            m.getPromotions().addPromotion("Portal Adept", true);
            h.gainStockpiledResource(r.getTileResources().get("Mana"), 25);
            StringBuilder sb = new StringBuilder("PORTAL mana before " + h.getResourceStockpiles().get("Mana") + " | on city: " + (m.getCurrentTile() == city.getCenterTile()) + " | actions:");
            com.unciv.models.UnitAction open = null;
            for (var a : kotlin.sequences.SequencesKt.asIterable(com.unciv.logic.map.mapunit.actions.UnitActions.INSTANCE.getUnitActions(m, com.unciv.models.UnitActionType.TriggerUnique))) {
                sb.append(" ").append(a.getType()).append(a.getTitle().isEmpty() ? "" : "(" + a.getTitle() + ")");
                if (a.getAssociatedUnique() != null && a.getAssociatedUnique().getText().contains("Portal Attunement")) open = a;
            }
            System.out.println(sb);
            if (open != null && open.getAction() != null) {
                open.getAction().invoke();
                boolean para = false; int pn = 0;
                for (var a : kotlin.sequences.SequencesKt.asIterable(com.unciv.logic.map.mapunit.actions.UnitActions.INSTANCE.getUnitActions(m, com.unciv.models.UnitActionType.Paradrop))) pn++;
                System.out.println("PORTAL paradrop actions " + pn + " | unit has paradrop unique " + m.hasUnique(com.unciv.models.ruleset.unique.UniqueType.MayParadrop, new com.unciv.models.ruleset.unique.GameContext(m), true) + " | movement left " + m.getCurrentMovement());
                for (var a : kotlin.sequences.SequencesKt.asIterable(com.unciv.logic.map.mapunit.actions.UnitActions.INSTANCE.getUnitActions(m, com.unciv.models.UnitActionType.Paradrop)))
                    para = para || a.getAction() != null;
                System.out.println("PORTAL after opening: mana " + h.getResourceStockpiles().get("Mana") + " | has status " + m.getPromotions().getPromotions().contains("Portal Attunement") + " / " + m.hasStatus("Portal Attunement") + " | paradrop action " + para);
            } else System.out.println("PORTAL open action not available");
        }
        // cleansing: can a Peasant / Cleric build the removal on a plagued tile, and a Farm elsewhere?
        Civilization hum = null;
        for (Civilization c : gi.getCivilizations()) if (c.getCivName().equals("Humans")) hum = c;
        com.unciv.logic.map.tile.Tile cap = hum.getCities().isEmpty() ? null : hum.getCities().get(0).getCenterTile();
        com.unciv.logic.map.tile.Tile start = null;
        for (MapUnit u : kotlin.sequences.SequencesKt.asIterable(hum.getUnits().getCivUnits())) { start = u.getCurrentTile(); break; }
        com.unciv.logic.map.tile.Tile plain = null, plague = null;
        for (com.unciv.logic.map.tile.Tile t : kotlin.sequences.SequencesKt.asIterable(start.getTilesInDistance(3))) {
            String b = t.getLastTerrain().getName();
            if (t != start && !t.isCityCenter() && (b.equals("Grassland") || b.equals("Plains") || b.equals("Tundra")) && t.getTerrainFeatures().isEmpty()) {
                if (plain == null) plain = t; else if (plague == null) plague = t;
            }
        }
        plague.addTerrainFeature("Plagued Land");
        hum.getTech().addTechnology("Priesthood", false);
        hum.getTech().addTechnology("Pottery", false);
        MapUnit peasant = hum.getUnits().placeUnitNearTile(plain.getPosition(), "Peasant");
        MapUnit cleric = hum.getUnits().placeUnitNearTile(plague.getPosition(), "Northshire Cleric");
        var rem = r.getTileImprovements().get("Remove Plagued Land");
        var farm = r.getTileImprovements().get("Farm");
        System.out.println("CLEANSE peasant on plague: " + peasant.canBuildImprovement(rem, plague)
            + " | cleric on plague: " + cleric.canBuildImprovement(rem, plague)
            + " | peasant farm on plain: " + peasant.canBuildImprovement(farm, plain)
            + " | cleric farm on plain: " + cleric.canBuildImprovement(farm, plain));
    }
}
