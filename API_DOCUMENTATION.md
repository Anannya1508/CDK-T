# 🔌 CKD Application API Documentation

## Base URL
```
http://localhost:5000
```

## Authentication
All endpoints requiring authentication need active session (login required)

---

## 🏠 Public Endpoints

### GET `/`
**Description:** Main splash page  
**Authentication:** Not required  
**Response:** HTML splash screen

```bash
curl http://localhost:5000/
```

---

### GET `/login`
**Description:** Login page  
**Authentication:** Not required  
**Response:** HTML login form

```bash
curl http://localhost:5000/login
```

---

### POST `/login`
**Description:** Authenticate user  
**Authentication:** Not required  
**Content-Type:** application/x-www-form-urlencoded

**Parameters:**
```
email: string (required)
password: string (required)
```

**Example:**
```bash
curl -X POST http://localhost:5000/login \
  -d "email=user@example.com&password=password123"
```

**Response:**
- Success: Redirect to `/dashboard`
- Error: Return login page with error message

---

### GET `/signup`
**Description:** Registration page  
**Authentication:** Not required  
**Response:** HTML signup form

```bash
curl http://localhost:5000/signup
```

---

### POST `/signup`
**Description:** Create new user account  
**Authentication:** Not required  
**Content-Type:** application/x-www-form-urlencoded

**Parameters:**
```
name: string (required)
email: string (required, unique)
password: string (required, min 6 chars)
confirm_password: string (required)
```

**Example:**
```bash
curl -X POST http://localhost:5000/signup \
  -d "name=John Doe&email=john@example.com&password=password123&confirm_password=password123"
```

**Response:**
- Success: Create user, set session, redirect to `/dashboard`
- Error: Return signup page with error message

---

## 🔐 Protected Endpoints (Require Login)

### GET `/dashboard`
**Description:** User dashboard  
**Authentication:** Required  
**Response:** HTML dashboard with recent predictions

```bash
curl -b "session_cookie" http://localhost:5000/dashboard
```

---

### GET `/predict-page`
**Description:** CKD prediction form page  
**Authentication:** Required  
**Response:** HTML prediction form

```bash
curl -b "session_cookie" http://localhost:5000/predict-page
```

---

### POST `/api/predict`
**Description:** Submit health data and get CKD prediction  
**Authentication:** Required  
**Content-Type:** application/json

**Request Body:**
```json
{
  "bp": 120,
  "sg": 1.020,
  "al": 0,
  "su": 0,
  "rbc": "normal",
  "pc": "normal",
  "pcc": "notpresent",
  "ba": "notpresent",
  "bgr": 110,
  "bu": 35,
  "sc": 0.9,
  "sod": 140,
  "pot": 4.5,
  "hemo": 14.0,
  "pcv": 42,
  "wc": 6,
  "rc": 5,
  "htn": "no",
  "dm": "no",
  "cad": "no",
  "appet": "good",
  "pe": "no",
  "ane": "no"
}
```

**Example (using cURL with authentication):**
```bash
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -b "session_cookie" \
  -d '{
    "bp": 120,
    "sg": 1.020,
    "al": 0,
    "su": 0,
    "rbc": "normal",
    "pc": "normal",
    "pcc": "notpresent",
    "ba": "notpresent",
    "bgr": 110,
    "bu": 35,
    "sc": 0.9,
    "sod": 140,
    "pot": 4.5,
    "hemo": 14.0,
    "pcv": 42,
    "wc": 6,
    "rc": 5,
    "htn": "no",
    "dm": "no",
    "cad": "no",
    "appet": "good",
    "pe": "no",
    "ane": "no"
  }'
```

**Success Response (200):**
```json
{
  "success": true,
  "prediction": 0,
  "risk_level": "Low Risk",
  "confidence": 85.5,
  "recommendations": {
    "title": "✓ Low Risk of Chronic Kidney Disease",
    "message": "Your health metrics indicate low risk of CKD.",
    "icon": "🟢",
    "recommendations": [
      "Continue maintaining healthy lifestyle",
      "Regular health check-ups (annually)",
      ...
    ]
  },
  "prediction_id": 1
}
```

**Error Response (400/500):**
```json
{
  "error": "Error message describing what went wrong"
}
```

**Field Descriptions:**

| Field | Type | Valid Values | Description |
|-------|------|--------------|-------------|
| bp | number | 0-200 | Blood Pressure (mmHg) |
| sg | number | 1.005-1.025 | Specific Gravity |
| al | number | 0-5 | Albumin level |
| su | number | 0-5 | Sugar level |
| rbc | string | "normal", "abnormal" | Red Blood Cells |
| pc | string | "normal", "abnormal" | Pus Cell |
| pcc | string | "present", "notpresent" | Pus Cell Clumps |
| ba | string | "present", "notpresent" | Bacteria |
| bgr | number | 0-300 | Blood Glucose Random (mg/dL) |
| bu | number | 0-150 | Blood Urea (mg/dL) |
| sc | number | 0-10 | Serum Creatinine (mg/dL) |
| sod | number | 100-160 | Sodium (mEq/L) |
| pot | number | 0-10 | Potassium (mEq/L) |
| hemo | number | 0-20 | Hemoglobin (g/dL) |
| pcv | number | 0-100 | Packed Cell Volume (%) |
| wc | number | 0-30 | White Blood Cell Count (K/uL) |
| rc | number | 0-10 | Red Blood Cell Count (M/uL) |
| htn | string | "yes", "no" | Hypertension |
| dm | string | "yes", "no" | Diabetes Mellitus |
| cad | string | "yes", "no" | Coronary Artery Disease |
| appet | string | "good", "poor" | Appetite |
| pe | string | "yes", "no" | Pedal Edema |
| ane | string | "yes", "no" | Anemia |

---

### GET `/prediction-history`
**Description:** Get user's prediction history  
**Authentication:** Required  
**Response:** HTML page with all predictions

```bash
curl -b "session_cookie" http://localhost:5000/prediction-history
```

---

### GET `/prediction/<prediction_id>`
**Description:** Get details of specific prediction  
**Authentication:** Required  
**Parameters:**
- `prediction_id` (path): ID of the prediction

```bash
curl -b "session_cookie" http://localhost:5000/prediction/1
```

**Response:** HTML page with detailed prediction analysis

---

### GET `/logout`
**Description:** Logout user and clear session  
**Authentication:** Required  
**Response:** Redirect to splash page

```bash
curl -b "session_cookie" http://localhost:5000/logout
```

---

## 📊 Response Models

### Prediction Result
```python
{
    "id": 1,
    "user_id": 1,
    "bp": 120.0,
    "sg": 1.020,
    "al": 0,
    "su": 0,
    "rbc": "normal",
    "pc": "normal",
    "pcc": "notpresent",
    "ba": "notpresent",
    "bgr": 110.0,
    "bu": 35.0,
    "sc": 0.9,
    "sod": 140.0,
    "pot": 4.5,
    "hemo": 14.0,
    "pcv": 42.0,
    "wc": 6.0,
    "rc": 5.0,
    "htn": "no",
    "dm": "no",
    "cad": "no",
    "appet": "good",
    "pe": "no",
    "ane": "no",
    "prediction_result": 0,
    "risk_level": "Low Risk",
    "confidence": 85.5,
    "created_at": "2024-01-15T10:30:00"
}
```

---

## 🔄 Common Workflows

### 1. User Registration & Login

```bash
# Step 1: Signup
curl -X POST http://localhost:5000/signup \
  -d "name=John&email=john@example.com&password=pass123&confirm_password=pass123"

# Step 2: Login (gets session cookie)
curl -X POST http://localhost:5000/login \
  -d "email=john@example.com&password=pass123" \
  -c cookies.txt

# Step 3: Access dashboard
curl -b cookies.txt http://localhost:5000/dashboard
```

---

### 2. Get Prediction

```bash
# Assuming logged in with session cookie
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "bp": 130,
    "sg": 1.020,
    "al": 1,
    "su": 0,
    "rbc": "normal",
    "pc": "normal",
    "pcc": "notpresent",
    "ba": "notpresent",
    "bgr": 120,
    "bu": 40,
    "sc": 1.1,
    "sod": 138,
    "pot": 4.8,
    "hemo": 13.5,
    "pcv": 41,
    "wc": 6.5,
    "rc": 4.8,
    "htn": "yes",
    "dm": "yes",
    "cad": "no",
    "appet": "good",
    "pe": "no",
    "ane": "no"
  }' | python -m json.tool
```

---

### 3. Get Prediction History

```bash
curl -b cookies.txt http://localhost:5000/prediction-history
```

---

### 4. View Specific Prediction

```bash
curl -b cookies.txt http://localhost:5000/prediction/1
```

---

## ⚠️ Error Codes

| Code | Error | Description |
|------|-------|-------------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid input data |
| 401 | Unauthorized | Not authenticated |
| 404 | Not Found | Endpoint not found |
| 405 | Method Not Allowed | Wrong HTTP method |
| 500 | Server Error | Internal server error |

---

## 🧪 Testing with Python

```python
import requests
import json

BASE_URL = "http://localhost:5000"

# Create session
session = requests.Session()

# Signup
signup_data = {
    "name": "Test User",
    "email": "test@example.com",
    "password": "password123",
    "confirm_password": "password123"
}
session.post(f"{BASE_URL}/signup", data=signup_data)

# Get prediction
prediction_data = {
    "bp": 120,
    "sg": 1.020,
    "al": 0,
    "su": 0,
    "rbc": "normal",
    "pc": "normal",
    "pcc": "notpresent",
    "ba": "notpresent",
    "bgr": 110,
    "bu": 35,
    "sc": 0.9,
    "sod": 140,
    "pot": 4.5,
    "hemo": 14.0,
    "pcv": 42,
    "wc": 6,
    "rc": 5,
    "htn": "no",
    "dm": "no",
    "cad": "no",
    "appet": "good",
    "pe": "no",
    "ane": "no"
}

response = session.post(
    f"{BASE_URL}/api/predict",
    json=prediction_data,
    headers={"Content-Type": "application/json"}
)

result = response.json()
print(json.dumps(result, indent=2))
```

---

## 📚 Additional Resources

- Flask Documentation: https://flask.palletsprojects.com/
- RESTful API Design: https://restfulapi.net/
- HTTP Status Codes: https://httpwg.org/specs/rfc7231.html

---

**API Version:** 1.0  
**Last Updated:** March 2026
