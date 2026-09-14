import sys
from pathlib import Path
repo_src = str(Path(__file__).resolve().parents[2] / "src")
if repo_src not in sys.path:
    sys.path.insert(0, repo_src)
from ansys_unified_mcp.products.mechanical import MechanicalController

mc = MechanicalController()
mc.connect(port=10000)

script = """
model = ExtAPI.DataModel.Project.Model
print("=== DEEP DIVE: RM OVER-CONSTRAINING & FLYING BODY AUDIT ===")

all_bodies = model.Geometry.GetChildren(DataModelObjectCategory.Body, True)
body_to_rps = {}
empty_rps = []

for rp in model.RemotePoints.Children:
    if not rp.Location or rp.Location.Entities.Count == 0:
        empty_rps.append(rp.Name)
        continue
    
    for entity in rp.Location.Entities:
        try:
            for b in entity.Bodies:
                body_to_rps[b.Name] = body_to_rps.get(b.Name, 0) + 1
        except:
            pass

print("Total bodies in model: " + str(len(all_bodies)))
print("Bodies tied to Remote Points: " + str(len(body_to_rps)))
print("Bodies with ZERO Remote Points: " + str(len(all_bodies) - len(body_to_rps)))
print("Empty/Invalid Remote Points: " + str(len(empty_rps)))

heavily_constrained = {k: v for k, v in body_to_rps.items() if v >= 10}
print("Top Heavily Constrained Bodies (>=10 RPs on single body): " + str(len(heavily_constrained)))
sorted_heavy = sorted(heavily_constrained.items(), key=lambda x: x[1], reverse=True)
for b_name, count in sorted_heavy[:10]:
    print("   * Body: " + b_name + " -> tied to " + str(count) + " Rigid Remote Points!")

unconstrained_bodies = [b.Name for b in all_bodies if b.Name not in body_to_rps]
print("Unconstrained Bodies count (Zero RM): " + str(len(unconstrained_bodies)))
for b_name in unconstrained_bodies[:15]:
    print("   - No RM Body: " + b_name)
"""

out = mc.run_script(script)
print(out)
