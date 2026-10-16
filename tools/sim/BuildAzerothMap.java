import com.badlogic.gdx.files.FileHandle;
import com.unciv.UncivGame;
import com.unciv.logic.files.MapSaver;
import com.unciv.logic.map.HexCoord;
import com.unciv.logic.map.HexMath;
import com.unciv.logic.map.MapParameters;
import com.unciv.logic.map.MapShape;
import com.unciv.logic.map.MapSize;
import com.unciv.logic.map.TileMap;
import com.unciv.logic.map.mapgenerator.MapGenerator;
import com.unciv.logic.map.tile.Tile;
import com.unciv.models.metadata.GameSettings;
import com.unciv.models.ruleset.Ruleset;
import com.unciv.models.ruleset.RulesetCache;
import com.unciv.ui.screens.mapeditorscreen.MapGeneratorSteps;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.*;

/** Builds the Azeroth map with Unciv's own classes from the tile list made by azeroth.py.
 *  args: tiles.txt  out_map_file  width height  [seed]
 *  Run with the working directory containing jsons/ (from Unciv.jar) and mods/UncivWarcraft. */
public class BuildAzerothMap {
    public static void main(String[] args) throws Exception {
        String tilesTxt = args[0], outFile = args[1];
        int width = Integer.parseInt(args[2]), height = Integer.parseInt(args[3]);
        long seed = args.length > 4 ? Long.parseLong(args[4]) : 20261016L;

        UncivGame game = new UncivGame(true);
        UncivGame.Companion.setCurrent(game);
        game.setSettings(new GameSettings());
        RulesetCache.INSTANCE.loadRulesets(true, false);
        Ruleset ruleset = RulesetCache.INSTANCE.get("UncivWarcraft");
        if (ruleset == null) throw new RuntimeException("UncivWarcraft ruleset not loaded");

        TileMap map = new TileMap(width, height, ruleset, false);
        MapParameters mp = map.getMapParameters();
        mp.setName("Azeroth");
        mp.setShape(MapShape.rectangular);
        mp.setMapSize(new MapSize(width, height));
        mp.setWorldWrap(false);
        mp.setBaseRuleset("UncivWarcraft");
        mp.setSeed(seed);

        List<String[]> starts = new ArrayList<>();
        for (String line : Files.readAllLines(Paths.get(tilesTxt), StandardCharsets.UTF_8)) {
            String[] p = line.split("\t", -1);
            if (p[0].equals("S")) { starts.add(p); continue; }
            Tile t = tileAt(map, Integer.parseInt(p[1]), Integer.parseInt(p[2]), width, height);
            t.setBaseTerrain(p[3]);
            List<String> feats = new ArrayList<>();
            if (!p[4].isEmpty()) feats.addAll(Arrays.asList(p[4].split("\\|")));
            t.setTerrainFeatures(feats);
            t.setNaturalWonder(p[5].isEmpty() ? null : p[5]);
        }
        map.setTransients(ruleset, true);

        MapGenerator gen = new MapGenerator(ruleset, kotlinx.coroutines.GlobalScope.INSTANCE);
        for (MapGeneratorSteps step : new MapGeneratorSteps[]{
                MapGeneratorSteps.LakesAndCoast, MapGeneratorSteps.Rivers,
                MapGeneratorSteps.Resources, MapGeneratorSteps.AncientRuins})
            gen.generateSingleStep(map, step);

        // Natural wonders and capitals must keep exactly what we gave them
        for (String line : Files.readAllLines(Paths.get(tilesTxt), StandardCharsets.UTF_8)) {
            String[] p = line.split("\t", -1);
            if (p[0].equals("T") && !p[5].isEmpty()) {
                Tile t = tileAt(map, Integer.parseInt(p[1]), Integer.parseInt(p[2]), width, height);
                t.setNaturalWonder(p[5]);
                t.setTileResource(null);
                t.setImprovement(null);
            }
        }
        for (String[] s : starts) {
            Tile t = tileAt(map, Integer.parseInt(s[1]), Integer.parseInt(s[2]), width, height);
            if (t.isWater() || t.isImpassible()) throw new RuntimeException("bad start for " + s[3]);
            t.setImprovement(null);  // no ruins on a capital
            map.addStartingLocation(s[3], t, TileMap.StartingLocation.Usage.Player);
        }

        String saved = MapSaver.INSTANCE.mapToSavedString(map);
        Files.write(Paths.get(outFile), saved.getBytes(StandardCharsets.UTF_8));

        // Round-trip check: load it back exactly as the game would
        TileMap back = MapSaver.INSTANCE.mapFromSavedString(saved);
        back.setTransients(ruleset, true);
        Map<String, Integer> res = new TreeMap<>();
        int land = 0, rivers = 0, ruins = 0;
        for (Tile t : back.getValues()) {
            if (t.isLand()) land++;
            if (t.getHasBottomRiver() || t.getHasBottomLeftRiver() || t.getHasBottomRightRiver()) rivers++;
            if (t.getResource() != null) res.merge(t.getResource(), 1, Integer::sum);
            if ("Ancient ruins".equals(t.getImprovement())) ruins++;
        }
        System.out.println("MAP OK: " + back.getValues().size() + " tiles, " + land + " land, "
                + back.getStartingLocations().size() + " starts, " + ruins + " ruins, river tiles " + rivers);
        System.out.println("RESOURCES: " + res);
    }

    static Tile tileAt(TileMap map, int c, int r, int width, int height) {
        // azeroth.py uses c,r from the north-west corner; Unciv centers columns/rows on 0 with rows growing north
        int col = c - width / 2, row = (height - 1) / 2 - r;
        HexCoord pos = HexMath.INSTANCE.getTileCoordsFromColumnRow(col, row);
        return map.get(pos);
    }
}
