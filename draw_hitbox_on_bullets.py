from PIL import Image, ImageDraw
import numpy as np
import tyro
from dataclasses import dataclass
import re
from pprint import pprint


@dataclass
class Args:
    input: str
    output: str
    shotdata: str


def parse_shotdata(text: str):
    re_flag = re.DOTALL | re.IGNORECASE | re.X

    re_ShotData = re.compile(
        r"""
        \s ShotData 
        \s* \{ ( 
        [^\{\}]+
        | [^\{\}]+ \{ [^\{\}]+ \} [^\{\}]+
        ) \}
        """,
        re_flag,
    )
    re_rect = re.compile(r"\s rect \s* = \s* \( (.+?) \)", re_flag)
    re_collision = re.compile(r"\s collision \s* = \s* ( \(.+?\) | \d+ )", re_flag)
    re_AnimationData = re.compile(r"\s AnimationData \s* \{ (.+?) \}", re_flag)
    re_animation_data = re.compile(r"\s animation_data \s* = \s* \( (.+?) \)", re_flag)

    results = []

    for ShotData in re_ShotData.finditer(text):
        ShotData = ShotData.group(1)
        item = {}

        if rect := re_rect.search(ShotData):
            item["rect"] = tuple(int(_.strip()) for _ in rect.group(1).split(","))

        if collision := re_collision.search(ShotData):
            collision = re.sub("[()]", "", collision.group(1)).split(",")
            item["collision"] = tuple(int(_.strip()) for _ in collision)

        if AnimationData := re_AnimationData.search(ShotData):
            animation_datas = []
            AnimationData = AnimationData.group(1)
            for animation_data in re_animation_data.finditer(AnimationData):
                animation_data = animation_data.group(1).split(",")
                animation_datas.append(tuple(int(_.strip()) for _ in animation_data))
            item["animation_data"] = animation_datas

        assert "rect" in item or "animation_data" in item

        results.append(item)

    return results


def get_circle_from_shotdata(data: dict):
    radius: int = 0
    x_offset: int = 0
    y_offset: int = 0
    centers = []

    if "animation_data" in data:
        rect = [_[1:] for _ in data["animation_data"]]
    else:
        rect = [data["rect"]]
    if "collision" in data:
        collision = data["collision"]
        radius = collision[0]
        if len(collision) == 3:
            x_offset, y_offset = collision[1:]
    else:
        w, h = rect[0][2] - rect[0][0], rect[0][3] - rect[0][1]
        if min(w, h) / 3 - 3 > 3:
            print("Radius compute risk")
        radius = max(min(w, h) // 3 - 3, 3)
    for rect in rect:
        c_x, c_y = (rect[0] + rect[2]) // 2, (rect[1] + rect[3]) // 2
        centers.append((c_x - x_offset, c_y - y_offset))

    return centers, radius


def main():
    args = tyro.cli(Args)

    img = Image.open(args.input)
    draw = ImageDraw.Draw(img)
    color = (255, 0, 0, 0)
    width = 1

    with open(args.shotdata, encoding="shift_jis") as f:
        shotdata = parse_shotdata(f.read())
        for data in shotdata:
            centers, radius = get_circle_from_shotdata(data)
            for center in centers:
                draw.circle(center, radius, outline=color, width=width)

    img.save(args.output)


if __name__ == "__main__":
    main()
