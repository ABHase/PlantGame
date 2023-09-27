document.addEventListener("DOMContentLoaded", function() {
    const registerForm = document.getElementById("register-form");

    registerForm.addEventListener("submit", function(event) {
        event.preventDefault();
        const formData = new FormData(registerForm);
        const data = Object.fromEntries(formData);

        fetch("/user_auth/register", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(data),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                // Redirect to login page or directly log the user in
                window.location.href = "/user_auth/login";
            } else {
                // Show error message
                alert("Registration failed: " + data.message);
            }
        });
    });
});
