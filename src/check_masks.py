from PIL import Image
import sys
import os

def exit(n=0):
    os.system("pause")
    sys.exit(n)

if __name__ == "__main__":
    os.chdir(os.path.dirname(sys.argv[0]))
    if len(sys.argv) != 2:
        print("Usage: {} mask_folder".format(sys.argv[0]))
        exit(1)

    if not os.path.isdir(sys.argv[1]):
        print("No such folder: {}".format(sys.argv[1]))
        exit(2)

    for i in ["corner", "diagonal", "half"]:
        if not os.path.isfile(os.path.join(sys.argv[1], i + ".png")):
            print("No such file: {}".format(os.path.join(sys.argv[1], i + ".png")))
            exit(2)

    masks = [Image.open(os.path.join(sys.argv[1], i + ".png")) for i in ["corner", "diagonal", "half"]]

    size = masks[0].size
    if size[0] != size[1]:
        print("Width != height, aborting")
        exit(3)
    if size != masks[1].size or size != masks[2].size:
        print("Masks with differrent sizes!")
        exit(3)
    scale = size[0]

    # (mask index, rotation clockwise)
    pattern = [
        [(1, 3), (1, 2), (1, 3), (1, 1), (0, 3)],
        [(2, 1), (2, 3), (0, 1), (2, 0), (0, 0)],
        [(1, 0), (2, 3), (0, 2), (2, 2), (0, 3)],
        [(1, 2), (0, 0), (2, 1), (1, 2), (0, 0)],
        [(1, 1), (2, 2), (1, 0), (1, 1), (0, 3)]
        ]

    res = Image.new("RGB", (scale * len(pattern[0]), scale * len(pattern)), (0, 100, 0))

    for y, line in enumerate(pattern):
        for x, inds in enumerate(line):
            img, rot = inds
            res.paste(masks[img].rotate(-90 * rot), (scale * x, scale * y))

    res = res.resize((1920, 1920), resample=Image.NEAREST)
    res.save("mask_checker.png")
