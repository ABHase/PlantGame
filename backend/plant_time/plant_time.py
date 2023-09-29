class PlantTime:
    def __init__(self, year=1, season='Spring', day=1, hour=0, update_counter=0):
        self.year = year
        self.season = season
        self.day = day
        self.hour = hour
        self.update_counter = update_counter

    def update(self):
        self.update_counter += 1
        if self.update_counter >= 10:
            self.hour += 1
            self.update_counter = 0

        if self.hour >= 24:
            self.day += 1
            self.hour = 0

        if self.day > 30:
            self.day = 1
            self.change_season()

        if self.season == 'Winter' and self.day == 30:
            self.year += 1

    def change_season(self):
        seasons = ['Spring', 'Summer', 'Autumn', 'Winter']
        current_index = seasons.index(self.season)
        next_index = (current_index + 1) % 4
        self.season = seasons[next_index]