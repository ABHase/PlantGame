let socket;
let gameState = {};  // Define gameState as a global variable
let isDay = null;
let biomeGroundWaterLevels = {}; // At the top of your script
let currentlyDisplayedBiomeId = null;
const plantContainerVisibility = {};
let partsCostConfig = {};
let upgradeDescriptions = {};
let unlockedUpgrades = [];
let biomePlantCounts = {};  // Global variable to hold plant counts for each biome
let biomeIdToNameMap = {};  // Global variable to hold the mappinglet biomeIdToNameMap = {};  // Global variable to hold the mapping
let plantsData = [];  // This will hold the current list of plants
let currentUserId = null;
let plantTime = null;  // Store plant_time data here
let sunriseSunsetTimes = {};  // Store sunrise and sunset times here
const BIOME_ORDER = ["Beginner's Garden", "Desert", "Tropical Forest", "Mountain", "Swamp"];
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
    
    socket.on('connect', function() {
        console.log("Socket is connected with ID:", socket.id); // This should now print a valid ID
        
        // Now that we're connected, send the initial game state request
        fetch('/game_state/init_game', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ sid: socket.id })
        })
        .then(response => response.json())
        .then(data => {
            console.log(data);
        });
    });

    // Fetch the parts cost config
    fetch('/game_state/part_costs')
    .then(response => response.json())
    .then(data => {
        partsCostConfig = data;  // Update the global partsCostConfig variable
    });

    socket.on('debug_message', function(data) {
        console.log(data.message);
    });

    // Fetch the biome timezone offsets
    fetch('/game_state/biome_timezone_offsets')
    .then(response => response.json())
    .then(data => {
        biomeTimezoneOffsets = data;
    });

    // Fetch the sunrise and sunset times
    fetch('/sunrise_sunset_times')
    .then(response => response.json())
    .then(data => {
        sunriseSunsetTimes = data;
    })

    //Fetch the upgrade descriptions
    fetch('/upgrade_descriptions')
    .then(response => response.json())
    .then(data => {
        upgradeDescriptions = data;
        displayUpgradeDetails('Beginner\'s Garden');  // display initial description

    })

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
        plantTime = data;  // Store the entire plant_time data
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
    });

    window.addEventListener('beforeunload', function() {
        socket.close();
    });

    // Initially show the upgrades section (or biomes-section if preferred)
    showSection('upgrades-section');


};

function updateUpgradesUI(upgradesList) {
    const upgradesContainer = document.getElementById('upgrades-container');
    upgradesContainer.innerHTML = '';  // Clear existing upgrades

    const table = document.createElement('table');

    // Separate the biomes and other upgrades
    const biomes = upgradesList.filter(upgrade => upgrade.type === 'biome');
    const otherUpgrades = upgradesList.filter(upgrade => upgrade.type !== 'biome');

    // Explicit association between biome names and secondary resources
    const biomeToSecondaryResource = {
        'Desert': 'silica',
        'Tropical Forest': 'tannins',
        'Mountain': 'calcium',
        'Swamp': 'fulvic'
    };

    biomes.forEach(biome => {
        const row = table.insertRow();
        const biomeCell = row.insertCell();
        
        let biomeDisplayName = biome.name.replace('Unlock ', '');

        // Create the biome button element
        const biomeButton = document.createElement('button');
        biomeButton.innerText = biomeDisplayName;
        biomeButton.dataset.upgradeName = biomeDisplayName;
        biomeButton.addEventListener('click', function() {
            displayUpgradeDetails(this.dataset.upgradeName);
        });
        biomeCell.appendChild(biomeButton);

        const associatedResource = biomeToSecondaryResource[biomeDisplayName] || (biomeDisplayName === "Beginner's Garden" ? null : undefined);
        const associatedUpgrades = otherUpgrades.filter(upgrade => upgrade.secondary_resource === associatedResource);

        associatedUpgrades.forEach(upgrade => {
            const upgradeCell = row.insertCell();
            let upgradeDisplayName = upgrade.name.replace('Unlock ', '');
            
            // Create the upgrade button element
            const upgradeButton = document.createElement('button');
            upgradeButton.innerText = upgradeDisplayName;
            upgradeButton.dataset.upgradeName = upgradeDisplayName;
            upgradeButton.addEventListener('click', function() {
                displayUpgradeDetails(this.dataset.upgradeName);
            });
            upgradeCell.appendChild(upgradeButton);
        });
    });

    upgradesContainer.appendChild(table);
}



function displayUpgradeDetails(upgradeName) {
    const descriptionContainer = document.getElementById('upgrade-description-container');
    // Find the upgrade in the upgradeDescriptions using its name
    const upgradeDetail = upgradeDescriptions.find(upgrade => upgrade.name === upgradeName);

    // If the upgrade is found and has a description, use it, otherwise fall back to a default description.
    const descriptionText = (upgradeDetail && upgradeDetail.description) ? upgradeDetail.description : "Description not available.";

    // Display the description. You can enhance this with more HTML structure if needed.
    descriptionContainer.innerHTML = `<strong>${upgradeName}</strong>: ${descriptionText}`;
}





// Function to update the time-related UI elements
function updatePlantTimeUI(plantTimeData) {
    const yearSpan = document.getElementById('year');
    const seasonSpan = document.getElementById('season');
    const daySpan = document.getElementById('day');
    //const hourSpan = document.getElementById('hour');
    //const timeOfDaySpan = document.getElementById('time-of-day');

    yearSpan.textContent = plantTimeData.year;
    seasonSpan.textContent = plantTimeData.season;
    daySpan.textContent = plantTimeData.day;
    //hourSpan.textContent = plantTimeData.hour;
    //timeOfDaySpan.textContent = plantTimeData.is_day ? 'Day' : 'Night';
}

// Function to update the global state-related UI elements
function updateGlobalStateUI(globalStateData) {
    console.log("Updating UI with data:", globalStateData);
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

function updateBiomeListUI(biomeList) {
    const biomeContainer = document.getElementById('biome-container');
    
    // Remove biomes that no longer exist
    const existingBiomeDivs = Array.from(biomeContainer.children);
    existingBiomeDivs.forEach(existingBiomeDiv => {
        const existingBiomeId = existingBiomeDiv.id.replace('biome-', '');
        if (!biomeList.some(biome => `biome-${biome.id}` === existingBiomeId)) {
            biomeContainer.removeChild(existingBiomeDiv);
        }
    });

    // Sort biomeList based on BIOME_ORDER
    biomeList.sort((a, b) => BIOME_ORDER.indexOf(a.name) - BIOME_ORDER.indexOf(b.name));

    // First, create biome buttons
    const biomeButtonsDiv = document.getElementById('biome-buttons');
    biomeButtonsDiv.innerHTML = '';  // Clear existing buttons

    biomeList.forEach(biome => {
        const { isDayForBiome } = getBiomeSpecificTime(plantTime, biome.name);
        const { weatherIcon, pestIcon } = getIconsForBiome(biome, isDayForBiome);

        const biomeButton = document.createElement('button');
        biomeButton.innerHTML = `${biome.name} ${weatherIcon} ${pestIcon}`;  // Set HTML content to display icons
        biomeButton.onclick = function() {
            showSpecificBiome(`biome-${biome.id}`);
        };
        biomeButtonsDiv.appendChild(biomeButton);
    });


    biomeList.forEach((biome, biomeIndex) => {
        let biomeDiv = document.querySelector(`#biome-${biome.id}`);
        if (!biomeDiv) {
            biomeDiv = document.createElement('div');
            biomeDiv.className = 'biome';
            biomeDiv.id = `biome-${biome.id}`;
            biomeContainer.appendChild(biomeDiv);
        }

        const { isDayForBiome, effectiveHour } = getBiomeSpecificTime(plantTime, biome.name);
        const { weatherIcon, pestIcon } = getIconsForBiome(biome, isDayForBiome);

        const plantCount = biomePlantCounts[biome.id] || 0;

        biomeDiv.innerHTML = `
            <h2 id="biome-header-${biomeIndex}">
                ${biome.name} ${effectiveHour}:00 ${weatherIcon} ${pestIcon}
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

        const plantContainerId = `plant-container-${biome.id}`;
        let plantContainer = document.getElementById(plantContainerId);

        if (!plantContainer) {
            plantContainer = document.createElement('div');
            plantContainer.id = plantContainerId;
            plantContainer.className = 'plant-container';
            biomeDiv.appendChild(plantContainer);
        }
    });
        // After you've created and appended all the biomes, check if a biome was previously being displayed
        if (currentlyDisplayedBiomeId) {
            // Hide all biomes
            const allBiomes = document.querySelectorAll('.biome');
            allBiomes.forEach(biome => {
                biome.style.display = 'none';
            });

            // Show the previously displayed biome
            const targetBiome = document.getElementById(currentlyDisplayedBiomeId);
            if (targetBiome) {
                targetBiome.style.display = 'block';
            }
    }
    updatePlantListUI();

}

// Function to update the plant list UI
function updatePlantListUI() {
    plantsData.forEach((plant) => {
        const plantContainer = document.getElementById(`plant-container-${plant.biome_id}`);
        if (!plantContainer) return;  // Skip if the container doesn't exist

        let plantDiv = document.querySelector(`#plant-${plant.id}`);
        if (!plantDiv) {
            plantDiv = document.createElement('div');
            plantDiv.className = 'plant';
            plantDiv.id = `plant-${plant.id}`;
            plantContainer.appendChild(plantDiv);
        }

        const groundWaterLevel = biomeGroundWaterLevels[plant.biome_id] || 0;
        const maxWaterCapacity = plant.vacuoles * 100;
        const currentWaterAmount = plant.water;
        const waterProgressPercentage = (currentWaterAmount / maxWaterCapacity) * 100;
        const biomeName = biomeIdToNameMap[plant.biome_id] || 'Unknown';
        const plantParts = ['roots', 'leaves', 'vacuoles', 'resin', 'taproot', 'pheromones', 'thorns'];

        let secondaryResource = 'Resource';
        if (biomeName === 'Desert') {
            secondaryResource = 'Silica';
        } else if (biomeName === 'Tropical Forest') {
            secondaryResource = 'Tannins';
        } else if (biomeName === 'Mountain') {
            secondaryResource = 'Calcium';
        } else if (biomeName === 'Swamp') {
            secondaryResource = 'Fulvic';
        }

        // Determine if it's day or night for the biome of the current plant
        const { isDayForBiome } = getBiomeSpecificTime(plantTime, biomeIdToNameMap[plant.biome_id]);

        const shouldSkipRow = (biomeName === 'Beginner\'s Garden');


        const table = plantDiv.querySelector('table') || document.createElement('table');

        table.style.width = '100%';
        table.style.borderCollapse = 'collapse';

        // For sunlight row
        updateRow(table, `sunlight-row-${plant.id}`, [
            { content: isDayForBiome ? `<button onclick="absorbResource('${plant.id}', 'sunlight', 10)">Absorb</button>` : `<button disabled>It's night...</button>`, type: 'td' },
            { content: 'Sunlight:', type: 'td' },
            { content: `<span id="sunlight-${plant.id}">${plant.sunlight}</span>`, type: 'td' }
        ]);

        // For water row
        updateRow(table, `water-row-${plant.id}`, [
            { content: groundWaterLevel >= 10 ? `<button onclick="absorbResource('${plant.id}', 'water', 10)">Absorb</button>` : `<button disabled>No water...</button>`, type: 'td' },
            { content: 'Water:', type: 'td' },
            { content: `<span id="water-${plant.id}">${plant.water}</span>`, type: 'td' }
        ]);

                // For water progress bar row
        updateRow(table, `water-progress-row-${plant.id}`, [
            {
                content: `
                <div class="water-progress-bar" id="water-storage-bar-${plant.id}">
                    <div class="water-progress-bar-fill" id="water-storage-fill-${plant.id}" style="width:${waterProgressPercentage}%"></div>
                </div>
                `,
                type: 'td', attributes: { colspan: "3" }
            }
        ]);

        // For each plant part row
        plantParts.forEach((partType) => {
            const cost = partsCostConfig[partType] || 'N/A';  // Fetch the cost from the config, default to 'N/A' if not found
            const isDisabled = plant.sugar < cost ? 'disabled' : '';
            if (unlockedUpgrades.includes(partType)) {
                updateRow(table, `${partType}-row-${plant.id}`, [
                    { content: `<button ${isDisabled} onclick="buyPlantPart('${plant.id}', '${partType}')">Grow (${cost})</button>`, type: 'td' },
                    { content: `${capitalizeFirstLetter(partType)}:`, type: 'td' },
                    { content: `<span id="${partType}-${plant.id}">${plant[partType] || 0}</span>`, type: 'td' }
                ]);
            }
        });

        // For sugar row
        updateRow(table, `sugar-row-${plant.id}`, [
            {
                content: `<input type="checkbox" id="${'sugarCheckbox' + plant.id}" ${plant.is_sugar_production_on ? 'checked' : ''} onchange="toggleSugar('${plant.id}', this.checked)">`,
                type: 'td'
            },
            { content: 'Sugar:', type: 'td' },
            { content: `<span id="sugar-${plant.id}">${formatNumber(plant.sugar)}</span>`, type: 'td' }
        ]);

        // For genetic marker row
        updateRow(table, `genetic-marker-row-${plant.id}`, [
            {
                content: `<input type="checkbox" id="${'geneticMarkerCheckbox' + plant.id}" ${plant.is_genetic_marker_production_on ? 'checked' : ''} onchange="toggleGeneticMarker('${plant.id}', this.checked)">`,
                type: 'td'
            },
            { content: 'DNA', type: 'td' },
            { content: '', type: 'td' }
        ]);

        // For secondary resource row
        if (!shouldSkipRow) {
            updateRow(table, `secondary-resource-row-${plant.id}`, [
                {
                    content: `<input type="checkbox" id="${'secondaryResourceCheckbox' + plant.id}" ${plant.is_secondary_resource_production_on ? 'checked' : ''} onchange="toggleSecondaryResource('${plant.id}', this.checked)">`,
                    type: 'td'
                },
                { content: secondaryResource, type: 'td' },
                { content: '', type: 'td' }
            ]);
        }

        const button = plantDiv.querySelector('button') || document.createElement('button');
        button.onclick = function() {
            purchaseSeed(plant.id);
        };
        button.innerText = 'Purchase Seed';
        plantDiv.appendChild(button);
        plantDiv.appendChild(table);
    });
}

function updateRow(parent, rowId, cells) {
    let row = parent.querySelector(`#${rowId}`);
    if (!row) {
        row = document.createElement('tr');
        row.id = rowId;
        parent.appendChild(row);
    }

    // Ensure that there are enough cells in the row
    while (row.children.length < cells.length) {
        row.appendChild(document.createElement('td'));
    }
    
    // Update each cell's content if it has changed
    cells.forEach((cell, index) => {
        const existingCell = row.children[index];
        
        if (existingCell.innerHTML !== cell.content) {
            existingCell.innerHTML = cell.content;
        }
        
        if (cell.attributes) {
            for (const attr in cell.attributes) {
                existingCell.setAttribute(attr, cell.attributes[attr]);
            }
        }
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

function showSection(sectionId) {
    // Hide all sections
    const sections = document.querySelectorAll('.content-section');
    sections.forEach(section => {
        section.style.display = 'none';
    });

    // Show the target section
    document.getElementById(sectionId).style.display = 'block';
}

function showSpecificBiome(biomeId) {
    // First, hide all content sections
    const sections = document.querySelectorAll('.content-section');
    sections.forEach(section => {
        section.style.display = 'none';
    });

    // Now, show the biomes-section
    const biomesSection = document.getElementById('biomes-section');
    biomesSection.style.display = 'block';

    // Hide all biomes within biomes-section
    const allBiomes = document.querySelectorAll('.biome');
    allBiomes.forEach(biome => {
        biome.style.display = 'none';
    });

    // Show the specific biome
    const targetBiome = document.getElementById(biomeId);
    if (targetBiome) {
        targetBiome.style.display = 'block';
    }

    // Update the currentlyDisplayedBiomeId
    currentlyDisplayedBiomeId = biomeId;
}

function getBiomeSpecificTime(plantTime, biomeName) {
    const offset = biomeTimezoneOffsets[biomeName] || 0;
    let effectiveHour = (plantTime.hour + offset) % 24;
    
    if (effectiveHour < 0) {
        effectiveHour += 24;
    }

    // Assuming you have similar logic in frontend for sunrise and sunset
    const { sunrise, sunset } = getSunriseSunset(plantTime.season);
    const isDayForBiome = sunrise <= effectiveHour && effectiveHour < sunset;

    return { isDayForBiome, effectiveHour };
}


function getIconsForBiome(biome, isDayForBiome) {
    const weather = biome.current_weather;
    let weatherIcon = {
        'Sunny': isDayForBiome ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>',
        'Rainy': isDayForBiome ? '<i class="fas fa-cloud-rain"></i>' : '<i class="fas fa-cloud-moon-rain"></i>',
        'Snowy': isDayForBiome ? '<i class="fas fa-snowflake"></i>' : '<i class="fas fa-cloud-moon"></i>',
        'Cloudy': isDayForBiome ? '<i class="fas fa-cloud"></i>' : '<i class="fas fa-cloud-moon"></i>'
    }[weather] || '';  // Default to empty string if weather doesn't match

    const currentPest = biome.current_pest;
    let pestIcon = {
        'Aphids': '🐛',
        'Deer': '🦌',
        'Boar': '🐗',
        'None': ''
    }[currentPest] || '';

    return { weatherIcon, pestIcon };
}

function getSunriseSunset(season) {
    return sunriseSunsetTimes[season] || { sunrise: 6, sunset: 18 }; // Default values if season doesn't match
}
