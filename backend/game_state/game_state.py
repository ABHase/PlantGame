"""
GameState Class (game_state.py)

    Attributes:
        plants: A list of all Plant objects.
        biomes: A list of all Biome objects.
        upgrades: A list of all Upgrade objects.
        genetic_markers: Total genetic markers.

    Methods:
        add_plant_to_biome(plant, biome): Add a plant to a biome.
        unlock_upgrade(upgrade): Unlock an upgrade.
        purchase_upgrade(upgrade): Purchase an upgrade.
        update(): Update the game state (called in the main game loop).
""" 
from constants import INITIAL_GENETIC_MARKER_THRESHOLD
from plants.plant import Plant
from biomes.biome import Biome
from plant_time import PlantTime
from game_resource import GameResource
from upgrades.upgrade import Upgrade


class GameState:
    def __init__(self, plants, biomes, upgrades, time, genetic_markers, seeds=5, genetic_marker_progress=0, genetic_marker_threshold=INITIAL_GENETIC_MARKER_THRESHOLD):
        self.plants = plants
        self.biomes = biomes
        self.upgrades = upgrades
        self.genetic_markers = genetic_markers
        self.genetic_marker_progress = genetic_marker_progress
        self.genetic_marker_threshold = genetic_marker_threshold
        self.seeds = seeds
        self.plant_time = time


    def update(self):
        self.plant_time.update()

        for biome in self.biomes:
            results = biome.update(self.plant_time.is_day)
            for can_produce, amount in results:  # Add water_absorbed here
                if can_produce:
                    self.update_genetic_marker_progress(amount)

        for upgrade in self.upgrades:
            upgrade_conditions = {
                'biome': len(self.biomes) >= 2,
                'plant part': len(self.plants) >= 2,  # You might want to update this condition too
                'genetic marker production rate': len(self.plants) >= 2,  # And this one
                'sugar production rate': len(self.plants) >= 2,  # And this one
                'plant capacity': len(self.biomes) >= 2
            }
            if upgrade.type in upgrade_conditions and upgrade_conditions[upgrade.type]:
                upgrade.unlock()

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
            initial_plant_parts = {'roots': GameResource('roots', 1), 'leaves': GameResource('leaves', 1)}
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
            'biomes': [
                {
                    'name': biome.name,
                    'capacity': biome.capacity,
                    'resource_modifiers': biome.resource_modifiers,
                    'ground_water_level': biome.ground_water_level,  # Include the missing field
                    'plants': [
                        {
                            'id': plant.id,
                            'maturity_level': plant.maturity_level,
                            'resources': {k: v.amount for k, v in plant.resources.items()},
                            'plant_parts': {k: v.amount for k, v in plant.plant_parts.items()},
                            'is_sugar_production_on': plant.is_sugar_production_on,
                            'is_genetic_marker_production_on': plant.is_genetic_marker_production_on,
                        }
                        for plant in biome.plants
                    ],
                }
                for biome in self.biomes
            ],
            'upgrades': [
                {
                    'name': upgrade.name,
                    'cost': upgrade.cost,
                    'type': upgrade.type,
                    'unlocked': upgrade.unlocked,
                }
                for upgrade in self.upgrades
            ],
            'plant_time': {
            'year': self.plant_time.year,
            'season': self.plant_time.season,
            'day': self.plant_time.day,
            'hour': self.plant_time.hour,
            'update_counter': self.plant_time.update_counter,
            'is_day': self.plant_time.is_day
            },
            'seeds': self.seeds,  
            'genetic_markers': self.genetic_markers,
            'genetic_marker_progress': self.genetic_marker_progress,
            'genetic_marker_threshold': self.genetic_marker_threshold,
        }

    @classmethod
    def from_dict(cls, data):
        biomes = []
        for biome_data in data['biomes']:
            plants = []
            for plant_data in biome_data['plants']:
                resources = {k: GameResource(k, v) for k, v in plant_data['resources'].items()}
                plant_parts = {k: GameResource(k, v) for k, v in plant_data['plant_parts'].items()}
                plant = Plant(
                    resources,
                    plant_parts,
                    None,  # Biome will be set later
                    plant_data['maturity_level'],
                    plant_data['is_sugar_production_on'],
                    plant_data['is_genetic_marker_production_on'],
                    plant_data['id']  # Include the id attribute
                )
                plant.is_sugar_production_on = plant_data['is_sugar_production_on']
                plant.is_genetic_marker_production_on = plant_data['is_genetic_marker_production_on']
                plants.append(plant)
            
            biome = Biome(
                biome_data['name'],
                biome_data['capacity'],
                biome_data['resource_modifiers'],
                biome_data['ground_water_level']  # Include the missing field
            )
            for plant in plants:
                plant.biome = biome
                biome.add_plant(plant)
            biomes.append(biome)

        upgrades = [Upgrade(upgrade_data['name'], upgrade_data['cost'], upgrade_data['type'], upgrade_data['unlocked']) for upgrade_data in data['upgrades']]

        plant_time_data = data.get('plant_time', {})
        plant_time = PlantTime()
        plant_time.year = plant_time_data.get('year', 1)
        plant_time.season = plant_time_data.get('season', 'Spring')
        plant_time.day = plant_time_data.get('day', 1)
        plant_time.hour = plant_time_data.get('hour', 0)
        plant_time.update_counter = plant_time_data.get('update_counter', 0)
        plant_time.is_day = plant_time_data.get('is_day', True)

        return cls(
            [],  # Plants will be populated through biomes
            biomes,
            upgrades,
            plant_time,
            data.get('genetic_markers', 0),  # Corrected this line
            data.get('seeds', 0),  # Corrected this line
            data.get('genetic_marker_progress', 0),  # Include the missing field
            data.get('genetic_marker_threshold', 0)  # Include the missing field
        )


    def __getstate__(self):
        return self.to_dict()

    def __setstate__(self, state):
        #print the state inside set state
        print("Set State")
        print(state)
        self.__dict__.update(GameState.from_dict(state).__dict__)