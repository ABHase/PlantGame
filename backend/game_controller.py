class GameController:
    def __init__(self, game_state):
        self.game_state = game_state

    def absorb_sunlight(self, plant):
        plant.absorb_resource('sunlight', 10)

    def absorb_water(self, plant):
        plant.absorb_resource('water', 10)

    def purchase_root(self, plant):
        plant.purchase_plant_part('roots', 10)

    def purchase_leaf(self, plant):
        plant.purchase_plant_part('leaves', 20)

    def purchase_seed(self, plant, target_biome):
        return plant.produce_seed(target_biome)
    