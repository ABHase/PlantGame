import uuid
from flask import Blueprint, jsonify, session, request, current_app
from time import sleep
from app import socketio
from plants.part_cost_config import PARTS_COST_CONFIG
from biomes.biomes_config import BIOMES
from plants.plant_parts_config import PLANT_PARTS_CONFIG  # Replace 'your_app_name' with the name of the package where app.py resides
from biomes.biome import Biome
from plants.plant import Plant
from upgrades.upgrades_config import UPGRADES
from game_state import GameState  # Import GameState
from socket_config import socketio
from flask_login import current_user, login_required
from user_auth.user_auth import (
    fetch_game_state_from_db, save_game_state_to_db,
    fetch_upgrades_from_db, save_upgrades_to_db,
    fetch_upgrade_by_index,
    fetch_biomes_from_db, save_biomes_to_db,
    fetch_plants_from_db, save_plants_to_db,
    fetch_global_state_from_db, save_global_state_to_db,
    fetch_plant_time_from_db, save_plant_time_to_db
)
from user_auth.models import UpgradeModel, PlantTimeModel, GlobalState
from action_dispatcher import dispatch_action
#import log with timestamp function
from plant_time.plant_time import PlantTime
import logging
from .initial_resources_config import INITIAL_RESOURCES
from models.biome_model import BiomeModel
from models.plant_model import PlantModel
from .plants_config import INITIAL_PLANT_CONFIG

logging.basicConfig(filename='app.log',level=logging.INFO)


game_state_bp = Blueprint('game_state', __name__)
running_tasks = {}
user_actions_queue = []


def background_task(app, user_id):
    with app.app_context():
        biomes_initialized = False  # Flag to check if biomes have been initialized and saved
        while True:
            upgrades_list = fetch_upgrades_from_db(user_id)
            biomes_list = fetch_biomes_from_db(user_id)  # Assuming you have a similar function for biomes
            plants_list = fetch_plants_from_db(user_id)  # Assuming you have a similar function for plants
            plant_time = fetch_plant_time_from_db(user_id)
            global_state = fetch_global_state_from_db(user_id)

            # Initialize game_state from global_state
            if global_state is not None:
                game_state = GameState.from_dict(global_state.to_dict())
            else:
                print("GlobalState is empty. Cannot initialize GameState.")
                continue  # Skip the rest of the loop iteration

            # Initialize PlantTime if needed
            if plant_time is None:
                print(f"PlantTime is empty for user {user_id}. Initializing new PlantTime.")
                plant_time = initialize_new_plant_time(user_id)
                save_plant_time_to_db(user_id, plant_time)

            # Initialize GlobalState if needed
            if global_state is None:
                print(f"GlobalState is empty for user {user_id}. Initializing new GlobalState.")
                global_state = initialize_new_global_state(user_id)
                save_global_state_to_db(user_id, global_state)

            # Check if upgrades_list is empty or None, and initialize if needed
            if upgrades_list is None or len(upgrades_list) == 0:
                print(f"Upgrades list is empty for user {user_id}. Initializing new upgrades list.")
                upgrades_list = initialize_new_upgrades(user_id)

            # Initialize biomes if needed
            if not biomes_initialized and (biomes_list is None or len(biomes_list) == 0):
                print(f"Biomes list is empty for user {user_id}. Initializing new biomes list.")
                biomes_list = initialize_new_biomes(user_id)  # Assuming you have a similar function for biomes
                save_biomes_to_db(user_id, biomes_list)  # Assuming you have a similar function for biomes
                biomes_initialized = True  # Set the flag to True

                # Refresh biomes_list after saving to DB
                biomes_list = fetch_biomes_from_db(user_id)

                # Initialize plants if needed
                if plants_list is None or len(plants_list) == 0:
                    print(f"Plants list is empty for user {user_id}. Initializing new plants list.")
                    # Get the biome_id for "Beginner's Garden" from biomes_list
                    beginner_garden_biome = next((biome for biome in biomes_list if biome.name == "Beginner's Garden"), None)
                    if beginner_garden_biome:
                        plants_list = initialize_new_plants(user_id, beginner_garden_biome.id)

            # Process all queued actions in a single tick
            while user_actions_queue:
                for action in list(user_actions_queue):  # Create a copy of the queue to iterate over
                    dispatch_action(action)
                    user_actions_queue.remove(action)  # Remove the processed action
                save_upgrades_to_db(user_id, upgrades_list)
                save_biomes_to_db(user_id, biomes_list)  # Assuming you have a similar function for biomes
                save_plants_to_db(user_id, plants_list)  # Assuming you have a similar function for plants


            game_state.update(user_id)
            save_upgrades_to_db(user_id, upgrades_list)
            save_biomes_to_db(user_id, biomes_list)  # Assuming you have a similar function for biomes
            save_plants_to_db(user_id, plants_list)  # Assuming you have a similar function for plants

            # Emit updated game state to client
            socketio.emit('game_state', game_state.to_dict())
            socketio.emit('global_state', global_state.to_dict())
            socketio.emit('plant_time', plant_time.to_dict())
            socketio.emit('upgrades_list', [upgrade.to_dict() for upgrade in upgrades_list])
            socketio.emit('biomes_list', [biome.to_dict() for biome in biomes_list])
            socketio.emit('plants_list', [plant.to_dict() for plant in plants_list])
            sleep(1)

def initialize_new_upgrades(user_id):
    logging.info(f"Inside initialize_new_upgrades for user {user_id}")
    new_upgrades = []
    for upgrade in UPGRADES:
        new_upgrade = UpgradeModel(
            user_id=user_id,
            name=upgrade['name'],
            cost=upgrade['cost'],
            type=upgrade['type'],
            unlocked=upgrade['unlocked'],
            effect=upgrade['effect']
        )
        print(f"New upgrade: {new_upgrade}")
        new_upgrades.append(new_upgrade)
    return new_upgrades

def initialize_new_biomes(user_id):
    logging.info(f"Inside initialize_new_biomes for user {user_id}")
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
    logging.info(f"Inside initialize_new_plants for user {user_id}")
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
    logging.info(f"Inside initialize_new_plant_time for user {user_id}")
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
    logging.info(f"Inside initialize_new_global_state for user {user_id}")
    new_global_state = GlobalState(
        user_id=user_id,
        genetic_marker_progress=0,
        genetic_marker_threshold=10,
        genetic_markers=50,
        seeds=5,
        silica=0,
        tannins=0,
        calcium=0,
        fulvic=0
    )
    print(f"New GlobalState: {new_global_state}")
    return new_global_state



@game_state_bp.route('/init_game', methods=['POST'])
def init_game():
    user_id = current_user.id if current_user.is_authenticated else None
    if user_id:
        if user_id not in running_tasks:
            running_tasks[user_id] = socketio.start_background_task(target=background_task, app=current_app._get_current_object(), user_id=user_id)
    print("Initializing game state...")

    print(f"Is user authenticated? {current_user.is_authenticated}")  # Debugging line

    if current_user.is_authenticated:
        saved_global_state = fetch_global_state_from_db(current_user.id)
        if saved_global_state:
            return jsonify({"status": "Game state loaded from database"})

    # Initialize new global state
    global_state = initialize_new_global_state(user_id)

    # Save the global state to the database if the user is logged in
    if current_user.is_authenticated:
        save_global_state_to_db(current_user.id, global_state)  # Removed to_dict()

    return jsonify({"status": "Game initialized"})



@game_state_bp.route("/game")
def game():
    return "This is the game."

@game_state_bp.route('/save_game', methods=['POST'])
def save_game():
    if current_user.is_authenticated:
        game_state = request.json  # Replace with how you actually get the game state
        save_game_state_to_db(current_user.id, game_state)
        return jsonify({"status": "Game state saved"})
    return jsonify({"status": "User not authenticated"})

@game_state_bp.route('/toggle_sugar', methods=['POST'])
@login_required
def toggle_sugar():
    user_id = current_user.id
    plantId = request.json.get('plantId')
    isChecked = request.json.get('isChecked')

    action = {
        "type": "toggle_sugar",
        "plant_id": plantId,
        "isChecked": isChecked
    }

    user_actions_queue.append(action)

    return jsonify({"status": "Sugar toggle action queued"})


#Absorb Resource Route and Function
@game_state_bp.route('/absorb_resource', methods=['POST'])
@login_required
def absorb_resource():
    user_id = current_user.id
    plantId = request.json.get('plantId')
    resourceType = request.json.get('resourceType')
    amount = request.json.get('amount')

    action = {
        "type": "absorb_resource",
        "plant_id": plantId,
        "resourceType": resourceType,
        "amount": amount
    }

    user_actions_queue.append(action)

    return jsonify({"status": "Absorb resource action queued"})

#Buy Plant Part Route and Function
@game_state_bp.route('/buy_plant_part', methods=['POST'])
@login_required
def buy_plant_part():
    user_id = current_user.id
    plantId = request.json.get('plantId')
    partType = request.json.get('partType')

    action = {
        "type": "buy_plant_part",
        "plant_id": plantId,
        "partType": partType,
    }

    user_actions_queue.append(action)

    return jsonify({"status": "Buy plant part action queued"})

#Toggle Genetic Marker Route and Function
@game_state_bp.route('/toggle_genetic_marker', methods=['POST'])
@login_required
def toggle_genetic_marker():
    user_id = current_user.id
    plantId = request.json.get('plantId')
    isChecked = request.json.get('isChecked')

    action = {
        "type": "toggle_genetic_marker",
        "plant_id": plantId,
        "isChecked": isChecked
    }

    user_actions_queue.append(action)

    return jsonify({"status": "Toggle genetic marker action queued"})

#Toggle Secondary Resource Route and Function
@game_state_bp.route('/toggle_secondary_resource', methods=['POST'])
@login_required
def toggle_secondary_resource():
    user_id = current_user.id
    plantId = request.json.get('plantId')
    isChecked = request.json.get('isChecked')

    action = {
        "type": "toggle_secondary_resource",
        "plant_id": plantId,
        "isChecked": isChecked
    }

    user_actions_queue.append(action)

    return jsonify({"status": "Toggle secondary resource action queued"})

@game_state_bp.route('/purchase_seed', methods=['POST'])
@login_required
def purchase_seed():
    user_id = current_user.id
    plant_id = request.json.get('plant_id')
    action = {
        "type": "purchase_seed",
        "plant_id": plant_id

    }
    user_actions_queue.append(action)
    return jsonify({"status": "Purchase seed action queued"})

@game_state_bp.route('/plant_seed_in_biome', methods=['POST'])
@login_required
def plant_seed_in_biome():
    user_id = current_user.id
    biome_id = request.json.get('biome_id')
    action = {
        "type": "plant_seed_in_biome",
        "biome_id": request.json.get('biome_id')
    }
    user_actions_queue.append(action)
    return jsonify({"status": "Plant seed in biome action queued"})



@game_state_bp.route('/unlock_upgrade', methods=['POST'])
@login_required
def unlock_upgrade():
    user_id = current_user.id
    upgrade_id = request.json.get('upgrade_id')

    action = {
        "type": "unlock_upgrade",
        "upgrade_id": upgrade_id
    }

    user_actions_queue.append(action)
    return jsonify({"status": "Unlock upgrade action queued"})

@game_state_bp.route('/part_costs', methods=['GET'])
def get_part_costs():
    return jsonify(PARTS_COST_CONFIG)
