import os
import filecmp

dir1 = r"F:\Ming_python\ansys-unified-mcp\skills\ansys-geometry-modeling"
dir2 = r"F:\Ming_python\ansys-unified-mcp\skills\ansys-spaceclaim-modeling"

print("Comparing ansys-geometry-modeling and ansys-spaceclaim-modeling:")
for root, dirs, files in os.walk(dir1):
    rel = os.path.relpath(root, dir1)
    other_root = os.path.join(dir2, rel)
    for f in files:
        f1 = os.path.join(root, f)
        f2 = os.path.join(other_root, f)
        if os.path.exists(f2):
            identical = filecmp.cmp(f1, f2, shallow=False)
            print(f"  {rel}/{f} identical? {identical}")
        else:
            print(f"  {rel}/{f} only in dir1")
