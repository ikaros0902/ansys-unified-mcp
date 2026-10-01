import os

local_skills = r"F:\Ming_python\ansys-unified-mcp\skills"
global_skills = r"C:\Users\Ming\.gemini\config\skills"

local_items = set([d for d in os.listdir(local_skills) if os.path.isdir(os.path.join(local_skills, d)) and not d.startswith('.')])
global_items = set([d for d in os.listdir(global_skills) if os.path.isdir(os.path.join(global_skills, d)) and not d.startswith('.')])

print("Local skills count:", len(local_items))
print("Global skills count:", len(global_items))
print("In both:", sorted(list(local_items.intersection(global_items))))
print("Only in local:", sorted(list(local_items - global_items)))
print("Only in global:", sorted(list(global_items - local_items)))
