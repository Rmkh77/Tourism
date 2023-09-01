from google_images_search import GoogleImagesSearch
from flask import Flask, request, render_template, jsonify, redirect, url_for, g,session
from flask_sqlalchemy import SQLAlchemy
import pyttsx3
import pandas as pd
import openai
from flask import flash

app = Flask(__name__)

class User_data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    interesting_places = db.Column(db.String(200), nullable=False)
    interesting_categories = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(100), nullable=False) 

def lock():
    locations_data = {}    
    locations = session.get('interesting_places')
    catts=session.get('categories') 
    for i in range(len(locc)):
        if (locc[i] in locations or cat[i] in catts) and (placc[i] not in locations_data):
            locations_data[placc[i]] =[img_1[i]]            
            locations_data[placc[i]].append(img_2[i]) 
            locations_data[placc[i]].append(img_3[i])             
            locations_data[placc[i]].append(locc[i]) 
            locations_data[placc[i]].append(cat[i])            
    for i in range(len(pl1)):
        if pl1[i] in locations_data:
            txt= ds1[i]
            locations_data[pl1[i]].append(txt) 
    return locations_data

#fetching images from google
def get_google_image_urls(name):
    image_urls = []
    _search_params = {
        'q': name,
        'num': 3,  
        'safe': 'high', 
        'fileType': 'jpg|png',
    }
    gis.search(search_params=_search_params)
    for image in gis.results():
        image_urls.append(image.url)
    return image_urls

# Function to close the database connection
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Route for the output.html
@app.route('/')
def index():
    return render_template('register.html')

@app.route('/output')
def output():
    locations = session.get('interesting_places')
    per_name = session.get('name')
    return render_template('output.html',per_name=per_name.capitalize(),interesting_places=locations,locations_data=lock())

@app.route('/exploring', methods=['GET', 'POST'])
def exploring():
    place_name= request.form['name']
    if place_name:        
        prompt = f"provide me introduction of {place_name} in 100 words"
        response = openai.Completion.create(
                    engine='text-davinci-003',
                    prompt=prompt,
                    max_tokens=1000
                )
        description_part1 = response.choices[0].text.strip()                
        prompt = f"when to visit {place_name} and time to be spent and budget of visiting in 100 words."
        response = openai.Completion.create(
                    engine='text-davinci-003',
                    prompt=prompt,
                    max_tokens=1000
                )
        description_part3 = response.choices[0].text.strip()        
        prompt = f" how to visit {place_name} so that as a tourist i will be satsfied 100 words mention them as point wise manner"
        response = openai.Completion.create(
                    engine='text-davinci-003',
                    prompt=prompt,
                    max_tokens=1000
                )
        description_part4 = response.choices[0].text.strip()        
        image_urls = get_google_image_urls(place_name)        
        return render_template('exploring.html', place=place_name.capitalize(), image_urls=image_urls,description_part1= description_part1, description_part3= description_part3,description_part4= description_part4)
    return render_template('exploring.html')

# Route for Explore page
@app.route('/explore', methods=['GET', 'POST'])
def explore():
    if request.method == 'POST':
        place_name = request.form['place']
        prompt = f"provide me introduction of {place_name} in 100 words"
        response = openai.Completion.create(
                    engine='text-davinci-003',
                    prompt=prompt,
                    max_tokens=500
                )
        description_part1 = response.choices[0].text.strip()        
        prompt = f" {place_name} is famous for 100 words."
        response = openai.Completion.create(
                    engine='text-davinci-003',
                    prompt=prompt,
                    max_tokens=500
                )
        description_part3 = response.choices[0].text.strip()        
        prompt = f"what tourist places are there nearby {place_name} to visit in 100 words"
        response = openai.Completion.create(
                    engine='text-davinci-003',
                    prompt=prompt,
                    max_tokens=500
                )
        description_part2 = response.choices[0].text.strip()        
        image_urls = get_google_image_urls(place_name)        
        return render_template('explore.html', place=place_name.capitalize(), image_urls=image_urls, description_part1= description_part1, description_part2= description_part2, description_part3= description_part3)
    return render_template('explore.html')

#Quick recommend 
@app.route('/quick_recommend', methods=['GET', 'POST'])
def quick_recommend():
    lf = list(df['location'].unique())
    cf = list(df['category'].unique())
    if request.method == 'POST':
        location_data = request.form.getlist('location')  
        categories_data = request.form.getlist('categories') 
        lst = []
        locations_data = {}
        if "All" in location_data:
            location_data = lf
        if "All" in categories_data:
            categories_data = cf
        for location in location_data:
            cluster_number = cluster_data.get(location, -1)
            if cluster_number != -1:
                # Get all places in the same cluster
                location_in_cluster = [place for place, cluster in cluster_data.items() if cluster == cluster_number]
                for i in range(len(locc)):
                    if locc[i] in location_in_cluster and cat[i] in categories_data and placc[i] not in lst:
                        lst.append(placc[i])
                        locations_data[placc[i]] =[img_1[i]]
                        locations_data[placc[i]].append(img_2[i])             
                        locations_data[placc[i]].append(img_3[i])             
                        locations_data[placc[i]].append(locc[i]) 
                        locations_data[placc[i]].append(cat[i]) 
                for i in range(len(pl1)):
                    if pl1[i] in locations_data:
                        locations_data[pl1[i]].append(ds1[i])                   
        return render_template('quick_recommend.html', places=lst, locations_data=locations_data)    
    return render_template('quick_recommend.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error_message = None
    if request.method == 'POST':
        user_name = request.form['user_name']
        password = request.form['password']
        # Check if the user_name and password are in the database
        user_data = User_data.query.filter_by(user_name=user_name).first()
        if user_data:
            if user_data.password == password:
    # Store the preferences in the session
                session['interesting_places'] = user_data.interesting_places
                session['categories'] = user_data.interesting_categories
                session['name']=user_data.name
                interesting_places = session.get('interesting_places')
                per_name = session.get('name')
                print(per_name)
                locations_data=lock()
                return render_template('output.html', per_name=per_name.capitalize(),interesting_places=interesting_places,locations_data=locations_data)          
            else:
                # If the password is incorrect, display an error message
                error_message = "Invalid password. Please try again."
        else:
            # If the user_name is not found in the database, display an error message
            error_message = "User not found. Please register before login."
    return render_template('login.html', error=error_message)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        user_name = request.form['user_name']
        email = request.form['email']
        phone = request.form['phone']
        interesting_places = request.form.getlist('interesting_places')
        interesting_categories = request.form.getlist('interesting_categories')
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        # Check if password and confirm password match
        if password != confirm_password:
            flash("Password and Confirm Password do not match.", "error")
            return redirect(url_for('register'))
        # Check if the email is already registered
        if User_data.query.filter_by(email=email).first():
            flash("Email is already registered. Please Login.", "error")
            return redirect(url_for('login'))
        if User_data.query.filter_by(user_name=user_name).first():
            flash("Username is already registered. Please try with another name.", "error")
            return redirect(url_for('register'))
        # Save the registration data to the database
        user_data = User_data(
            name=name,
            user_name = user_name,
            email=email,
            phone=phone,
            interesting_places=', '.join(interesting_places),
            interesting_categories=', '.join(interesting_categories),
            password=password
        )
        db.session.add(user_data)
        db.session.commit()
        # Redirect to the login page after successful registration
        flash("Registration successful. Please login.", "success")
        return redirect(url_for('login'))       
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

