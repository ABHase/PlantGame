"""
Upgrade Class (upgrade.py)

    Attributes:
        name: Name of the upgrade.
        cost: Cost in genetic markers.
        type: Type of upgrade (biome, plant part, etc.)
        unlocked: Boolean indicating if the upgrade is unlocked.

    Methods:
        unlock(): Unlock this upgrade.
"""
class Upgrade:
    def __init__(self, name, cost, type, unlocked=False):
        self.name = name
        self.cost = cost
        self.type = type
        self.unlocked = unlocked

    def unlock(self):
        self.unlocked = True
