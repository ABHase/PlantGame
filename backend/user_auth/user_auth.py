import uuid
from ..app import db
from ..upgrades.upgrades_config import UPGRADES
from ..biomes.biomes_config import BIOMES
from ..game_state.plants_config import INITIAL_PLANT_CONFIG  
from .models import User, UpgradeModel, GlobalState, PlantTimeModel  
from flask import json
from datetime import datetime
from ..models.biome_model import BiomeModel
from ..models.plant_model import PlantModel

def log_with_timestamp(message):
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}")


def fetch_game_state_from_db(user_id):
    user = User.query.get(user_id)
    if user and user.game_state:
        #log_with_timestamp(f"Fetching game state for user_id: {user_id}")
        #log_with_timestamp("Game state loaded from database {}.".format(user.game_state))
        return json.loads(user.game_state)
    #log_with_timestamp(f"No game state found for user_id: {user_id}")
    return None

def save_game_state_to_db(user_id, game_state):
    user = User.query.get(user_id)
    if user:
        #log_with_timestamp(f"Saving game state for user_id: {user_id}")
        #log_with_timestamp("Game state before saving: {}".format(game_state))
        user.game_state = json.dumps(game_state)
        db.session.commit()
        #log_with_timestamp("Game state after saving: {}".format(game_state))

def fetch_upgrades_from_db(user_id):
    return UpgradeModel.query.filter_by(user_id=user_id).all()

def save_upgrades_to_db(user_id, upgrades_list):
    for upgrade in upgrades_list:
        db.session.merge(upgrade)
    db.session.commit()

def fetch_upgrade_by_effect_and_user(effect, user_id):
    return UpgradeModel.query.filter_by(effect=effect, user_id=user_id).first()

def fetch_upgrade_by_index(user_id, index):
    upgrades = UpgradeModel.query.filter_by(user_id=user_id).all()
    if index < len(upgrades):
        return upgrades[index]
    return None

def fetch_biomes_from_db(user_id):
    return BiomeModel.query.filter_by(user_id=user_id).all()

def save_biomes_to_db(user_id, biomes_list):
    for biome in biomes_list:
        existing_biome = BiomeModel.query.filter_by(user_id=user_id, name=biome.name).first()
        if existing_biome:
            existing_biome.ground_water_level = biome.ground_water_level
            existing_biome.current_weather = biome.current_weather
            existing_biome.current_pest = biome.current_pest
            existing_biome.snowpack = biome.snowpack
            existing_biome.resource_modifiers = biome.resource_modifiers
            existing_biome.capacity = biome.capacity
        else:
            db.session.add(biome)
        db.session.commit()

def save_single_biome_to_db(biome):
    existing_biome = BiomeModel.query.filter_by(id=biome.id).first()
    if existing_biome:
        existing_biome.ground_water_level = biome.ground_water_level
        existing_biome.current_weather = biome.current_weather
        existing_biome.current_pest = biome.current_pest
        existing_biome.snowpack = biome.snowpack
        existing_biome.resource_modifiers = biome.resource_modifiers
        existing_biome.capacity = biome.capacity
        db.session.commit()
    else:
        print(f"No biome found with id {biome.id}")

def initialize_new_biome(user_id, biome_name):
    biome_data = BIOMES.get(biome_name)
    if biome_data:
        new_biome = BiomeModel(
        user_id=user_id,
        name=biome_name,
        capacity=biome_data['capacity'],
        ground_water_level=biome_data['ground_water_level'],
        current_weather=biome_data['current_weather'],
        current_pest=None,  # Initialize with no pests
        snowpack=biome_data['snowpack'],
        resource_modifiers=biome_data['resource_modifiers'],
        rain_intensity=biome_data['rain_intensity'],
        snow_intensity=biome_data['snow_intensity']
    )
        db.session.add(new_biome)
        db.session.commit()
        print(f"New biome {biome_name} initialized.")
    else:
        print(f"Biome {biome_name} not found in config.")

def fetch_plants_from_db(user_id):
    return PlantModel.query.filter_by(user_id=user_id).all()

def fetch_plants_from_db_by_biome_id_and_user(biome_id, user_id):
    return PlantModel.query.filter_by(biome_id=biome_id, user_id=user_id).all()

def save_plants_to_db(user_id, plants_list):
    for plant in plants_list:
        existing_plant = PlantModel.query.filter_by(user_id=user_id, id=plant.id).first()
        if existing_plant:
            existing_plant.maturity_level = plant.maturity_level
            existing_plant.sugar_production_rate = plant.sugar_production_rate
            existing_plant.genetic_marker_production_rate = plant.genetic_marker_production_rate
            existing_plant.is_sugar_production_on = plant.is_sugar_production_on
            existing_plant.is_genetic_marker_production_on = plant.is_genetic_marker_production_on
            
            # Update individual resource and plant part columns
            existing_plant.sunlight = plant.sunlight
            existing_plant.water = plant.water
            existing_plant.sugar = plant.sugar
            existing_plant.ladybugs = plant.ladybugs
            existing_plant.roots = plant.roots
            existing_plant.leaves = plant.leaves
            existing_plant.vacuoles = plant.vacuoles
            existing_plant.resin = plant.resin
            existing_plant.taproot = plant.taproot
            existing_plant.pheromones = plant.pheromones
            existing_plant.thorns = plant.thorns
        else:
            db.session.add(plant)

def save_single_plant_to_db(plant):
    existing_plant = PlantModel.query.filter_by(id=plant.id).first()
    if existing_plant:
        existing_plant.maturity_level = plant.maturity_level
        existing_plant.sugar_production_rate = plant.sugar_production_rate
        existing_plant.genetic_marker_production_rate = plant.genetic_marker_production_rate
        existing_plant.is_sugar_production_on = plant.is_sugar_production_on
        existing_plant.is_genetic_marker_production_on = plant.is_genetic_marker_production_on
        
        # Update individual resource and plant part columns
        existing_plant.sunlight = plant.sunlight
        existing_plant.water = plant.water
        existing_plant.sugar = plant.sugar
        existing_plant.ladybugs = plant.ladybugs
        existing_plant.roots = plant.roots
        existing_plant.leaves = plant.leaves
        existing_plant.vacuoles = plant.vacuoles
        existing_plant.resin = plant.resin
        existing_plant.taproot = plant.taproot
        existing_plant.pheromones = plant.pheromones
        existing_plant.thorns = plant.thorns
        db.session.commit()
    else:
        print(f"No plant found with id {plant.id}")

def save_new_plant_to_db(user_id, biome_id):
    new_plant = PlantModel(
        id=str(uuid.uuid4()),
        user_id=user_id,
        biome_id=biome_id,
        **INITIAL_PLANT_CONFIG
    )
    db.session.add(new_plant)
    db.session.commit()

def fetch_global_state_from_db(user_id):
    return GlobalState.query.filter_by(user_id=user_id).first()

def save_global_state_to_db(user_id, global_state):
    global_state.user_id = user_id  # Set the user_id
    db.session.merge(global_state)
    db.session.commit()

def fetch_plant_time_from_db(user_id):
    return PlantTimeModel.query.filter_by(user_id=user_id).first()

def save_plant_time_to_db(user_id, plant_time):
    plant_time.user_id = user_id  # Set the user_id
    db.session.merge(plant_time)
    db.session.commit()

def initialize_user_game(user_id):
    """Initialize game components for a user."""
    # Initialize global state
    global_state = initialize_new_global_state(user_id)
    save_global_state_to_db(user_id, global_state)
    
    # Initialize upgrades
    upgrades = initialize_new_upgrades(user_id)
    save_upgrades_to_db(user_id, upgrades)
    
    # Initialize biomes
    biomes = initialize_new_biomes(user_id)
    save_biomes_to_db(user_id, biomes)
    
    # Get the biome_id for "Beginner's Garden" from biomes_list
    beginner_garden_biome = next((biome for biome in biomes if biome.name == "Beginner's Garden"), None)
    if beginner_garden_biome:
        plants = initialize_new_plants(user_id, beginner_garden_biome.id)
        save_plants_to_db(user_id, plants)
    
    # Initialize plant time
    plant_time = initialize_new_plant_time(user_id)
    save_plant_time_to_db(user_id, plant_time)
    
    # Mark the user as initialized
    user = User.query.get(user_id)
    user.is_initialized = True
    db.session.commit()

def initialize_new_upgrades(user_id):
    new_upgrades = []
    for upgrade in UPGRADES:
        new_upgrade = UpgradeModel(
            user_id=user_id,
            name=upgrade['name'],
            cost=upgrade['cost'],
            type=upgrade['type'],
            unlocked=upgrade['unlocked'],
            effect=upgrade['effect'],
            secondary_cost=upgrade.get('secondary_cost', 0),  # Using .get() with default in case it's not present in some upgrades
            secondary_resource=upgrade.get('secondary_resource'),  # Using .get() with default None
            cost_modifier=upgrade.get('cost_modifier', 0.0)  # Using .get() with default 0.0
        )
        print(f"New upgrade: {new_upgrade}")
        new_upgrades.append(new_upgrade)
    return new_upgrades

def initialize_new_biomes(user_id):
    new_biomes = []

    # Only initialize the "Beginner's Garden" biome
    biome_data = BIOMES["Beginner's Garden"]
    new_biome = BiomeModel(
        user_id=user_id,
        name="Beginner's Garden",
        capacity=biome_data['capacity'],
        ground_water_level=biome_data['ground_water_level'],
        current_weather=biome_data['current_weather'],
        current_pest=None,  # Initialize with no pests
        snowpack=biome_data['snowpack'],
        resource_modifiers=biome_data['resource_modifiers'],
        rain_intensity=biome_data['rain_intensity'],
        snow_intensity=biome_data['snow_intensity']
    )
    print(f"New biome: {new_biome}")
    new_biomes.append(new_biome)

    return new_biomes

def initialize_new_plants(user_id, biome_id):
    new_plants = []

    # Initialize a standard plant for "Beginner's Garden"
    new_plant = PlantModel(
         id=str(uuid.uuid4()),
        user_id=user_id,
        biome_id=biome_id,
        **INITIAL_PLANT_CONFIG
    )
    print(f"New plant: {new_plant}")
    new_plants.append(new_plant)

    return new_plants

def initialize_new_plant_time(user_id):
    new_plant_time = PlantTimeModel(
        user_id=user_id,
        day=1,
        hour=6,
        is_day=True,
        season="Spring",
        update_counter=6,
        year=1
    )
    print(f"New PlantTime: {new_plant_time}")
    return new_plant_time

def initialize_new_global_state(user_id):
    new_global_state = GlobalState(
        user_id=user_id,
        genetic_marker_progress=0,
        genetic_marker_threshold=10,
        genetic_markers=50,
        seeds=5,
        silica=0,
        tannins=0,
        calcium=0,
        fulvic=0,
        cost_modifier=0.0
    )
    print(f"New GlobalState: {new_global_state}")
    return new_global_state

