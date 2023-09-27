// Function to create a new plant div with default values
function createPlantDiv(plantId) {
    const plantDiv = document.createElement('div');
    plantDiv.className = 'plant';
    plantDiv.dataset.id = plantId;
    plantDiv.innerHTML = `
        <h3 class="plant-name">Plant in [Biome Name]</h3>
        <p>Maturity Level: <span class="maturity-level">0</span></p>
        <div class="resources">
            <p>Sunlight: <span class="sunlight">0</span></p>
            <p>Water: <span class="water">0</span></p>
            <p>Sugar: <span class="sugar">0</span></p>
        </div>
        <div class="plant-parts">
            <p>Roots: <span class="roots">0</span></p>
            <p>Leaves: <span class="leaves">0</span></p>
        </div>
        <div class="actions">
            <button class="absorb-sunlight">Absorb Sunlight</button>
            <button class="absorb-water">Absorb Water</button>
            <button class="buy-root">Buy Root</button>
            <button class="buy-leaf">Buy Leaf</button>
        </div>
        <div class="toggle-actions">
            <label><input type="checkbox" class="toggle-sugar"> Enable Sugar Production</label>
            <label><input type="checkbox" class="toggle-genetic-marker"> Enable Genetic Marker Production</label>
        </div>
    `;
    return plantDiv;
}

// Function to update an existing plant div based on new data
function updatePlantDiv(plantData, plantDiv, plantId) {
    plantDiv.querySelector('.plant-name').textContent = `Plant in ${plantData.biome}`;
    plantDiv.querySelector('.maturity-level').textContent = plantData.maturity_level;
    plantDiv.querySelector('.sunlight').textContent = plantData.resources.sunlight;
    plantDiv.querySelector('.water').textContent = plantData.resources.water;
    plantDiv.querySelector('.sugar').textContent = plantData.resources.sugar;
    plantDiv.querySelector('.roots').textContent = plantData.plant_parts.roots;
    plantDiv.querySelector('.leaves').textContent = plantData.plant_parts.leaves;
    plantDiv.querySelector('.toggle-sugar').checked = plantData.is_sugar_production_on;
    plantDiv.querySelector('.toggle-genetic-marker').checked = plantData.is_genetic_marker_production_on;
}
