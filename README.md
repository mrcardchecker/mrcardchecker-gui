# MrCardChecker GUI – Premium Credit Card Validator & BIN Tool Suite

MrCardChecker is a professional, dark‑themed GUI application built with **PyQt5** for Kali Linux and other Debian‑based systems. It combines a powerful set of tools for validating credit card numbers, checking BIN/IIN details, and generating test card numbers – all within a sleek, responsive interface.

> ⚠️ **Note:** This tool is intended for educational and testing purposes only. Use it exclusively on cards you own or have explicit permission to validate.

---

## ✨ Features

| Feature | Description |
| :--- | :--- |
| **CCN Gate 1 (Free)** | Local Luhn validation + expiry check + 15% live simulation. No internet required. |
| **CCN3 Gate Premium** | Requires login; uses your existing user database and API. Shows live/declined status with balance ($1–$5). Plans: Silver (30% live), Gold (60%), Lifetime VIP (90%). |
| **BIN Checker** | Enter the first 6 digits and instantly get brand, card type (Credit/Debit), and level (Classic, Gold, Platinum, Infinite). |
| **BIN Generator** | Generate any number of valid test cards (with Luhn checksum) from a given BIN. Output format: `NUMBER\|MM\|YY\|CVV`. |
| **Background Threading** | All heavy tasks run in separate threads – the GUI never freezes. You can start/stop at any time. |
| **Premium UI** | Dark theme, gradient headers, clickable links, progress bars, and dedicated Clear Log / Clear Cards buttons. |
| **Kali Integration** | `.desktop` file included – easily add to the Kali application menu under Penetration Testing. |

---

## 🖥️ Screenshots

*(Placeholder – replace with actual screenshots once you run the app.)*

* **Main Interface:** ![Main Dashboard](https://screenshots/main.png)
* **Premium Dashboard:** ![Premium Gate](https://screenshots/premium.png)

---

## 📦 Requirements

| Package | Minimum Version |
| :--- | :--- |
| **Python 3** | ≥ 3.8 |
| **PyQt5** | ≥ 5.15 |
| **Requests** | ≥ 2.25 |

*All other modules (`sys`, `re`, `random`, `datetime`) are built into Python.*

---

## 🔧 Installation (Kali Linux)

### 1. Clone the Repository
```bash
git clone [https://github.com/your-username/mrcardchecker-gui.git](https://github.com/mrcardchecker/mrcardchecker-gui.git)
cd mrcardchecker-gui
sudo apt update
sudo apt install python3-pyqt5 python3-requests
pip3 install -r requirements.txt
chmod +x main.py
sudo cp mrcardchecker.desktop /usr/share/applications/
sudo update-desktop-database
🚀 How to Run
From the project directory:

Bash
python3 main.py
Or, if you installed the .desktop file, simply click the menu icon from your desktop environment.
🧠 How It Works
Free Checker: Runs entirely on your machine. It parses each card, checks expiry and Luhn, then simulates a 15% live chance.

Premium Checker: Sends the card data (via a secure session) to your own API endpoint (api_python.php). The server checks the user’s plan, applies the appropriate live rate, and returns the result. Balances are capped at $5.00 and are only shown to logged‑in users.

BIN Checker: Uses a local lookup table to identify the brand and generates a random card type/level.

BIN Generator: Creates valid test cards using the Luhn algorithm.

All processing is done in background threads, so the interface stays responsive. You can stop the process at any time using the Stop button.

🛠️ Customisation
Change the live rate: Modify $live_chance in api_python.php.

Adjust the balance range: Edit the rand(100,500) values in api_python.php.

Alter the delay between cards: Change the 2000 (milliseconds) in gui/worker.py.

📁 Project Structure
Plaintext
mrcardchecker-gui/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── mrcardchecker.desktop   # .desktop file for Kali integration
├── core/
│   ├── __init__.py
│   └── checker.py          # Luhn, brand, validation, generator logic
├── gui/
│   ├── __init__.py
│   ├── main_window.py      # Main GUI window with tabs
│   ├── login_dialog.py     # Login dialog for premium access
│   ├── worker.py           # QThread worker for background processing
│   └── resources/
│       ├── style.qss       # Dark theme stylesheet
│       └── icon.png        # Application icon
└── README.md
🔐 API Endpoints Used
Login: https://mrcardchecker.live/user/api_login.php

Premium Checker: https://api.ghakr.com/api_python.php

Make sure these endpoints are deployed and correctly configured on your servers.

🐞 Troubleshooting
"Unknown property transition" warnings: These are harmless QSS warnings from PyQt; you can safely ignore them.

Login fails: Check that your api_login.php is reachable and returns a valid JSON response.

GUI doesn't start: Ensure all system dependencies are installed correctly (pip3 install -r requirements.txt).

📜 License
This project is open‑source and provided as‑is for educational purposes. You are free to modify and distribute it, but please do not use it for illegal activities.

🙏 Credits
Built with ❤️ using PyQt5 and Python 3.

Icons provided by Icons8.
