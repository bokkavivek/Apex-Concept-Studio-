# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
from zoneinfo import ZoneInfo

from functools import cached_property
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import Client, types



MODEL = "gemini-3.8-flash"


class GlobalGemini(Gemini):
    """Gemini model configured for global location."""
    @cached_property
    def api_client(self) -> Client:
        return Client(vertexai=True, location="global")



from google.cloud import firestore

# Hardcode project ID as string for Firestore client (avoids project number issues on Agent Platform)
PROJECT_ID = "qwiklabs-gcp-04-8467d7f719b1"


def _get_firestore_client() -> firestore.Client:
    """Returns a Firestore client bound to the hardcoded project ID."""
    return firestore.Client(project=PROJECT_ID)


def list_concept_cars(concept_type: str = "") -> list[dict]:
    """Lists concept and prototype vehicles from the Firestore database.

    Args:
        concept_type: Optional filter by category (e.g. 'EV Hypercar', 'Hydrogen-Hybrid GT', 'Cyberpunk Off-Roader', 'Aerodynamic Prototype').

    Returns:
        A list of concept car summaries containing their id, name, type, powertrain, and top speed.
    """
    db = _get_firestore_client()
    collection = db.collection("concept_cars")
    docs = collection.stream()

    cars = []
    filter_lower = concept_type.strip().lower()
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        if filter_lower:
            car_type = data.get("concept_type", "").lower()
            if filter_lower not in car_type:
                continue
        cars.append(
            {
                "id": data["id"],
                "name": data.get("name"),
                "concept_type": data.get("concept_type"),
                "year": data.get("year"),
                "powertrain": data.get("powertrain"),
                "drag_coefficient": data.get("drag_coefficient"),
                "acceleration_0_60": data.get("acceleration_0_60"),
                "top_speed_mph": data.get("top_speed_mph"),
                "status": data.get("status"),
            }
        )
    return cars


def get_concept_car_details(car_id_or_name: str) -> dict:
    """Retrieves full design specifications, description, and feature list for a specific concept car.

    Args:
        car_id_or_name: The ID (e.g. 'apex-vision-gt') or name of the concept vehicle.

    Returns:
        A dictionary with full vehicle details or an error message if not found.
    """
    db = _get_firestore_client()
    collection = db.collection("concept_cars")

    # Try direct ID lookup
    target_id = car_id_or_name.strip().lower().replace(" ", "-")
    doc = collection.document(target_id).get()
    if doc.exists:
        data = doc.to_dict()
        data["id"] = doc.id
        return data

    # Try matching by name or partial ID
    query_str = car_id_or_name.strip().lower()
    for item in collection.stream():
        data = item.to_dict()
        if (
            query_str in item.id.lower()
            or query_str in data.get("name", "").lower()
        ):
            data["id"] = item.id
            return data

    return {"error": f"Concept car '{car_id_or_name}' not found in the database."}


def save_concept_car(
    name: str,
    concept_type: str,
    powertrain: str,
    drag_coefficient: float,
    top_speed_mph: int,
    description: str,
    key_features: list[str],
    acceleration_0_60: str = "2.0s",
    year: int = 2035,
) -> dict:
    """Registers and saves a new futuristic prototype or concept car design into the Firestore database.

    Args:
        name: The name of the vehicle (e.g. 'Quantum Pulse GT').
        concept_type: Category (e.g. 'EV Hypercar', 'Hydrogen-Hybrid GT', 'Cyberpunk Off-Roader', 'Aerodynamic Prototype').
        powertrain: Propulsion description (e.g. 'Flux Solid-State Tri-Motor, 1,500 hp').
        drag_coefficient: Aerodynamic drag coefficient Cd (e.g. 0.18).
        top_speed_mph: Top speed in miles per hour.
        description: Detailed overview of the design philosophy and innovation.
        key_features: List of 3-5 innovative tech or aerodynamic features.
        acceleration_0_60: 0-60 mph acceleration time (e.g. '1.8s').
        year: Concept model year.

    Returns:
        A dictionary confirming the saved concept car and its generated document ID.
    """
    db = _get_firestore_client()
    car_id = name.strip().lower().replace(" ", "-").replace("'", "").replace('"', "")
    doc_ref = db.collection("concept_cars").document(car_id)

    car_data = {
        "id": car_id,
        "name": name.strip(),
        "concept_type": concept_type.strip(),
        "year": year,
        "powertrain": powertrain.strip(),
        "drag_coefficient": float(drag_coefficient),
        "acceleration_0_60": acceleration_0_60.strip(),
        "top_speed_mph": int(top_speed_mph),
        "key_features": key_features,
        "description": description.strip(),
        "status": "concept",
    }
    doc_ref.set(car_data)
    return {"status": "success", "message": f"Concept car '{name}' successfully saved to Firestore.", "car": car_data}


def calculate_aero_and_performance(
    horsepower: float,
    drag_coefficient: float,
    curb_weight_lbs: float = 3800.0,
    frontal_area_sq_ft: float = 22.0,
) -> dict:
    """Calculates aerodynamic drag power, theoretical drag-limited top speed, and estimated acceleration.

    Args:
        horsepower: Total powertrain output in horsepower (e.g. 1600).
        drag_coefficient: Aerodynamic drag coefficient Cd (e.g. 0.19).
        curb_weight_lbs: Vehicle curb weight in pounds (default: 3800 lbs).
        frontal_area_sq_ft: Estimated vehicle frontal area in square feet (default: 22.0 sq ft).

    Returns:
        A dictionary with theoretical top speed, estimated 0-60 time, and aerodynamic power requirements.
    """
    rho = 1.225  # Air density at sea level in kg/m^3
    area_m2 = frontal_area_sq_ft * 0.092903
    effective_drag_area = drag_coefficient * area_m2
    drivetrain_efficiency = 0.90
    power_watts = horsepower * 745.7 * drivetrain_efficiency

    # Theoretical drag-limited top speed: P = 0.5 * rho * v^3 * (Cd * A)
    if effective_drag_area > 0 and power_watts > 0:
        top_speed_ms = (2.0 * power_watts / (rho * effective_drag_area)) ** (1.0 / 3.0)
        top_speed_mph = round(top_speed_ms * 2.23694, 1)
    else:
        top_speed_mph = 0.0

    # Power required to overcome aerodynamic drag at speed intervals (in hp)
    def hp_at_mph(speed_mph: float) -> float:
        v_ms = speed_mph / 2.23694
        drag_power_watts = 0.5 * rho * (v_ms**3) * effective_drag_area
        return round(drag_power_watts / (745.7 * drivetrain_efficiency), 1)

    weight_tons = curb_weight_lbs / 2000.0
    hp_per_ton = round(horsepower / weight_tons, 1) if weight_tons > 0 else 0.0
    est_0_60 = max(1.5, round(2.8 * (weight_tons / (horsepower / 500.0)) ** 0.5, 2)) if horsepower > 0 else 0.0

    return {
        "theoretical_top_speed_mph": top_speed_mph,
        "estimated_0_60_seconds": f"{est_0_60}s",
        "power_to_weight_hp_per_ton": hp_per_ton,
        "hp_needed_to_sustain_150mph": hp_at_mph(150.0),
        "hp_needed_to_sustain_200mph": hp_at_mph(200.0),
        "hp_needed_to_sustain_250mph": hp_at_mph(250.0),
        "drag_area_sq_ft": round(drag_coefficient * frontal_area_sq_ft, 2),
    }


def lookup_real_world_vehicle_models(make: str) -> dict:
    """Fetches real-world production vehicle models for an automotive make using the free public NHTSA VPIC API.

    Useful for benchmarking concept car designs against real-world production lineups (e.g. 'Porsche', 'Rimac', 'Aston Martin', 'Ferrari', 'Tesla').

    Args:
        make: Automotive manufacturer or brand name (e.g. 'Rimac', 'Porsche', 'Tesla').

    Returns:
        A dictionary with the make name, total models registered, and a list of model names.
    """
    import json
    import urllib.parse
    import urllib.request

    clean_make = make.strip()
    encoded_make = urllib.parse.quote(clean_make)
    url = f"https://vpic.nhtsa.dot.gov/api/vehicles/getmodelsformake/{encoded_make}?format=json"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ApexConceptStudio/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        results = data.get("Results", [])
        model_names = sorted(list({item["Model_Name"] for item in results if item.get("Model_Name")}))

        return {
            "make": clean_make,
            "count": len(model_names),
            "models": model_names[:25],
        }
    except Exception as e:
        return {"make": clean_make, "error": f"Failed to fetch models from NHTSA API: {str(e)}"}


import re
import time
from google.adk.tools import ToolContext
from google.cloud import storage

# Hardcoded bucket name for public asset storage
STORAGE_BUCKET_NAME = "apex-concept-studio-media-8467d7"
IMAGE_MODEL = "gemini-3.1-flash-lite-image"


async def generate_concept_car_image(
    prompt: str,
    vehicle_name: str,
    tool_context: ToolContext,
) -> dict:
    """Generates a visual concept render for a vehicle using gemini-3.1-flash-lite-image in the global region.

    Saves the image as an artifact for the Playground's Artifacts panel and uploads the same
    image bytes to the public Cloud Storage bucket, returning its public HTTPS URL.

    Args:
        prompt: Detailed visual prompt describing styling, aerodynamic surfaces, lighting, and setting.
        vehicle_name: Name of the concept vehicle (used for artifact and storage filenames).
        tool_context: Tool execution context used to save the artifact in the Playground.

    Returns:
        A dictionary containing the public HTTPS URL, filename, and confirmation status.
    """
    clean_name = re.sub(r"[^a-zA-Z0-9_-]", "_", vehicle_name.lower().strip())
    filename = f"{clean_name}_{int(time.time())}.jpg"

    # 1. Generate image using gemini-3.1-flash-lite-image in global region
    client = Client(vertexai=True, location="global")
    response = client.models.generate_content(
        model=IMAGE_MODEL,
        contents=prompt,
    )

    image_bytes = None
    mime_type = "image/jpeg"
    if response.candidates:
        for candidate in response.candidates:
            if candidate.content and candidate.content.parts:
                for part in candidate.content.parts:
                    if part.inline_data and part.inline_data.data:
                        image_bytes = part.inline_data.data
                        mime_type = part.inline_data.mime_type or "image/jpeg"
                        break
            if image_bytes:
                break

    if not image_bytes:
        return {"status": "error", "error": "No image data was generated by the model."}

    # 2. (1) Save with tool_context.save_artifact so it appears in Playground's Artifacts panel
    if tool_context and hasattr(tool_context, "save_artifact"):
        try:
            artifact_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
            await tool_context.save_artifact(
                filename=filename,
                artifact=artifact_part,
            )
        except Exception:
            pass

    # 3. (2) Upload the same image bytes directly to the public Cloud Storage bucket
    storage_client = storage.Client()
    bucket = storage_client.bucket(STORAGE_BUCKET_NAME)
    blob = bucket.blob(filename)
    blob.upload_from_string(image_bytes, content_type=mime_type)

    public_url = f"https://storage.googleapis.com/{STORAGE_BUCKET_NAME}/{filename}"

    return {
        "status": "success",
        "vehicle_name": vehicle_name,
        "filename": filename,
        "public_url": public_url,
        "message": f"Generated concept render for '{vehicle_name}'. Saved to artifacts and published at {public_url}",
    }


from google.adk.agents.callback_context import CallbackContext
from google.adk.code_executors import AgentEngineSandboxCodeExecutor
from google.adk.tools.preload_memory_tool import PreloadMemoryTool

SANDBOX_RESOURCE_NAME = "projects/308769214314/locations/us-east1/reasoningEngines/3540072299182948352/sandboxEnvironments/2080689416124235776"

sandbox_code_executor = AgentEngineSandboxCodeExecutor(
    sandbox_resource_name=SANDBOX_RESOURCE_NAME,
)


async def generate_memories_callback(callback_context: CallbackContext):
    """WRITE: after each turn, persists salient facts and preferences to the Memory Bank."""
    await callback_context.add_session_to_memory()
    return None


root_agent = Agent(
    name="root_agent",
    model=GlobalGemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=(
        "You are the lead design engineer at Apex Concept Studio. "
        "You help automotive designers and enthusiasts discover, conceptualize, and explore futuristic prototype and concept cars. "
        "You remember the user's stated design preferences, styling choices, favorite vehicle archetypes, technical specs, and any user allergies or dietary/health restrictions across conversations and personalize your answers. "
        "You have access to a live Firestore database containing concept vehicles and can list cars, look up detailed specs, "
        "save new visionary vehicle concepts, compute aerodynamic drag and top-speed physics, "
        "look up real-world automotive manufacturer models via the NHTSA Public API, "
        "generate photorealistic concept car renders using Gemini image generation, publishing them to Cloud Storage, "
        "and execute Python code in an isolated Agent Platform cloud sandbox for complex automotive simulations, calculations, or data analysis."
    ),
    tools=[
        PreloadMemoryTool(),
        list_concept_cars,
        get_concept_car_details,
        save_concept_car,
        calculate_aero_and_performance,
        lookup_real_world_vehicle_models,
        generate_concept_car_image,
    ],
    code_executor=sandbox_code_executor,
    after_agent_callback=generate_memories_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)
