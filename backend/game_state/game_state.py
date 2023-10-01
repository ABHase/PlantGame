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
from constants import INITIAL_GENETIC_MARKER_THRESHOLD
from plants.plant import Plant
from biomes.biome import Biome
from biomes.biomes_config import BIOMES
from plant_time import PlantTime
from game_resource import GameResource
from events.event_emitter import EventEmitter

class GameState(EventEmitter):
    def __init__(self, plants, biomes, time, genetic_markers, seeds=5, genetic_marker_progress=0, genetic_marker_threshold=INITIAL_GENETIC_MARKER_THRESHOLD):
        super().__init__()
        self.plants = plants
        self.biomes = biomes
        self.genetic_markers = genetic_markers
        self.genetic_marker_progress = genetic_marker_progress
        self.genetic_marker_threshold = genetic_marker_threshold
        self.seeds = seeds
        self.plant_time = time


    def update(self):
        new_day, new_hour = self.plant_time.update()  # Assuming update() returns True if a new day has started

        for biome in self.biomes:
            results = biome.update(self.plant_time.is_day, new_day, new_hour, self.plant_time.season)
            for can_produce, amount in results:
                if can_produce:
                    self.update_genetic_marker_progress(amount)

    def handle_unlock_upgrade(self, upgrade):
        if upgrade.type == "biome":
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
            new_plant = Plant(initial_resources, initial_plant_parts, target_biome, 0, 25, 1)
            
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
            'biomes': self.biomes_to_dict(),
            'plant_time': self.plant_time_to_dict(),
            'seeds': self.seeds,
            'genetic_markers': self.genetic_markers,
            'genetic_marker_progress': self.genetic_marker_progress,
            'genetic_marker_threshold': self.genetic_marker_threshold,
        }

    def biomes_to_dict(self):
        return [
            {
                'name': biome.name,
                'capacity': biome.capacity,
                'resource_modifiers': biome.resource_modifiers,
                'ground_water_level': biome.ground_water_level,
                'current_weather': biome.current_weather,
                'snowpack': biome.snowpack,
                'plants': self.plants_to_dict(biome)
            }
            for biome in self.biomes
        ]

    def plants_to_dict(self, biome):
        return [
            {
                'id': plant.id,
                'maturity_level': plant.maturity_level,
                'resources': {k: v.amount for k, v in plant.resources.items()},
                'plant_parts': {k: v.amount for k, v in plant.plant_parts.items()},
                'sugar_production_rate': plant.sugar_production_rate,
                'genetic_marker_production_rate': plant.genetic_marker_production_rate,
                'is_sugar_production_on': plant.is_sugar_production_on,
                'is_genetic_marker_production_on': plant.is_genetic_marker_production_on,
            }
            for plant in biome.plants
        ]

    def plant_time_to_dict(self):
        return {
            'year': self.plant_time.year,
            'season': self.plant_time.season,
            'day': self.plant_time.day,
            'hour': self.plant_time.hour,
            'update_counter': self.plant_time.update_counter,
            'is_day': self.plant_time.is_day
        }
    
    @classmethod
    def from_dict(cls, data):
        biomes = cls.biomes_from_dict(data['biomes'])
        plant_time = cls.plant_time_from_dict(data.get('plant_time', {}))
        return cls(
            [],
            biomes,
            plant_time,
            data.get('genetic_markers', 0),
            data.get('seeds', 0),
            data.get('genetic_marker_progress', 0),
            data.get('genetic_marker_threshold', 0)
        )

    @classmethod
    def biomes_from_dict(cls, biomes_data):
        biomes = []
        for biome_data in biomes_data:
            plants = cls.plants_from_dict(biome_data['plants'])
            biome = Biome(biome_data['name'], biome_data['ground_water_level'], biome_data['current_weather'], biome_data['snowpack'])
            for plant in plants:
                plant.biome = biome
                biome.add_plant(plant)
            biomes.append(biome)
        return biomes

    @classmethod
    def plants_from_dict(cls, plants_data):
        plants = []
        for plant_data in plants_data:
            resources = {k: GameResource(k, v) for k, v in plant_data['resources'].items()}
            plant_parts = {k: GameResource(k, v) for k, v in plant_data['plant_parts'].items()}
            plant = Plant(
                resources,
                plant_parts,
                None,
                plant_data['maturity_level'],
                plant_data['sugar_production_rate'],
                plant_data['genetic_marker_production_rate'],
                plant_data['id'],
                plant_data['is_sugar_production_on'],
                plant_data['is_genetic_marker_production_on'],
                
            )
            plants.append(plant)
        return plants

    @classmethod
    def plant_time_from_dict(cls, plant_time_data):
        plant_time = PlantTime()
        plant_time.year = plant_time_data.get('year', 1)
        plant_time.season = plant_time_data.get('season', 'Spring')
        plant_time.day = plant_time_data.get('day', 1)
        plant_time.hour = plant_time_data.get('hour', 0)
        plant_time.update_counter = plant_time_data.get('update_counter', 0)
        plant_time.is_day = plant_time_data.get('is_day', True)
        return plant_time


    def __getstate__(self):
        return self.to_dict()

    def __setstate__(self, state):
        #print the state inside set state
        self.__dict__.update(GameState.from_dict(state).__dict__)