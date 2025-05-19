import cv2
import numpy as np
import tyro
from dataclasses import dataclass

@dataclass
class Args:
    input: str
    output: str


def main():
    args = tyro.cli(Args)
    img = cv2.imread(args.input)
    if img is None:
        raise FileNotFoundError("Input image not found")
    center = (128, 129.5)
    radius = 10
    color = (255, 255, 255)
    thickness = 1

    cv2.circle(img, )

if __name__ == "__main__":
    main()