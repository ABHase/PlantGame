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
        console.log('Received game_state:', data);
        // Update your client-side game state here
        updateUI(data);
    });

    // Save game state when the user is about to leave the page
    window.onbeforeunload = function() {
        // Notify the server that the user is about to leave
        socket.emit('save_game_state');
    };
};

// Function to update the UI based on the game state
function updateUI(gameState) {
    const biomeContainer = document.getElementById('biome-container');
    const oldState = {}; // To store the previous checkbox states
    
    // Store the current checkbox states before clearing the container
    gameState.biomes.forEach((biome, biomeIndex) => {
        biome.plants.forEach((_, plantIndex) => {
            const checkboxId = `sugar-toggle-${biomeIndex}-${plantIndex}`;
            const checkbox = document.getElementById(checkboxId);
            if (checkbox) {
                oldState[checkboxId] = checkbox.checked;
            }
        });
    });

    biomeContainer.innerHTML = '';  // Clear existing biomes and plants

    gameState.biomes.forEach((biome, biomeIndex) => {
        const biomeDiv = document.createElement('div');
        biomeDiv.className = 'biome';
        biomeDiv.innerHTML = `<h2>${biome.name}</h2>`;
        
        biome.plants.forEach((plant, plantIndex) => {
            const plantDiv = document.createElement('div');
            plantDiv.className = 'plant';
            plantDiv.id = `plant-${biomeIndex}-${plantIndex}`;
            
            const checkboxId = `sugar-toggle-${biomeIndex}-${plantIndex}`;
            
            // Restore the checkbox state or use the state from the game state
            const isChecked = oldState.hasOwnProperty(checkboxId) ? oldState[checkboxId] : plant.is_sugar_production_on;
            
            plantDiv.innerHTML = `
          <p>Sunlight: <span id="sunlight-${biomeIndex}-${plantIndex}">${plant.resources.sunlight}</span></p>
          <p>Water: <span id="water-${biomeIndex}-${plantIndex}">${plant.resources.water}</span></p>
          <p>Sugar: <span id="sugar-${biomeIndex}-${plantIndex}">${plant.resources.sugar}</span></p>
          <!-- More attributes -->
          <button onclick="buyRoot(${biomeIndex}, ${plantIndex})">Buy Root</button>
          <input type="checkbox" id="${checkboxId}" ${isChecked ? 'checked' : ''} onchange="toggleSugar(${biomeIndex}, ${plantIndex}, this.checked)">
          <label for="${checkboxId}">Sugar Production</label>
          <button onclick="produceSeed(${biomeIndex}, ${plantIndex})">Produce Seed</button>
        `;
        
        biomeDiv.appendChild(plantDiv);
      });
      
      biomeContainer.appendChild(biomeDiv);
    });
  }
  
  // Listen for game state updates from the server
  socket.on('game_state', function(gameState) {
    console.log("Received new game state", gameState);
    updateUI(gameState);
});

  // Functions to handle user actions
  function buyRoot(biomeIndex, plantIndex) {
    fetch('/game_state/buy_root', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ biomeIndex, plantIndex })
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


  
  function produceSeed(biomeIndex, plantIndex) {
    // Make an AJAX call to the backend to produce a seed for the specific plant
  }