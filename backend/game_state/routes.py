from flask import Blueprint, jsonify, session, request, current_app
from time import sleep
from app import socketio  # Replace 'your_app_name' with the name of the package where app.py resides
from game_controller import GameController
from biomes.biome import Biome
from plants.plant import Plant
from game_resource import GameResource
from upgrades.upgrade import Upgrade
from upgrades.upgrades_config import UPGRADES
from game_state import GameState  # Import GameState
from socket_config import socketio
from flask_login import current_user, login_required
from user_auth.user_auth import fetch_game_state_from_db, save_game_state_to_db, fetch_upgrades_from_db, save_upgrades_to_db, fetch_upgrade_by_index
from user_auth.models import UpgradeModel
from action_dispatcher import dispatch_action
#import log with timestamp function
from user_auth.user_auth import log_with_timestamp
from plant_time.plant_time import PlantTime
import logging

logging.basicConfig(filename='app.log',level=logging.INFO)


game_state_bp = Blueprint('game_state', __name__)
running_tasks = {}
user_actions_queue = []


def background_task(app, user_id):
    with app.app_context():
        while True:
            game_state_dict = fetch_game_state_from_db(user_id)
            upgrades_list = fetch_upgrades_from_db(user_id)
            
            # Check if upgrades_list is empty or None, and initialize if needed
            if upgrades_list is None or len(upgrades_list) == 0:
                print(f"Upgrades list is empty for user {user_id}. Initializing new upgrades list.")
                upgrades_list = initialize_new_upgrades(user_id)

            #print(f"Game state after fetch: {game_state_dict}")
            if game_state_dict is not None:
                game_state = GameState.from_dict(game_state_dict)
                game_state.on("unlock_upgrade", game_state.handle_unlock_upgrade)
            else:
                game_state = initialize_new_game_state()

            # Process queued actions
            while user_actions_queue:
                action = user_actions_queue.pop(0)
                dispatch_action(action, game_state)
                save_game_state_to_db(user_id, game_state.to_dict())
                save_upgrades_to_db(user_id, upgrades_list)

            game_state.update()
            save_game_state_to_db(user_id, game_state.to_dict())
            save_upgrades_to_db(user_id, upgrades_list)

            # Emit updated game state to client
            socketio.emit('game_state', game_state.to_dict())
            socketio.emit('upgrades_list', [upgrade.to_dict() for upgrade in upgrades_list]) 
            sleep(1)


def initialize_new_game_state():
    # Initialize a sample plant
    initial_resources = {
        'sunlight': GameResource('sunlight', 0),
        'water': GameResource('water', 0),
        'sugar': GameResource('sugar', 0),
    }
    initial_plant_parts = {
        'roots': GameResource('roots', 2),
        'leaves': GameResource('leaves', 1),
        'vacuoles': GameResource('vacuoles', 1),  # Initialize with 1 vacuole
        'resin': GameResource('resin', 0),  # Initialize with 0 resin
    }

    plant1 = Plant(initial_resources, initial_plant_parts, None, 0, 1, 1)  # Biome will be set later

    # Initialize a sample biome
    biome1 = Biome('Beginner\'s Garden',ground_water_level=1000,current_weather="Sunny")  # Attributes will be fetched from BIOMES dictionary
    biome1.add_plant(plant1)
    plant1.biome = biome1  # Set the biome for the plant

    # Initialize time object
    initial_time = PlantTime(year=1, season='Spring', day=1, hour=6, update_counter=0)

    initial_plants = [plant1]
    initial_biomes = [biome1]
    initial_genetic_markers = 5

    # Print initializing game state
    print("Initializing Game State")
    game_state = GameState(initial_plants, initial_biomes, initial_time, initial_genetic_markers)
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
    cost = request.json.get('cost')

    action = {
        "type": "buy_plant_part",
        "biomeIndex": biomeIndex,
        "plantIndex": plantIndex,
        "partType": partType,
        "cost": cost
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

    action = {
        "type": "unlock_upgrade",
        "index": index,
        "cost": cost,
        "user_id": user_id,  # Add this line
        "upgrade": upgrade.to_dict()
    }

    user_actions_queue.append(action)
    return jsonify({"status": "Unlock upgrade action queued"})

