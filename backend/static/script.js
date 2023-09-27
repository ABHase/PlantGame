// Initialize the game when the page loads
window.onload = function() {
    // Establish a Socket.IO connection
    const socket = io.connect();

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
    });

    // Save game state when the user is about to leave the page
    window.onbeforeunload = function() {
        // Notify the server that the user is about to leave
        socket.emit('save_game_state');
    };
    
};
