let socket;

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
        updateUI(data);
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
    // Update genetic marker information
    const geneticMarkersSpan = document.getElementById('genetic-markers');
    const geneticMarkerProgressSpan = document.getElementById('genetic-marker-progress');
    const geneticMarkerThresholdSpan = document.getElementById('genetic-marker-threshold');

    geneticMarkersSpan.textContent = gameState.genetic_markers;
    geneticMarkerProgressSpan.textContent = gameState.genetic_marker_progress;
    geneticMarkerThresholdSpan.textContent = gameState.genetic_marker_threshold;

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
        biomeDiv.innerHTML = `<h2 id="biome-header-${biomeIndex}">${biome.name} (${biome.plants.length}/${biome.capacity})</h2>
        <button onclick="plantSeedInBiome('${biome.name.replace(/'/g, "\\'")}', 1)">Plant Seed in Biome</button>`;

        
        const plantContainer = document.createElement('div');
        plantContainer.id = `plant-container-${biomeIndex}`;

        // Restore the display state or use the default
        const displayState = oldState.hasOwnProperty(`plant-container-${biomeIndex}`) ? oldState[`plant-container-${biomeIndex}`] : 'block';
        plantContainer.style.display = displayState;

        biome.plants.forEach((plant, plantIndex) => {
            const plantDiv = document.createElement('div');
            plantDiv.className = 'plant';
            plantDiv.id = `plant-${biomeIndex}-${plantIndex}`;

            const checkboxId = `sugar-toggle-${biomeIndex}-${plantIndex}`;
            const geneticMarkerCheckboxId = `genetic-marker-toggle-${biomeIndex}-${plantIndex}`;

            // Restore the checkbox state or use the state from the game state
            const isChecked = oldState.hasOwnProperty(checkboxId) ? oldState[checkboxId] : plant.is_sugar_production_on;
            const isGeneticMarkerChecked = oldState.hasOwnProperty(geneticMarkerCheckboxId) ? oldState[geneticMarkerCheckboxId] : plant.is_genetic_marker_production_on;

                plantDiv.innerHTML = `
                <table style="border-collapse: collapse;">
                    <tr style="border: 1px solid black;">
                    <td><button onclick="absorbResource(${biomeIndex}, ${plantIndex}, 'sunlight', 10)">Absorb</button></td>
                    <td>Sunlight:</td>
                    <td><span id="sunlight-${biomeIndex}-${plantIndex}">${formatNumber(plant.resources.sunlight)}</span></td>
                    </tr>
                    <tr style="border: 1px solid black;">
                    <td><button onclick="absorbResource(${biomeIndex}, ${plantIndex}, 'water', 10)">Absorb</button></td>
                    <td>Water:</td>
                    <td><span id="water-${biomeIndex}-${plantIndex}">${formatNumber(plant.resources.water)}</span></td>
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
                plantContainer.style.display = (plantContainer.style.display === 'none' || plantContainer.style.display === '') ? 'block' : 'none';
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
