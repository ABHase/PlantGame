from flask import Blueprint, render_template, request, redirect, url_for, current_app
from flask_login import login_user, logout_user, login_required
from ..app import db  # Importing db directly from app
from .models import User  # Make sure to import User appropriately
from flask import json, jsonify
from .user_auth import initialize_user_game
from werkzeug.security import check_password_hash, generate_password_hash

user_auth_bp = Blueprint('user_auth', __name__)

@user_auth_bp.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        # Input validation
        if not username or not password:
            return jsonify({"status": "fail", "message": "Both username and password are required."})
        
        # Check if the username is already taken
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return jsonify({"status": "fail", "message": "Username is already taken."})

        # Hash the password and create the new user
        hashed_password = generate_password_hash(password, method='sha256')
        user = User(username=username, password=hashed_password)

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
        
        # Input validation (basic)
        if not username or not password:
            return jsonify({"status": "fail", "message": "Both username and password are required."})
        
        # Fetch the user based on the username
        user = User.query.filter_by(username=username).first()
        
        # Validate the user and password
        if user and check_password_hash(user.password, password):
            login_user(user)
            return jsonify({"status": "success", "message": "Successfully logged in", "user_id": user.id})
        else:
            return jsonify({"status": "fail", "message": "Invalid credentials"})
    
    return render_template('login.html')