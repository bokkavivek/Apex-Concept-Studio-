"""Seed script for Apex Concept Studio Firestore database."""

from google.cloud import firestore

# Hardcoded project ID as string to avoid project number issues on Agent Platform
PROJECT_ID = "qwiklabs-gcp-04-8467d7f719b1"

SEED_CARS = [
    {
        "id": "apex-vision-gt",
        "name": "Apex Vision GT",
        "concept_type": "EV Hypercar",
        "year": 2030,
        "powertrain": "Quad-Motor Solid-State EV (1,850 hp)",
        "drag_coefficient": 0.19,
        "acceleration_0_60": "1.7s",
        "top_speed_mph": 275,
        "key_features": [
            "Morphing carbon fiber active aero",
            "Solid-state 120 kWh structural battery",
            "Augmented reality canopy cockpit",
            "In-wheel flux vectoring",
        ],
        "description": "Ultra-lightweight visionary hypercar designed for zero-emission top speed endurance and dynamic downforce regulation.",
        "status": "prototype",
    },
    {
        "id": "solaris-hyperion",
        "name": "Solaris Hyperion",
        "concept_type": "Hydrogen-Hybrid GT",
        "year": 2032,
        "powertrain": "Liquid Hydrogen Turbine + Dual Electric Motors (1,400 hp)",
        "drag_coefficient": 0.21,
        "acceleration_0_60": "2.1s",
        "top_speed_mph": 245,
        "key_features": [
            "Cryogenic liquid hydrogen tanks",
            "Photovoltaic solar skin bodywork",
            "Regenerative aero braking foils",
            "Bio-synthetic leather interior",
        ],
        "description": "Continental grand tourer prototype combining zero-emission hydrogen combustion with solar energy harvesting.",
        "status": "concept",
    },
    {
        "id": "vortex-cybercross",
        "name": "Vortex Cybercross",
        "concept_type": "Cyberpunk Off-Roader",
        "year": 2033,
        "powertrain": "All-Terrain Tri-Motor Electric (1,100 hp)",
        "drag_coefficient": 0.28,
        "acceleration_0_60": "2.8s",
        "top_speed_mph": 170,
        "key_features": [
            "Exoskeleton titanium-graphene alloy frame",
            "Independent active pneumatic suspension with 18-inch travel",
            "Integrated drone scout launcher",
            "Autonomous terrain mapping LiDAR",
        ],
        "description": "Extreme exploration concept built to traverse unpaved alien terrains and urban wilderness with adaptive chassis architecture.",
        "status": "prototype",
    },
    {
        "id": "aero-phantom-streamliner",
        "name": "Aero Phantom Streamliner",
        "concept_type": "Aerodynamic Prototype",
        "year": 2035,
        "powertrain": "Dual Axial-Flux Motors (950 hp)",
        "drag_coefficient": 0.15,
        "acceleration_0_60": "2.3s",
        "top_speed_mph": 260,
        "key_features": [
            "Tear-drop teardown teardown laminar airflow body",
            "Virtual side mirrors with neural eye tracking",
            "Active wake-cancellation diffuser",
            "Carbon nanotube monocoque",
        ],
        "description": "Pure aerodynamic pursuit vehicle setting the benchmark for the lowest recorded drag coefficient in road vehicle design.",
        "status": "in_design",
    },
]


def seed():
    print(f"Connecting to Firestore for project: {PROJECT_ID}...")
    db = firestore.Client(project=PROJECT_ID)
    collection = db.collection("concept_cars")

    print(f"Seeding {len(SEED_CARS)} concept cars...")
    for car in SEED_CARS:
        doc_ref = collection.document(car["id"])
        doc_ref.set(car)
        print(f"  ✓ Seeded: {car['name']} (ID: {car['id']})")

    print("\nFirestore seeding complete! Verifying count:")
    docs = list(collection.stream())
    print(f"Total documents in 'concept_cars': {len(docs)}")


if __name__ == "__main__":
    seed()
