# 🚀 Quick Setup & Run Guide

## For Windows Users

### Step 1: Open Command Prompt or PowerShell
```powershell
# Navigate to project folder
cd C:\CDK-T
```

### Step 2: Create Virtual Environment
```powershell
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Generate Model
```powershell
python create_model.py
```

Output should show:
```
============================================================
 CKD PREDICTION MODEL GENERATOR
============================================================

[1] Creating sample model...
✓ Model trained on 400 samples
✓ Model accuracy on training data: 85%
✓ Features: 24

[2] Saving model...
✓ Model saved to: app/model.pkl

[3] Loading and testing model...
✓ Model loaded from: app/model.pkl
✓ Test prediction: No CKD (0)
✓ Prediction probabilities: No CKD=65.00%, CKD=35.00%

============================================================
 ✓ Setup complete! Model is ready for use.
============================================================
```

### Step 5: Run Flask Application
```powershell
cd app
python app.py
```

Output should show:
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

### Step 6: Open Browser
Navigate to: **http://localhost:5000**

---

## For macOS/Linux Users

### Step 1: Open Terminal
```bash
cd ~/CDK-T
```

### Step 2: Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Generate Model
```bash
python create_model.py
```

### Step 5: Run Flask Application
```bash
cd app
python app.py
```

### Step 6: Open Browser
Open: http://localhost:5000

---

## 📝 Application Login Credentials (For Testing)

Since this is a fresh database, create your own account:

1. Click "Sign up here" on the login page
2. Fill in:
   - Full Name: e.g., "John Doe"
   - Email: e.g., "john@example.com"
   - Password: e.g., "password123" (min 6 characters)
   - Confirm Password: Match the password
3. Click "Create Account"
4. You'll be automatically logged in to dashboard

---

## 🧪 Test the Prediction System

### Sample Patient Data (For Testing)

**Patient 1: Low Risk Profile**
```
Blood Pressure: 120
Specific Gravity: 1.020
Albumin: 0
Sugar: 0
RBC: Normal
Pus Cell: Normal
Pus Cell Clumps: Not Present
Bacteria: Not Present
Blood Glucose Random: 110
Blood Urea: 35
Serum Creatinine: 0.9
Sodium: 140
Potassium: 4.5
Hemoglobin: 14.0
Packed Cell Volume: 42
White Blood Cell Count: 6
Red Blood Cell Count: 5
Hypertension: No
Diabetes Mellitus: No
Coronary Artery Disease: No
Appetite: Good
Pedal Edema: No
Anemia: No
```

**Patient 2: High Risk Profile**
```
Blood Pressure: 160
Specific Gravity: 1.010
Albumin: 2
Sugar: 2
RBC: Abnormal
Pus Cell: Abnormal
Pus Cell Clumps: Present
Bacteria: Present
Blood Glucose Random: 180
Blood Urea: 70
Serum Creatinine: 2.8
Sodium: 135
Potassium: 6.2
Hemoglobin: 10
Packed Cell Volume: 30
White Blood Cell Count: 12
Red Blood Cell Count: 3.5
Hypertension: Yes
Diabetes Mellitus: Yes
Coronary Artery Disease: Yes
Appetite: Poor
Pedal Edema: Yes
Anemia: Yes
```

---

## 🛑 Stopping the Application

Press `Ctrl+C` in the terminal/command prompt where Flask is running:

```
^C
```

---

## 🔄 If Something Goes Wrong

### 1. Model file exists?
```bash
# Windows
dir app\model.pkl

# macOS/Linux
ls -la app/model.pkl
```

### 2. Virtual environment activated?
Look for `(venv)` prefix in your terminal prompt

### 3. All dependencies installed?
```bash
pip list
```
Should show: Flask, pandas, numpy, scikit-learn, SQLAlchemy

### 4. Port 5000 already in use?
```bash
# Use different port
python app.py --port 5001
# Then visit: http://localhost:5001
```

### 5. Database corrupted?
```bash
# Delete old database
rm app/ckd_users.db  # macOS/Linux
del app\ckd_users.db  # Windows

# Restart Flask (will auto-create new database)
python app.py
```

---

## 📊 Exploring the Database

### View Users
```python
from app import app, db, User
with app.app_context():
    users = User.query.all()
    for user in users:
        print(f"User: {user.email}, Name: {user.name}")
```

### View Predictions
```python
from app import app, db, PredictionHistory
with app.app_context():
    predictions = PredictionHistory.query.all()
    for pred in predictions:
        print(f"Risk: {pred.risk_level}, Confidence: {pred.confidence}%")
```

---

## 🔧 Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'flask'` | Run: `pip install -r requirements.txt` |
| `Address already in use` | Port 5000 busy; use `--port 5001` |
| `FileNotFoundError: model.pkl` | Run: `python create_model.py` |
| `Database is locked` | Delete `app/ckd_users.db` and restart |
| `No virtual environment` | Run: `python -m venv venv` then activate |

---

## 📱 Access from Other Devices

To access the app from other computers on your network:

1. Find your computer's IP address:
   ```bash
   # Windows
   ipconfig

   # macOS/Linux
   ifconfig | grep inet
   ```

2. Run Flask with:
   ```bash
   python app.py --host 0.0.0.0
   ```

3. From another device, visit:
   ```
   http://<your-ip>:5000
   ```

---

## 🎓 Learning Points

### Key Technologies Used:
- **Flask**: Web framework
- **SQLAlchemy**: Database ORM
- **scikit-learn**: ML models
- **pandas**: Data manipulation
- **SQLite**: Database

### Code Structure:
- `/app/app.py`: Main Flask application
- `/app/templates/`: HTML templates
- `/app/static/`: CSS and JavaScript
- `create_model.py`: Model generation script

### Feature Implementation:
- User authentication with sessions
- Database relationships
- ML model integration
- Form validation
- AJAX API calls
- Responsive CSS grid layouts

---

## 📞 Next Steps

1. ✅ Application is running successfully
2. ⏭️ Create a user account
3. ⏭️ Try the prediction form
4. ⏭️ View prediction history
5. ⏭️ Integrate your actual CKD model
6. ⏭️ Deploy to production

---

## 🎯 Customization Ideas

- Add age field to predictions
- Implement email verification
- Add password reset functionality
- Create admin dashboard
- Export predictions as PDF
- Add data visualization charts
- Implement SMS alerts
- Add multi-language support
- Integrate with medical records API
- Deploy to cloud (Heroku, AWS, Google Cloud)

---

**Happy Learning! 🎉**
