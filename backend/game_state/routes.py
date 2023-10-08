import uuid
from flask import Blueprint, jsonify, session, request, current_app
from time import sleep
from ..app import socketio
from ..plants.part_cost_config import PARTS_COST_CONFIG
from ..biomes.biomes_config import BIOMES
from ..plants.plant_parts_config import PLANT_PARTS_CONFIG  # Replace 'your_app_name' with the name of the package where app.py resides
from ..biomes.biome import Biome
from ..plants.plant import Plant
from ..upgrades.upgrades_config import UPGRADES
from ..game_state import GameState  # Import GameState
from ..socket_config import socketio, disconnect
from flask_login import current_user, login_required
from ..user_auth.user_auth import (
    fetch_game_state_from_db, save_game_state_to_db,
    fetch_upgrades_from_db, save_upgrades_to_db,
    fetch_upgrade_by_index,
    fetch_biomes_from_db, save_biomes_to_db,
    fetch_plants_from_db, save_plants_to_db,
    fetch_global_state_from_db, save_global_state_to_db,
    fetch_plant_time_from_db, save_plant_time_to_db
)
from ..user_auth.models import UpgradeModel, PlantTimeModel, GlobalState
from ..action_dispatcher import dispatch_action
#import log with timestamp function
from ..plant_time.plant_time import PlantTime
import logging
from ..models.biome_model import BiomeModel
from ..models.plant_model import PlantModel
from .plants_config import INITIAL_PLANT_CONFIG
from .BIOME_TIMEZONE_OFFSETS import BIOME_TIMEZONE_OFFSETS
from .sunrise_sunset_config import SUNRISE_SUNSET_TIMES
from ..upgrades.upgrades_description import UPGRADE_DESCRIPTIONS

logging.basicConfig(filename='app.log',level=logging.INFO)


game_state_bp = Blueprint('game_state', __name__)
running_tasks = {}
user_actions_queue = []

socket_to_user_mapping = {}

active_sockets = {}
users_connected = {}

@socketio.on('disconnect')
def handle_disconnect():
    # Find the user associated with this socket
    user_id = socket_to_user_mapping.get(request.sid)
    if user_id:
        del socket_to_user_mapping[request.sid]  # Remove this socket from our mapping

        # Check if the user's tasks are in the running_tasks dictionary and delete them
        if user_id in running_tasks:
            del running_tasks[user_id]

@socketio.on('connect')
def handle_connect():
    user_id = request.args.get('userId')
    users_connected[user_id] = True
    if user_id in active_sockets:
        # Handle reconnection scenario
        old_socket = active_sockets[user_id]
        disconnect(old_socket)
    active_sockets[user_id] = request.sid

def action_processor_task(app, user_id, socket_id):
    with app.app_context():
        print(f"Starting action processor task for user: {user_id} with socket_id: {socket_id}")
        while True:
            try:
                # Check if the socket is still connected
                if socket_id not in socket_to_user_mapping:
                    print(f"User {user_id} disconnected. Stopping action processor task.")
                    return  # This will end the action processor task

                if user_actions_queue:
                    for action in list(user_actions_queue):
                        dispatch_action(action)
                        user_actions_queue.remove(action)
                sleep(0.1)  # small sleep to prevent busy-waiting, adjust as needed
            except Exception as e:
                print(f"Error in action_processor_task for user {user_id}: {str(e)}")


def background_task(app, user_id, socket_id):
    with app.app_context():
        print(f"Starting background task for user: {user_id} with socket_id: {socket_id}")
        socketio.emit('debug_message', {'message': 'Background task started'}, room=socket_id)
        #emit debug message with socket_to_user_mapping
        socketio.emit('debug_message', {'message': f"Socket to user mapping: {socket_to_user_mapping}"}, room=socket_id)

        while True:
            try:
                # Check if the socket is still connected
                if socket_id not in socket_to_user_mapping:
                    print(f"User {user_id} disconnected. Stopping background task.")
                    return  # This will end the background task

                # 1. Fetching the Game State
                upgrades_list = fetch_upgrades_from_db(user_id)
                biomes_list = fetch_biomes_from_db(user_id)
                plants_list = fetch_plants_from_db(user_id)
                plant_time = fetch_plant_time_from_db(user_id)
                global_state = fetch_global_state_from_db(user_id)

                if global_state is None:
                    print("GlobalState is empty. Cannot initialize GameState.")
                    continue

                game_state = GameState.from_dict(global_state.to_dict())

                # 2. Updating the Game State
                game_state.update(user_id)

                # 3. Emitting to Client
                socketio.emit('game_state', game_state.to_dict(), room=socket_id)
                socketio.emit('global_state', global_state.to_dict(), room=socket_id)
                socketio.emit('plant_time', plant_time.to_dict(), room=socket_id)
                socketio.emit('upgrades_list', [upgrade.to_dict() for upgrade in upgrades_list], room=socket_id)
                socketio.emit('biomes_list', [biome.to_dict() for biome in biomes_list], room=socket_id)
                socketio.emit('plants_list', [plant.to_dict() for plant in plants_list], room=socket_id)

                sleep(1)
            except Exception as e:
                print(f"Error in background_task for user {user_id}: {str(e)}")


@game_state_bp.route('/init_game', methods=['POST'])
def init_game():
    try:
        data = request.get_json()
        socket_id = data['sid']  # Get the socket ID from the request data

        user_id = current_user.id if current_user.is_authenticated else None
        socket_to_user_mapping[socket_id] = user_id

        logging.info("Initializing game...")

        logging.info(f"User {user_id} connected. Socket ID: {socket_id}")
        if user_id:
            logging.info(f"User {user_id} authenticated. Initializing game...")
            if user_id not in running_tasks:
                logging.info(f"User {user_id} not in running_tasks. Initializing game...")
                running_tasks[user_id] = {
                    "game_task": socketio.start_background_task(target=background_task, app=current_app._get_current_object(), user_id=user_id, socket_id=socket_id),  # added socket_id
                    "action_task": socketio.start_background_task(target=action_processor_task, app=current_app._get_current_object(), user_id=user_id, socket_id=socket_id)
                }

        print("Initializing game state...")

        print(f"Is user authenticated? {current_user.is_authenticated}")  # Debugging line

        if current_user.is_authenticated:
            saved_global_state = fetch_global_state_from_db(current_user.id)
            if saved_global_state:
                return jsonify({"status": "Game state loaded from database"})

        return jsonify({"status": "Game initialized"})
    except Exception as e:
        logging.error(f"Error initializing game: {str(e)}")
        return jsonify({"error": "Error initializing game", "details": str(e)}), 500



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

@game_state_bp.route('/biome_timezone_offsets', methods=['GET'])
def get_biome_timezone_offsets():
    return jsonify(BIOME_TIMEZONE_OFFSETS)

@game_state_bp.route('/sunrise_sunset_times')
def get_sunrise_sunset_times():
    return jsonify(SUNRISE_SUNSET_TIMES)

@game_state_bp.route('/upgrade_descriptions')
def get_upgrade_descriptions():
    return jsonify(UPGRADE_DESCRIPTIONS)