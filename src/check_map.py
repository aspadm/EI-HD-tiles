import sys
import os
from PIL import Image, ImageDraw

# Add scripts dir to python search path
sys.path.append(os.path.dirname(os.path.abspath(sys.argv[0])))
from maps_def import maps as MAPS

BORDERS = True
IDS = True

def bake_map(tiles, info):
    size = tiles[0].size[0]
    res = Image.new("RGB", (len(info[0]) * size, len(info) * size))
    z_d = ImageDraw.Draw(res)

    for y, line in enumerate(info):
        for x, tile in enumerate(line):
            res.paste(tiles[tile[0]].rotate(-90 * tile[1]),
                      (x * size, (len(info) - 1) * size - y * size))
            # naming
            if IDS:
                z_d.text((x * size + 10,
                          (len(info) - 1) * size - y * size + 2),
                         str(tile[0]),
                         fill=(255, 0, 0))

    # Tiles borders
    if BORDERS:
        for i in range(len(info)):
            z_d.line((0, i * size, len(info[0]) * size, i * size), fill=(0, 0, 100))

        # vertical
        for i in range(len(info[0])):
            z_d.line((i * size, 0, i * size, len(info) * size), fill=(0, 0, 100))

    return res

def read_info(map_name):
    atls_cnt, y, x = MAPS[map_name.lower()][0]
    tmp = MAPS[map_name.lower()][1:]

    res = [tmp[i*x:(i+1)*x] for i in range(y)]

    return atls_cnt, res

def read_tiles(tiles_path, map_name, tilesets_count):
    res = []
    for i in range(tilesets_count):
        if not os.path.isfile(os.path.join(tiles_path, "{:}{:03d}.png".format(map_name, i))):
            print("No such file:", os.path.join(tiles_path, "{:}{:03d}.png".format(map_name, i)))
            sys.exit(-2)
        atlas = Image.open(os.path.join(tiles_path, "{:}{:03d}.png".format(map_name, i))).transpose(Image.FLIP_TOP_BOTTOM)
        t_size = atlas.size[0] // 8
        frame = t_size // 8
        usful = t_size * 3 // 4
        for y in range(8):
            for x in range(8):
                res.append(atlas.crop((x * t_size + frame,
                                       y * t_size + frame,
                                       x * t_size + frame + usful,
                                       y * t_size + frame + usful)).transpose(Image.FLIP_TOP_BOTTOM))
    return res

if __name__ == "__main__":
    if os.environ.get("DONT_CHANGE_CWD", "0").lower() not in ("1", "yes", "true", "on"):
        os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

    if len(sys.argv) != 3:
        print("Usage: check_map map_name tiles_dir")
        sys.exit(0)
    map_name = sys.argv[1]
    tiles_path = sys.argv[2]

    if map_name.lower() not in MAPS.keys() or \
        map_name not in ["BaseGipat", "bz2g", "bz3g", "bz4g", "bz5g", "bz6g", "Zone1", "Zone2", "Zone3Obr", "Zone4", "Zone6", "Zone6_2", "Zone7", "Zone8", "zone9", "ZoneMainMenuNew", "bz10k", "bz8k", "bz9k", "Zone11", "Zone12", "Zone13", "bz11k", "Zone14", "bz13h", "bz16h", "Zone15", "Zone18", "Zone19", "bz14h", "bz15h", "bz18h", "Bz7g", "Zone16", "Zone17", "Zone20", "Zone5_1", "Zone10"]:
        print("Unknown map:", map_name)
        sys.exit(-1)

    tilesets_count, info = read_info(map_name)
    tiles = read_tiles(tiles_path, map_name, tilesets_count)
    res = bake_map(tiles, info)
    res.save("map_checker.png")
