from flask import Flask, request, jsonify, session, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import base64
import pandas as pd
import matplotlib.pyplot as plt
from flask_socketio import SocketIO, emit
import io
import os
import cv2
import pytesseract
from datetime import datetime
from models import db,User, FloorPlan, MeetingRoom
from datetime import datetime
app= Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/91982/Desktop/MovieInSync/instance/database.db'
db.init_app(app)
app.secret_key='heudbw2735snd0182bdh376ch3865271'


        	
with app.app_context():
    db.create_all()

  

@app.route('/')
def dash():
    return render_template('dash.html')


pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.form
        hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256', salt_length=8)
        new_user = User(username=data['name'], password=hashed_password, email=data['email'])
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    session.pop('user', None)
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        admin_login = request.form.get('admin_login') == 'true'
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['email'] = user.email
            if admin_login and email in ['neermita@gmail.com']:
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('new_dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

def setup_meeting_rooms():
    predefined_rooms = [
        {'name': 'M1', 'capacity': 10},
        {'name': 'M2', 'capacity': 8},
        {'name': 'M3', 'capacity': 6},
        {'name': 'M4', 'capacity': 3}
    ]
    
    for room in predefined_rooms:
        existing_room = MeetingRoom.query.filter_by(name=room['name']).first()
        if not existing_room:
            new_room = MeetingRoom(name=room['name'], capacity=room['capacity'])
            db.session.add(new_room)
    db.session.commit()
    
@app.route('/admin_dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if 'user_id' not in session or session.get('email') not in ['neermita@gmail.com']:
        return redirect(url_for('login'))
    predefined_rooms = [
        {'name': 'M1', 'capacity': 10},
        {'name': 'M2', 'capacity': 8},
        {'name': 'M3', 'capacity': 6},
        {'name': 'M4', 'capacity': 3}
    ]
    
    for room in predefined_rooms:
        existing_room = MeetingRoom.query.filter_by(name=room['name']).first()
        if not existing_room:
            new_room = MeetingRoom(name=room['name'], capacity=room['capacity'])
            db.session.add(new_room)
    db.session.commit()

    floorplans = FloorPlan.query.all()
    meeting_rooms = MeetingRoom.query.all()

    return render_template('admin_dashboard.html', floorplans=floorplans, meeting_rooms=meeting_rooms)

@app.route('/new')
def new_dashboard():
    user_id = session['user_id']
    
    username = session.get('username')
    email = session.get('email')
    floorplans = FloorPlan.query.filter_by(username=username).all()
    meeting_rooms = MeetingRoom.query.all()
    return render_template('new.html', floorplans=floorplans, meeting_rooms=meeting_rooms, username=username)



def convert_meters_to_inches(meters):
    return meters * 39.37


def convert_coords_to_inches(feet_inch_str):
    feet, inch = feet_inch_str.split("'")
    inch = inch.replace('"', '')
    return (int(feet) * 12) + float(inch)

def generate_plot(data):
    fig, ax = plt.subplots()
    for room in data:
        name, dims, coords, time = room
        dims_parts = dims.split(', ')
        width_meters = float(dims_parts[0])
        height_meters = float(dims_parts[1])
        width_inches = convert_meters_to_inches(width_meters)
        height_inches = convert_meters_to_inches(height_meters)
        
        coords_parts = coords.split(', ')
        x_inches = convert_coords_to_inches(coords_parts[0])
        y_inches = convert_coords_to_inches(coords_parts[1])
        
        rect = plt.Rectangle((x_inches, y_inches), width_inches, height_inches, color='blue', alpha=0.5)
        ax.add_patch(rect)
        ax.text(x_inches + width_inches / 2, y_inches + height_inches / 2, name, fontsize=12, ha='center')
    
    ax.set_xlim(0, 1000) 
    ax.set_ylim(0, 1000)  
    ax.set_aspect('equal')
    plt.xlabel('X (inches)')
    plt.ylabel('Y (inches)')
    plt.title('Floor Plan')

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')
    
    plt.close(fig)
    
    return img_base64

@app.route('/upload_text', methods=['GET', 'POST'])
def upload_text():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        username = session.get('username')
        user_id = session['user_id']
        names = request.form.getlist('room_name[]')
        dimensions = request.form.getlist('dimensions[]')
        coordinates = request.form.getlist('coordinates[]')
        timestamps = request.form.getlist('timestamp[]')


        timestamp_objects = [datetime.strptime(ts, '%m/%d/%Y, %I:%M:%S %p') for ts in timestamps]

        data = list(zip(names, dimensions, coordinates, timestamp_objects))
        

        img_base64 = generate_plot(data)
        

        for room in data:
            name, dims, coords, timestamp = room
            floorplan = FloorPlan(username=username, name=name, dimensions=dims, coordinates=coords, timestamp=timestamp, image=img_base64)
            db.session.add(floorplan)
        db.session.commit()
        
        return redirect(url_for('new_dashboard'))
    return render_template('upload_text.html')


@app.route('/book_meeting_room', methods=['POST'])
def book_meeting_room():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    room_name = request.form['room_name']
    meeting_room = MeetingRoom.query.filter_by(name=room_name).first()
    if meeting_room and meeting_room.capacity > 0:
        meeting_room.booked_by = session['username']
        meeting_room.capacity -= 1
        db.session.commit()
    return redirect(url_for('new_dashboard'))

    




# Upload image floor plan
# @app.route('/upload_image', methods=['GET', 'POST'])
# def upload_image():
#     if 'user_id' not in session:
#         return redirect(url_for('login'))

#     if request.method == 'POST':
#         file = request.files['image']
#         filename = secure_filename(file.filename)
#         file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
#         img = cv2.imread(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#         gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#         blur = cv2.GaussianBlur(gray, (3, 3), 0)
#         thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
#         data = pytesseract.image_to_string(thresh)
        
#         new_plan = FloorPlan(user_id=session['user_id'], data=data, version=1)
#         existing_plan = FloorPlan.query.filter_by(user_id=session['user_id']).order_by(FloorPlan.timestamp.desc()).first()

#         if existing_plan:
#             new_plan = resolve_conflict(existing_plan, new_plan)

#         db.session.add(new_plan)
#         db.session.commit()
#         return redirect(url_for('new'))
    
#     return render_template('upload_image.html')

# def resolve_conflict(existing_plan, new_plan):

#     if new_plan.timestamp > existing_plan.timestamp:
#         new_plan.version = existing_plan.version + 1
#     else:
#         new_plan.version = existing_plan.version
    
#     # You can add more sophisticated conflict resolution logic here
#     return new_plan



if __name__ == '__main__':

    app.run(debug=True)