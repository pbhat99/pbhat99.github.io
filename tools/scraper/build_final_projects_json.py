import json
import re

# Read extracted projects
with open('data/weebly_extracted_projects.json', 'r', encoding='utf-8') as f:
    raw_projects = json.load(f)

projects_final = []

# Curated details for notable projects
curated_details = {
    "directv-goatbusters": {
        "title": "DirecTV - GOATbusters",
        "client": "DirecTV",
        "role": "Lead Compositor",
        "year": "2023",
        "category": "commercials",
        "tools": ["Nuke", "Maya", "Python", "Flame"],
        "description": "Ghostbusters-themed commercial featuring hologram compositing, particle simulations, and intricate live plate cleanup.",
        "hasBeforeAfter": True,
        "beforeLabel": "Raw Plate / Rigs",
        "afterLabel": "Final Composite",
        "highlight": True
    },
    "hummer-ev": {
        "title": "GMC Hummer EV - Quiet Revolution",
        "client": "GMC",
        "role": "Senior Compositing Artist",
        "year": "2023",
        "category": "commercials",
        "tools": ["Nuke Studio", "V-Ray", "Houdini"],
        "description": "Photoreal CG truck integration, interactive lighting reflections on wet asphalt, and realistic tire dust spray passes.",
        "hasBeforeAfter": True,
        "beforeLabel": "Clay / Wireframe",
        "afterLabel": "Beauty Comp",
        "highlight": True
    },
    "buschlight-voice-of-the-mountains": {
        "title": "BuschLight - Voice of the Mountains",
        "client": "Busch Light",
        "role": "Compositor",
        "year": "2023",
        "category": "commercials",
        "tools": ["Nuke", "Photoshop", "SynthEyes"],
        "description": "Extensive matte painting set extension, icy atmospheric snow simulation, and character integration.",
        "hasBeforeAfter": True,
        "beforeLabel": "Greenscreen Plate",
        "afterLabel": "Final Composite",
        "highlight": True
    },
    "pepsi-the-call-super-bowl": {
        "title": "Pepsi - 'The Call' Super Bowl Halftime",
        "client": "Pepsi / NFL",
        "role": "Compositing Artist",
        "year": "2022",
        "category": "commercials",
        "tools": ["Nuke", "Maya", "Mocha Pro"],
        "description": "Halftime show teaser featuring stadium-scale CG crowd multiplication, holographic displays, and energetic lighting passes.",
        "hasBeforeAfter": False,
        "highlight": True
    },
    "xbox-forza-getaway-driver": {
        "title": "Xbox Forza - The Getaway Driver",
        "client": "Microsoft / Xbox",
        "role": "VFX Compositor",
        "year": "2021",
        "category": "commercials",
        "tools": ["Nuke", "Maya"],
        "description": "High-octane car chase sequences blending live-action stunt driving with CG sports cars and motion blur.",
        "hasBeforeAfter": False,
        "highlight": True
    },
    "three-5g": {
        "title": "Three 5G - Real 5G Has Arrived",
        "client": "Three UK",
        "role": "Compositor",
        "year": "2021",
        "category": "commercials",
        "tools": ["Nuke", "Flame"],
        "description": "Futuristic London city transformation, holographic AR interfaces, digital doubles, and seamless invisible VFX.",
        "hasBeforeAfter": False,
        "highlight": True
    },
    "the-disney-wish": {
        "title": "The Disney Wish - Cruise Line",
        "client": "Disney",
        "role": "Compositor",
        "year": "2022",
        "category": "commercials",
        "tools": ["Nuke", "Houdini"],
        "description": "Magical particle effects, fairy dust simulation compositing, water plate extension, and photoreal CG Disney ship.",
        "hasBeforeAfter": False,
        "highlight": True
    },
    "the-chemical-brothers-free-yourself": {
        "title": "The Chemical Brothers - Free Yourself",
        "client": "Virgin EMI",
        "role": "VFX Compositor",
        "year": "2018",
        "category": "music-videos",
        "tools": ["Nuke", "Maya"],
        "description": "Award-winning music video featuring dancing robots, photoreal chrome/metal shading comp, and mocap alignment.",
        "hasBeforeAfter": False,
        "highlight": True
    },
    "adidas-create-the-answer": {
        "title": "Adidas - Create The Answer",
        "client": "Adidas",
        "role": "Compositor",
        "year": "2018",
        "category": "commercials",
        "tools": ["Nuke", "After Effects"],
        "description": "Fast-paced World Cup campaign with dynamic camera transitions, rapid roto, holographic UI elements, and color grading.",
        "hasBeforeAfter": False,
        "highlight": True
    },
    "anjaniputra": {
        "title": "Anjaniputra",
        "client": "MNK Movies",
        "role": "Senior Compositor",
        "year": "2017",
        "category": "films",
        "tools": ["Nuke", "Silhouette", "Mocha"],
        "description": "Action feature film: wire removals, muzzle flash hits, matte backgrounds, and dynamic speed ramping.",
        "hasBeforeAfter": False,
        "highlight": True
    },
    "kataka": {
        "title": "Kataka",
        "client": "Feature Film",
        "role": "Visual Effects Lead",
        "year": "2017",
        "category": "films",
        "tools": ["Nuke", "Maya", "Photoshop"],
        "description": "Supernatural horror feature film with creature compositing, dark atmosphere layering, and set cleanups.",
        "hasBeforeAfter": False,
        "highlight": True
    }
}

seen_ids = set()

for p in raw_projects:
    pid = p['id']
    if pid in seen_ids:
        continue
    seen_ids.add(pid)

    # Check if curated
    matching_curated = None
    for k, c in curated_details.items():
        if k in pid or pid in k:
            matching_curated = c
            break

    if matching_curated:
        item = {
            "id": pid,
            "title": matching_curated["title"],
            "client": matching_curated["client"],
            "category": matching_curated["category"],
            "year": matching_curated["year"],
            "role": matching_curated["role"],
            "thumbnail": p["image"],
            "description": matching_curated["description"],
            "tools": matching_curated["tools"],
            "hasBeforeAfter": matching_curated.get("hasBeforeAfter", False),
            "highlight": matching_curated.get("highlight", False)
        }
        if item["hasBeforeAfter"]:
            item["beforeImage"] = p["image"]
            item["afterImage"] = "assets/images/portfolio/pepsi-the-call-super-bowl-56-mp4-snapshot-00-21-2023-12-14-13-14-22_orig.jpg"
            item["beforeLabel"] = matching_curated["beforeLabel"]
            item["afterLabel"] = matching_curated["afterLabel"]
    else:
        # Standard project
        item = {
            "id": pid,
            "title": p["title"],
            "client": "Production",
            "category": p["category"],
            "year": "2018 - 2023",
            "role": "Compositing Artist",
            "thumbnail": p["image"],
            "description": f"Visual effects compositing, clean plate reconstruction, and integration for {p['title']}.",
            "tools": ["Nuke", "Maya"] if p["category"] == "films" else ["Nuke", "Mocha"],
            "hasBeforeAfter": False,
            "highlight": False
        }
    
    projects_final.append(item)

print(f"Total structured projects: {len(projects_final)}")
with open('data/projects.json', 'w', encoding='utf-8') as f:
    json.dump(projects_final, f, indent=2)

print("data/projects.json updated successfully!")
