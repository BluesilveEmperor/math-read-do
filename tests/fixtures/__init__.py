# Test fixtures for QEM tool

"""
Cube.obj — 8 vertices, 12 triangles (6 faces × 2 triangles each)
Centered at origin, size 2×2×2
"""
CUBE_OBJ = """# Cube test fixture
o Cube

v -1.0 -1.0 -1.0
v -1.0 -1.0  1.0
v -1.0  1.0 -1.0
v -1.0  1.0  1.0
v  1.0 -1.0 -1.0
v  1.0 -1.0  1.0
v  1.0  1.0 -1.0
v  1.0  1.0  1.0

vn -1 0 0
vn 1 0 0
vn 0 -1 0
vn 0 1 0
vn 0 0 -1
vn 0 0 1

f 1//1 3//1 4//1
f 1//1 4//1 2//1
f 5//2 7//2 8//2
f 5//2 8//2 6//2
f 1//3 2//3 6//3
f 1//3 6//3 5//3
f 3//4 7//4 8//4
f 3//4 8//4 4//4
f 1//5 5//5 7//5
f 1//5 7//5 3//5
f 2//6 6//6 8//6
f 2//6 8//6 4//6
"""

"""
Plane.obj — 4 vertices, 2 triangles (a flat quad)
A simple 2×2 plane on the XZ plane
"""
PLANE_OBJ = """# Plane test fixture
o Plane

v -1.0 0.0 -1.0
v -1.0 0.0  1.0
v  1.0 0.0 -1.0
v  1.0 0.0  1.0

vt 0.0 0.0
vt 0.0 1.0
vt 1.0 0.0
vt 1.0 1.0

f 1/1 2/2 3/3
f 3/3 2/2 4/4
"""

"""
Tetrahedron.obj — 4 vertices, 4 triangles
"""
TETRA_OBJ = """# Tetrahedron test fixture
o Tetrahedron

v  0.0  0.0  1.0
v  0.0  1.0 -0.5
v -0.866 -0.5 -0.5
v  0.866 -0.5 -0.5

f 1 2 3
f 1 3 4
f 1 4 2
f 2 4 3
"""

"""
Sphere.obj (low poly UV sphere) — simplified for testing
"""
SPHERE_OBJ = """# Low-poly UV sphere test fixture (3 segments × 3 stacks)
o Sphere

v 0.000000 1.000000 0.000000
v 0.000000 0.500000 0.866025
v 0.750000 0.500000 0.433013
v 0.750000 0.500000 -0.433013
v 0.000000 0.500000 -0.866025
v -0.750000 0.500000 -0.433013
v -0.750000 0.500000 0.433013
v 0.000000 -0.500000 0.866025
v 0.750000 -0.500000 0.433013
v 0.750000 -0.500000 -0.433013
v 0.000000 -0.500000 -0.866025
v -0.750000 -0.500000 -0.433013
v -0.750000 -0.500000 0.433013
v 0.000000 -1.000000 0.000000

f 1 2 3
f 1 3 4
f 1 4 5
f 1 5 6
f 1 6 7
f 1 7 2
f 2 8 9
f 2 9 3
f 3 9 10
f 3 10 4
f 4 10 11
f 4 11 5
f 5 11 12
f 5 12 6
f 6 12 13
f 6 13 7
f 7 13 8
f 7 8 2
f 8 14 9
f 9 14 10
f 10 14 11
f 11 14 12
f 12 14 13
f 13 14 8
"""
