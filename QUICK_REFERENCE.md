# ⚡ Quick Reference Card

## 🚀 Quick Start (5 Minutes)

```bash
# 1. Navigate to project
cd CDK-T

# 2. Create virtual environment
python -m venv venv

# 3. Activate (Windows)
venv\Scripts\activate

# 4. Activate (Mac/Linux)
source venv/bin/activate

# 5. Install packages
pip install -r requirements.txt

# 6. Generate model
python create_model.py

# 7. Start app
cd app && python app.py

# 8. Open browser
Visit: http://localhost:5000
```

---

## 📋 Form Fields (23 Parameters)

### Section 1: Vital Signs (1)
| Field | Type | Example |
|-------|------|---------|
| bp | Number | 120 |

### Section 2: Urine Test (7)
| Field | Type | Example |
|-------|------|---------|
| sg | Decimal | 1.020 |
| al | Dropdown | 0 |
| su | Dropdown | 0 |
| rbc | Dropdown | normal |
| pc | Dropdown | normal |
| pcc | Dropdown | notpresent |
| ba | Dropdown | notpresent |

### Section 3: Blood Test (5)
| Field | Type | Example |
|-------|------|---------|
| bgr | Number | 110 |
| bu | Number | 35 |
| sc | Number | 0.9 |
| sod | Number | 140 |
| pot | Number | 4.5 |

### Section 4: Blood Cell Analysis (4)
| Field | Type | Example |
|-------|------|---------|
| hemo | Number | 14.0 |
| pcv | Number | 42 |
| wc | Number | 6 |
| rc | Number | 5 |

### Section 5: Medical History (6)
| Field | Type | Example |
|-------|------|---------|
| htn | Yes/No | no |
| dm | Yes/No | no |
| cad | Yes/No | no |
| appet | Dropdown | good |
| pe | Yes/No | no |
| ane | Yes/No | no |

---

## 🔧 Environment Variables

```python
# In app.py
DEBUG = True/False              # Enable/disable debug mode
SECRET_KEY = "change-me"        # Change in production
DATABASE_URI = "sqlite://..."   # SQLite by default
PERMANENT_LIFETIME = 604800     # 7 days session timeout
HOST = "0.0.0.0"                # Listen on all IPs
PORT = 5000                     # Flask port
```

---

## 🛣️ URL Routes

| Route | Method | Auth? | Purpose |
|-------|--------|-------|---------|
| `/` | GET | No | Splash page |
| `/signup` | GET/POST | No | User registration |
| `/login` | GET/POST | No | User login |
| `/dashboard` | GET | Yes | Main dashboard |
| `/predict-page` | GET | Yes | Prediction form |
| `/api/predict` | POST | Yes | Prediction API |
| `/prediction-history` | GET | Yes | View history |
| `/prediction/<id>` | GET | Yes | Prediction detail |
| `/logout` | GET | Yes | Logout |

---

## 📊 API Quick Test

### Using cURL
```bash
# Login
curl -X POST http://localhost:5000/login \
  -d "email=user@example.com&password=pass123" \
  -c cookies.txt

# Make prediction
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "bp": 120, "sg": 1.020, "al": 0, "su": 0,
    "rbc": "normal", "pc": "normal", "pcc": "notpresent",
    "ba": "notpresent", "bgr": 110, "bu": 35, "sc": 0.9,
    "sod": 140, "pot": 4.5, "hemo": 14.0, "pcv": 42,
    "wc": 6, "rc": 5, "htn": "no", "dm": "no",
    "cad": "no", "appet": "good", "pe": "no", "ane": "no"
  }'
```

### Using Python
```python
import requests

session = requests.Session()

# Signup
session.post('http://localhost:5000/signup', data={
    'name': 'User Name',
    'email': 'user@example.com',
    'password': 'password123',
    'confirm_password': 'password123'
})

# Predict
response = session.post('http://localhost:5000/api/predict', json={
    'bp': 120, 'sg': 1.020, 'al': 0, 'su': 0,
    'rbc': 'normal', 'pc': 'normal', 'pcc': 'notpresent',
    'ba': 'notpresent', 'bgr': 110, 'bu': 35, 'sc': 0.9,
    'sod': 140, 'pot': 4.5, 'hemo': 14.0, 'pcv': 42,
    'wc': 6, 'rc': 5, 'htn': 'no', 'dm': 'no',
    'cad': 'no', 'appet': 'good', 'pe': 'no', 'ane': 'no'
})

print(response.json())
```

---

## 🗄️ Database Queries

### View All Users
```python
from app import app, db, User

with app.app_context():
    users = User.query.all()
    for user in users:
        print(f"{user.email}: {user.name}")
```

### View All Predictions
```python
from app import app, db, PredictionHistory

with app.app_context():
    predictions = PredictionHistory.query.all()
    for pred in predictions:
        print(f"Risk: {pred.risk_level}, Confidence: {pred.confidence}%")
```

### Delete All Data
```python
from app import app, db, User, PredictionHistory

with app.app_context():
    # Delete all
    db.session.query(PredictionHistory).delete()
    db.session.query(User).delete()
    db.session.commit()
```

---

## 🎨 CSS Color Reference

```css
/* Primary Colors */
$primary: #667eea          /* Purple-Blue */
$secondary: #764ba2        /* Dark Purple */
$success: #28a745          /* Green */
$danger: #dc3545           /* Red */
$warning: #fd7e14          /* Orange */
$light: #f5f7fa            /* Light Gray */

/* Gradients */
--gradient-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
--gradient-danger: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
```

---

## 🔐 Security Checklist

- [ ] Change `SECRET_KEY` in production
- [ ] Set `DEBUG = False` in production
- [ ] Use HTTPS/SSL certificate
- [ ] Use PostgreSQL instead of SQLite
- [ ] Add CSRF protection
- [ ] Implement rate limiting
- [ ] Add 2FA if needed
- [ ] Regular security audits

---

## 📱 Responsive Breakpoints

```css
/* Mobile: 320px - 767px */
/* Tablet: 768px - 1199px */
/* Desktop: 1200px+ */

@media (max-width: 768px) {
    /* Mobile specific styles */
}

@media (min-width: 1200px) {
    /* Desktop specific styles */
}
```

---

## 🐛 Common Errors & Fixes

| Error | Fix |
|-------|-----|
| `ModuleNotFoundError: Flask` | `pip install -r requirements.txt` |
| `Port 5000 already in use` | `python app.py --port 5001` |
| `FileNotFoundError: model.pkl` | `python create_model.py` |
| `Database locked` | Delete `app/ckd_users.db` |
| `(venv) not in terminal` | Activate: `venv\Scripts\activate` |
| Import errors | Reinstall: `pip install --upgrade -r requirements.txt` |

---

## 📊 File Sizes

| File | Size | Type |
|------|------|------|
| app.py | ~27 KB | Python |
| predict.html | ~12 KB | HTML |
| predict.css | ~10 KB | CSS |
| create_model.py | ~5 KB | Python |
| dashboard.css | ~6 KB | CSS |
| predict.js | ~5 KB | JavaScript |
| **Total** | **~200 KB** | **All** |

---

## ⏱️ Performance Benchmarks

| Operation | Expected Time |
|-----------|---|
| Page load | < 1s |
| Form submit | 2-5s |
| Prediction API | < 3s |
| Database query | < 100ms |
| Model prediction | < 1s |

---

## 🔄 Development Workflow

### 1. Setup
```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate
pip install -r requirements.txt
python create_model.py
```

### 2. Development
```bash
cd app
python app.py
# Edit files while running (auto-reload in debug mode)
```

### 3. Testing
```bash
# In separate terminal
python -c "from app import app, db; app.app_context().push()"
# Or use curl/Postman
```

### 4. Deployment
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## 📚 Documentation Index

| File | Purpose | Read Time |
|------|---------|-----------|
| README.md | Overview & features | 10 min |
| SETUP_GUIDE.md | Installation | 5 min |
| INSTALLATION_CHECKLIST.md | Verification | 15 min |
| API_DOCUMENTATION.md | API reference | 15 min |
| PROJECT_SUMMARY.md | Project overview | 20 min |
| FILE_MANIFEST.md | File inventory | 10 min |

**Total**: ~75 minutes of reference material

---

## 🎯 Quick Tips

1. **Debug Mode**: Add `print()` statements, they'll show in console
2. **Hot Reload**: Flask auto-reloads Python files in debug mode
3. **Database**: Delete `.db` file to reset with fresh schema
4. **Models**: Replace `model.pkl` to use different ML model
5. **Styling**: Edit CSS directly, refresh browser to see changes
6. **Forms**: Update `predict.html` to add/remove fields
7. **Routes**: Add new routes in `app.py`, restart server
8. **Database**: Use `db.create_all()` to recreate schema

---

## 🚀 Production Deployment

### Heroku
```bash
echo "web: gunicorn app:app" > Procfile
git init
git add .
git commit -m "Initial commit"
heroku create app-name
git push heroku main
```

### AWS/DigitalOcean
```bash
# Install Gunicorn
pip install gunicorn

# Run on port 80 (requires sudo)
sudo gunicorn -w 4 -b 0.0.0.0:80 app:app

# Use systemd for auto-start (Linux)
# Copy app to /opt/ckd/
# Create service file and enable
```

---

## 💡 Customization Examples

### Change Primary Color
```css
/* In all CSS files, replace: */
#667eea → YOUR_COLOR
#764ba2 → YOUR_ACCENT_COLOR
```

### Add New Health Parameter
1. Add `<input>` in `predict.html`
2. Add mapping in `app.py` `prepare_prediction_data()`
3. Retrain model with new feature
4. Update `model.pkl`

### Modify Recommendations
```python
# In app.py, update get_risk_recommendation():
if risk_level.lower() == 'high risk':
    return {...}  # Edit return dict
```

---

## 🧠 Learning Resources

- **Flask**: https://flask.palletsprojects.com/
- **SQLAlchemy**: https://docs.sqlalchemy.org/
- **scikit-learn**: https://scikit-learn.org/
- **CKD Info**: https://www.kidney.org/
- **Medical**: https://medlineplus.gov

---

## 📞 Quick Support

**Issue**: Model not found  
**Solution**: `python create_model.py`

**Issue**: Port busy  
**Solution**: `python app.py --port 5001`

**Issue**: Dependencies missing  
**Solution**: `pip install -r requirements.txt`

**Issue**: Database error  
**Solution**: Delete `app/ckd_users.db`

---

## ✅ Pre-Launch Checklist

- [ ] `python -r requirements.txt` done
- [ ] `python create_model.py` done
- [ ] `model.pkl` file exists
- [ ] App starts without errors
- [ ] Splash page visible
- [ ] Can create account
- [ ] Can login
- [ ] Can fill prediction form
- [ ] Can get results
- [ ] Can view history
- [ ] All links work

---

## 🎓 Code Examples

### Query Predictions for User
```python
user = User.query.filter_by(email='user@example.com').first()
predictions = user.predictions  # All predictions for user
```

### Save Prediction
```python
pred = PredictionHistory(
    user_id=session['user_id'],
    bp=120, sg=1.020, al=0, # ... other fields
    prediction_result=0,
    risk_level='Low Risk',
    confidence=85.5
)
db.session.add(pred)
db.session.commit()
```

### Get Model Prediction
```python
import pickle
import pandas as pd

model = pickle.load(open('model.pkl', 'rb'))
data = pd.DataFrame([features_dict])
prediction = model.predict(data)[0]
confidence = model.predict_proba(data)[0]
```

---

**This quick reference has everything you need!** ⚡

For detailed info, check the full documentation files.

**Happy Coding!** 🚀
