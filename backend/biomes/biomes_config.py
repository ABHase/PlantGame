BIOMES = {
    "Beginner's Garden": {
        'capacity': 3,
        'resource_modifiers': {'sunlight': 1, 'water': 1},
        'weather_conditions': {
            'Spring': {'Sunny': 0.6, 'Rainy': 0.3, 'Cloudy': 0.1},
            'Summer': {'Sunny': 0.7, 'Rainy': 0.2, 'Cloudy': 0.1},
            'Autumn': {'Sunny': 0.5, 'Rainy': 0.3, 'Cloudy': 0.2},
            'Winter': {'Sunny': 0.4, 'Snowy': 0.4, 'Cloudy': 0.2},
        },
        'rain_intensity': 5,
        'snow_intensity': 4  # Amount of water to add when it snows
    },
    'Desert': {
        'capacity': 5,
        'resource_modifiers': {'sunlight': 1.5, 'water': 0.5},
        'weather_conditions': {
            'Spring': {'Sunny': 0.9, 'Rainy': 0.05, 'Cloudy': 0.05},
            'Summer': {'Sunny': 0.95, 'Rainy': 0.03, 'Cloudy': 0.02},
            'Autumn': {'Sunny': 0.9, 'Rainy': 0.05, 'Cloudy': 0.05},
            'Winter': {'Sunny': 0.9, 'Snowy': 0.05, 'Cloudy': 0.05},
        },
        'rain_intensity': 20,
        'snow_intensity': 15  # Desert snow can be rare but intense
    },
    'Tropical Forest': {
        'capacity': 4,
        'resource_modifiers': {'sunlight': 1.2, 'water': 1.3},
        'weather_conditions': {
            'Spring': {'Sunny': 0.4, 'Rainy': 0.5, 'Cloudy': 0.1},
            'Summer': {'Sunny': 0.3, 'Rainy': 0.6, 'Cloudy': 0.1},
            'Autumn': {'Sunny': 0.4, 'Rainy': 0.5, 'Cloudy': 0.1},
            'Winter': {'Sunny': 0.5, 'Rainy': 0.4, 'Cloudy': 0.1},
        },
        'rain_intensity': 10,
        'snow_intensity': 0  # No snow in tropical forest
    },
    'Mountain': {
        'capacity': 2,
        'resource_modifiers': {'sunlight': 1.1, 'water': 0.9},
        'weather_conditions': {
            'Spring': {'Sunny': 0.5, 'Rainy': 0.2, 'Cloudy': 0.3},
            'Summer': {'Sunny': 0.6, 'Rainy': 0.1, 'Cloudy': 0.3},
            'Autumn': {'Sunny': 0.4, 'Rainy': 0.2, 'Cloudy': 0.4},
            'Winter': {'Sunny': 0.3, 'Snowy': 0.5, 'Cloudy': 0.2},
        },
        'rain_intensity': 8,
        'snow_intensity': 12  # Heavy snowfall in winter
    },
    'Swamp': {
        'capacity': 6,
        'resource_modifiers': {'sunlight': 0.8, 'water': 1.4},
        'weather_conditions': {
            'Spring': {'Sunny': 0.3, 'Rainy': 0.6, 'Cloudy': 0.1},
            'Summer': {'Sunny': 0.2, 'Rainy': 0.7, 'Cloudy': 0.1},
            'Autumn': {'Sunny': 0.3, 'Rainy': 0.6, 'Cloudy': 0.1},
            'Winter': {'Sunny': 0.4, 'Snowy': 0.3, 'Cloudy': 0.3},
        },
        'rain_intensity': 12,
        'snow_intensity': 8  # Moderate snowfall in winter
    }
}
