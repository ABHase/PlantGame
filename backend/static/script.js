let socket;
let gameState = {};  // Define gameState as a global variable

// Initialize the game when the page loads
window.onload = function() {
    // Establish a Socket.IO connection
    socket = io.connect();

    // Fetch initial game state
    fetch('/game_state/init_game', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);  // Should print {"status": "Game initialized"}
    });

    // Listen for game_state updates from the server
    socket.on('game_state', function(data) {
        // Update your client-side game state here
        gameState = data;  // Update the global gameState variable
        updateUI(data);
    });

    // Listen for upgrades_list updates from the server
    socket.on('upgrades_list', function(data) {
        // Update your client-side upgrades list here
        updateUpgradesUI(data, gameState);
    });

    // Save game state when the user is about to leave the page
    window.onbeforeunload = function() {
        // Notify the server that the user is about to leave
        socket.emit('save_game_state');
    };
};

function formatNumber(num) {
    if (num < 1000) {
        return Math.floor(num);
    } else {
        let formatted = (num / 1000).toFixed(1);
        // Remove trailing zeros after the decimal point
        formatted = parseFloat(formatted).toString();
        return formatted + 'K';
    }
}



// Function to update the UI based on the game state
function updateUI(gameState) {
    console.log("Updating UI with gameState:", gameState);
    
    // Determine if it's day or night
    const isDay = gameState.plant_time.is_day;

    // Update time information
    const yearSpan = document.getElementById('year');
    const seasonSpan = document.getElementById('season');
    const daySpan = document.getElementById('day');
    const hourSpan = document.getElementById('hour');
    const timeOfDaySpan = document.getElementById('time-of-day');
    
    yearSpan.textContent = gameState.plant_time.year;
    seasonSpan.textContent = gameState.plant_time.season;
    daySpan.textContent = gameState.plant_time.day;
    hourSpan.textContent = gameState.plant_time.hour;
    timeOfDaySpan.textContent = gameState.plant_time.is_day ? 'Day' : 'Night';
    
    // Update genetic marker information

    const geneticMarkersSpan = document.getElementById('genetic-markers');
    const geneticMarkerProgressSpan = document.getElementById('genetic-marker-progress');
    const geneticMarkerThresholdSpan = document.getElementById('genetic-marker-threshold');
    const seedsSpan = document.getElementById('seeds');

    geneticMarkersSpan.textContent = gameState.genetic_markers;
    geneticMarkerProgressSpan.textContent = gameState.genetic_marker_progress;
    geneticMarkerThresholdSpan.textContent = gameState.genetic_marker_threshold;
    seedsSpan.textContent = gameState.seeds;

    // Optional: Update progress bar
    const progressBar = document.getElementById('progress-bar');
    const progressPercentage = (gameState.genetic_marker_progress / gameState.genetic_marker_threshold) * 100;
    progressBar.style.width = `${progressPercentage}%`;

    const biomeContainer = document.getElementById('biome-container');
    const oldState = {}; // To store the previous checkbox states

    // Store the current checkbox states before clearing the container
    gameState.biomes.forEach((biome, biomeIndex) => {
        biome.plants.forEach((_, plantIndex) => {
            const geneticMarkerCheckboxId = `genetic-marker-toggle-${biomeIndex}-${plantIndex}`;
            const geneticMarkerCheckbox = document.getElementById(geneticMarkerCheckboxId);
            const checkboxId = `sugar-toggle-${biomeIndex}-${plantIndex}`;
            const checkbox = document.getElementById(checkboxId);
            if (geneticMarkerCheckbox) {
                oldState[geneticMarkerCheckboxId] = geneticMarkerCheckbox.checked;
            }
            if (checkbox) {
                oldState[checkboxId] = checkbox.checked;
            }
        });
    });

    // Store the current display states before clearing the container
    gameState.biomes.forEach((biome, biomeIndex) => {
        const plantContainerId = `plant-container-${biomeIndex}`;
        const plantContainer = document.getElementById(plantContainerId);
        if (plantContainer) {
            oldState[plantContainerId] = plantContainer.style.display;
        }
    });

    biomeContainer.innerHTML = '';  // Clear existing biomes and plants

    gameState.biomes.forEach((biome, biomeIndex) => {
        const biomeDiv = document.createElement('div');
        biomeDiv.className = 'biome';

        const weather = biome.current_weather;

        let weatherIcon = '';

        if (isDay) {
            weatherIcon = {
                'Sunny': '<i class="fas fa-sun"></i>',
                'Rainy': '<i class="fas fa-cloud-rain"></i>',
                'Snowy': '<i class="fas fa-snowflake"></i>',
                'Cloudy': '<i class="fas fa-cloud"></i>'
            }[weather];
        } else {
            weatherIcon = weather === 'Sunny' ? '<i class="fas fa-moon"></i>' : 
                        weather === 'Rainy' ? '<i class="fas fa-cloud-moon-rain"></i>' : 
                        weather === 'Snowy' ? '<i class="fas fa-cloud-moon"></i>' : 
                        weather === 'Cloudy' ? '<i class="fas fa-cloud-moon"></i>' : '';
        }

        biomeDiv.innerHTML = `<h2 id="biome-header-${biomeIndex}">${biome.name} (${biome.plants.length}/${biome.capacity}) ${weatherIcon} 
            <br>Ground Water: ${Math.floor(biome.ground_water_level)} <br>Snow Pack: ${Math.floor(biome.snowpack)}</h2>
            <button onclick="plantSeedInBiome('${biome.name.replace(/'/g, "\\'")}', 1)">Plant Seed in Biome</button>`;

        
        const plantContainer = document.createElement('div');
        plantContainer.id = `plant-container-${biomeIndex}`;
        plantContainer.className = 'plant-container';

        // Restore the display state or use the default
        const displayState = oldState.hasOwnProperty(`plant-container-${biomeIndex}`) ? oldState[`plant-container-${biomeIndex}`] : 'flex';
        plantContainer.style.display = displayState;

        biome.plants.forEach((plant, plantIndex) => {

            const absorbAmount = weather === 'Sunny' ? 10 : 
                                weather === 'Cloudy' ? 5 : 
                                weather === 'Rainy' ? 2 : 
                                weather === 'Snowy' ? 1 : 0;  // Default to 0 if none match

            const plantDiv = document.createElement('div');
            plantDiv.className = 'plant';
            plantDiv.id = `plant-${biomeIndex}-${plantIndex}`;

            const checkboxId = `sugar-toggle-${biomeIndex}-${plantIndex}`;
            const geneticMarkerCheckboxId = `genetic-marker-toggle-${biomeIndex}-${plantIndex}`;
            
            // Disable the button if it's night for absorb sunlight
            const absorbSunlightButtonHTML = isDay ? 
            `<button onclick="absorbResource(${biomeIndex}, ${plantIndex}, 'sunlight', ${absorbAmount})">Absorb</button>` : 
            `<button disabled>It's night...</button>`;

            // Disable the button if ground_water_level is less than 10
            const absorbWaterButtonHTML = biome.ground_water_level >= 10 ? 
            `<button onclick="absorbResource(${biomeIndex}, ${plantIndex}, 'water', 10)">Absorb</button>` : 
            `<button disabled>No water...</button>`;

            // Restore the checkbox state or use the state from the game state
            const isChecked = oldState.hasOwnProperty(checkboxId) ? oldState[checkboxId] : plant.is_sugar_production_on;
            const isGeneticMarkerChecked = oldState.hasOwnProperty(geneticMarkerCheckboxId) ? oldState[geneticMarkerCheckboxId] : plant.is_genetic_marker_production_on;

            //Progress Bar for Water
            const maxWaterCapacity = plant.plant_parts.vacuoles * 100;  // Assuming each vacuole can hold 100 units of water
            const currentWaterAmount = plant.resources.water;
            const waterProgressPercentage = (currentWaterAmount / maxWaterCapacity) * 100;

                plantDiv.innerHTML = `
                <table style=width: 100%; "border-collapse: collapse;">
                    <tr style="border: 1px solid black;">
                    <td>${absorbSunlightButtonHTML}</td>
                    <td>Sunlight:</td>
                    <td><span id="sunlight-${biomeIndex}-${plantIndex}">${formatNumber(plant.resources.sunlight)}</span></td>
                    </tr>
                    <tr style="border: 1px solid black;">
                    <td>${absorbWaterButtonHTML}</td>
                    <td>Water:</td>
                    <td><span id="water-${biomeIndex}-${plantIndex}">${formatNumber(plant.resources.water)}</span></td>
                    </tr>
                    <tr style="border: 1px solid black;">
                        <td colspan="3">
                            <div class="water-progress-bar" id="water-storage-bar-${biomeIndex}-${plantIndex}">
                                <div class="water-progress-bar-fill" id="water-storage-fill-${biomeIndex}-${plantIndex}" style="width:${waterProgressPercentage}%"></div>
                            </div>
                        </td>
                    </tr>
                    <tr style="border: 1px solid black;">
                    <td><button onclick="buyPlantPart(${biomeIndex}, ${plantIndex}, 'roots', 10)">Grow</button></td>
                    <td>Roots:</td>
                    <td><span id="roots-${biomeIndex}-${plantIndex}">${plant.plant_parts.roots}</span></td>                
                    </tr>
                    <tr style="border: 1px solid black;">
                    <td><button onclick="buyPlantPart(${biomeIndex}, ${plantIndex}, 'leaves', 10)">Grow</button></td>
                    <td>Leaves:</td>
                    <td><span id="leaves-${biomeIndex}-${plantIndex}">${plant.plant_parts.leaves}</span></td>                
                    </tr>
                    <tr style="border: 1px solid black;">
                    <td><button onclick="buyPlantPart(${biomeIndex}, ${plantIndex}, 'vacuoles', 10)">Grow</button></td>
                    <td>Vacuoles:</td>
                    <td><span id="vacuoles-${biomeIndex}-${plantIndex}">${plant.plant_parts.vacuoles}</span></td>                
                    </tr>
                    <tr style="border: 1px solid black;">
                    <td><button onclick="buyPlantPart(${biomeIndex}, ${plantIndex}, 'resin', 10)">Grow</button></td>
                    <td>Resin:</td>
                    <td><span id="resin-${biomeIndex}-${plantIndex}">${plant.plant_parts.resin || 0}</span></td>                
                    </tr>
                    <tr style="border: 1px solid black;">
                    <td><input type="checkbox" id="${checkboxId}" ${isChecked ? 'checked' : ''} onchange="toggleSugar(${biomeIndex}, ${plantIndex}, this.checked)"></td>
                    <td>Sugar:</td>
                    <td><span id="sugar-${biomeIndex}-${plantIndex}">${formatNumber(plant.resources.sugar)}</span></td>
                    <td></td>
                    </tr>
                    <tr style="border: 1px solid black;">
                    <td><input type="checkbox" id="${geneticMarkerCheckboxId}" ${isGeneticMarkerChecked ? 'checked' : ''} onchange="toggleGeneticMarker(${biomeIndex}, ${plantIndex}, this.checked)"></td>
                    <td>DNA</td>
                    <td></td>
                    </tr>
                </table>
                <button onclick="purchaseSeed(${biomeIndex}, ${plantIndex}, 10)">Purchase Seed</button>
                `;

                plantContainer.appendChild(plantDiv);  // Append plantDiv to plantContainer
            });
    
            biomeDiv.appendChild(plantContainer);  // Append plantContainer to biomeDiv
            biomeContainer.appendChild(biomeDiv);  // Append biomeDiv to biomeContainer
    
            document.getElementById(`biome-header-${biomeIndex}`).addEventListener('click', function() {
                const plantContainer = document.getElementById(`plant-container-${biomeIndex}`);
                plantContainer.style.display = (plantContainer.style.display === 'none' || plantContainer.style.display === '') ? 'flex' : 'none';
            });
        });
    }

 //Function to buy plant parts
function buyPlantPart(biomeIndex, plantIndex, partType, cost) {
    fetch('/game_state/buy_plant_part', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ biomeIndex, plantIndex, partType, cost })
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
    });
}
  
 function toggleSugar(biomeIndex, plantIndex, isChecked) {
    fetch('/game_state/toggle_sugar', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ biomeIndex, plantIndex, isChecked })
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        if (data.status === "Sugar toggled successfully") {
            // Update the UI here or wait for the next game_state update from the server
        }
    });
}


function absorbResource(biomeIndex, plantIndex, resourceType, amount) {
    fetch('/game_state/absorb_resource', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ biomeIndex, plantIndex, resourceType, amount })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log(data);
    })
    .catch(error => {
        console.log('Fetch error:', error);
    });
}

function toggleGeneticMarker(biomeIndex, plantIndex, isChecked) {
    fetch('/game_state/toggle_genetic_marker', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ biomeIndex, plantIndex, isChecked })
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        if (data.status === "Genetic Marker toggled successfully") {
            // Update the UI here or wait for the next game_state update from the server
        }
    });
}


function plantSeedInBiome(biomeName, geneticMarkerCost) {
    fetch('/game_state/plant_seed_in_biome', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ biome_name: biomeName, genetic_marker_cost: geneticMarkerCost })
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
    });
}

function purchaseSeed(biomeIndex, plantIndex, cost) {
    fetch('/game_state/purchase_seed', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ biomeIndex, plantIndex, cost })
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
    });
}

function updateUpgradesUI(upgradesList) {
    const upgradesContainer = document.getElementById('upgrades-container');
    upgradesContainer.innerHTML = '';  // Clear existing upgrades

    const table = document.createElement('table');
    upgradesList.forEach((upgrade, index) => {
        const row = table.insertRow();
        const cell1 = row.insertCell(0);

        const isUnlocked = upgrade.unlocked ? 'Unlocked' : 'Locked';
        const canUnlock = !upgrade.unlocked && gameState.genetic_markers >= upgrade.cost;

        cell1.innerHTML = `${upgrade.name} (${isUnlocked}) <br>` + 
                          (canUnlock ? `<button onclick="unlockUpgrade(${index})">Unlock (${upgrade.cost} GM)</button>` : '');
    });

    upgradesContainer.appendChild(table);
}


function unlockUpgrade(index) {
    fetch('/game_state/unlock_upgrade', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ index })
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
    });
}
