from flask import Blueprint, render_template, request, redirect, url_for, current_app
from flask_login import login_user, logout_user, login_required
from ..app import db  # Importing db directly from app
from .models import User  # Make sure to import User appropriately
from flask import json, jsonify
from .user_auth import initialize_user_game

user_auth_bp = Blueprint('user_auth', __name__)

@user_auth_bp.route("/register", methods=['GET', 'POST'])
def register():
    print(f"Current app name: {current_app.name}")

    # Debugging: Check the database when a GET request is made
    if request.method == 'GET':
        print("Debug: Checking the database...")
        users = db.session.query(User).all()
        for user in users:
            print(f"Debug: Found user {user.username} with id {user.id}")

    if request.method == 'POST':
        data = request.json  # This line is new
        username = data.get('username')  # Modified this line
        password = data.get('password')  # Modified this line
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        login_user(user)

        # Initialize game components for the user
        initialize_user_game(user.id)

        return jsonify({"status": "success", "message": "Successfully registered"})

    return render_template('register.html')

@user_auth_bp.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        # Assuming you have a method to validate the user
        user = User.query.filter_by(username=username, password=password).first()
        
        if user:
            login_user(user)
            return jsonify({"status": "success", "message": "Successfully logged in"})
        else:
            return jsonify({"status": "fail", "message": "Invalid credentials"})
    
    return render_template('login.html')