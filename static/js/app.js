// --- Loading Animation Controller ---
function showLoader() {
    document.getElementById('loader').classList.remove('hidden');
}

// --- Light/Dark Theme Preference Toggle Tracker ---
const themeToggle = document.getElementById('theme-toggle');
if (themeToggle) {
    themeToggle.addEventListener('click', () => {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const targetTheme = currentTheme === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', targetTheme);
        localStorage.setItem('theme', targetTheme);
    });
}

// Set saved theme on load
const savedTheme = localStorage.getItem('theme') || 'light';
document.documentElement.setAttribute('data-theme', savedTheme);

// --- Browser Geolocation Handling Routing Trigger ---
const geoBtn = document.getElementById('geo-btn');
if (geoBtn) {
    geoBtn.addEventListener('click', () => {
        if (navigator.geolocation) {
            showLoader();
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const lat = position.coords.latitude;
                    const lon = position.coords.longitude;
                    window.location.href = `/?lat=${lat}&lon=${lon}`;
                },
                (error) => {
                    alert("Error identifying location: " + error.message);
                    document.getElementById('loader').classList.add('hidden');
                }
            );
        } else {
            alert("Geolocation services are not supported by your browser software setup.");
        }
    });
}

// --- Asynchronous Favorites Add/Removal Handler ---
const favBtn = document.getElementById('fav-toggle-btn');
if (favBtn) {
    favBtn.addEventListener('click', function() {
        const targetCity = this.getAttribute('data-city');
        const formData = new FormData();
        formData.append('city', targetCity);

        fetch('/favorite/toggle', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                if (data.action === 'added') {
                    this.textContent = '⭐ Favorited';
                } else {
                    this.textContent = '☆ Add Favorite';
                }
                // Refresh to update layout items synchronously if desired
                window.location.reload();
            }
        })
        .catch(err => console.error('Error toggling structural state:', err));
    });
}
