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
from ..models.biome_model import BiomeModel
from ..user_auth.models import PlantTimeModel
from ..constants import INITIAL_GENETIC_MARKER_THRESHOLD
from ..plants.plant import Plant
from ..biomes.biome import Biome
from ..biomes.biomes_config import BIOMES
from ..plant_time import PlantTime
from ..events.event_emitter import EventEmitter
from ..user_auth.user_auth import fetch_biomes_from_db, fetch_plant_time_from_db, save_plant_time_to_db, save_biomes_to_db, save_plants_to_db, fetch_plants_from_db, fetch_plants_from_db_by_biome_id_and_user, fetch_global_state_from_db, save_global_state_to_db


class GameState(EventEmitter):
    def __init__(self, genetic_markers, seeds=5, silica = 0, tannins = 0, calcium = 0, fulvic = 0, genetic_marker_progress=0, genetic_marker_threshold=INITIAL_GENETIC_MARKER_THRESHOLD):
        super().__init__()
        self.genetic_markers = genetic_markers
        self.genetic_marker_progress = genetic_marker_progress
        self.genetic_marker_threshold = genetic_marker_threshold
        self.seeds = seeds
        self.silica = silica
        self.tannins = tannins
        self.calcium = calcium
        self.fulvic = fulvic

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
            # Fetch PlantModels for this biome from the database
            plant_models = fetch_plants_from_db_by_biome_id_and_user(biome.id, user_id)
            # Convert PlantModels to Plant objects
            plants = [Plant.from_dict(model.to_dict()) for model in plant_models]
            # Populate the plants attribute of the biome
            biome.plants = plants
            
            # Update each plant
            for plant in plants:
                can_produce, amount, water_absorbed, is_producing_secondary_resource = plant.update(plant_time.is_day, biome.ground_water_level, biome.current_weather)
                biome.ground_water_level -= water_absorbed
                if biome.ground_water_level < 0:
                    biome.ground_water_level = 0

                if is_producing_secondary_resource:
                    # Fetch the biome name from the database
                    existing_biome_model = BiomeModel.query.filter_by(id=plant.biome_id).first()
                    if existing_biome_model:
                        print(f"Existing biome model: {existing_biome_model}")
                        biome_name = existing_biome_model.name
                        self.update_secondary_resources(biome_name)  # Pass the biome name
                
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


    def update_genetic_marker_progress(self, amount):
        self.genetic_marker_progress += amount
        if self.genetic_marker_progress >= self.genetic_marker_threshold:
            self.genetic_markers += 1
            self.genetic_marker_progress -= self.genetic_marker_threshold
            self.genetic_marker_threshold += self.genetic_marker_threshold  # Increase the threshold

    def update_secondary_resources(self, biome_name):
        print(f"Updating secondary resources for biome {biome_name}")
        if biome_name == 'Desert':  # Replace with actual biome names
            self.silica += 1
        elif biome_name == 'Tropical Forest':
            self.tannins += 1
        elif biome_name == 'Mountain':
            self.calcium += 1
        elif biome_name == 'Swamp':
            self.fulvic += 1
        

            
    def to_dict(self):
        return {
            'genetic_markers': self.genetic_markers,
            'genetic_marker_progress': self.genetic_marker_progress,
            'genetic_marker_threshold': self.genetic_marker_threshold,
            'seeds': self.seeds,
            'silica': self.silica,
            'tannins': self.tannins,
            'calcium': self.calcium,
            'fulvic': self.fulvic
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data.get('genetic_markers', 0),
            data.get('seeds', 0),
            data.get('silica', 0),
            data.get('tannins', 0),
            data.get('calcium', 0),
            data.get('fulvic', 0),
            data.get('genetic_marker_progress', 0),
            data.get('genetic_marker_threshold', 0)
            
        )

    def __getstate__(self):
        return self.to_dict()

    def __setstate__(self, state):
        #print the state inside set state
        self.__dict__.update(GameState.from_dict(state).__dict__)