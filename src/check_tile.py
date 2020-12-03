from PIL import Image
import sys
import os

def exit(n=0):
    os.system("pause")
    sys.exit(n)

if __name__ == "__main__":
    os.chdir(os.path.dirname(sys.argv[0]))
    if len(sys.argv) != 2:
        print("Usage: {:} tile".format(sys.argv[0]))
        exit(1)
    
    if not os.path.isfile(sys.argv[1]):
        print("No such file: {}".format(sys.argv[1]))
        exit(2)

    tile = Image.open(sys.argv[1])
    if tile.size[0] != tile.size[1]:
        print("Width != height, aborting")
        exit(3)
    
    scale = tile.size[0]

    # rotation clockwise
    pattern = [
        [1, 2, 3],
        [2, 0, 2],
        [2, 2, None]
        ]

    res = Image.new("RGB", (scale * len(pattern[0]), scale * len(pattern)), (0, 0, 0))

    for y, line in enumerate(pattern):
        for x, rot in enumerate(line):
            if rot is None:
                continue
            res.paste(tile.rotate(-90 * rot), (scale * x, scale * y))

    res = res.resize((1152, 1152), resample=Image.NEAREST)
    res.save("tile_checker.png")
