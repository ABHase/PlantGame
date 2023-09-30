class PlantTime:
    def __init__(self, year=1, season='Spring', day=1, hour=0, update_counter=0):
        self.year = year
        self.season = season
        self.day = day
        self.hour = hour
        self.update_counter = update_counter
        self.is_day = self.calculate_is_day()

    def update(self):
        new_day = False  # Initialize the flag
        self.update_counter += 1
        if self.update_counter >= 10:
            self.hour += 1
            self.update_counter = 0
            self.is_day = self.calculate_is_day()  # Update is_day when the hour changes

        if self.hour >= 24:
            self.day += 1
            self.hour = 0
            new_day = True  # Set the flag to True when a new day starts

        if self.day > 30:
            self.day = 1
            self.change_season()

        if self.season == 'Winter' and self.day == 30:
            self.year += 1

        return new_day  # Return the flag

    def change_season(self):
        seasons = ['Spring', 'Summer', 'Autumn', 'Winter']
        current_index = seasons.index(self.season)
        next_index = (current_index + 1) % 4
        self.season = seasons[next_index]

    def calculate_is_day(self):
        sunrise, sunset = self.get_sunrise_sunset()
        return sunrise <= self.hour < sunset

    def get_sunrise_sunset(self):
        if self.season == 'Spring':
            return 6, 20
        elif self.season == 'Summer':
            return 5, 21
        elif self.season == 'Autumn':
            return 7, 19
        elif self.season == 'Winter':
            return 8, 18
