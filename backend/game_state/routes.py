from flask import Blueprint, jsonify, session, request, current_app
from time import sleep
from app import socketio  # Replace 'your_app_name' with the name of the package where app.py resides
from game_controller import GameController
from biomes.biome import Biome
from plants.plant import Plant
from game_resource import GameResource
from upgrades.upgrade import Upgrade
from game_state import GameState  # Import GameState
from socket_config import socketio
from flask_login import current_user, login_required
from user_auth.user_auth import fetch_game_state_from_db, save_game_state_to_db

game_state_bp = Blueprint('game_state', __name__)
running_tasks = {}
user_actions_queue = []


def background_task(app, user_id):
    with app.app_context():
        while True:
            game_state_dict = fetch_game_state_from_db(user_id)
            if game_state_dict is not None:
                game_state = GameState.from_dict(game_state_dict)
            else:
                print("game_state_dict is None, initializing a new game state.")
                game_state = initialize_new_game_state()

            # Process queued actions
            while user_actions_queue:
                action = user_actions_queue.pop(0)
                if action["type"] == "toggle_sugar":
                    #print toggling sugar for plant with id
                    print(f"Plant ID: {game_state.biomes[action['biomeIndex']].plants[action['plantIndex']].id}")
                    #print the is_sugar_production_on for the plant before toggling
                    print(f"Is sugar production on before toggling: {game_state.biomes[action['biomeIndex']].plants[action['plantIndex']].is_sugar_production_on}")
                    #print the game state before toggling
                    print(f"Game state before toggling: {game_state}")
                    plant = game_state.biomes[action["biomeIndex"]].plants[action["plantIndex"]]
                    plant.toggle_sugar_production()
                    #print the game state after toggling
                    print(f"Game state after toggling: {game_state}")
                    #print the is_sugar_production_on for the plant after toggling
                    print(f"Is sugar production on after toggling: {game_state.biomes[action['biomeIndex']].plants[action['plantIndex']].is_sugar_production_on}")
                    save_game_state_to_db(user_id, game_state.to_dict())

            # Update and save game state
            game_state.update()
            save_game_state_to_db(user_id, game_state.to_dict())

            # Emit updated game state to client
            socketio.emit('game_state', game_state.to_dict())
            sleep(1)




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
    print(f"Game state after initialization: {game_state}")
    print(f"Game state plants: {game_state.plants}")
    print(f"Game state biomes: {game_state.biomes}")
    print(f"Game state upgrades: {game_state.upgrades}")
    print(f"Game state genetic markers: {game_state.genetic_markers}")

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

def initialize_new_game_state():
    # Initialize a sample plant
    initial_resources = {
        'sunlight': GameResource('sunlight', 0),
        'water': GameResource('water', 0),
        'sugar': GameResource('sugar', 0),
    }
    initial_plant_parts = {'roots': GameResource('roots', 1), 'leaves': GameResource('leaves', 1)}
    plant1 = Plant(initial_resources, initial_plant_parts, 'Beginner\'s Garden', 0, 25, 1)

    # Initialize a sample biome
    biome1 = Biome('Beginner\'s Garden', 3, {'sunlight': 1, 'water': 1})
    biome1.add_plant(plant1)

    # Initialize a sample upgrade
    upgrade1 = Upgrade('Desert', 5, 'biome')

    initial_plants = [plant1]
    initial_biomes = [biome1]
    initial_upgrades = [upgrade1]
    initial_genetic_markers = 0

    return GameState(initial_plants, initial_biomes, initial_upgrades, initial_genetic_markers)

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
