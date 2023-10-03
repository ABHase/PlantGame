"""
GameState Class (game_state.py)

    Attributes:
        plants: A list of all Plant objects.
        biomes: A list of all Biome objects.
        genetic_markers: Total genetic markers.

    Methods:
        add_plant_to_biome(plant, biome): Add a plant to a biome.
        update(): Update the game state (called in the main game loop).
""" 
from user_auth.models import PlantTimeModel
from constants import INITIAL_GENETIC_MARKER_THRESHOLD
from plants.plant import Plant
from biomes.biome import Biome
from biomes.biomes_config import BIOMES
from plant_time import PlantTime
from game_resource import GameResource
from events.event_emitter import EventEmitter
from .initial_resources_config import INITIAL_RESOURCES
from user_auth.user_auth import fetch_biomes_from_db, fetch_plant_time_from_db, save_plant_time_to_db, save_biomes_to_db, save_plants_to_db, fetch_plants_from_db, fetch_plants_from_db_by_biome_id_and_user, fetch_global_state_from_db, save_global_state_to_db


class GameState(EventEmitter):
    def __init__(self, genetic_markers, seeds=5, genetic_marker_progress=0, genetic_marker_threshold=INITIAL_GENETIC_MARKER_THRESHOLD):
        super().__init__()
        self.genetic_markers = genetic_markers
        self.genetic_marker_progress = genetic_marker_progress
        self.genetic_marker_threshold = genetic_marker_threshold
        self.seeds = seeds  

    def update(self, user_id=None):
        # Fetch and update PlantTime
        plant_time_model = fetch_plant_time_from_db(user_id)
        plant_time = PlantTime.from_dict(plant_time_model.to_dict())
        new_day, new_hour = plant_time.update()
        updated_plant_time_dict = plant_time.to_dict()
        for key, value in updated_plant_time_dict.items():
            setattr(plant_time_model, key, value)
        save_plant_time_to_db(user_id, plant_time_model)

        # Fetch and update GlobalState
        global_state_model = fetch_global_state_from_db(user_id)
        if global_state_model:
            self.genetic_markers = global_state_model.genetic_markers
            self.genetic_marker_progress = global_state_model.genetic_marker_progress
            self.genetic_marker_threshold = global_state_model.genetic_marker_threshold
            self.seeds = global_state_model.seeds

        # Fetch BiomeModels from the database
        biome_models = fetch_biomes_from_db(user_id)
        
        # Convert BiomeModels to Biome objects
        biomes = [Biome.from_dict(model.to_dict()) for model in biome_models]
        
        for biome in biomes:
            #Print biome id
            print(f"Biome ID: {biome.id}")
            # Fetch PlantModels for this biome from the database
            plant_models = fetch_plants_from_db_by_biome_id_and_user(biome.id, user_id)
            print(f"Plant Models: {plant_models}")
            # Convert PlantModels to Plant objects
            plants = [Plant.from_dict(model.to_dict()) for model in plant_models]
            print(f"Plants: {plants}")
            # Populate the plants attribute of the biome
            biome.plants = plants
            
            # Update each plant
            for plant in plants:
                can_produce, amount, water_absorbed = plant.update(plant_time.is_day, biome.ground_water_level, biome.current_weather)
                biome.ground_water_level -= water_absorbed
                if biome.ground_water_level < 0:
                    biome.ground_water_level = 0
                
                # Handle genetic markers, etc.
            
            # Update the biome
            results = biome.update(plant_time.is_day, new_day, new_hour, plant_time.season)
            
            for can_produce, amount in results:
                if can_produce:
                    self.update_genetic_marker_progress(amount)
            
            # Save updated Biome and Plant objects back to the database
            save_biomes_to_db(user_id, biomes)  # Pass the list of Biome objects
            for plant in plants:
                save_plants_to_db(user_id, plants)

            # Update GlobalState in the database
            for key, value in self.to_dict().items():
                setattr(global_state_model, key, value)
            save_global_state_to_db(user_id, global_state_model)

    def handle_unlock_upgrade(self, upgrade, cost):
        if self.genetic_markers >= cost:
            if upgrade.type == "biome":
                self.unlock_biome(upgrade)
            elif upgrade.type == "plant_part":
                self.unlock_plant_part(upgrade)
            # Subtract the cost here
            self.genetic_markers -= cost
        else:
            print(f"Not enough genetic markers to unlock this upgrade.")

    def unlock_biome(self, upgrade):
        biome_name = upgrade.effect  # Fetch the name from the effect field
        biome_config = BIOMES.get(biome_name)
        if biome_config:
            new_biome = Biome(
                name=biome_name,
                ground_water_level=biome_config['ground_water_level'],
                current_weather=biome_config['current_weather']
                # ... any other attributes ...
            )
            self.biomes.append(new_biome)

    def unlock_plant_part(self, upgrade):
        plant_part_to_unlock = upgrade.effect  # Fetch the plant part name from the effect field
        # Iterate through all biomes
        for biome in self.biomes:
            # Iterate through all plants in each biome
            for plant in biome.plants:
                # Check if the plant part exists in this plant
                if plant_part_to_unlock in plant.plant_parts:
                    # Unlock the plant part
                    plant.plant_parts[plant_part_to_unlock].unlock()
                    plant.plant_parts[plant_part_to_unlock].set_unlocked(True)



    def update_genetic_marker_progress(self, amount):
        self.genetic_marker_progress += amount
        if self.genetic_marker_progress >= self.genetic_marker_threshold:
            self.genetic_markers += 1
            self.genetic_marker_progress -= self.genetic_marker_threshold
            self.genetic_marker_threshold += self.genetic_marker_threshold  # Increase the threshold

    # Method to purchase a seed using a specific plant
    def purchase_seed_using_plant(self, plant_id, cost):
        print(f"Plant ID: {plant_id}")
        print(f"Purchase: Seed")
        
        # Search for the plant in all biomes
        plant = None
        for biome in self.biomes:
            plant = next((plant for plant in biome.plants if plant.id == plant_id), None)
            if plant is not None:
                break  # Exit the loop if the plant is found
        
        if plant is None:
            print("Plant is None.")
            return False  # Failed to purchase seed
        
        if plant.purchase_seed(cost):
            self.seeds += 1  # Increment the number of seeds
            return True  # Seed successfully purchased
        
        return False  # Failed to purchase seed

    
    # Method to plant a seed in a specific biome
    def plant_seed_in_biome(self, biome_name, genetic_marker_cost):
        print("Plant Seed in Biome backend")
        
        # Debug: Print the incoming parameters
        print(f"Biome Name: {biome_name}, Genetic Marker Cost: {genetic_marker_cost}")
        
        # Debug: Print the current state
        print(f"Current Seeds: {self.seeds}, Current Genetic Markers: {self.genetic_markers}")
        
        target_biome = next((biome for biome in self.biomes if biome.name == biome_name), None)
        
        # Debug: Check if the target biome was found
        if target_biome is None:
            print("Target biome not found.")
            return False
        
        print(f"Target Biome: {target_biome.name}, Capacity: {target_biome.capacity}, Current Plants: {len(target_biome.plants)}")
        
        if target_biome and self.seeds > 0 and self.genetic_markers > genetic_marker_cost and len(target_biome.plants) < target_biome.capacity:
            initial_resources = INITIAL_RESOURCES
            new_plant = Plant(initial_resources, None, None, 0, 1, 1)
            
            # Debug: Print the new plant details
            print(f"New Plant: {new_plant}")
            
            target_biome.add_plant(new_plant)
            self.seeds -= 1  # Decrement the number of seeds
            self.genetic_markers -= genetic_marker_cost
            
            # Debug: Confirm successful planting
            print("Seed successfully planted.")
            
            return True  # Seed successfully planted
        
        # Debug: Print why the seed planting failed
        print("Failed to plant seed.")
        return False  # Failed to plant seed

            
    def to_dict(self):
        return {
            'genetic_markers': self.genetic_markers,
            'genetic_marker_progress': self.genetic_marker_progress,
            'genetic_marker_threshold': self.genetic_marker_threshold,
            'seeds': self.seeds
        }


    @classmethod
    def from_dict(cls, data):
        return cls(
            data.get('genetic_markers', 0),
            data.get('seeds', 0),
            data.get('genetic_marker_progress', 0),
            data.get('genetic_marker_threshold', 0)
        )

    def __getstate__(self):
        return self.to_dict()

    def __setstate__(self, state):
        #print the state inside set state
        self.__dict__.update(GameState.from_dict(state).__dict__)