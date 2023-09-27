"""
GameResource Class (game_resource.py)

    Attributes:
        resource_type: Type of the resource (sunlight, water, etc.)
        amount: Amount of the resource.

    Methods:
        add_amount(amount): Add to the resource.
        subtract_amount(amount): Subtract from the resource.
"""

class GameResource:
    def __init__(self, resource_type, amount):
        self.resource_type = resource_type
        self.amount = amount

    def add_amount(self, amount):
        self.amount += amount

    def subtract_amount(self, amount):
        self.amount -= amount