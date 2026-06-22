import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from datetime import datetime
from dotenv import load_dotenv

# Initialize and load environment variables from local hidden .env file
load_dotenv()

app = Flask(__name__)

# Dynamically pull secret key setup configuration securely from memory state
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'super_secret_weather_key')

# MySQL Configuration matching your target schemas
# Force-connect directly to your cloud DB strings
# MySQL Configuration matching your target schemas
app.config['MYSQL_HOST'] = 'your-aiven-hostname.aivencloud.com' # <-- Replace with real Aiven Host
app.config['MYSQL_USER'] = 'avnadmin'                           # <-- Replace with real Aiven User
app.config['MYSQL_PASSWORD'] = 'your_aiven_password_here'       # <-- Replace with real Aiven Password
app.config['MYSQL_DB'] = 'defaultdb'                            # <-- Replace with real Aiven DB Name
app.config['MYSQL_PORT'] = 25061
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'                  # Helps Flask read table columns safely
app.config['MYSQL_CUSTOM_OPTIONS'] = {"ssl": {"ssl-mode": "REQUIRED"}}

mysql = MySQL(app)

# Dynamically assigned OpenWeather token variable
API_KEY = os.getenv('OPENWEATHER_API_KEY', 'YOUR_OPENWEATHERMAP_API_KEY')

# --- HELPER FUNCTIONS FOR WEATHER API ---
def get_weather_data(lat=None, lon=None, city=None):
    """Fetches comprehensive weather, forecast, and AQI details."""
    try:
        # 1. Resolve coordinates if city name is passed
        if city:
            geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={API_KEY}"
            geo_res = requests.get(geo_url).json()
            if not geo_res: return None
            lat, lon = geo_res[0]['lat'], geo_res[0]['lon']
            display_name = geo_res[0]['name']
        else:
            display_name = f"Coords: {lat}, {lon}"

        # 2. Current Weather
        weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        w_data = requests.get(weather_url).json()
        if city: w_data['name'] = display_name

        # 3. 5-Day Forecast
        forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        f_data = requests.get(forecast_url).json()

        # Filter forecast for 1 entry per day (around noon)
        daily_forecast = []
        for item in f_data.get('list', []):
            if "12:00:00" in item['dt_txt']:
                dt = datetime.strptime(item['dt_txt'], '%Y-%m-%d %H:%M:%S')
                item['day_name'] = dt.strftime('%A')
                daily_forecast.append(item)

        # 4. Air Quality Index (AQI)
        aqi_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
        aqi_data = requests.get(aqi_url).json()
        aqi_val = aqi_data['list'][0]['main']['aqi'] if 'list' in aqi_data else "N/A"

        # Time conversions
        sunrise = datetime.fromtimestamp(w_data['sys']['sunrise']).strftime('%I:%M %p')
        sunset = datetime.fromtimestamp(w_data['sys']['sunset']).strftime('%I:%M %p')

        return {
            'current': w_data,
            'forecast': daily_forecast[:5],
            'aqi': aqi_val,
            'sunrise': sunrise,
            'sunset': sunset
        }
    except Exception as e:
        print(f"API Error: {e}")
        return None

# --- AUTHENTICATION ROUTES ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_pw = generate_password_hash(password)

        cur = mysql.connection.cursor()
        try:
            cur.execute("INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)", (username, email, hashed_pw))
            mysql.connection.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception:
            flash('Username or Email already exists.', 'danger')
        finally:
            cur.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", [email])
        user = cur.fetchone()
        cur.close()

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash(f"Welcome back, {user['username']}!", 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# --- CORE WEATHER ROUTES ---
@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    weather_data = None
    city = request.args.get('city')
    lat = request.args.get('lat')
    lon = request.args.get('lon')

    cur = mysql.connection.cursor()

    if city:
        weather_data = get_weather_data(city=city)
        if weather_data:
            # Save Search History
            cur.execute("INSERT INTO search_history (user_id, city_name) VALUES (%s, %s)", (session['user_id'], city))
            mysql.connection.commit()
        else:
            flash('City not found!', 'danger')
    elif lat and lon:
        weather_data = get_weather_data(lat=lat, lon=lon)
        if not weather_data:
            flash('Could not fetch data for your current location.', 'danger')

    # Fetch User data for Dashboard Sidebar
    cur.execute("SELECT city_name FROM search_history WHERE user_id = %s ORDER BY searched_at DESC LIMIT 5", [session['user_id']])
    history = cur.fetchall()

    cur.execute("SELECT city_name FROM favorites WHERE user_id = %s", [session['user_id']])
    favorites = cur.fetchall()
    cur.close()

    # Check if currently viewed city is inside user favorites
    is_fav = False
    if weather_data and any(f['city_name'].lower() == weather_data['current']['name'].lower() for f in favorites):
        is_fav = True

    return render_template('index.html', weather=weather_data, history=history, favorites=favorites, is_fav=is_fav)

# --- USER FAVORITES & HISTORY ENDPOINTS ---
@app.route('/favorite/toggle', methods=['POST'])
def toggle_favorite():
    if 'user_id' not in session: return jsonify({'status': 'unauthorized'}), 401
    
    city = request.form.get('city')
    cur = mysql.connection.cursor()
    
    cur.execute("SELECT id FROM favorites WHERE user_id = %s AND city_name = %s", (session['user_id'], city))
    fav = cur.fetchone()

    if fav:
        cur.execute("DELETE FROM favorites WHERE id = %s", [fav['id']])
        action = 'removed'
    else:
        cur.execute("INSERT INTO favorites (user_id, city_name) VALUES (%s, %s)", (session['user_id'], city))
        action = 'added'

    mysql.connection.commit()
    cur.close()
    return jsonify({'status': 'success', 'action': action})

@app.route('/favorites')
def favorites_page():
    if 'user_id' not in session: return redirect(url_for('login'))
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT city_name FROM favorites WHERE user_id = %s", [session['user_id']])
    fav_cities = cur.fetchall()
    cur.close()

    fav_data = []
    for fav in fav_cities:
        w = get_weather_data(city=fav['city_name'])
        if w:
            fav_data.append({
                'name': fav['city_name'],
                'temp': w['current']['main']['temp'],
                'desc': w['current']['weather'][0]['description'],
                'icon': w['current']['weather'][0]['icon']
            })
    return render_template('favorites.html', favorites=fav_data)

@app.route('/history/clear', methods=['POST'])
def clear_history():
    if 'user_id' not in session: return redirect(url_for('login'))
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM search_history WHERE user_id = %s", [session['user_id']])
    mysql.connection.commit()
    cur.close()
    flash('Search history cleared.', 'info')
    return redirect(url_for('index'))

@app.route('/testdb')
def test_db():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT 1")
        cur.close()
        return "🎉 Database connected successfully!"
    except Exception as e:
        return f"❌ Database connection failed! Error: {str(e)}"

# --- SERVER STARTUP CONTROLS ---
if __name__ == '__main__':
    # Automatically verify localized database state on local startup console log
    with app.app_context():
        try:
            test_cursor = mysql.connection.cursor()
            test_cursor.execute("SELECT 1")
            test_cursor.close()
            print("\n>>> 👍 BACKEND LOGLINK: DATABASE RUNNING SUCCESSFULLY! <<<\n")
        except Exception as db_err:
            print(f"\n>>> 🛑 BACKEND LOGLINK: ERROR STARTING UP SQL SUITE: {db_err} <<<\n")

    app.run(debug=True)
