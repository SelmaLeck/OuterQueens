"""Create an idempotent SQL seed from the user's 2026-11-02 Litematica material list.
No external dependency; English names and recipes are maintained below.
"""
import csv, json, math, re, uuid
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
rows=[]
for line in (ROOT/'data/cinderella-materials.tsv').read_text(encoding='utf-8').splitlines():
    de,amount=line.rsplit('|',1)
    rows.append((de,int(amount)))
# Identical names can appear twice in pasted screenshots/text. Avoid duplicate tiles.
combined={}
for de,amt in rows: combined[de]=combined.get(de,0)+amt

colors={'Hellgraue':'Light Gray','Hellgrauer':'Light Gray','Hellgraues':'Light Gray','Blaue':'Blue','Blauer':'Blue','Blaues':'Blue','Weiße':'White','Weißer':'White','Weißes':'White','Graue':'Gray','Grauer':'Gray','Graues':'Gray','Grüne':'Green','Grüner':'Green','Grünes':'Green','Gelbe':'Yellow','Gelber':'Yellow','Gelbes':'Yellow','Magenta':'Magenta','Rosa':'Pink','Roter':'Red','Rote':'Red','Rotes':'Red','Violetter':'Purple','Violette':'Purple','Violettes':'Purple','Türkiser':'Cyan','Türkise':'Cyan','Brauner':'Brown','Braune':'Brown','Braunes':'Brown','Schwarze':'Black','Schwarzer':'Black','Schwarzes':'Black','Hellblaue':'Light Blue','Hellblauer':'Light Blue','Orange':'Orange'}
woods={'Kirschholz':'Cherry','Birkenholz':'Birch','Fichtenholz':'Spruce','Schwarzeichenholz':'Dark Oak','Eichenholz':'Oak','Akazienholz':'Acacia','Mangrovenholz':'Mangrove','Bambus':'Bamboo','Karmesin':'Crimson','Wirr':'Warped'}
wood_suffixes=[('hängeschild','Hanging Sign'),('druckplatte','Pressure Plate'),('zauntor','Fence Gate'),('falltür','Trapdoor'),('setzling','Sapling'),('stamm','Log'),('bretter','Planks'),('treppe','Stairs'),('stufe','Slab'),('schild','Sign'),('knopf','Button'),('zaun','Fence'),('tür','Door'),('laub','Leaves')]
mat_suffixes=[('treppe','Stairs'),('stufe','Slab'),('mauer','Wall'),('knopf','Button')]
mat_base={'Steinziegel':'Stone Brick','Tiefenschieferziegel':'Deepslate Brick','Tiefenschieferfliesen':'Deepslate Tile','Bruchtiefenschiefer':'Cobbled Deepslate','Bruchstein':'Cobblestone','Schlammziegel':'Mud Brick','Andesit':'Andesite','Diorit':'Diorite','Schwarzstein':'Blackstone','Tiefenschiefer':'Deepslate','Sandstein':'Sandstone','Stein':'Stone','Netherziegel':'Nether Brick','Endsteinziegel':'End Stone Brick','Ziegelstein':'Brick'}
normal={
'Stein':'Stone','Bruchstein':'Cobblestone','Glatter Stein':'Smooth Stone','Glatter Sandstein':'Smooth Sandstone','Andesit':'Andesite',
'Abgestorbener Hirnkorallenblock':'Dead Brain Coral Block','Gemeißelte Tuffsteinziegel':'Chiseled Tuff Bricks','Polierter Tuffstein':'Polished Tuff',
'Kies':'Gravel','Fackel':'Torch','Tropfsteinblock':'Dripstone Block','Wassereimer':'Water Bucket','Geschnittener Sandstein':'Cut Sandstone',
'Brauner Pilzblock':'Brown Mushroom Block','Farn':'Fern','Schmelzofen':'Blast Furnace','Webstuhl':'Loom','Moosblock':'Moss Block',
'Rissige Steinziegel':'Cracked Stone Bricks','Fass':'Barrel','Kerze':'Candle','Truhe':'Chest',
'Karmesin-Nezel':'Crimson Nylium','Karmesin-Netzel':'Crimson Nylium','Feuerkorallenblock':'Fire Coral Block','Fester Schlamm':'Packed Mud','Niedriges Gras':'Short Grass','Komposter':'Composter',
'Eisenkette':'Chain','Leuchtflechte':'Glow Lichen','Steinsäge':'Stonecutter','Laterne':'Lantern','Gemeißelter Sandstein':'Chiseled Sandstone',
'Schmiedetisch':'Smithing Table','Entrindetes Eichenholz':'Stripped Oak Wood','Polierter Schwarzsteinknopf':'Polished Blackstone Button',
'Bienenstock':'Beehive','Leiter':'Ladder','Netherwarzenblock':'Nether Wart Block','Notenblock':'Note Block','Gearbeitetes Bücherregal':'Chiseled Bookshelf',
'Räucherofen':'Smoker','Knochenblock':'Bone Block','Hebel':'Lever','Netherrack':'Netherrack','Blumentopf':'Flower Pot','Lagerfeuer':'Campfire','Seelenerde':'Soul Soil',
'Meeresgurke':'Sea Pickle','Lesepult':'Lectern','Golddurchzogener Schwarzstein':'Gilded Blackstone','Amboss':'Anvil','Bogentisch':'Fletching Table',
'Glocke':'Bell','Azaleenlaub':'Azalea Leaves','Strohballen':'Hay Bale','Eisengitter':'Iron Bars','Haken':'Tripwire Hook',
'Blitzableiter':'Lightning Rod','Eisentür':'Iron Door','Kessel':'Cauldron','Werkbank':'Crafting Table','Bienennest':'Bee Nest',
'Schnee':'Snow','Kalzit':'Calcite','Tiefenschiefer':'Deepslate','Pilzstiel':'Mushroom Stem','Eichenstamm':'Oak Log',
'Gewachste angelaufene Kupferleuchte':'Waxed Exposed Copper Bulb','Nethergolderz':'Nether Gold Ore','Redstone-Lampe':'Redstone Lamp',
'Schildkrötenei':'Turtle Egg','Grasblock':'Grass Block','Trichter':'Hopper','Schleifstein':'Grindstone','Werker':'Crafter',
'Braustand':'Brewing Stand','Schiene':'Rail','Gerüst':'Scaffolding','Kartentisch':'Cartography Table','Schlamm':'Mud','Glatter Quarzblock':'Smooth Quartz Block',
'Honigblock':'Honey Block','Azalee':'Azalea','Faden':'String','Große Amethystknospe':'Large Amethyst Bud','Honigwabenblock':'Honeycomb Block',
'Geweihkorallenfächer':'Horn Coral Fan','Karmesinwurzeln':'Crimson Roots','Mangroven-Keimling':'Mangrove Propagule','Moosteppich':'Moss Carpet',
'Ofen':'Furnace','Plattenspieler':'Jukebox','Blühende Azalee':'Flowering Azalea','Gemeißelte Steinziegel':'Chiseled Stone Bricks',
'Hohes Gras':'Tall Grass','Karmesinpilz':'Crimson Fungus','Ockernes Froschlicht':'Ochre Froglight','Piglinkopf':'Piglin Head',
'Polierter Basalt':'Polished Basalt','Prismarin':'Prismarine','Seelensand':'Soul Sand','Amethysthaufen':'Amethyst Cluster',
'Endertruhe':'Ender Chest','Grobwägeplatte':'Heavy Weighted Pressure Plate','Lapislazulierz':'Lapis Lazuli Ore','Magmablock':'Magma Block',
'Netherwarze':'Nether Wart','Pilzlicht':'Shroomlight','Weinender Obsidian':'Crying Obsidian','Wirrpilz':'Warped Fungus','Zaubertisch':'Enchanting Table',
'Bücherregal':'Bookshelf','Verzierter Krug':'Decorated Pot','Weiße Tulpe':'White Tulip','Rosa Tulpe':'Pink Tulip','Rote Tulpe':'Red Tulip',
'Roter Pilzblock':'Red Mushroom Block','Blühendes Azaleenlaub':'Flowering Azalea Leaves','Netherziegelzaun':'Nether Brick Fence','Prismarintreppe':'Prismarine Stairs',
'Glasscheibe':'Glass Pane','Steindruckplatte':'Stone Pressure Plate','Polierter Diorit':'Polished Diorite','Polierter Andesit':'Polished Andesite',
'Polierter Schwarzstein':'Polished Blackstone','Schwarzstein':'Blackstone','Polierter Tiefenschiefer':'Polished Deepslate',
'Bruchtiefenschiefer':'Cobbled Deepslate','Schlammziegel':'Mud Bricks','Tiefenschieferziegel':'Deepslate Bricks','Tiefenschieferfliesen':'Deepslate Tiles',
'Ziegelsteinmauer':'Brick Wall','Karmesinfalltür':'Crimson Trapdoor','Wirrtür':'Warped Door','Wirrstufe':'Warped Slab','Wirrtreppe':'Warped Stairs',
'Wirrzaun':'Warped Fence','Wirrzauntor':'Warped Fence Gate','Karmesinstufe':'Crimson Slab','Karmesintür':'Crimson Door',
'Wassereimer':'Water Bucket',
}

def en_name(de):
    if de in normal:return normal[de]
    if de.startswith('Entrindete'):
        t=de.replace('Entrindetes ','').replace('Entrindeter ','')
        for wood,en in woods.items():
            if t==wood+'stamm':return f'Stripped {en} Log'
            if t==wood:return f'Stripped {en} Wood'
        if t=='Schwarzeichenstamm':return 'Stripped Dark Oak Log'
        if t=='Birkenstamm':return 'Stripped Birch Log'
        if t=='Fichtenstamm':return 'Stripped Spruce Log'
        if t=='Mangrovenstamm':return 'Stripped Mangrove Log'
    for wood,en in woods.items():
        if de==wood: return en+' Wood' if wood not in ['Bambus','Karmesin','Wirr'] else {'Bambus':'Bamboo','Karmesin':'Crimson Stem','Wirr':'Warped Stem'}[wood]
        for suffix,ensuffix in wood_suffixes:
            if de==wood+suffix: return f'{en} {ensuffix}'
        # Birch, spruce, oak stem language names: Fichtenstamm = Spruce Log
    for wood,en in [('Fichten','Spruce'),('Eichen','Oak'),('Birken','Birch'),('Kirsch','Cherry'),('Akazien','Acacia'),('Mangroven','Mangrove'),('Schwarzeichen','Dark Oak')]:
        if de==wood+'stamm':return en+' Log'
        if de==wood+'setzling':return en+' Sapling'
        if de==wood+'laub':return en+' Leaves'
    # Color family; some split forms e.g. 'Hellgraue glasierte Keramik'
    for color,colen in colors.items():
        if de.startswith(color+' '):
            suffix=de[len(color)+1:]
            cs={'Wolle':'Wool','Beton':'Concrete','Trockenbeton':'Concrete Powder','Keramik':'Terracotta','glasierte Keramik':'Glazed Terracotta','Glasscheibe':'Stained Glass Pane','Glas':'Stained Glass','Teppich':'Carpet','Bett':'Bed','Kerze':'Candle'}
            if suffix in cs: return colen+' '+cs[suffix]
    for prefix,base in [('Glatte ','Smooth '),('Glatter ','Smooth '),('Polierte ','Polished '),('Polierter ','Polished '),('Geschnittene ','Cut '),('Geschnittener ','Cut '),('Gemeißelte ','Chiseled '),('Gemeißelter ','Chiseled ')]:
        if de.startswith(prefix):
            rest=de[len(prefix):]
            suffixtranslation=''
            for suffix,ensuffix in mat_suffixes:
                if rest.endswith(suffix):
                    rest=rest[:-len(suffix)];suffixtranslation=' '+ensuffix;break
            if rest in mat_base:return base+mat_base[rest]+suffixtranslation
            if rest=='Tuffstein':return base+'Tuff'+suffixtranslation
            if rest=='Quarz':return base+'Quartz'+suffixtranslation
    for basename,english in mat_base.items():
        if de==basename: return english + ('s' if basename in ('Steinziegel','Schlammziegel','Tiefenschieferziegel','Tiefenschieferfliesen') else '')
        for suffix,en_suffix in mat_suffixes:
            if de==basename+suffix:return english+' '+en_suffix
    if de.startswith('Glatte ') or de.startswith('Glatter '):
        pass
    return None

# Map materials to achievable resource farms, not all craftable variants or nonrenewables.
farms=[
('Stone Farm','Bruchstein-Generator + Schmelzöfen/Silk Touch für Stein. Materialbedarf und Schematic ergänzen.'),
('Cobblestone Farm','Automatischer Bruchstein-Generator. Materialliste und Bauplan ergänzen.'),
('Cherry Tree Farm','Kirschbaum-Holz für Stämme, Holz und Bretter.'),
('Birch Tree Farm','Birkenbaum-Holz für Stämme, Holz und Bretter.'),
('Spruce Tree Farm','Fichtenholz für Bretter, Stämme und Holzbauteile.'),
('Oak Tree Farm','Eichenholz für Bretter und Holzbauteile.'),
('Dark Oak Tree Farm','Schwarzeichenholz für Holzbauteile.'),
('Mangrove Tree Farm','Mangrovenholz und Wurzeln.'),
('Bamboo Farm','Automatische Bambusproduktion für Bambusbretter und Bambusprodukte.'),
('Wool Farm','Automatische Schafschur; gewünschte Farben mit Farbstoffen herstellen.'),
('Iron Farm','Eisen für Eimer, Ketten, Laternen, Trichter und andere Crafting-Rezepte.'),
('Moss Farm','Moosproduktion mit Knochenmehl für Moosblöcke und Moosteppiche.'),
('Mud Farm','Erde mit Wasserflaschen zu Schlamm umwandeln, Schlammziegel weiterverarbeiten.'),
('Dripstone Farm','Spitzer Tropfstein wächst und lässt sich zu Tropfsteinblöcken craften.'),
('Flower Farm','Blumenproduktion mit Knochenmehl; je nach Biome und Farm-Design.'),
('Bee Farm','Honig und Honigwaben für Bienenstöcke und Honigblöcke.'),
('Mushroom Farm','Pilzblöcke via Riesenpilze; passende Pilze und Knochenmehl.'),
('Coral Farm','Korallen und Korallenfächer in warmen Ozeanen mit Knochenmehl; Blöcke ggf. mit Behutsamkeit abbauen.'),
('Concrete Factory','Betonpulver durch Kontakt mit Wasser zu Beton härten. Sand/Kies/Farbstoffe separat sammeln.'),
('Mob Farm','Drops wie Faden, Knochen und Schwarzpulver für weitere Crafting-Schritte.'),
('Froglight Farm','Frösche + kleine Magmawürfel im Nether; Bauplan ergänzen.'),
('Basalt Generator','Erzeugt Basalt mit Seelenerde, Lava und Blaueis.'),
('Azalea Farm','Moos- und Azaleenproduktion mit Knochenmehl.'),
('Village Trading Hall','Dorfbewohner-Handel für Glas, Quarzblöcke, Redstone und andere Gegenstände.'),
('Wood Farm','Allgemeine Holzfarm für weitere Holzarten.'),
]
namespace=uuid.UUID('97748f2a-15c5-4d90-9fc2-54e1861c0bce')
farmids={name:str(uuid.uuid5(namespace,'farm:'+name)) for name,description in farms}

def farm_for(de,en):
    if 'Cherry' in en or 'Kirsch' in de: return 'Cherry Tree Farm'
    if 'Birch' in en or 'Birken' in de: return 'Birch Tree Farm'
    if 'Spruce' in en or 'Fichten' in de: return 'Spruce Tree Farm'
    if 'Dark Oak' in en or 'Schwarzeichen' in de: return 'Dark Oak Tree Farm'
    if 'Mangrove' in en or 'Mangroven' in de: return 'Mangrove Tree Farm'
    if 'Bamboo' in en or 'Bambus' in de: return 'Bamboo Farm'
    if 'Oak' in en or 'Eichen' in de: return 'Oak Tree Farm'
    if 'Acacia' in en or 'Akazien' in de: return 'Wood Farm'
    if 'Wool' in en or 'Carpet' in en or 'Wolle' in de: return 'Wool Farm'
    if 'Cobblestone' in en or 'Bruchstein' in de:return 'Cobblestone Farm'
    if de=='Stein' or en.startswith('Stone ') or en in ['Smooth Stone','Stone','Stone Bricks','Cracked Stone Bricks','Chiseled Stone Bricks']:return 'Stone Farm'
    if 'Tropfstein' in de: return 'Dripstone Farm'
    if 'Moos' in de: return 'Moss Farm'
    if 'Schlamm' in de: return 'Mud Farm'
    if 'Azalee' in de or 'Azaleen' in de:return 'Azalea Farm'
    if de in ('Weiße Tulpe','Rosa Tulpe','Rote Tulpe','Farn','Niedriges Gras','Hohes Gras'):return 'Flower Farm'
    if 'Bienenstock' in de or 'Bienennest' in de or 'Honig' in de:return 'Bee Farm'
    if 'Pilzblock' in de or 'Pilzstiel' in de:return 'Mushroom Farm'
    if de in ('Geweihkorallenfächer',):return 'Coral Farm'
    if 'Froschlicht' in de:return 'Froglight Farm'
    if 'Beton' in de and 'Trockenbeton' not in de: return 'Concrete Factory'
    if de in ('Faden','Knochenblock'):return 'Mob Farm'
    if de in ('Wassereimer','Eisenkette','Eisentür','Trichter','Eisengitter','Amboss','Kessel','Laterne','Blitzableiter'):return 'Iron Farm' if de!='Blitzableiter' else None
    if de=='Polierter Basalt':return 'Basalt Generator'
    return None

def hint_for(de,en):
    mapping={
      'Abgestorbener Hirnkorallenblock':'Warmer Ozean: lebenden Hirnkorallenblock mit Behutsamkeit abbauen, ohne Wasser stirbt er ab.',
      'Feuerkorallenblock':'Warmer Ozean; mit Behutsamkeit abbauen. Blöcke sind nicht direkt über Knochenmehl farmbar.',
      'Kies':'Kies abbauen, z. B. in Flüssen oder Ozeanen; auch Piglin-Tauschhandel möglich.',
      'Sandstein':'Aus Sand craften (4 Sand → 1 Sandstein) oder natürlich abbauen.',
      'Wassereimer':'Eimer aus 3 Eisenbarren craften und an einer Wasserquelle füllen; nicht stackbar.',
      'Blaue Wolle':'Schafe blau färben oder weiße Wolle färben; Farbstoff einplanen.',
      'Hellgraue Wolle':'Hellgrau gefärbte Schafe scheren; Farbstoff einplanen.',
      'Blauer Beton':'Betonpulver mit Wasser härten; Sand, Kies und blauer Farbstoff nötig.',
      'Glatter Sandstein':'Sandstein im Ofen schmelzen.',
      'Glatter Stein':'Stein im Ofen schmelzen (Bruchstein zuerst zu Stein schmelzen).',
      'Karmesin-Netzel':'Karmesinwald im Nether; mit Behutsamkeit abbauen.',
      'Karmesin-Nezel':'Karmesinwald im Nether; mit Behutsamkeit abbauen.',
      'Nethergolderz':'Nether in goldführenden Bereichen; mit Behutsamkeit als Block mitnehmen.',
      'Schildkrötenei':'Schildkröten nach Paarung Eier legen lassen; nur mit Behutsamkeit abbauen.',
      'Piglinkopf':'Spezielle Mob-Drops; kein gewöhnlicher Farm-Drop.',
      'Weinender Obsidian':'Piglin-Tauschhandel, zerstörte Netherportale oder Bastionsruinen.',
      'Netherwarze':'In Netherfestungen/Bastionen sammeln; auf Seelensand vermehren.',
      'Ockernes Froschlicht':'Warmer Frosch, der kleine Magmawürfel frisst.',
      'Blitzableiter':'Aus 3 Kupferbarren craften.',
      'Gold durchzogener Schwarzstein':'Bastionsruinen im Nether (mit Behutsamkeit).',
      'Golddurchzogener Schwarzstein':'Bastionsruinen im Nether (mit Behutsamkeit).',
      'Eichenholzdruckplatte':'Achtung: In der gelieferten Liste zweimal aufgeführt; Mengen wurden addiert.',
      'Verzierter Krug':'Aus Ziegeln oder Töpferscherben craften.',
    }
    if de in mapping:return mapping[de]
    if 'Wassereimer' in de: return 'Aus Eisen craften und Wasser aufnehmen.'
    if 'Sandstein' in de: return 'Sandstein aus Sand herstellen oder in Wüsten abbauen.'
    if 'Tuff' in de:return 'Tuff natürlich im Untergrund abbauen (keine einfache Vanilla-Farm).'
    if 'Keramik' in de:return 'Ton zu Terrakotta brennen; für Farben Farbstoffe verwenden.'
    if 'Tiefenschiefer' in de:return 'Tief in der Oberwelt abbauen; Variationen über Crafting/Steinsäge.'
    return None

def recipe_for(de,en):
    # Minecraft crafting table recipes. Stonecutter may give better output than crafting table.
    suffix=next((s for s in [' Stairs',' Slab',' Wall'] if en.endswith(s)),None)
    if not suffix: return None
    base=en[:-len(suffix)]
    material=None
    if any(base==name for name in woods.values()):material=base+' Planks'
    elif base=='Bamboo':material='Bamboo Planks'
    elif base in ('Crimson','Warped'):material=base+' Planks'
    elif base=='Cobblestone':material='Cobblestone'
    elif base=='Stone Brick':material='Stone Bricks'
    elif base=='Mud Brick':material='Mud Bricks'
    elif base=='Deepslate Brick':material='Deepslate Bricks'
    elif base=='Deepslate Tile':material='Deepslate Tiles'
    elif base=='Nether Brick':material='Nether Bricks'
    elif base=='End Stone Brick':material='End Stone Bricks'
    elif base=='Brick':material='Bricks'
    else:material=base
    from_de={'Bamboo Planks':'Bambusbretter','Cobblestone':'Bruchstein','Stone Bricks':'Steinziegel','Mud Bricks':'Schlammziegel','Deepslate Bricks':'Tiefenschieferziegel','Deepslate Tiles':'Tiefenschieferfliesen','Nether Bricks':'Netherziegel','End Stone Bricks':'Endsteinziegel','Bricks':'Ziegelsteine',
             'Stone':'Stein','Andesite':'Andesit','Sandstone':'Sandstein','Polished Andesite':'Polierter Andesit','Polished Diorite':'Polierter Diorit','Polished Blackstone':'Polierter Schwarzstein','Polished Deepslate':'Polierter Tiefenschiefer','Smooth Sandstone':'Glatter Sandstein','Cut Sandstone':'Geschnittener Sandstein','Smooth Stone':'Glatter Stein','Smooth Quartz':'Glatter Quarzblock','Blackstone':'Schwarzstein','Deepslate':'Tiefenschiefer','Cobbled Deepslate':'Bruchtiefenschiefer','Prismarine':'Prismarin'}
    for german,english in woods.items():
        from_de[english+' Planks']=german+'bretter'
    if suffix==' Stairs': ingredient_per_craft,output_per_craft=6,4
    elif suffix==' Slab':ingredient_per_craft,output_per_craft=3,6
    else:ingredient_per_craft,output_per_craft=6,6
    return from_de.get(material,material),ingredient_per_craft,output_per_craft

unknown=[de for de in combined if en_name(de) is None]
if unknown:
    print('Untranslated items:',len(unknown),unknown)
    raise SystemExit('Fix missing EN translations before producing seed.')

def sqlval(value):
    if value is None:return 'NULL'
    if isinstance(value,int):return str(value)
    return "'"+value.replace("'","''")+"'"

out=[]
out.append('-- Cinderella’s castle — aus der Litematica-Materialliste (Screenshots + Text).')
out.append('-- Idempotent: feste IDs, bei erneutem Ausführen bleiben Beiträge und Aufgaben erhalten.')
out.append('-- Voraussetzung: supabase/schema.sql einmal ausführen, danach dieses Skript.')
out.append('begin;')
for name,description in farms:
    fid=farmids[name]
    out.append(f"insert into public.farms(id,name,description,status) values ({sqlval(fid)},{sqlval(name)},{sqlval(description)},'planned') on conflict (id) do nothing;")
out.append('-- Materialliste (Anzahl: Zielmenge, nicht vorhandener Bestand).')
for de,amount in combined.items():
    en=en_name(de); farm=farm_for(de,en);hint=hint_for(de,en)
    recipe=recipe_for(de,en); ingredient,per,output=recipe if recipe else (None,None,None)
    size=1 if de=='Wassereimer' or de.endswith(' Bett') else 64
    iid=str(uuid.uuid5(namespace,'item:'+de))
    vals=[iid,de,en,amount,size,ingredient,per,output,farmids.get(farm),hint]
    query='insert into public.items(id,name_de,name_en,required,stack_size,ingredient_name,ingredient_per_craft,output_per_craft,farm_id,source_hint) values ('+','.join(map(sqlval,vals))+') on conflict (id) do update set name_de=excluded.name_de,name_en=excluded.name_en,required=excluded.required,stack_size=excluded.stack_size,ingredient_name=excluded.ingredient_name,ingredient_per_craft=excluded.ingredient_per_craft,output_per_craft=excluded.output_per_craft,farm_id=excluded.farm_id,source_hint=excluded.source_hint;'
    out.append(query)
out.append('commit;')
(ROOT/'supabase/seed-cinderella.sql').write_text('\n'.join(out)+'\n',encoding='utf-8')
materials=[{'name_de':de,'name_en':en_name(de),'required':amount,'stack_size':1 if de=='Wassereimer' or de.endswith(' Bett') else 64,'farm':farm_for(de,en_name(de)),'recipe':recipe_for(de,en_name(de)),'source_hint':hint_for(de,en_name(de))} for de,amount in combined.items()]
(ROOT/'data/cinderella-materials.json').write_text(json.dumps(materials,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'OK: {len(rows)} source lines, {len(materials)} unique items, {sum(combined.values()):,} total units, {len(farms)} farms')
print('Recipe-linked:',sum(bool(x['recipe']) for x in materials),'Farm-linked:',sum(bool(x['farm']) for x in materials),'English names:',sum(bool(x['name_en']) for x in materials))
