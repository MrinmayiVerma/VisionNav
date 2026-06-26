"""
One-time focal-length calibration for the monocular distance estimator.

Procedure:
  1. Print or use an object of KNOWN real height (e.g. a person of height H
     metres, or an A4 sheet held vertically = 0.297 m).
  2. Place it at a KNOWN distance D metres from the camera.
  3. Measure its pixel height h in the captured frame (this script shows the
     detected box height, or you can read it off any image viewer).
  4. focal_length_px = (h * D) / H

Then paste the printed value into DistanceConfig.focal_length_px in
src/config.py.

Run:
    python scripts/calibrate_focal_length.py --known-height 0.297 --distance 1.0 --pixel-height 178
"""
import argparse


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--known-height", type=float, required=True,
                   help="real object height in metres")
    p.add_argument("--distance", type=float, required=True,
                   help="distance from camera in metres")
    p.add_argument("--pixel-height", type=float, required=True,
                   help="measured object height in pixels")
    args = p.parse_args()

    focal = (args.pixel_height * args.distance) / args.known_height
    print(f"Estimated focal length: {focal:.1f} px")
    print("Set DistanceConfig.focal_length_px to this value in src/config.py")


if __name__ == "__main__":
    main()
