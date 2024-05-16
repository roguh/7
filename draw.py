#!/usr/bin/env python3
"""Draw geometric art based on heptagons (7-sided polygons) in 
2D Euclidean space using Python's Turtle module.

Recursive, overlapping tiling pattern with an organic appearance at higher recursion depths.

There would be no overlapping in Minkowski or Hyperbolic space :)

FELINA@FELINA.ART
"""
import argparse
from collections import defaultdict
import pprint
import time

try:
    import turtle
except ImportError as exc:
    print(
        """Try installing the tk library with:
    sudo pacman -S tk
    sudo apt install tk
    sudo dnf install tk
"""
    )
    raise exc

SKIP2 = True  # moar fast
CHILD_SIZING_ALGORITHMS = {
    "id": lambda s: s,
    "p67": lambda s: s ** (6 / 7),
    "p97": lambda s: s ** (9 / 7),
    "m57": lambda s: s * 5 / 7,
    "m37": lambda s: s * 3 / 7,  # VERY NICE alignment
    "1m37": lambda s: s * 3 / 7 if int(s) == s else s,  # VERY NICE alignment
    "Mm37": lambda s: s * 3 / 7 if s > 20 else s,  # VERY NICE alignment
    "m97": lambda s: s * 9 / 7,
}

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--levels", type=int, required=True)
parser.add_argument("--size", type=int, default=50)
parser.add_argument("--write", action="store_true")
parser.add_argument("--light-mode", action="store_true")
parser.add_argument(
    "--childsizing", choices=CHILD_SIZING_ALGORITHMS.keys(), default="id"
)
parser.add_argument(
    "--filename", type=str, default="heptagon_tile_euclidean_TIME_ARGS.eps"
)

STATS = {"SIZES": {}, "TOTAL": 0, "SIDES": 0, "TOTAL_PER": defaultdict(lambda: 0)}
guy = turtle.Turtle()
guy.shape("turtle")
guy.shapesize(2, 2)


def print_side_number(side: int, color: tuple[int, int, int], font_size: int = 13):
    """Label each of the 7 side labels in Roman numerals."""
    r, g, b = color
    label = str(side)
    label = "I II III IV V VI VII".split()[side % 7]
    align = "left" if side < 3 or side == 5 else "right"
    if side == 4:
        align = "center"
    guy.color((r, g, b))
    guy.write(label, align=align, font=("Mono", font_size - 1, "bold"))
    guy.color((255 - r, 255 - g, 255 - b))
    guy.write(label, align=align, font=("Mono", font_size, "normal"))
    guy.color(color)


BREWER_PuRd9 = [
    (247, 244, 249),
    (231, 225, 239),
    (212, 185, 218),
    (201, 148, 199),
    (223, 101, 176),
    (231, 41, 138),
    (206, 18, 86),
    (152, 0, 67),
    (103, 0, 31),
]
BREWER_PuRd9.reverse()
BREWER_PuRd9.insert(0, (0, 255, 0))
# BREWER_PuRd9.insert(0, (255, 0, 255))

ORIGINAL = [(255, 0, 0), (255, 196, 0), (196, 48, 0), (255, 96, 0)]


# wow:
# levels=3,2 size=[(10,20,30), 100, 100, 100, ...]
def heptagons(
    size,
    direction=1,
    levels=0,
    root=True,
    parent_side=0,
    writing=False,
    childsizing=lambda x: x,
) -> tuple[int, int]:
    """Draw a recursive, overlapping heptagon tile pattern."""
    # Draw as fast as possible
    guy.speed("fastest")
    turtle.delay(0)
    turtle.colormode(255)

    colors = BREWER_PuRd9
    if root:
        # Root heptagon is black
        r, g, b = turtle.bgcolor()
        colors.insert(levels, (255, 255, 255))
        guy.penup()
        guy.setpos(-size / 2, size)
        guy.pendown()

    mmax_x, mmax_y = 0, 0
    STATS["SIZES"][levels] = size
    STATS["TOTAL"] += 1
    STATS["TOTAL_PER"][levels] += 1
    # for side in range(5): NOOOOOO stop at 6, not limit
    for side in range(7):
        STATS["SIDES"] += 1
        # This helps a lot with limiting recursion, closer to the hyperbolic tiling too
        is_outer = side not in [0, 1, 6]

        child_size = childsizing(size)

        (r, g, _) = colors[levels % len(colors)]
        b = (parent_side * 40) % 255
        if SKIP2:
            if side in [3, 6]:
                guy.penup()
            else:
                guy.pendown()
        guy.color((r, g, b))

        # Draw first part 1 side
        pensize = levels * 3 + 1
        guy.pensize(pensize)
        size0 = max(0, (size - child_size) / 2)
        if size0 > 0:
            guy.forward(size0)
        # TODO NEW_SHAPE.eps
        # turn right(dir*360/7)
        # after going forward(size-childsize)/2 guy.right(direction * 360 / 7)

        if levels > 0 and (is_outer or root):
            # Draw child heptagon
            max_x, max_y = heptagons(
                child_size,
                direction=-direction,
                levels=levels - 1,
                root=False,
                parent_side=side,
                childsizing=childsizing,
            )

            # Find max x, y the turtle reached
            mmax_x = max(max_x, mmax_x)
            mmax_y = max(max_y, mmax_y)

        # Draw first part 1 side
        guy.color((r, g, b))

        # Draw number
        if root and writing:
            print_side_number(side, (r, g, b))

        guy.pensize(pensize)
        guy.forward(size - size0)
        guy.right(direction * 360 / 7)

        # Find max x, y the turtle reached
        x, y = guy.pos()
        mmax_x = max(int(x), mmax_x)
        mmax_y = max(int(y), mmax_y)

    if root:
        # Show turtle on top right corner of drawing
        guy.penup()
        guy.color("green")
        guy.setpos(mmax_x + 20, mmax_y + 20)
    return mmax_x, mmax_y


def main(args=None):
    """Parse command line args and draw art, then save as a vector graphics EPS file."""
    arg = parser.parse_args(args)
    arg_summary = f"{arg.levels}_{arg.size}_{arg.childsizing}"

    algo = CHILD_SIZING_ALGORITHMS[arg.childsizing]
    print(
        "arguments:",
        arg_summary,
        "size sequence:",
        arg.size,
        algo(arg.size),
        algo(algo(arg.size)),
    )

    # TODO: --start-color --end-color --theme (brewer, custom, reverse, etc)
    # TODO: more child sizing
    # TODO: Minkowski metric child sizing for a seamless tiling (HOW????????????????????????????????????????)
    turtle.colormode(255)
    if arg.light_mode:
        turtle.bgcolor((235, 235, 255))
    else:
        turtle.bgcolor((0, 0, 0))

    filename = arg.filename
    filename = filename.replace("TIME", str(int(time.time())))
    filename = filename.replace("ARGS", arg_summary)

    start_time = time.time()
    ok = False
    try:
        heptagons(arg.size, levels=arg.levels, writing=arg.write, childsizing=algo)
        ok = True
    except (KeyboardInterrupt, EOFError):
        print("bye")
    finally:
        print("saving output to vector graphics file:", filename)
        guy.getscreen().getcanvas().postscript(file=filename)
        print("seconds elapsed:", time.time() - start_time)
        pprint.pprint(STATS)
    if ok:
        print("shutting down soon")
        time.sleep(8)


if __name__ == "__main__":
    main()
