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

/** Depth-pass checks: hidden-branch adoption, boss rebels, trophies and the Raid victory, choice events. */
public class DepthCheck {
    static void trig(String text, Civilization c) {
        Unique u = new Unique(text, UniqueTarget.Triggerable, "test");
        boolean ok = UniqueTriggerActivation.INSTANCE.triggerUnique(u, c, null, null, null, null, null);
        System.out.println("TRIGGER " + text + " -> " + ok);
    }
    static int count(Civilization c, String name) {
        int n = 0;
        for (MapUnit u : kotlin.sequences.SequencesKt.asIterable(c.getUnits().getCivUnits())) if (u.getName().equals(name)) n++;
        return n;
    }
    public static void main(String[] args) {
        UncivGame game = new UncivGame(true);
        UncivGame.Companion.setCurrent(game);
        game.setSettings(new GameSettings());
        RulesetCache.INSTANCE.loadRulesets(true, false);
        TileSetCache.INSTANCE.loadTileSetConfigs(true);
        Ruleset r = RulesetCache.INSTANCE.get("UncivWarcraft");
        GameParameters gp = new GameParameters();
        gp.setBaseRuleset("UncivWarcraft");
        gp.setNumberOfCityStates(0);
        gp.setVictoryTypes(new ArrayList<>(java.util.List.of("Scientific","Cultural","Domination","Diplomatic","Time","Raid","Religious")));
        ArrayList<Player> players = new ArrayList<>();
        for (String s : new String[]{"Humans", "Orcs", "Scourge", "Night Elves"}) players.add(new Player(s, PlayerType.AI, ""));
        players.add(new Player(com.unciv.Constants.spectator, PlayerType.Human, ""));
        gp.setPlayers(players);
        MapParameters mp = new MapParameters();
        mp.setMapSize(new MapSize("Tiny"));
        GameInfo gi = GameStarter.Companion.startNewGame(new GameSetupInfo(gp, mp));
        Civilization h = null, barb = null, orcs = null;
        for (Civilization c : gi.getCivilizations()) {
            if (c.getCivName().equals("Humans")) h = c;
            if (c.getCivName().equals("Orcs")) orcs = c;
            if (c.isBarbarian()) barb = c;
        }
        System.out.println("VICTORY TYPES " + r.getVictories().keySet());
        // found the capital (opening event should fire for an AI civ)
        MapUnit settler = null;
        for (MapUnit u : kotlin.sequences.SequencesKt.asIterable(h.getUnits().getCivUnits())) if (u.getName().equals("Settler")) settler = u;
        float faith0 = h.getReligionManager().getStoredFaith();
        int mil0 = count(h, "Militia");
        com.unciv.logic.map.mapunit.actions.UnitActions.INSTANCE.invokeUnitAction(settler, com.unciv.models.UnitActionType.FoundCity);
        System.out.println("OPENING faith " + faith0 + " -> " + h.getReligionManager().getStoredFaith() + " | militia " + mil0 + " -> " + count(h, "Militia"));
        // fateful choice through an event (AI chooses)
        trig("Triggers a [The Covenants Call] event", h);
        System.out.println("ADOPTED " + h.getPolicies().getAdoptedPolicies());
        trig("Adopt [Rejected the Fel]", h);
        System.out.println("ADOPTED " + h.getPolicies().getAdoptedPolicies());
        int n = 0;
        for (Unique u : kotlin.sequences.SequencesKt.asIterable(h.getMatchingUniques(UniqueType.StatsPerCity, h.getState()))) n++;
        System.out.println("CIV StatsPerCity uniques active: " + n);
        // a raid boss rebels near the Humans
        trig("A [Onyxia] rebels", h);
        System.out.println("BOSS barbarian Onyxia count " + count(barb, "Onyxia"));
        MapUnit boss = null;
        for (MapUnit u : kotlin.sequences.SequencesKt.asIterable(barb.getUnits().getCivUnits())) if (u.getName().equals("Onyxia")) boss = u;
        MapUnit sw = h.getUnits().placeUnitNearTile(boss.getCurrentTile().getPosition(), "Swordsman");
        boss.setHealth(1);
        float tr0 = h.getResourceAmount("Raid Trophy"); int g0 = h.getGold();
        com.unciv.logic.battle.Battle.INSTANCE.attack(new com.unciv.logic.battle.MapUnitCombatant(sw), new com.unciv.logic.battle.MapUnitCombatant(boss));
        System.out.println("KILL boss alive? " + boss.isDestroyed() + " | trophies " + tr0 + " -> " + h.getResourceAmount("Raid Trophy") + " | gold " + g0 + " -> " + h.getGold() + " | promos " + sw.getPromotions().getPromotions());
        int before = count(barb, "Ragnaros the Firelord");
        System.out.println("culture before events " + h.getPolicies().getStoredCulture());
        for (int i = 0; i < 20; i++) UniqueTriggerActivation.INSTANCE.triggerUnique(new Unique("Triggers a [Raid: Ragnaros] event", UniqueTarget.Triggerable, "t"), h, null, null, null, null, null);
        trig("A [Ragnaros the Firelord] rebels", h);
        System.out.println("DIRECT Ragnaros count " + count(barb, "Ragnaros the Firelord") + " culture " + h.getPolicies().getStoredCulture());
        System.out.println("RAID EVENT x20 -> Ragnaros spawned " + (count(barb, "Ragnaros the Firelord") - before) + " | humans gold " + h.getGold());
        trig("Triggers a [Raid: Ragnaros] event", orcs);
        System.out.println("BOSS barbarian Ragnaros count " + count(barb, "Ragnaros the Firelord") + " | orc gold " + orcs.getGold());
        // trophies and the Raid victory
        for (int i = 0; i < 6; i++) trig("Instantly gain [1] [Raid Trophy]", h);
        System.out.println("TROPHIES " + h.getResourceStockpiles().get("Raid Trophy"));
        System.out.println("GAME VICTORY TYPES " + gi.getGameParameters().getVictoryTypes());
        var raid = r.getVictories().get("Raid");
        System.out.println("RAID milestone done? " + raid.getMilestoneObjects().get(0).hasBeenCompletedBy(h) + " | won? " + h.getVictoryManager().getVictoryTypeAchieved());
        trig("Adopt [Kyrian Covenant]", h);
        int k = 0;
        for (Unique u : kotlin.sequences.SequencesKt.asIterable(h.getMatchingUniques(UniqueType.StatsPerCity, h.getState()))) { k++; System.out.println("  " + u.getText()); }
        System.out.println("CIV StatsPerCity after Kyrian: " + k);
    }
}
