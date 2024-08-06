n0 = (290, 1550)
n3 = (355, 1440)
d_m = 80


def distance(p1, p2):
    return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5


print(f"Distanza pixel: {distance(n0, n3)}")
d_pixel = distance(n0, n3)

f = d_m / d_pixel

n0_m = (290 * f, 1550 * f)
n3_m = (355 * f, 1440 * f)

print(f"n0_m: {n0_m}")
print(f"n3_m: {n3_m}")

print(f"Distanza metri: {distance(n0_m, n3_m)}")
