# ✅ Installation & Deployment Checklist

## Pre-Installation Requirements

### System Requirements
- [ ] Python 3.7+ installed
- [ ] pip package manager installed
- [ ] Internet connection for downloading packages
- [ ] 50MB+ free disk space
- [ ] Admin/user permissions to install software

### Verification
```bash
# Verify Python installation
python --version
pip --version
```

---

## 🔧 Installation Checklist

### Step 1: Download Project Files
- [ ] Project files downloaded to `C:\CDK-T\` (Windows) or `~/CDK-T` (Mac/Linux)
- [ ] All files and folders present:
  - [ ] `/app/` folder
  - [ ] `/app/templates/` folder with 8 HTML files
  - [ ] `/app/static/` folder with CSS, JS, and images
  - [ ] `create_model.py` script
  - [ ] `requirements.txt` file
  - [ ] `README.md` documentation
  - [ ] `SETUP_GUIDE.md` guide
  - [ ] `API_DOCUMENTATION.md` documentation

### Step 2: Virtual Environment Setup
- [ ] Virtual environment created in project directory
- [ ] Command used:
  ```bash
  python -m venv venv
  ```
- [ ] Virtual environment activated:
  ```bash
  # Windows
  venv\Scripts\activate
  
  # Mac/Linux
  source venv/bin/activate
  ```
- [ ] Terminal shows `(venv)` prefix

### Step 3: Install Dependencies
- [ ] All packages installed successfully
  ```bash
  pip install -r requirements.txt
  ```
- [ ] Verify installation:
  ```bash
  pip list
  ```
- [ ] Check for these packages:
  - [ ] Flask (2.3.3+)
  - [ ] Flask-SQLAlchemy (3.0.5+)
  - [ ] pandas (2.0.3+)
  - [ ] numpy (1.24.3+)
  - [ ] scikit-learn (1.3.0+)

### Step 4: Generate ML Model
- [ ] Model generation script executed:
  ```bash
  python create_model.py
  ```
- [ ] Output shows success message:
  - [ ] "Model trained on 400 samples"
  - [ ] "Model accuracy: XX%"
  - [ ] "Model saved to: app/model.pkl"
  - [ ] "Setup complete! Model is ready for use."
- [ ] `app/model.pkl` file created (size ~2-5MB)

### Step 5: Verify Setup
- [ ] Navigate to app directory:
  ```bash
  cd app
  ```
- [ ] Check for all required files:
  - [ ] `app.py` exists and is readable
  - [ ] `model.pkl` exists
  - [ ] `templates/` folder with all HTML files
  - [ ] `static/css/` folder with all CSS files
  - [ ] `static/js/` folder with all JS files

---

## 🚀 Running the Application

### Start Flask Server
- [ ] Navigate to app directory: `cd app`
- [ ] Run Flask application:
  ```bash
  python app.py
  ```
- [ ] Verify startup:
  - [ ] No errors in console
  - [ ] Output shows "Running on http://127.0.0.1:5000"
  - [ ] Output shows "Debug mode: on"
  - [ ] Output shows "Debugger is active!"

### Access Application
- [ ] Open web browser
- [ ] Navigate to: `http://localhost:5000`
- [ ] Verify splash page appears:
  - [ ] Medical logo visible
  - [ ] "CKD Prediction" title visible
  - [ ] Loading spinner animated
  - [ ] Auto-redirects to login page after 2-3 seconds

---

## 👤 User Authentication Testing

### Test Signup
- [ ] Click "Sign up here" link
- [ ] Fill signup form with valid data:
  - Full Name: "Test User"
  - Email: "test@example.com"
  - Password: "TestPass123"
  - Confirm Password: "TestPass123"
- [ ] Click "Create Account"
- [ ] Account created successfully
- [ ] Automatically logged in
- [ ] Redirected to dashboard

### Test Login/Logout
- [ ] Click logout button
- [ ] Session cleared
- [ ] Redirected to splash page
- [ ] Login with created credentials
- [ ] Successfully logged in
- [ ] Dashboard displayed

---

## 🏥 Application Features Testing

### Dashboard
- [ ] [ ] Dashboard loads successfully
- [ ] [ ] Welcome message displays user name
- [ ] [ ] All action cards visible:
  - [ ] Health Prediction card
  - [ ] Prediction History card
  - [ ] CKD Information card
- [ ] [ ] Recent predictions section (if any)
- [ ] [ ] Logout button functional

### Prediction Form
- [ ] Click "Start Prediction" button
- [ ] Prediction form loads with all sections:
  - [ ] Section 1: Vital Signs (1 field)
  - [ ] Section 2: Urine Test (7 fields)
  - [ ] Section 3: Blood Test (5 fields)
  - [ ] Section 4: Blood Cell Analysis (4 fields)
  - [ ] Section 5: Medical History (6 fields)
- [ ] Total of 23 fields visible
- [ ] Form validation works:
  - [ ] Required fields marked with *
  - [ ] Cannot submit empty form
  - [ ] Number fields validate numeric input
  - [ ] Dropdown fields have proper options

### Submit Prediction
- [ ] Fill form with sample patient data (see SETUP_GUIDE.md)
- [ ] Click "Get Prediction" button
- [ ] Loading spinner appears
- [ ] Prediction completes in 2-5 seconds
- [ ] Results modal appears with:
  - [ ] Risk level (High Risk / Low Risk)
  - [ ] Confidence percentage
  - [ ] Icon and title
  - [ ] Medical recommendations
  - [ ] Disclaimer message

### Prediction History
- [ ] Click "View History" link
- [ ] History page loads
- [ ] Recent prediction appears in list:
  - [ ] Risk level displayed
  - [ ] Date/time shown
  - [ ] Confidence percentage visible
  - [ ] Key metrics displayed
- [ ] Click "View Details" on prediction
- [ ] Detail page shows all information:
  - [ ] All 23 medical parameters
  - [ ] Prediction result and confidence
  - [ ] Medical recommendations
  - [ ] Action buttons

---

## 🗄️ Database Testing

### Database Creation
- [ ] `ckd_users.db` file created in `/app/` directory
- [ ] Database size ~10-50KB

### Database Content Verification
```python
# In Python console:
from app import app, db, User, PredictionHistory

with app.app_context():
    # Check users
    users = User.query.all()
    print(f"Total users: {len(users)}")
    
    # Check predictions
    predictions = PredictionHistory.query.all()
    print(f"Total predictions: {len(predictions)}")
```
- [ ] Can query user and prediction data successfully

---

## 🎯 API Testing

### Test POST /api/predict
Using cURL, Python, or Postman:

```bash
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
- [ ] API returns JSON response
- [ ] Response includes: success, prediction, risk_level, confidence
- [ ] Recommendations included in response

---

## 🎨 UI/UX Testing

### Responsive Design
- [ ] Test on different screen sizes
- [ ] Mobile (320px):
  - [ ] Navigation stacked vertically
  - [ ] Forms single column
  - [ ] Buttons full width
- [ ] Tablet (768px):
  - [ ] 2-column layouts work
  - [ ] Readable text
  - [ ] Touch-friendly buttons
- [ ] Desktop (1200px+):
  - [ ] Multi-column layouts work
  - [ ] Proper spacing
  - [ ] Good visual hierarchy

### Animation & Interactions
- [ ] [ ] Splash screen logo bounces (animations work)
- [ ] [ ] Forms have smooth transitions
- [ ] [ ] Buttons have hover effects
- [ ] [ ] Loading spinner animates during prediction
- [ ] [ ] Modal slides in smoothly
- [ ] [ ] Cards have hover animations

### Color & Accessibility
- [ ] [ ] Text is readable (good contrast)
- [ ] [ ] Colors used meaningfully:
  - [ ] Green for success/low risk
  - [ ] Red for danger/high risk
  - [ ] Purple for primary actions
- [ ] [ ] Medical icons used appropriately

---

## 🔒 Security Testing

### Password Security
- [ ] [ ] Password hashing works (not stored as plain text)
- [ ] [ ] Session timeout works (7-day default)
- [ ] [ ] Logout clears session

### Input Validation
- [ ] [ ] SQL injection prevented (using ORM)
- [ ] [ ] Form validation catches invalid data
- [ ] [ ] File upload restricted (if applicable)

### Authentication
- [ ] [ ] Cannot access dashboard without login
- [ ] [ ] Cannot access prediction history without login
- [ ] [ ] Session cookies set correctly

---

## 📊 Performance Testing

### Load Time
- [ ] [ ] Splash page loads < 1 second
- [ ] [ ] Login page loads < 1 second
- [ ] [ ] Dashboard loads < 2 seconds
- [ ] [ ] Prediction form loads < 2 seconds
- [ ] [ ] Prediction API responds < 5 seconds

### Database Performance
- [ ] [ ] Predictions save successfully
- [ ] [ ] History page loads with multiple predictions
- [ ] [ ] Detail page loads quickly

### Browser Compatibility
- [ ] [ ] Chrome works
- [ ] [ ] Firefox works
- [ ] [ ] Safari works
- [ ] [ ] Edge works

---

## 🐛 Error Handling Testing

### Test Error Cases
- [ ] [ ] Wrong password: Shows error message
- [ ] [ ] Duplicate email: Shows error message
- [ ] [ ] Invalid form data: Shows validation error
- [ ] [ ] Missing model.pkl: Shows error message
- [ ] [ ] Database error: Shows error message
- [ ] [ ] 404 page: Custom error page displays
- [ ] [ ] 500 page: Custom error page displays

---

## 🚀 Deployment Preparation

### Pre-Deployment
- [ ] [ ] All tests passed
- [ ] [ ] No errors in console
- [ ] [ ] Database working properly
- [ ] [ ] All features functional

### Production Checklist
- [ ] [ ] Set `debug=False` in `app.py`
- [ ] [ ] Change `SECRET_KEY` to secure random string
- [ ] [ ] Update database to PostgreSQL (optional, not SQLite)
- [ ] [ ] Configure HTTPS/SSL certificate
- [ ] [ ] Set up logging
- [ ] [ ] Test on production-like environment
- [ ] [ ] Backup strategy in place
- [ ] [ ] Monitor scripts set up

### Deployment Command
```bash
# Using Gunicorn (production WSGI server)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## 📋 Post-Installation Tasks

### Documentation
- [ ] [ ] README.md read and understood
- [ ] [ ] SETUP_GUIDE.md reviewed
- [ ] [ ] API_DOCUMENTATION.md reviewed
- [ ] [ ] Code commented and understood

### Model Integration
- [ ] [ ] Sample model works and tested
- [ ] [ ] Understand how to replace with actual model
- [ ] [ ] Feature mapping verified
- [ ] [ ] Model performance acceptable

### Backup & Maintenance
- [ ] [ ] Database backup strategy planned
- [ ] [ ] Update plan for dependencies
- [ ] [ ] Monitoring alerts configured
- [ ] [ ] Disaster recovery plan

---

## 🎓 Educational Review

### Understanding the Code
- [ ] [ ] Flask routes understood
- [ ] [ ] Database models understood
- [ ] [ ] ML model integration understood
- [ ] [ ] Form handling understood
- [ ] [ ] Session management understood

### Learning Outcomes
- [ ] [ ] Can explain application architecture
- [ ] [ ] Can explain ML model integration
- [ ] [ ] Can add new features
- [ ] [ ] Can fix basic bugs
- [ ] [ ] Can deploy to production

---

## ✨ Final Verification

Run through complete user journey:

1. [ ] Start application: `python app.py`
2. [ ] Open browser: `http://localhost:5000`
3. [ ] See splash screen
4. [ ] Auto-redirect to login
5. [ ] Sign up new user
6. [ ] See dashboard
7. [ ] Click "Start Prediction"
8. [ ] Fill prediction form
9. [ ] Submit form
10. [ ] See results with recommendations
11. [ ] View prediction history
12. [ ] Click logout
13. [ ] Verify redirected to splash page
14. [ ] Stop server: `Ctrl+C`

All steps completed: ✅ **READY FOR DEPLOYMENT**

---

## 📞 Support Resources

If issues occur:
1. Check `README.md` - General information
2. Check `SETUP_GUIDE.md` - Setup troubleshooting
3. Check `API_DOCUMENTATION.md` - API reference
4. Check console logs for error messages
5. Verify all files present in correct directories
6. Verify Python version >= 3.7
7. Verify all packages installed: `pip list`

---

**Checklist Version:** 1.0  
**Date:** March 2026  
**Status:** Ready for Use

✅ Mark all items as you complete them!
