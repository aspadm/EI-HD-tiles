import sys
import os
import yaml
import datetime
import subprocess
import zipfile
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor

# Add scripts dir to python search path
sys.path.append(os.path.dirname(os.path.abspath(sys.argv[0])))
import gen_tileset
from gen_tileset import test_err, convert_tileset

def exit(n=0):
    os.system("pause")
    sys.exit(n)

def construct_dxt1_mmp(width, height, packing, mips, data):
    # magic
    res = bytes([0x4d, 0x4d, 0x50, 0x00])

    res += width.to_bytes(4, "little")
    res += height.to_bytes(4, "little")
    res += mips.to_bytes(4, "little")

    # FourCC
    if packing == "DXT1":
        res += bytes([0x44, 0x58, 0x54, 0x31])
        bit_count = 4
    else:
        raise ValueError("Unknown texture compression")

    res += bit_count.to_bytes(4, "little")
    # padding
    res += bytes([0] * 48)
    # Offset
    res += bytes([0x00, 0x00, 0x00, 0x00])
    assert len(res) == 76

    return res + data

def dds_read(file):
    magic = file.read(4)
    assert magic == b"\x44\x44\x53\x20"

    header_size = int.from_bytes(file.read(4), "little")
    assert header_size == 124

    _ = int.from_bytes(file.read(4), "little") # flags

    height = int.from_bytes(file.read(4), "little")
    width = int.from_bytes(file.read(4), "little")

    assert height == width

    _ = file.read(8)

    mips = int.from_bytes(file.read(4), "little")

    assert 2 ** (mips - 1) == width

    file.seek(76)

    header_size = int.from_bytes(file.read(4), "little")
    assert header_size == 32

    pix_flags = int.from_bytes(file.read(4), "little")

    if pix_flags & 0x4:
        packing = file.read(4).decode("ASCII")
        assert packing == "DXT1"
        data_size = sum([((((2 ** i) ** 2 - 1) // 16 + 1) * 16) // 2 for i in range(mips)])
    else:
        raise ValueError("Unknown format")

    file.seek(128)

    print(file.name, packing, width, "x", height, data_size, "bytes")
    data = file.read(data_size)
    assert len(data) == data_size, "expected: {}, real: {}".format(data_size, len(data))

    return width, height, packing, mips, data

def convert_texture(img_name):
    print("Converting {} from png to dds".format(img_name))
    subprocess.check_call([
        os.path.join(gen_tileset.TOOLS_DIR, "nvcompress.exe"),
        "-color", "-bc1", "-silent",
        os.path.join(OUT_DIR, img_name + ".png"),
        os.path.join(OUT_DIR, img_name + ".dds"),
    ])

    print("Converting {} from dds to mmp".format(img_name))
    with open(os.path.join(OUT_DIR, img_name + ".dds"), "rb") as f:
        width, height, packing, mips, data = dds_read(f)
    with open(os.path.join(OUT_DIR, "textures_res", img_name + ".mmp"), "wb") as f:
        f.write(construct_dxt1_mmp(width, height, packing, mips, data))

def sanitize_mod(mod_def):
    test_err(isinstance(mod_def, dict), "Incorrect common format")
    test_err(isinstance(mod_def["mod_name"], str), "Incorrect mod name")
    test_err(len(mod_def["mod_name"]), "Empty mod name")
    test_err(isinstance(mod_def["author"], str), "Incorrect author name")
    test_err(isinstance(mod_def["version"], str), "Incorrect version string")
    test_err(isinstance(mod_def["author_email"], str), "Incorrect author email")
    test_err(isinstance(mod_def["author_url"], str), "Incorrect author URL")

    test_err(isinstance(mod_def["maps"], list), "Incorrect maps format")
    test_err(len(mod_def["maps"]), "No maps in mod")

    for i, tileset in enumerate(mod_def["maps"]):
        test_err(isinstance(tileset, str), "Incorrect map name")
        mod_def["maps"][i] = os.path.join(gen_tileset.MAPS_DIR, tileset + ".yaml")

    mod_def["date"] = datetime.datetime.today().strftime("%d.%m.%Y")

def create_mod(mod_path):
    with open(mod_path) as f:
        try:
            mod_def = yaml.safe_load(f)
        except Exception as e:
            print(e)
            exit(2)

    sanitize_mod(mod_def)

    for tileset in mod_def["maps"]:
        if not os.path.isfile(tileset):
            print("File {:} not exist!".format(tileset))
            exit(1)

    if not os.path.isdir(os.path.join(OUT_DIR, "textures_res")):
        os.makedirs(os.path.join(OUT_DIR, "textures_res"))

    with ThreadPoolExecutor(max(2, os.cpu_count() // 2)) as executor:
        print("Converting tilesets")
        futures = [executor.submit(convert_tileset, tileset) for tileset in mod_def["maps"]]
        converted_tilesets = ["{}{:03d}".format(img_name, i)
                              for img_count, img_name in (f.result() for f in futures)
                              for i in range(img_count)]

        print("Converting textures format")
        futures = [executor.submit(convert_texture, img_name) for img_name in converted_tilesets]
        for future in futures:
            future.result()

    with open(os.path.join(OUT_DIR, "config.ini"), "w") as f:
        f.write("""[MOD]
Title={}
Author={}
AuthorEmail={}
URL={}
Date_DMY={}
Version={}
Single=1
Multi=1
GameSaves=0
[RES]
textures.res=textures.res""".format(
    mod_def["mod_name"],
    mod_def["author"],
    mod_def["author_email"],
    mod_def["author_url"],
    mod_def["date"],
    mod_def["version"]))

    subprocess.call(os.path.join(gen_tileset.TOOLS_DIR, "eipacker.exe") +
        " " + os.path.join(OUT_DIR, "config.ini"), shell=True)

    subprocess.call(os.path.join(gen_tileset.TOOLS_DIR, "eipacker.exe") +
        " " + os.path.join(OUT_DIR, "textures_res"), shell=True)

    time.sleep(1) # Fix error with zipfile

    with zipfile.ZipFile(os.path.join(MOD_OUT_DIR, mod_def["mod_name"] + ".zip"), "w") as z:
        z.write(os.path.join(OUT_DIR, "config.reg"), arcname=os.path.join(mod_def["mod_name"], "config.reg"))
        z.write(os.path.join(OUT_DIR, "textures.res"), arcname=os.path.join(mod_def["mod_name"], "textures.res"))

if __name__ == "__main__":
    if os.environ.get("DONT_CHANGE_CWD", "0").lower() not in ("1", "yes", "true", "on"):
        os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

    if len(sys.argv) != 2:
        print("Usage: {} <mod.yaml>".format(sys.argv[0]))
        exit(1)

    gen_tileset.read_config()

    MOD_OUT_DIR = gen_tileset.OUT_DIR

    if not os.path.isfile(sys.argv[1]):
        print("File {:} not exist!".format(sys.argv[1]))
        exit(1)

    temp_dir = tempfile.TemporaryDirectory()
    print("Temp dir:", temp_dir.name)

    gen_tileset.OUT_DIR = temp_dir.name
    OUT_DIR = temp_dir.name

    start_time = time.time()
    create_mod(sys.argv[1])
    mins, secs = [int(x) for x in divmod(time.time() - start_time, 60)]
    print("Mod has been successfully created in {} minutes and {} seconds".format(mins, secs))
    exit(0)
