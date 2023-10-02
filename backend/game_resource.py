class GameResource:
    def __init__(self, resource_type, amount, is_locked=False, is_unlocked=False):
        self.resource_type = resource_type
        self.amount = amount
        self.is_locked = is_locked
        self.is_unlocked = is_unlocked

    def add_amount(self, amount):
        self.amount += amount

    def subtract_amount(self, amount):
        self.amount -= amount

    def lock(self):
        self.is_locked = True

    def unlock(self):
        self.is_locked = False

    def set_unlocked(self, value):
        self.is_unlocked = value

    def to_dict(self):
        return {
            'resource_type': self.resource_type,
            'amount': self.amount,
            'is_locked': self.is_locked,
            'is_unlocked': self.is_unlocked
        }
