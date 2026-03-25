# CKD (Chronic Kidney Disease) Prediction Web Application
"Made by Trisha"

A comprehensive Flask-based medical web application for predicting chronic kidney disease risk using machine learning. The application includes user authentication, interactive prediction forms, prediction history tracking, and medical recommendations.

## 🎯 Features

### Authentication & User Management
- ✅ User signup with email and password validation
- ✅ Secure login system with hashed passwords
- ✅ Session management
- ✅ SQLite database for user data storage

### CKD Prediction System
- ✅ 25-parameter health assessment form
- ✅ Real-time ML model predictions
- ✅ Medical form with sections:
  - Vital Signs (Blood Pressure)
  - Urine Tests (SG, Albumin, Sugar, RBC, etc.)
  - Blood Tests (Glucose, Urea, Creatinine, etc.)
  - Blood Cell Analysis (Hemoglobin, WBC, RBC, etc.)
  - Medical History (Hypertension, Diabetes, etc.)

### Predictions & History
- ✅ Save prediction results to database
- ✅ View prediction history with timeline
- ✅ Detailed prediction analysis page
- ✅ Confidence scores for predictions

### User Interface
- ✅ Responsive design (mobile-friendly)
- ✅ Animated splash screen
- ✅ Modern CSS styling with gradients
- ✅ User-friendly forms with validation
- ✅ Medical recommendations based on results

## 📁 Project Structure

```
CDK-T/
├── app/
│   ├── app.py                 # Flask application
│   ├── templates/             # HTML templates
│   │   ├── splash.html
│   │   ├── signup.html
│   │   ├── login.html
│   │   ├── dashboard.html
│   │   ├── predict.html
│   │   ├── history.html
│   │   ├── prediction_detail.html
│   │   ├── 404.html
│   │   └── 500.html
│   ├── static/                # Static files
│   │   ├── css/
│   │   │   ├── splash.css
│   │   │   ├── auth.css
│   │   │   ├── dashboard.css
│   │   │   ├── predict.css
│   │   │   └── error.css
│   │   ├── js/
│   │   │   ├── predict.js
│   │   │   └── dashboard.js
│   │   └── images/
│   ├── model.pkl              # Trained ML model (generated)
│   └── ckd_users.db           # SQLite database (auto-created)
├── create_model.py            # Script to generate sample model
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.7 or higher
- pip (Python package manager)
- Git (optional, for cloning)

### 2. Installation

**Step 1: Clone or download the repository**
```bash
# If using git
git clone <repository-url>
cd CDK-T

# Or manually download and extract the files
```

**Step 2: Create a virtual environment (recommended)**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

**Step 3: Install dependencies**
```bash
pip install -r requirements.txt
```

**Step 4: Generate the ML model**
```bash
python create_model.py
```

This will create a sample `model.pkl` file. For production, replace this with your actual trained model.

**Step 5: Run the Flask application**
```bash
cd app
python app.py
```

**Step 6: Open in browser**
Navigate to: `http://localhost:5000`

## 📋 Application Flow

### 1. Landing Page
- Splash screen with animated logo (2-3 seconds)
- Auto-redirects to login page

### 2. Authentication
- **Signup**: Create account with name, email, password
- **Login**: Sign in with existing credentials
- Password hashing using Werkzeug

### 3. Dashboard
- Welcome message
- Quick action cards
- Recent prediction history
- Links to prediction form and history

### 4. CKD Prediction Form
- Organized into 5 sections
- Real-time form validation
- Dropdown and number inputs
- Clear instructions and units

### 5. Prediction Results
- Risk level (High Risk / Low Risk)
- Confidence percentage
- Medical recommendations
- Risk indicators

### 6. Prediction History
- Timeline of all predictions
- Quick view of key metrics
- Detailed analysis page for each prediction
- Trend analysis capability

## 🗄️ Database Schema

### User Table
```
id (Integer, Primary Key)
name (String)
email (String, Unique)
password_hash (String)
created_at (DateTime)
```

### PredictionHistory Table
```
id (Integer, Primary Key)
user_id (Integer, Foreign Key)
[23 medical feature columns]
prediction_result (Integer: 0 or 1)
risk_level (String: 'High Risk' or 'Low Risk')
confidence (Float)
created_at (DateTime)
```

## 🤖 ML Model Integration

### Supported Model Types
- scikit-learn classifiers (RandomForest, LogisticRegression, etc.)
- Any model with `predict()` and `predict_proba()` methods
- Custom models via pickle

### Using Your Own Model

1. Train your CKD prediction model using your dataset
2. Save it as a pickle file:
   ```python
   import pickle
   with open('app/model.pkl', 'wb') as f:
       pickle.dump(your_trained_model, f)
   ```
3. Ensure feature order matches your form fields
4. Update feature mapping in `app.py` if needed

## 🔧 Configuration

Edit `app/app.py`:

```python
# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ckd_users.db'

# Secret key (change in production!)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'

# Session timeout
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# Debug mode (disable in production)
app.run(debug=True)
```

## 📊 API Endpoints

### POST `/api/predict`
Sends form data for CKD prediction
- Requires: JSON form data
- Returns: JSON with prediction results
- Requires login

### GET `/predict-page`
Display prediction form (requires login)

### GET `/prediction-history`
View all user predictions (requires login)

### GET `/prediction/<id>`
View specific prediction details (requires login)

## 🎨 UI/UX Features

### Responsive Design
- Mobile-friendly layouts
- Flexible grid system
- Adaptive font sizes
- Touch-friendly buttons

### Color Scheme
- Primary: #667eea (Purple-blue)
- Secondary: #764ba2 (Dark purple)
- Success: #28a745 (Green)
- Danger: #dc3545 (Red)
- Neutral: #f5f7fa (Light gray)

### Animation
- Fade-in effects
- Slide animations
- Hover transitions
- Smooth scrolling

## 📝 Medical Features (25 Parameters)

| Section | Feature | Type | Range/Options |
|---------|---------|------|---------------|
| **Vital Signs** | Blood Pressure (bp) | Number | 0-200 mmHg |
| **Urine Test** | Specific Gravity (sg) | Decimal | 1.005-1.025 |
| | Albumin (al) | Dropdown | 0-5 |
| | Sugar (su) | Dropdown | 0-5 |
| | RBC | Dropdown | Normal/Abnormal |
| | Pus Cell (pc) | Dropdown | Normal/Abnormal |
| | Pus Cell Clumps (pcc) | Dropdown | Present/Not Present |
| | Bacteria (ba) | Dropdown | Present/Not Present |
| **Blood Test** | Blood Glucose Random (bgr) | Number | 0-300 mg/dL |
| | Blood Urea (bu) | Number | 0-150 mg/dL |
| | Serum Creatinine (sc) | Number | 0-10 mg/dL |
| | Sodium (sod) | Number | 100-160 mEq/L |
| | Potassium (pot) | Number | 0-10 mEq/L |
| **Blood Cell Analysis** | Hemoglobin (hemo) | Number | 0-20 g/dL |
| | Packed Cell Volume (pcv) | Number | 0-100 % |
| | White Blood Cell Count (wc) | Number | 0-30 K/uL |
| | Red Blood Cell Count (rc) | Number | 0-10 M/uL |
| **Medical History** | Hypertension (htn) | Yes/No | yes/no |
| | Diabetes Mellitus (dm) | Yes/No | yes/no |
| | Coronary Artery Disease (cad) | Yes/No | yes/no |
| | Appetite (appet) | Dropdown | Good/Poor |
| | Pedal Edema (pe) | Yes/No | yes/no |
| | Anemia (ane) | Yes/No | yes/no |

## 🔒 Security Features

- Password hashing using Werkzeug
- Session-based authentication
- CSRF protection (can be added)
- Input validation on forms
- SQL injection prevention via SQLAlchemy ORM
- Secure database storage

## 🐛 Troubleshooting

### Model not loading
```bash
# Regenerate model
python create_model.py

# Check model file exists
ls app/model.pkl  # or dir on Windows
```

### Database errors
```bash
# Delete old database and restart
rm app/ckd_users.db
python app/app.py
```

### Port already in use
```bash
# Use different port
python app/app.py --port 5001
```

### Dependencies not installing
```bash
# Update pip
pip install --upgrade pip

# Install requirements again
pip install -r requirements.txt
```

## 📚 Code Comments & Documentation

The code is extensively commented for educational purposes:
- Each function has docstrings
- Complex logic is explained
- Variable names are descriptive
- Step-by-step comments in routes

## 🧪 Testing

### Manual Testing Checklist

```
[ ] Splash screen appears and redirects
[ ] Signup validation works
[ ] Login works with correct credentials
[ ] Login fails with wrong credentials
[ ] Dashboard displays after login
[ ] Prediction form loads
[ ] Form validation works
[ ] Prediction API returns results
[ ] Results display correctly
[ ] History saves predictions
[ ] History page loads
[ ] Prediction detail page works
[ ] Logout clears session
```

## 🔄 Model Training Pipeline

For best results with your own data:

```python
# 1. Prepare CKD dataset (CSV format)
data = pd.read_csv('ckd_dataset.csv')

# 2. Train model
from sklearn.ensemble import RandomForestClassifier
model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)

# 3. Save model
pickle.dump(model, open('app/model.pkl', 'wb'))

# 4. Update feature names in app.py
```

## 📖 Learning Resources

### Flask Documentation
- https://flask.palletsprojects.com/

### SQLAlchemy ORM
- https://docs.sqlalchemy.org/

### scikit-learn Models
- https://scikit-learn.org/

### CKD Medical Information
- https://www.kidney.org/
- https://www.niddk.nih.gov/

## 🚀 Deployment

### Production Checklist

```bash
# 1. Set debug=False in app.py
# 2. Change SECRET_KEY to random string
# 3. Use production database (PostgreSQL)
# 4. Set up HTTPS/SSL certificate
# 5. Use production WSGI server (Gunicorn)
# 6. Set up error logging
# 7. Configure backup strategy

# Example Gunicorn deployment
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app.app:app
```

## 📄 License

This project is for educational purposes.

## 👨‍💻 Author Notes

This application is designed to be:
- **Educational**: Easy to understand with clear comments
- **Maintainable**: Well-structured code
- **Extensible**: Easy to add new features
- **Secure**: Basic security measures implemented

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review code comments
3. Check Flask documentation
4. Verify all dependencies are installed

---

**Version**: 1.0.0  
**Last Updated**: March 2026  
**Status**: Ready for deployment
