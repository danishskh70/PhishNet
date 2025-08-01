# 🛡️ PhishNet – Ethical Phishing Campaign Simulator

PhishNet is a phishing awareness and credential logging simulation project designed for ethical hacking education and awareness.

## 🔧 Features
- Fake login page (Gmail-style)
- Awareness page
- Admin dashboard to monitor victims
- IP Geolocation lookup
- CSV logging
- Chart analytics

## 🚀 How to Run

1. Clone the repo  
2. Install dependencies:  
   `pip install -r requirements.txt`  
3. Run the Flask server:  
   `python app.py`

## 📁 Folder Structure

<pre> ```txt PhishNet/ ├── static/ # Static files (CSS, JS, icons) │ └── style.css # Custom stylesheet for phishing pages │ ├── templates/ # HTML templates rendered by Flask │ ├── index.html # Fake login page (Gmail/Google) │ ├── awareness.html # Cybersecurity awareness page │ └── admin.html # Admin dashboard with logs/charts │ ├── credentials.csv # Logged credential data (email, password, timestamp, IP) ├── app.py # Main Flask server handling phishing, logging, API, and dashboard ├── requirements.txt # Python dependencies ├── README.md # Project overview and instructions ├── .gitignore # Git ignored files └── LICENSE # Open-source license file ``` </pre>



> ⚠️ For ethical educational use only. Do not deploy publicly without permission.
