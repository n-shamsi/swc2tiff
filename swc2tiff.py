import sys

import numpy as np
import tifffile


class Point:
    def __init__(self, x=0, y=0, z=0, r=0):
        self.x = int(x)
        self.y = int(y)
        self.z = int(z)
        self.r = int(r)


def read_swcs(filename):
    try:
        points = []
        with open(filename, 'r') as file:
            for line in file:
                if line[0] == '#':  # skip comments
                    continue

                values = line.split()
                x = float(values[2])
                y = float(values[3])
                z = float(values[4])
                r = float(values[5])

                point = Point(x, y, z, r)
                points.append(point)

        return points

    except FileNotFoundError:
        print(f"Unable to open SWC file: {filename}")
        exit(1)


def brush3D(image, x, y, z, radius):
    radius_sqr = 0.25*(radius ** 2)

    for i in range(x-int(radius), x+int(radius)):
        for j in range(y-int(radius), y+int(radius)):
            for k in range(z-int(radius), z+int(radius)):
                dist_sqr = (i-x) ** 2+(j-y) ** 2+(k-z) ** 2
                if dist_sqr <= radius_sqr:
                    try:
                        image[:, k, j, i] = 255
                    except IndexError:
                        continue

    return image


def swc2tif(args):
    if len(args) == 3:
        image_path, swc_file, output_tiff = args
    else:
        image_path = sys.argv[1]
        swc_file = sys.argv[2]
        output_tiff = sys.argv[3]

    image = tifffile.imread(image_path)
    points = read_swcs(swc_file)

    # Create a 3D image with the same dimensions as the input image
    mask = np.zeros_like(image, dtype=np.uint8)

    for point in points:
        x = point.x
        y = point.y
        z = point.z
        r = point.r

        # Draw a sphere at the specified coordinates with the specified radius
        mask = brush3D(mask, x, y, z, r)

    tifffile.imwrite(output_tiff, mask)

    return 0
