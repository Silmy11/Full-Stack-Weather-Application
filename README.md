# SkyCast 🌤️
### A full-stack weather dashboard with user authentication, live forecasts, and city favorites.

**Live Demo → [https://full-stack-weather-application-2.onrender.com](https://full-stack-weather-application-2.onrender.com)**

---

## Features

- **User Authentication** — register, login, logout with bcrypt password hashing
- **Live Weather Search** — current conditions, temperature, humidity, wind speed
- **5-Day Forecast** — daily weather breakdown with weather icons
- **Air Quality Index (AQI)** — real-time pollution data
- **Geolocation** — one-click weather for your current location
- **Favorites** — save and revisit cities instantly
- **Search History** — last 5 searches per user
- **Dark / Light Theme** — toggle with preference saved in browser
- **Sunrise & Sunset Times** — per searched city

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| Database | MySQL (Aiven Cloud) |
| DB Driver | PyMySQL (pure Python) |
| Frontend | HTML5, CSS3, Vanilla JS |
| Weather API | OpenWeatherMap |
| Deployment | Render |
| Auth | Werkzeug password hashing, Flask sessions |

---

## Project Structure

```
SkyCast/
├── app.py               # Flask app, routes, DB logic
├── requirements.txt     # Python dependencies
├── Procfile             # Render deployment config
├── schema.sql           # Database schema
├── .env.example         # Environment variable template
├── templates/
│   ├── base.html        # Base layout with navbar
│   ├── index.html       # Main weather dashboard
│   ├── login.html       # Login page
│   ├── register.html    # Register page
│   └── favorites.html   # Saved cities page
└── static/
    ├── css/style.css    # Styles + dark/light theme
    └── js/app.js        # Theme toggle, geolocation, favorites
```

---

## Getting Started Locally

### 1. Clone the repo
```bash
git clone https://github.com/Silmy11/Full-Stack-Weather-Application.git
cd Full-Stack-Weather-Application
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up environment variables
```bash
cp .env.example .env
```
Fill in your values in `.env` (see below).

### 4. Set up the database
Run `schema.sql` on your MySQL instance:
```bash
mysql -u root -p < schema.sql
```

### 5. Run the app
```bash
python app.py
```
Visit `http://localhost:5000`

---

## Environment Variables

Create a `.env` file in the root:

```
FLASK_SECRET_KEY=your-secret-key-here
OPENWEATHER_API_KEY=your-openweathermap-key
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your-db-password
DB_NAME=weather_db
DB_PORT=3306
```

Get your free OpenWeatherMap API key at [openweathermap.org/api](https://openweathermap.org/api)

---

## Deployment

Deployed on **Render** with **Aiven** as the managed MySQL cloud database.

- `Procfile` → `web: gunicorn app:app`
- All environment variables set via Render dashboard
- Aiven IP filter set to `0.0.0.0/0` for Render access

---

## Database Schema

```sql
users           → id, username, email, password_hash, created_at
search_history  → id, user_id, city_name, searched_at
favorites       → id, user_id, city_name (unique per user)
```

Full schema in [`schema.sql`](./schema.sql)

---

## API Reference

Uses [OpenWeatherMap](https://openweathermap.org/api) APIs:
- **Geocoding API** — city name → coordinates
- **Current Weather API** — live conditions
- **5-Day Forecast API** — daily forecast data
- **Air Pollution API** — AQI data

---

## Author

**Silmy Nosheen**
- GitHub: [@Silmy11](https://github.com/Silmy11)
- LinkedIn: [linkedin.com/in/silmy-nosheen-1a87a9306](https://linkedin.com/in/silmy-nosheen-1a87a9306)
