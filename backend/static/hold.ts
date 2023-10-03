// Function to update the UI based on the game state
function updateUI(gameState) {
    
    // Determine if it's day or night
    const isDay = gameState.plant_time.is_day;
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
      
        biomeDiv.innerHTML = `<h2 id="biome-header-${biomeIndex}">${biome.name} (${biome.plants.length}/${biome.capacity}) ${weatherIcon} ${pestIcon}
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
            const maxWaterCapacity = plant.plant_parts.vacuoles.amount * 100;  // Assuming each vacuole can hold 100 units of water
            const currentWaterAmount = plant.resources.water.amount;
            const waterProgressPercentage = (currentWaterAmount / maxWaterCapacity) * 100;

            let plantPartsRows = '';
            for (const [partType, partData] of Object.entries(plant.plant_parts)) {
                if (!partData.is_locked) {
                    plantPartsRows += `
                    <tr style="border: 1px solid black;">
                        <td><button onclick="buyPlantPart(${biomeIndex}, ${plantIndex}, '${partType}')">Grow</button>Grow</button></td>
                        <td>${capitalizeFirstLetter(partType)}:</td>
                        <td><span id="${partType}-${biomeIndex}-${plantIndex}">${partData.amount || 0}</span></td>
                    </tr>`;
                }
            }

                plantDiv.innerHTML = `
                <table style=width: 100%; "border-collapse: collapse;">
                    <tr style="border: 1px solid black;">
                    <td>${absorbSunlightButtonHTML}</td>
                    <td>Sunlight:</td>
                    <td><span id="sunlight-${biomeIndex}-${plantIndex}">${formatNumber(plant.resources.sunlight.amount)}</span></td>
                    </tr>
                    <tr style="border: 1px solid black;">
                    <td>${absorbWaterButtonHTML}</td>
                    <td>Water:</td>
                    <td><span id="water-${biomeIndex}-${plantIndex}">${formatNumber(plant.resources.water.amount)}</span></td>
                    </tr>
                    <tr style="border: 1px solid black;">
                        <td colspan="3">
                            <div class="water-progress-bar" id="water-storage-bar-${biomeIndex}-${plantIndex}">
                                <div class="water-progress-bar-fill" id="water-storage-fill-${biomeIndex}-${plantIndex}" style="width:${waterProgressPercentage}%"></div>
                            </div>
                        </td>
                    </tr>
                    ${plantPartsRows}
                    <tr style="border: 1px solid black;">
                    <td><input type="checkbox" id="${checkboxId}" ${isChecked ? 'checked' : ''} onchange="toggleSugar(${biomeIndex}, ${plantIndex}, this.checked)"></td>
                    <td>Sugar:</td>
                    <td><span id="sugar-${biomeIndex}-${plantIndex}">${formatNumber(plant.resources.sugar.amount)}</span></td>
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
