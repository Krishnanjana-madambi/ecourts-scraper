import json
import os

# Data to store in JSON
manifest_data = {
    "date": "2025-10-15",
    "state": "Delhi",
    "district": "New Delhi",
    "court_complex": "District Court Complex",
    "downloads": [
        {
            "court": "Court No.1",
            "judge": "A B",
            "file": "output/Delhi/New Delhi/District Court Complex/2025-10-15/Court No.1.pdf"
        }
    ]
}

# Make sure output folder exists
os.makedirs("output", exist_ok=True)

# Path to save JSON file
manifest_path = os.path.join("output", "2025-10-15_manifest.json")

# Save as JSON file
with open(manifest_path, "w") as f:
    json.dump(manifest_data, f, indent=2)

print(f"✅ Manifest file created at: {manifest_path}")
