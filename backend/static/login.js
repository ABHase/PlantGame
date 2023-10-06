document.addEventListener("DOMContentLoaded", function() {
    const loginForm = document.getElementById("login-form");

    loginForm.addEventListener("submit", function(event) {
        event.preventDefault();
        const formData = new FormData(loginForm);
        const data = Object.fromEntries(formData);

        fetch("/user_auth/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(data),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                // Establish a Socket.IO connection with the user_id
                socket = io.connect(socketURL, {
                    transports: ['websocket'],
                    query: { userId: data.user_id }
                });

                // Then, redirect to game or dashboard page
                window.location.href = "/game";
            } else {
                // Show error message
                alert("Login failed: " + data.message);
            }
        });
    });
});
