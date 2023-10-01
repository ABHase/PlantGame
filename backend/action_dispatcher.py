# action_dispatcher.py

from action_handlers.toggle_sugar_handler import handle_toggle_sugar
from action_handlers.buy_plant_part_handler import handle_buy_plant_part
from action_handlers.absorb_resource_handler import handle_absorb_resource
from action_handlers.toggle_genetic_marker_handler import handle_toggle_genetic_marker
from action_handlers.purchase_seed_handler import handle_purchase_seed
from action_handlers.plant_seed_in_biome_handler import handle_plant_seed_in_biome

action_handlers = {
    "toggle_sugar": handle_toggle_sugar,
    "buy_plant_part": handle_buy_plant_part,
    "absorb_resource": handle_absorb_resource,
    "toggle_genetic_marker": handle_toggle_genetic_marker,
    "purchase_seed": handle_purchase_seed,
    "plant_seed_in_biome": handle_plant_seed_in_biome
}


def dispatch_action(action, game_state):
    action_type = action["type"]
    handler = action_handlers.get(action_type)
    if handler:
        handler(action, game_state)
    else:
        print(f"Unknown action type: {action_type}")

