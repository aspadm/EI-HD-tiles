import os
vipshome = "./"
os.environ["PATH"] = vipshome + ";" + os.environ["PATH"]

import pyvips as ps
import numpy as np
import sys
import glob
import yaml

def exit(n=0):
    os.system("pause")
    sys.exit(n)

def test_err(test_expr, err_str):
    if not test_expr:
        print(err_str)
        exit(3)

def vs2np_uchar(img):
    if img.hasalpha():
        img = img[:,:,:3]
    assert img.format == "uchar", "Got {}, not uchar".format(img.type)
    return np.ndarray(buffer=img.write_to_memory(),
        dtype=np.uint8,
        shape=[img.height, img.width, 3]).astype(np.float64)

def np2vs_uchar(arr):
    assert arr.dtype == np.uint8, "Got {}, not uint8".format(arr.dtype)
    height, width, bands = arr.shape
    linear = arr.reshape(width * height * bands)
    return ps.Image.new_from_memory(linear.data, width, height, bands, "uchar")

def np_mix_2(b1, m1, b2):
    return np.sqrt(
        np.square(b1)                # base 1
          * (1.0 - (m1 / 255.0)) +   # mask 1
        np.square(b2) * (m1 / 255.0) # base 2, mask 1
        ).astype(np.uint8)

def np_mix_3(b1, m1, b2, m2, b3):
    return np.sqrt(
        (
        np.square(b1)                # base 1
          * (1.0 - (m1 / 255.0)) +   # mask 1
        np.square(b2) * (m1 / 255.0) # base 2, mask 1
        ) * (1.0 - (m2 / 255.0)) +   # mask 2
        np.square(b3) * (m2 / 255.0) # base 3, mask 2
        ).astype(np.uint8)

def np_mix_4(b1, m1, b2, m2, b3, m3, b4):
    return np.sqrt(
        (
        (
        np.square(b1)                # base 1
          * (1.0 - (m1 / 255.0)) +   # mask 1
        np.square(b2) * (m1 / 255.0) # base 2, mask 1
        ) * (1.0 - (m2 / 255.0)) +   # mask 2
        np.square(b3) * (m2 / 255.0) # base 3, mask 2
        ) * (1.0 - (m3 / 255.0)) +   # mask 3
        np.square(b4) * (m3 / 255.0) # base 4, mask 3
        ).astype(np.uint8)

def mix_tile(tile) -> ps.Image:
    if len(tile) == 1 and tile[0]["base"] is None:
        return ps.Image.black(COMMON_RES, COMMON_RES, bands=3)

    # res = sqrt(mask * sqr(a) + (1 - mask) * sqr(b))

    if len(tile) == 1:
        # bottom base (base 1)
        b1 = ps.Image.new_from_file(tile[0]["base"],
                                    memory=True).rot(tile[0]["rotation"])
        if b1.hasalpha():
            b1 = b1[:,:,:3]
        test_err(b1.height == b1.width == COMMON_RES,
                 "Incorrect resolution in {}".format(tile[0]["base"]))
        return b1
    elif len(tile) == 3:
        # bottom base (base 1)
        b1 = ps.Image.new_from_file(tile[0]["base"],
                                    memory=True).rot(tile[0]["rotation"])
        test_err(b1.height == b1.width == COMMON_RES,
                 "Incorrect resolution in {}".format(tile[0]["base"]))
        # mask 1
        m1 = ps.Image.new_from_file(tile[1]["mask"],
                                    memory=True).rot(tile[1]["rotation"])
        test_err(m1.height == m1.width == COMMON_RES,
                 "Incorrect resolution in {}".format(tile[1]["mask"]))
        if tile[1]["inverted"]:
            m1 = m1.invert()
        # base 2
        b2 = ps.Image.new_from_file(tile[2]["base"],
                                    memory=True).rot(tile[2]["rotation"])
        test_err(b2.height == b2.width == COMMON_RES,
                 "Incorrect resolution in {}".format(tile[2]["base"]))

        return np2vs_uchar(np_mix_2(
            vs2np_uchar(b1),
            vs2np_uchar(m1),
            vs2np_uchar(b2)
        ))
    elif len(tile) == 5:
        # bottom base (base 1)
        b1 = ps.Image.new_from_file(tile[0]["base"],
                                    memory=True).rot(tile[0]["rotation"])
        test_err(b1.height == b1.width == COMMON_RES,
                 "Incorrect resolution in {}".format(tile[0]["base"]))
        # mask 1
        m1 = ps.Image.new_from_file(tile[1]["mask"],
                                    memory=True).rot(tile[1]["rotation"])
        test_err(m1.height == m1.width == COMMON_RES,
                 "Incorrect resolution in {}".format(tile[1]["mask"]))
        if tile[1]["inverted"]:
            m1 = m1.invert()
        # base 2
        b2 = ps.Image.new_from_file(tile[2]["base"],
                                    memory=True).rot(tile[2]["rotation"])
        test_err(b2.height == b2.width == COMMON_RES,
                 "Incorrect resolution in {}".format(tile[2]["base"]))
        # mask 2
        m2 = ps.Image.new_from_file(tile[3]["mask"],
                                    memory=True).rot(tile[3]["rotation"])
        test_err(m2.height == m2.width == COMMON_RES,
                 "Incorrect resolution in {}".format(tile[3]["mask"]))
        if tile[3]["inverted"]:
            m2 = m2.invert()
        # base 3
        b3 = ps.Image.new_from_file(tile[4]["base"],
                                    memory=True).rot(tile[4]["rotation"])
        test_err(b3.height == b3.width == COMMON_RES,
                 "Incorrect resolution in {}".format(tile[4]["base"]))

        return np2vs_uchar(np_mix_3(
            vs2np_uchar(b1),
            vs2np_uchar(m1),
            vs2np_uchar(b2),
            vs2np_uchar(m2),
            vs2np_uchar(b3)
        ))
    else: # 7
        # bottom base (base 1)
        b1 = ps.Image.new_from_file(tile[0]["base"],
                                    memory=True).rot(tile[0]["rotation"])
        test_err(b1.height == b1.width == COMMON_RES,
                 "Incorrect resolution in {}".format(tile[0]["base"]))
        # mask 1
        m1 = ps.Image.new_from_file(tile[1]["mask"],
                                    memory=True).rot(tile[1]["rotation"])
        test_err(m1.height == m1.width == COMMON_RES,
                 "Incorrect resolution in {}".format(tile[1]["mask"]))
        if tile[1]["inverted"]:
            m1 = m1.invert()
        # base 2
        b2 = ps.Image.new_from_file(tile[2]["base"],
                                    memory=True).rot(tile[2]["rotation"])
        test_err(b2.height == b2.width == COMMON_RES,
                 "Incorrect resolution in {}".format(tile[2]["base"]))
        # mask 2
        m2 = ps.Image.new_from_file(tile[3]["mask"],
                                    memory=True).rot(tile[3]["rotation"])
        test_err(m2.height == m2.width == COMMON_RES,
                 "Incorrect resolution in {}".format(tile[3]["mask"]))
        if tile[3]["inverted"]:
            m2 = m2.invert()
        # base 3
        b3 = ps.Image.new_from_file(tile[4]["base"],
                                    memory=True).rot(tile[4]["rotation"])
        test_err(b3.height == b3.width == COMMON_RES,
                 "Incorrect resolution in {}".format(tile[4]["base"]))
        # mask 3
        m3 = ps.Image.new_from_file(tile[5]["mask"],
                                    memory=True).rot(tile[5]["rotation"])
        test_err(m3.height == m3.width == COMMON_RES,
                 "Incorrect resolution in {}".format(tile[5]["mask"]))
        if tile[5]["inverted"]:
            m3 = m3.invert()
        # base 4
        b4 = ps.Image.new_from_file(tile[6]["base"],
                                    memory=True).rot(tile[6]["rotation"])
        test_err(b4.height == b4.width == COMMON_RES,
                 "Incorrect resolution in {}".format(tile[6]["base"]))

        return np2vs_uchar(np_mix_4(
            vs2np_uchar(b1),
            vs2np_uchar(m1),
            vs2np_uchar(b2),
            vs2np_uchar(m2),
            vs2np_uchar(b3),
            vs2np_uchar(m3),
            vs2np_uchar(b4)
        ))

def prepare_tile(tile):
    return mix_tile(tile).embed(FRAME_RES, FRAME_RES,
                                TILE_RES, TILE_RES,
                                extend="mirror")

def get_image_path(img_no_ext):
    paths = glob.glob(img_no_ext + ".*", recursive=False)

    exts = {
        # lossless
        ".png": 5,
        ".bmp": 5,
        ".tif": 5,
        ".tiff": 5,
        # lossy
        ".webm": 4,
        ".gif": 2,
        ".jpg": 1,
        ".jpeg": 1,
    }

    valid = []
    for path in paths:
        w = exts.get(os.path.splitext(path)[1].lower(), 0)
        if w:
            valid.append((w, path))

    valid.sort(reverse=True)

    if len(valid):
        return valid[0][1]
    else:
        None

def sanitize_def(map_def):
    test_err(isinstance(map_def, dict), "Incorrect common format")
    test_err(isinstance(map_def["map_name"], str), "Incorrect map name")
    test_err(isinstance(map_def["tiles"], list), "Incorrect tiles format")
    test_err(0 < len(map_def["tiles"]) < 513, "Incorrect number of tiles")
    test_err(len(map_def["tiles"]) % 64 == 0, "Incomplete number of tiles for tileset")

    for tile in map_def["tiles"]:
        test_err(isinstance(tile, list), "Incorrect tile format")
        test_err(len(tile) % 2 == 1, "Incorrect layers count")
        test_err(0 < len(tile) < 8, "Incorrect layers count")

        for i, part in enumerate(tile):
            test_err(isinstance(part, dict), "Incorrect layer format")

            if i % 2 == 0: # base
                test_err("base" in part.keys(), "No base layer found")
                test_err(isinstance(part["base"], str), "Incorrect base path format")

                if len(tile) == 1 and part["base"] == "":
                    part["base"] = None
                    break

                tmp_base = get_image_path(os.path.join(TILES_DIR, part["base"]))
                test_err(tmp_base, "Base layer file {} not found".format(part["base"]))
                part["base"] = tmp_base

                if "rotation" not in part.keys():
                    part.update({"rotation": 0})

                test_err(isinstance(part["rotation"], int), "Incorrect rotation")
                part["rotation"] *= -1
                part["rotation"] %= 360
                test_err(part["rotation"] in [0, 90, 180, 270], "Incorrect rotation")
                part["rotation"] //= 90
            else: # mask
                test_err("mask" in part.keys(), "No mask layer found")
                test_err(isinstance(part["mask"], str), "Incorrect mask path format")

                tmp_mask = get_image_path(os.path.join(MASKS_DIR, part["mask"]))
                test_err(tmp_mask, "Mask layer file {} not found".format(part["mask"]))
                part["mask"] = tmp_mask

                if "rotation" not in part.keys():
                    part.update({"rotation": 0})

                test_err(isinstance(part["rotation"], int), "Incorrect rotation")
                part["rotation"] *= -1
                part["rotation"] %= 360
                test_err(part["rotation"] in [0, 90, 180, 270], "Incorrect rotation")
                part["rotation"] //= 90

                if "inverted" not in part.keys():
                    part.update({"inverted": False})

                test_err(isinstance(part["inverted"], bool), "Incorrect inverted flag")

def make_tileset(map_def):
    for tileset in range(len(map_def["tiles"]) // 64):
        print("Bake tileset", tileset)
        tile_array = [prepare_tile(i) for i in
            map_def["tiles"][tileset*64:(tileset+1)*64]]
        res = ps.Image.arrayjoin(tile_array, across=8).flipver()
        res.write_to_file(os.path.join(OUT_DIR,
            map_def["map_name"] + "{:03d}.png".format(tileset)))

def convert_tileset(map_name):
    print("Start work on {}".format(map_name))
    try:
        with open(map_name) as f:
            map_def = yaml.safe_load(f)
    except Exception as e:
        print(e)
        exit(2)
    print("Check structure")
    sanitize_def(map_def)
    print("Generating tilesets")
    make_tileset(map_def)
    print("Task done")

    return len(map_def["tiles"]) // 64, map_def["map_name"]

def read_config():
    global COMMON_RES
    global OUT_DIR
    global TILES_DIR
    global MASKS_DIR
    global FRAME_RES
    global TILE_RES
    global MAPS_DIR
    global TOOLS_DIR

    if os.path.isfile("config.yaml"):
        with open("config.yaml") as f:
            conf = yaml.safe_load(f)
    else:
        conf = {}

    COMMON_RES = conf.get("tile_resolution", 192)
    OUT_DIR = conf.get("output_directory", "output")
    TILES_DIR = conf.get("tiles_directory", "tiles")
    MASKS_DIR = conf.get("masks_directory", "masks")
    MAPS_DIR = conf.get("maps_directory", "maps")
    TOOLS_DIR = conf.get("tools_directory", "tools")

    test_err(COMMON_RES in [48, 96, 192], "Incorrect tile_resolution: {}".format(COMMON_RES))
    test_err(os.path.isdir(OUT_DIR), "Output directory {} not exist".format(OUT_DIR))
    test_err(os.path.isdir(TILES_DIR), "Tiles directory {} not exist".format(TILES_DIR))
    test_err(os.path.isdir(MASKS_DIR), "Masks directory {} not exist".format(MASKS_DIR))
    test_err(os.path.isdir(MAPS_DIR), "Maps directory {} not exist".format(MAPS_DIR))
    test_err(os.path.isdir(TOOLS_DIR), "Tools directory {} not exist".format(TOOLS_DIR))

    FRAME_RES = COMMON_RES // 6
    TILE_RES = FRAME_RES * 8

if __name__ == "__main__":
    if os.environ.get("DONT_CHANGE_CWD", "0").lower() not in ("1", "yes", "true", "on"):
        os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

    if len(sys.argv) < 2:
        print("Usage: {:} <map.yaml> [map2.yaml ...]".format(sys.argv[0]))
        exit(1)

    read_config()

    for map_name in sys.argv[1:]:
        if not os.path.isfile(map_name):
            print("File {:} not exist!".format(map_name))
            exit(1)

    print("Start work")
    for map_name in sys.argv[1:]:
        convert_tileset(map_name)
    print("All tasks done")
