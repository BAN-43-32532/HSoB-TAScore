from PIL import Image, ImageDraw
import numpy as np
import tyro
from dataclasses import dataclass
import re


@dataclass
class Args:
    input: str
    output: str

def parse_shotdata(text: str):
    pattern_shotdata = re.compile(r'ShotData\s*\{(.*?)\}', re.DOTALL | re.IGNORECASE)
    pattern_rect = re.compile(r'rect\s*=\s*\(([^)]+)\)', re.IGNORECASE)
    pattern_collision = re.compile(r'collision\s*=\s*(\d+)', re.IGNORECASE)
    pattern_animation_block = re.compile(r'AnimationData\s*\{(.*?)\}', re.DOTALL | re.IGNORECASE)
    pattern_animation_data = re.compile(r'animation_data\s*=\s*\(([^)]+)\)', re.IGNORECASE)

    results = []

    for block_match in pattern_shotdata.finditer(text):
        block = block_match.group(1)
        item = {}

        # rect
        rect_match = pattern_rect.search(block)
        if rect_match:
            rect_str = rect_match.group(1)
            # 转成int tuple
            item['rect'] = tuple(map(int, map(str.strip, rect_str.split(','))))
        else:
            item['rect'] = None

        # collision
        collision_match = pattern_collision.search(block)
        if collision_match:
            item['collision'] = int(collision_match.group(1))
        else:
            item['collision'] = None

        # animation_data列表
        animation_datas = []
        animation_block_match = pattern_animation_block.search(block)
        if animation_block_match:
            anim_block = animation_block_match.group(1)
            for anim_match in pattern_animation_data.finditer(anim_block):
                anim_str = anim_match.group(1)
                anim_tuple = tuple(map(int, map(str.strip, anim_str.split(','))))
                animation_datas.append(anim_tuple)
        item['animation_data'] = animation_datas

        results.append(item)

    return results

def main():
    args = tyro.cli(Args)
    img = Image.open(args.input)
    draw = ImageDraw.Draw(img)

    center = (140, 129)
    radius = 10
    color = (255, 255, 255, 255)
    width = 1

    draw.circle(center, radius, width=width)

    img.save(args.output)


if __name__ == "__main__":
    main()
