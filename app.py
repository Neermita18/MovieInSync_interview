from flask import Flask, request, jsonify, session, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

import os
import cv2
import pytesseract
from datetime import datetime
from models import db,User, FloorPlan
app= Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/91982/Desktop/MovieInSync/instance/database.db'
db.init_app(app)
app.secret_key='heudbw2735snd0182bdh376ch3865271'


        	
with app.app_context():
    db.create_all()
with app.app_context():
    metadata = db.metadata
    
    # Get the specific table you want to drop from the metadata
    table_name = 'usersdb'
    table_to_drop = metadata.tables.get(table_name)
    
    # Drop the table if it exists
    if table_to_drop is not None:
        table_to_drop.drop(db.engine)
  

@app.route('/')
def dash():
    return render_template('dash.html')


pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.form
        hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256', salt_length=8)
        new_user = User(username=data['name'], password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.form
        user = User.query.filter_by(username=data['name']).first()
        if user and check_password_hash(user.password, data['password']):
            session['user_id'] = user.id
            return redirect(url_for('upload'))
        return render_template('login.html', error='Invalid credentials')
    return render_template('new.html')

# Logout route
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return render_template('logout.html')

@app.route('/upload_text', methods=['GET', 'POST'])
def upload_text():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        room_names = request.form.getlist('room_name[]')
        dimensions = request.form.getlist('dimensions[]')
        coordinates = request.form.getlist('coordinates[]')

        combined_data = []
        for name, dimension, coordinate in zip(room_names, dimensions, coordinates):
            combined_data.append({
                "room_name": name,
                "dimensions": dimension,
                "coordinates": coordinate
            })

        data = str(combined_data)  # Convert list of dictionaries to string for storage

        new_plan = FloorPlan(user_id=session['user_id'], data=data, version=1)
        existing_plan = FloorPlan.query.filter_by(user_id=session['user_id']).order_by(FloorPlan.timestamp.desc()).first()

        # if existing_plan:
        #     new_plan = resolve_conflict(existing_plan, new_plan)

        db.session.add(new_plan)
        db.session.commit()
        return redirect(url_for('dash'))
    
    return render_template('new.html')

# Upload image floor plan
@app.route('/upload_image', methods=['GET', 'POST'])
def upload_image():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        file = request.files['image']
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        img = cv2.imread(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (3, 3), 0)
        thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        data = pytesseract.image_to_string(thresh)
        
        new_plan = FloorPlan(user_id=session['user_id'], data=data, version=1)
        existing_plan = FloorPlan.query.filter_by(user_id=session['user_id']).order_by(FloorPlan.timestamp.desc()).first()

     

        db.session.add(new_plan)
        db.session.commit()
        return redirect(url_for('dash'))
    
    return render_template('new.html')



if __name__ == '__main__':

    app.run(debug=True)