import uuid
from flask import Blueprint, jsonify, session, request, current_app
from time import sleep
from app import socketio
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
            game_state_dict = fetch_game_state_from_db(user_id)
            upgrades_list = fetch_upgrades_from_db(user_id)
            biomes_list = fetch_biomes_from_db(user_id)  # Assuming you have a similar function for biomes
            plants_list = fetch_plants_from_db(user_id)  # Assuming you have a similar function for plants
            plant_time = fetch_plant_time_from_db(user_id)
            global_state = fetch_global_state_from_db(user_id)

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



            #print(f"Game state after fetch: {game_state_dict}")
            if game_state_dict is not None:
                game_state = GameState.from_dict(game_state_dict)
                game_state.on("unlock_upgrade", game_state.handle_unlock_upgrade)
            else:
                game_state = initialize_new_game_state()

            # Process all queued actions in a single tick
            while user_actions_queue:
                for action in list(user_actions_queue):  # Create a copy of the queue to iterate over
                    dispatch_action(action, game_state)
                    user_actions_queue.remove(action)  # Remove the processed action
                save_game_state_to_db(user_id, game_state.to_dict())
                save_upgrades_to_db(user_id, upgrades_list)
                save_biomes_to_db(user_id, biomes_list)  # Assuming you have a similar function for biomes
                save_plants_to_db(user_id, plants_list)  # Assuming you have a similar function for plants


            game_state.update(user_id)
            save_game_state_to_db(user_id, game_state.to_dict())
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


def initialize_new_game_state():
    # Initialize a sample plant
    #initial_resources = INITIAL_RESOURCES

    #plant1 = Plant(initial_resources, None, None, 0, 1, 1)  # Biome will be set later

    # Initialize a sample biome
    #biome1 = Biome('Beginner\'s Garden', ground_water_level=1000, current_weather="Sunny")  # Attributes will be fetched from BIOMES dictionary
    #biome1.add_plant(plant1)
    #plant1.biome = biome1  # Set the biome for the plant

    # Initialize time object
    #initial_time = PlantTime(year=1, season='Spring', day=1, hour=6, update_counter=0)

    #initial_plants = [plant1]
    #initial_biomes = [biome1]
    initial_genetic_markers = 5

    # Print initializing game state
    print("Initializing Game State")
    game_state = GameState(initial_genetic_markers)
    game_state.on("unlock_upgrade", game_state.handle_unlock_upgrade)

    return game_state


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
        genetic_markers=5,
        seeds=5
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
        saved_game_state = fetch_game_state_from_db(current_user.id)
        if saved_game_state:
            return jsonify({"status": "Game state loaded from database"})

    # Initialize new game state
    game_state = initialize_new_game_state()


    # Save the game state to the database if the user is logged in
    if current_user.is_authenticated:
        save_game_state_to_db(current_user.id, game_state.to_dict())

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

@game_state_bp.route('/buy_root', methods=['POST'])
@login_required
def buy_root():
    user_id = current_user.id
    biomeIndex = request.json.get('biomeIndex')
    plantIndex = request.json.get('plantIndex')

    game_state_dict = fetch_game_state_from_db(user_id)
    game_state = GameState.from_dict(game_state_dict)

    plant = game_state.biomes[biomeIndex].plants[plantIndex]
    plant.purchase_plant_part('roots', 10)  # Assuming 10 is the cost

    save_game_state_to_db(user_id, game_state.to_dict())
    return jsonify({"status": "Root bought successfully"})

@game_state_bp.route('/toggle_sugar', methods=['POST'])
@login_required
def toggle_sugar():
    user_id = current_user.id
    biomeIndex = request.json.get('biomeIndex')
    plantIndex = request.json.get('plantIndex')
    isChecked = request.json.get('isChecked')

    action = {
        "type": "toggle_sugar",
        "biomeIndex": biomeIndex,
        "plantIndex": plantIndex,
        "isChecked": isChecked
    }

    user_actions_queue.append(action)

    return jsonify({"status": "Sugar toggle action queued"})

#Absorb Resource Route and Function
@game_state_bp.route('/absorb_resource', methods=['POST'])
@login_required
def absorb_resource():
    user_id = current_user.id
    biomeIndex = request.json.get('biomeIndex')
    plantIndex = request.json.get('plantIndex')
    resourceType = request.json.get('resourceType')
    amount = request.json.get('amount')

    action = {
        "type": "absorb_resource",
        "biomeIndex": biomeIndex,
        "plantIndex": plantIndex,
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
    biomeIndex = request.json.get('biomeIndex')
    plantIndex = request.json.get('plantIndex')
    partType = request.json.get('partType')

    action = {
        "type": "buy_plant_part",
        "biomeIndex": biomeIndex,
        "plantIndex": plantIndex,
        "partType": partType,
    }

    user_actions_queue.append(action)

    return jsonify({"status": "Buy plant part action queued"})

#Toggle Genetic Marker Route and Function
@game_state_bp.route('/toggle_genetic_marker', methods=['POST'])
@login_required
def toggle_genetic_marker():
    user_id = current_user.id
    biomeIndex = request.json.get('biomeIndex')
    plantIndex = request.json.get('plantIndex')
    isChecked = request.json.get('isChecked')

    action = {
        "type": "toggle_genetic_marker",
        "biomeIndex": biomeIndex,
        "plantIndex": plantIndex,
        "isChecked": isChecked
    }

    user_actions_queue.append(action)

    return jsonify({"status": "Toggle genetic marker action queued"})

@game_state_bp.route('/purchase_seed', methods=['POST'])
@login_required
def purchase_seed():
    user_id = current_user.id
    action = {
        "type": "purchase_seed",
        "biomeIndex": request.json.get('biomeIndex'),
        "plantIndex": request.json.get('plantIndex'),
        "cost": request.json.get('cost')
    }
    user_actions_queue.append(action)
    return jsonify({"status": "Purchase seed action queued"})

@game_state_bp.route('/plant_seed_in_biome', methods=['POST'])
@login_required
def plant_seed_in_biome():
    user_id = current_user.id
    action = {
        "type": "plant_seed_in_biome",
        "biome_name": request.json.get('biome_name'),
        "genetic_marker_cost": request.json.get('genetic_marker_cost')
    }
    user_actions_queue.append(action)
    return jsonify({"status": "Plant seed in biome action queued"})

@game_state_bp.route('/unlock_upgrade', methods=['POST'])
@login_required
def unlock_upgrade():
    user_id = current_user.id
    index = request.json.get('index')
    cost = request.json.get('cost')
    upgrade = fetch_upgrade_by_index(user_id, index)  # Fetch the upgrade here
    print(f"Cost from request: {request.json.get('cost')}")

    action = {
        "type": "unlock_upgrade",
        "index": index,
        "cost": cost,
        "user_id": user_id,  # Add this line
        "upgrade": upgrade.to_dict()
    }

    user_actions_queue.append(action)
    return jsonify({"status": "Unlock upgrade action queued"})

