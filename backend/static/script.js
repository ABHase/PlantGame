let socket;
let gameState = {};  // Define gameState as a global variable
let isDay = null;
let biomeGroundWaterLevels = {}; // At the top of your script
const plantContainerVisibility = {};
let partsCostConfig = {};
let unlockedUpgrades = [];
let biomePlantCounts = {};  // Global variable to hold plant counts for each biome
let biomeIdToNameMap = {};  // Global variable to hold the mappinglet biomeIdToNameMap = {};  // Global variable to hold the mapping
let plantsData = [];  // This will hold the current list of plants
let currentUserId = null;
let socketURL;
if (APP_ENV === 'production') {
    socketURL = 'wss://idleplantgame-67d196ad0035.herokuapp.com/';
} else {
    socketURL = 'http://localhost:5000/';  // or whatever your local port is
}

// Initialize the game when the page loads
window.onload = function() {
    // Establish a Socket.IO connection
    socket = io.connect(socketURL, {
        transports: ['websocket'],
        query: { userId: currentUserId }
    });

    // Fetch initial game state
    fetch('/game_state/init_game', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ sid: socket.id })  // send the socket ID to the server
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);  // Should print {"status": "Game initialized"}
    });
    
    // Fetch the parts cost config
    fetch('/game_state/part_costs')
    .then(response => response.json())
    .then(data => {
        partsCostConfig = data;  // Update the global partsCostConfig variable
    });

    // Listen for game_state updates from the server
    socket.on('game_state', function(data) {
        // Update your client-side game state here
        gameState = data;  // Update the global gameState variable
        //updateUI(data);
    });

    // Listen for upgrades_list updates from the server
    socket.on('upgrades_list', function(data) {
        // Update your client-side upgrades list here
        updateUpgradesUI(data, gameState);
        unlockedUpgrades = data.filter(upgrade => upgrade.unlocked && upgrade.type === 'plant_part').map(upgrade => upgrade.effect);
    });

    // Listen for global_state updates from the server
    socket.on('global_state', function(data) {
        // Update your client-side global_state here
        updateGlobalStateUI(data);
    });

    // Listen for plant_time updates from the server
    socket.on('plant_time', function(data) {
        // Update your client-side plant_time here
        updatePlantTimeUI(data);
        isDay = data.is_day;
    });

    // Listen for biome_list updates from the server
    socket.on('biomes_list', function(data) {
        // Update your client-side biome_list here
        updateBiomeListUI(data);
        // Update the ground water levels for each biome
        data.forEach(biome => {
            biomeGroundWaterLevels[biome.id] = biome.ground_water_level;
            biomeIdToNameMap[biome.id] = biome.name;  // Populate the mapping
        });
    });

    // Listen for plant_list updates from the server
    socket.on('plants_list', function(data) {
        // Reset the plant counts
        biomePlantCounts = {};

        // Count the number of plants for each biome
        data.forEach(plant => {
            if (!biomePlantCounts[plant.biome_id]) {
                biomePlantCounts[plant.biome_id] = 0;
            }
            biomePlantCounts[plant.biome_id]++;
        });
        plantsData = data;  // Update the global plantsData variable
        updatePlantListUI();
    });

    window.addEventListener('beforeunload', function() {
        socket.close();
    });

};



function updateUpgradesUI(upgradesList) {
    const upgradesContainer = document.getElementById('upgrades-container');
    upgradesContainer.innerHTML = '';  // Clear existing upgrades

    const table = document.createElement('table');
    upgradesList.forEach((upgrade, index) => {
        if (upgrade.unlocked) {
            return;  // Skip this iteration if the upgrade is already unlocked
        }

        const row = table.insertRow();
        const cell1 = row.insertCell(0);

        const isUnlocked = upgrade.unlocked ? 'Unlocked' : 'Locked';
        const canUnlock = !upgrade.unlocked && gameState.genetic_markers >= upgrade.cost;

        cell1.innerHTML = `${upgrade.name} (${isUnlocked}) <br>` + 
                          (canUnlock ? `<button onclick="unlockUpgrade(${upgrade.id})">Unlock (${upgrade.cost} GM)</button>` : '');
    });

    upgradesContainer.appendChild(table);
}

// Function to update the time-related UI elements
function updatePlantTimeUI(plantTimeData) {
    const yearSpan = document.getElementById('year');
    const seasonSpan = document.getElementById('season');
    const daySpan = document.getElementById('day');
    const hourSpan = document.getElementById('hour');
    const timeOfDaySpan = document.getElementById('time-of-day');

    yearSpan.textContent = plantTimeData.year;
    seasonSpan.textContent = plantTimeData.season;
    daySpan.textContent = plantTimeData.day;
    hourSpan.textContent = plantTimeData.hour;
    timeOfDaySpan.textContent = plantTimeData.is_day ? 'Day' : 'Night';
}

// Function to update the global state-related UI elements
function updateGlobalStateUI(globalStateData) {
    const geneticMarkersSpan = document.getElementById('genetic-markers');
    const geneticMarkerProgressSpan = document.getElementById('genetic-marker-progress');
    const geneticMarkerThresholdSpan = document.getElementById('genetic-marker-threshold');
    const seedsSpan = document.getElementById('seeds');
    // UI elements for other global state variables silica, tannins, calcium, fulvic
    const silicaSpan = document.getElementById('silica');
    const tanninsSpan = document.getElementById('tannins');
    const calciumSpan = document.getElementById('calcium');
    const fulvicSpan = document.getElementById('fulvic');


    geneticMarkersSpan.textContent = globalStateData.genetic_markers;
    geneticMarkerProgressSpan.textContent = globalStateData.genetic_marker_progress;
    geneticMarkerThresholdSpan.textContent = globalStateData.genetic_marker_threshold;
    seedsSpan.textContent = globalStateData.seeds;
    // Update the UI elements for other global state variables silica, tannins, calcium, fulvic
    silicaSpan.textContent = globalStateData.silica;
    tanninsSpan.textContent = globalStateData.tannins;
    calciumSpan.textContent = globalStateData.calcium;
    fulvicSpan.textContent = globalStateData.fulvic;

    // Optional: Update progress bar
    const progressBar = document.getElementById('progress-bar');
    const progressPercentage = (globalStateData.genetic_marker_progress / globalStateData.genetic_marker_threshold) * 100;
    progressBar.style.width = `${progressPercentage}%`;
}

// Function to update the biome list UI
function updateBiomeListUI(biomeList) {
    const biomeContainer = document.getElementById('biome-container');
    biomeContainer.innerHTML = '';  // Clear existing biomes

    biomeList.forEach((biome, biomeIndex) => {
        const biomeDiv = document.createElement('div');
        biomeDiv.className = 'biome';
        biomeDiv.id = `biome-${biome.id}`;  // Assuming each biome has a unique id

        const weather = biome.current_weather;
        const currentPest = biome.current_pest;

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

        let pestIcon = currentPest ? {
            'Aphids': '🐛',
            'Deer': '🦌',
            'Boar': '🐗',
            'None': ''
        }[currentPest] : '';


        const plantCount = biomePlantCounts[biome.id] || 0;

        biomeDiv.innerHTML = `
            <h2 id="biome-header-${biomeIndex}">
                ${biome.name} ${weatherIcon} ${pestIcon}
            </h2>
            <table>
                <tr>
                    <td style="border: 1px solid black;">
                        Surface Water:
                    </td> 
                    <td style="border: 1px solid black;">
                        Snow Pack:
                    </td>
                    <td style="border: 1px solid black;">
                        Capacity:
                    </td>
                </tr>
                <tr>
                    <td style="border: 1px solid black;">
                        ${Math.floor(biome.ground_water_level)}
                    </td>
                    <td style="border: 1px solid black;">
                        ${Math.floor(biome.snowpack)}
                    </td>
                    <td style="border: 1px solid black;">
                    ${plantCount} / ${biome.capacity}
                    </td>
                </tr>
            </table>
            <button onclick="plantSeedInBiome('${biome.id}')">Plant Seed in Biome</button>
        `;

        // Add an empty container for plants
        const plantContainer = document.createElement('div');
        const plantContainerId = `plant-container-${biome.id}`;
        plantContainer.id = plantContainerId;
        plantContainer.className = 'plant-container';

        // Restore the visibility state if it exists
        if (plantContainerVisibility.hasOwnProperty(plantContainerId)) {
            plantContainer.style.display = plantContainerVisibility[plantContainerId];
        }

        biomeDiv.appendChild(plantContainer);
        biomeContainer.appendChild(biomeDiv);

        // Add event listener for toggling plant container visibility
        document.getElementById(`biome-header-${biomeIndex}`).addEventListener('click', function() {
            const plantContainer = document.getElementById(plantContainerId);
            plantContainer.style.display = (plantContainer.style.display === 'none' || plantContainer.style.display === '') ? 'flex' : 'none';
            // Update the visibility state
            plantContainerVisibility[plantContainerId] = plantContainer.style.display;
        });
    });
}

// Function to update the plant list UI
function updatePlantListUI() {
    plantsData.forEach((plant) => {
        const plantContainer = document.getElementById(`plant-container-${plant.biome_id}`);
        if (!plantContainer) return;  // Skip if the container doesn't exist

        const plantDiv = document.createElement('div');
        plantDiv.className = 'plant';
        plantDiv.id = `plant-${plant.id}`;

        const checkboxId = `sugar-toggle-${plant.id}`;
        const geneticMarkerCheckboxId = `genetic-marker-toggle-${plant.id}`;

        const absorbSunlightButtonHTML = isDay ? 
            `<button onclick="absorbResource('${plant.id}', 'sunlight', 10)">Absorb</button>` : 
            `<button disabled>It's night...</button>`;

        // Assuming you have a way to get the ground_water_level for the biome
        const groundWaterLevel = biomeGroundWaterLevels[plant.biome_id] || 0;
        
        const absorbWaterButtonHTML = groundWaterLevel >= 10 ? 
            `<button onclick="absorbResource('${plant.id}', 'water', 10)">Absorb</button>` : 
            `<button disabled>No water...</button>`;

        const maxWaterCapacity = plant.vacuoles * 100;
        const currentWaterAmount = plant.water;
        const waterProgressPercentage = (currentWaterAmount / maxWaterCapacity) * 100;
        const biomeName = biomeIdToNameMap[plant.biome_id] || 'Unknown';  // Fetch the biome name, default to 'Unknown' if not found

        let secondaryResource = 'Resource';  // Default value
        if (biomeName === 'Desert') {
            secondaryResource = 'Silica';
        } else if (biomeName === 'Tropical Forest') {
            secondaryResource = 'Tannins';
        } else if (biomeName === 'Mountain') {
            secondaryResource = 'Calcium';
        } else if (biomeName === 'Swamp') {
            secondaryResource = 'Fulvic';
        }

        let plantPartsRows = '';
        const plantParts = ['roots', 'leaves', 'vacuoles', 'resin', 'taproot', 'pheromones', 'thorns'];
        plantParts.forEach((partType) => {
            const cost = partsCostConfig[partType] || 'N/A';  // Fetch the cost from the config, default to 'N/A' if not found
            const isDisabled = plant.sugar < cost ? 'disabled' : '';
            if (unlockedUpgrades.includes(partType)) {
                plantPartsRows += `
                    <tr style="border: 1px solid black;">
                        <td><button ${isDisabled} onclick="buyPlantPart('${plant.id}', '${partType}')">Grow (${cost})</button></td>
                        <td>${capitalizeFirstLetter(partType)}:</td>
                        <td><span id="${partType}-${plant.id}">${plant[partType] || 0}</span></td>
                    </tr>`;
            }
        });        

        const shouldSkipRow = (biomeName === 'Beginner\'s Garden');  // Replace this condition with your actual criteria

        const secondaryResourceRow = shouldSkipRow ? '' : `
            <tr style="border: 1px solid black;">
                <td><input type="checkbox" id="${'secondaryResourceCheckbox' + plant.id}" ${plant.is_secondary_resource_production_on ? 'checked' : ''} onchange="toggleSecondaryResource('${plant.id}', this.checked)"></td>
                <td>${secondaryResource}</td>
                <td></td>
            </tr>
        `;


        plantDiv.innerHTML = `
            <table style="width: 100%; border-collapse: collapse;">
                <tr style="border: 1px solid black;">
                    <td>${absorbSunlightButtonHTML}</td>
                    <td>Sunlight:</td>
                    <td><span id="sunlight-${plant.id}">${plant.sunlight}</span></td>
                </tr>
                <tr style="border: 1px solid black;">
                    <td>${absorbWaterButtonHTML}</td>
                    <td>Water:</td>
                    <td><span id="water-${plant.id}">${plant.water}</span></td>
                </tr>
                <tr style="border: 1px solid black;">
                    <td colspan="3">
                        <div class="water-progress-bar" id="water-storage-bar-${plant.id}">
                            <div class="water-progress-bar-fill" id="water-storage-fill-${plant.id}" style="width:${waterProgressPercentage}%"></div>
                        </div>
                    </td>
                </tr>
                ${plantPartsRows}
                <tr style="border: 1px solid black;">
                <td><input type="checkbox" id="${'sugarCheckbox' + plant.id}" ${plant.is_sugar_production_on ? 'checked' : ''} onchange="toggleSugar('${plant.id}', this.checked)"></td>
                    <td>Sugar:</td>
                    <td><span id="sugar-${plant.id}">${formatNumber(plant.sugar)}</span></td>
                </tr>
                <tr style="border: 1px solid black;">
                <td><input type="checkbox" id="${'geneticMarkerCheckbox' + plant.id}" ${plant.is_genetic_marker_production_on ? 'checked' : ''} onchange="toggleGeneticMarker('${plant.id}', this.checked)"></td>
                    <td>DNA</td>
                    <td></td>
                </tr>
                ${secondaryResourceRow} 
                </tr>
            </table>
            <button onclick="purchaseSeed('${plant.id}')">Purchase Seed</button>
        `;

        plantContainer.appendChild(plantDiv);
    });
}

function unlockUpgrade(upgradeId) {  // Add cost as a parameter
    fetch('/game_state/unlock_upgrade', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ "upgrade_id": upgradeId })
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
    });
}

function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

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

 //Function to buy plant parts
 function buyPlantPart(plantId, partType) {
    fetch('/game_state/buy_plant_part', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ plantId, partType  })
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
    });
}
  
function toggleSugar(plantId, isChecked) {
    fetch('/game_state/toggle_sugar', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ plantId, isChecked })
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        if (data.status === "Sugar toggled successfully") {
            // Update the UI here or wait for the next game_state update from the server
        }
    });
}



function absorbResource(plantId, resourceType, amount) {
    fetch('/game_state/absorb_resource', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ plantId, resourceType, amount })
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

function toggleGeneticMarker(plantId, isChecked) {
    fetch('/game_state/toggle_genetic_marker', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ plantId, isChecked })
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        if (data.status === "Genetic Marker toggled successfully") {
            // Update the UI here or wait for the next game_state update from the server
        }
    });
}

// Function to toggle secondary resource production
function toggleSecondaryResource(plantId, isChecked) {
    fetch('/game_state/toggle_secondary_resource', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ plantId, isChecked })
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        if (data.status === "Secondary resource toggled successfully") {
            // Update the UI here or wait for the next game_state update from the server
        }
    });
}

function plantSeedInBiome(biomeId) {
    fetch('/game_state/plant_seed_in_biome', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ biome_id: biomeId })
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
    });
}

function purchaseSeed(plantId) {
    fetch('/game_state/purchase_seed', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ plant_id: plantId })
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
    });
}