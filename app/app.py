import os
import io
import json
import textwrap
import smtplib
from email.message import EmailMessage
from sqlalchemy import inspect, text
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file, flash, get_flashed_messages
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit, join_room
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta, timezone
from functools import wraps
import uuid
import pickle
import pandas as pd
import numpy as np
import joblib
import warnings

warnings.filterwarnings('ignore')

# Initialize Flask app
app = Flask(__name__, template_folder='templates', static_folder='static')

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ckd_users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# Initialize database
app.jinja_env.globals['datetime'] = datetime

try:
    from zoneinfo import ZoneInfo
    DEFAULT_TIMEZONE = ZoneInfo('Asia/Dhaka')
except ImportError:
    DEFAULT_TIMEZONE = None


def format_datetime(value, fmt='%B %d, %Y at %I:%M %p', tz=None):
    if value is None:
        return ''
    if not isinstance(value, datetime):
        return str(value)
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    if tz is None:
        tz = DEFAULT_TIMEZONE
    if tz:
        try:
            value = value.astimezone(tz)
        except Exception:
            value = value.astimezone(timezone.utc)
    return value.strftime(fmt)

app.jinja_env.filters['format_datetime'] = format_datetime


db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins='*', async_mode='threading')
user_rooms = {}

# ==================== DATABASE MODELS ====================

# Database Model for User
class User(db.Model):
    """User account model for authentication"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='patient', nullable=False)
    specialization = db.Column(db.String(120))
    experience_years = db.Column(db.Integer)
    hospital_name = db.Column(db.String(160))
    license_number = db.Column(db.String(120))
    phone = db.Column(db.String(25))
    is_doctor_profile_active = db.Column(db.Boolean, default=False)
    # Doctor-specific integration fields
    preferred_video_platform = db.Column(db.String(50))
    platform_email = db.Column(db.String(120))
    payment_provider = db.Column(db.String(50))
    payment_account = db.Column(db.String(150))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    predictions = db.relationship('PredictionHistory', backref='user', lazy=True, cascade='all, delete-orphan')
    appointments = db.relationship('Appointment', foreign_keys='Appointment.user_id', backref='patient', lazy=True, cascade='all, delete-orphan')
    doctor_appointments = db.relationship('Appointment', foreign_keys='Appointment.doctor_id', backref='doctor_user', lazy=True)
    notifications = db.relationship('Notification', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.email}>'

# Database Model for Prediction History
class PredictionHistory(db.Model):
    """Store user prediction results for history tracking"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Additional info
    age = db.Column(db.Integer)
    
    # Input Features
    bp = db.Column(db.Float)
    sg = db.Column(db.Float)
    al = db.Column(db.Integer)
    su = db.Column(db.Integer)
    rbc = db.Column(db.String(20))
    pc = db.Column(db.String(20))
    pcc = db.Column(db.String(20))
    ba = db.Column(db.String(20))
    bgr = db.Column(db.Float)
    bu = db.Column(db.Float)
    sc = db.Column(db.Float)
    sod = db.Column(db.Float)
    pot = db.Column(db.Float)
    hemo = db.Column(db.Float)
    pcv = db.Column(db.Float)
    wc = db.Column(db.Float)
    rc = db.Column(db.Float)
    htn = db.Column(db.String(10))
    dm = db.Column(db.String(10))
    cad = db.Column(db.String(10))
    appet = db.Column(db.String(20))
    pe = db.Column(db.String(10))
    ane = db.Column(db.String(10))
    
    # Results
    prediction_result = db.Column(db.Integer)  # 0 or 1
    risk_level = db.Column(db.String(20))  # 'High Risk' or 'Low Risk'
    confidence = db.Column(db.Float)
    explanation = db.Column(db.Text)
    suggestions = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<PredictionHistory {self.id} - {self.risk_level}>'


class Appointment(db.Model):
    """Stores user bookings with kidney specialists."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    prediction_id = db.Column(db.Integer, nullable=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    doctor_name = db.Column(db.String(120), nullable=False)
    doctor_experience = db.Column(db.String(50), nullable=False)
    hospital = db.Column(db.String(160), nullable=False)
    patient_email = db.Column(db.String(120))
    appointment_datetime = db.Column(db.DateTime, nullable=False)
    mode = db.Column(db.String(20), default='In-person')
    meeting_platform = db.Column(db.String(50))
    meeting_link = db.Column(db.String(255))
    payment_status = db.Column(db.String(20), default='Pending')
    payment_reference = db.Column(db.String(150))
    reason = db.Column(db.Text)
    status = db.Column(db.String(20), default='Requested')
    decision_note = db.Column(db.Text)
    approved_at = db.Column(db.DateTime)
    rejected_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Appointment {self.id} - {self.doctor_name}>'


def generate_meeting_link(appointment):
    """Generate a mock meeting link based on selected platform."""
    if appointment.meeting_platform == 'Google Meet':
        return f'https://meet.google.com/{appointment.id:03d}-{appointment.doctor_id}-{appointment.user_id}'
    # Default Zoom-style placeholder
    return f'https://zoom.us/j/{appointment.id}{appointment.doctor_id}{appointment.user_id}'


class Notification(db.Model):
    """Simple in-app notification model."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(180), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(30), default='info')
    link = db.Column(db.String(255))
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ChatMessage(db.Model):
    """Stores patient-doctor chat messages."""
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sender_role = db.Column(db.String(20), nullable=False)
    message = db.Column(db.Text, nullable=False)
    attachment_url = db.Column(db.String(300), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Create database tables
with app.app_context():
    db.create_all()
    # Ensure schema has latest columns for older databases.
    from sqlalchemy import inspect, text
    try:
        inspector = inspect(db.engine)

        prediction_cols = [c['name'] for c in inspector.get_columns('prediction_history')]
        prediction_updates = [
            ('age', 'INTEGER'),
            ('explanation', 'TEXT'),
            ('suggestions', 'TEXT')
        ]

        for col_name, col_type in prediction_updates:
            if col_name not in prediction_cols:
                try:
                    with db.engine.connect() as conn:
                        conn.execute(text(f'ALTER TABLE prediction_history ADD COLUMN {col_name} {col_type}'))
                        conn.commit()
                    print(f'Added missing {col_name} column to prediction_history table')
                except Exception as e:
                    print(f'Could not add {col_name} column: {e}')

        user_cols = [c['name'] for c in inspector.get_columns('user')]
        user_updates = [
            ('role', "VARCHAR(20) DEFAULT 'patient'"),
            ('specialization', 'VARCHAR(120)'),
            ('experience_years', 'INTEGER'),
            ('hospital_name', 'VARCHAR(160)'),
            ('license_number', 'VARCHAR(120)'),
            ('phone', 'VARCHAR(25)'),
            ('is_doctor_profile_active', 'BOOLEAN DEFAULT 0'),
            ('preferred_video_platform', 'VARCHAR(50)'),
            ('platform_email', 'VARCHAR(120)'),
            ('payment_provider', 'VARCHAR(50)'),
            ('payment_account', 'VARCHAR(150)')
        ]
        for col_name, col_type in user_updates:
            if col_name not in user_cols:
                try:
                    with db.engine.connect() as conn:
                        conn.execute(text(f'ALTER TABLE user ADD COLUMN {col_name} {col_type}'))
                        conn.commit()
                    print(f'Added missing {col_name} column to user table')
                except Exception as e:
                    print(f'Could not add {col_name} column to user table: {e}')

        appointment_cols = [c['name'] for c in inspector.get_columns('appointment')]
        appointment_updates = [
            ('patient_email', 'VARCHAR(120)'),
            ('meeting_platform', 'VARCHAR(50)'),
            ('meeting_link', 'VARCHAR(255)'),
            ('payment_status', 'VARCHAR(20)'),
            ('payment_reference', 'VARCHAR(150)'),
            ('decision_note', 'TEXT'),
            ('approved_at', 'DATETIME'),
            ('rejected_at', 'DATETIME')
        ]
        for col_name, col_type in appointment_updates:
            if col_name not in appointment_cols:
                try:
                    with db.engine.connect() as conn:
                        conn.execute(text(f'ALTER TABLE appointment ADD COLUMN {col_name} {col_type}'))
                        conn.commit()
                    print(f'Added missing {col_name} column to appointment table')
                except Exception as e:
                    print(f'Could not add {col_name} column to appointment table: {e}')

        chat_cols = [c['name'] for c in inspector.get_columns('chat_message')]
        if 'attachment_url' not in chat_cols:
            try:
                with db.engine.connect() as conn:
                    conn.execute(text('ALTER TABLE chat_message ADD COLUMN attachment_url VARCHAR(300)'))
                    conn.commit()
                print('Added missing attachment_url column to chat_message table')
            except Exception as e:
                print(f'Could not add attachment_url column to chat_message table: {e}')
    except Exception as e:
        print(f'Database schema check skipped: {e}')

# ==================== ML MODEL LOADING ====================

def load_model():
    """Load the pre-trained ML model from pickle file"""
    try:
        model_path = os.path.join(os.path.dirname(__file__), 'model.pkl')
        if os.path.exists(model_path):
            try:
                # Try joblib first (better for sklearn models)
                model = joblib.load(model_path)
                print("✓ ML Model loaded successfully with joblib")
                return model
            except:
                # Fallback to pickle
                with open(model_path, 'rb') as f:
                    model = pickle.load(f)
                    print("✓ ML Model loaded successfully with pickle")
                    return model
        else:
            print("⚠ Model file not found at:", model_path)
            return None
    except Exception as e:
        print(f"✗ Error loading model: {e}")
        return None

ml_model = load_model()

# ==================== UTILITY FUNCTIONS ====================

FEATURES_ORDER = [
    'id', 'age', 'bp', 'sg', 'al', 'su', 'rbc', 'pc', 'pcc', 'ba',
    'bgr', 'bu', 'sc', 'sod', 'pot', 'hemo', 'pcv', 'wc', 'rc',
    'htn', 'dm', 'cad', 'appet', 'pe', 'ane'
]

def login_required(f):
    """Decorator to check if user is logged in"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def role_required(role_name):
    """Role-based access control decorator."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login'))
            if session.get('user_role') != role_name:
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def set_user_session(user):
    """Centralized session setup for authenticated users."""
    session['user_id'] = user.id
    session['user_name'] = user.name
    session['user_email'] = user.email
    session['user_role'] = user.role
    session.permanent = True


def get_available_doctors():
    """Return active registered doctors for patient consultation page."""
    doctors = User.query.filter_by(role='doctor', is_doctor_profile_active=True).order_by(User.name.asc()).all()
    return [
        {
            'id': doctor.id,
            'name': doctor.name,
            'experience': f"{doctor.experience_years or 0} years",
            'hospital': doctor.hospital_name or 'N/A',
            'specialty': doctor.specialization or 'Nephrology'
        }
        for doctor in doctors
    ]


def get_doctor_by_id(doctor_id):
    """Return doctor object by user id from registered doctors."""
    doctor = User.query.filter_by(id=doctor_id, role='doctor', is_doctor_profile_active=True).first()
    if not doctor:
        return None

    return {
        'id': doctor.id,
        'name': doctor.name,
        'experience': f"{doctor.experience_years or 0} years",
        'hospital': doctor.hospital_name or 'N/A',
        'specialty': doctor.specialization or 'Nephrology',
        'email': doctor.email
    }


def create_notification(user_id, title, message, notification_type='info', link=None):
    """Create a persistent in-app notification."""
    note = Notification(
        user_id=user_id,
        title=title,
        message=message,
        notification_type=notification_type,
        link=link
    )
    db.session.add(note)


def send_email_notification(to_email, subject, body):
    """Send SMTP email notification if env settings are configured."""
    smtp_host = os.getenv('SMTP_HOST')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_user = os.getenv('SMTP_USER')
    smtp_password = os.getenv('SMTP_PASSWORD')
    from_email = os.getenv('SMTP_FROM', smtp_user or 'no-reply@ckd-app.local')

    if not smtp_host or not smtp_user or not smtp_password:
        return False

    try:
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = from_email
        msg['To'] = to_email
        msg.set_content(body)

        with smtplib.SMTP(smtp_host, smtp_port, timeout=20) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f'Email send failed: {e}')
        return False


def get_recent_notifications(user_id, limit=5):
    """Fetch recent notifications for dashboard."""
    return Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).limit(limit).all()


def get_unread_notification_count(user_id):
    """Count unread notifications for badge display."""
    return Notification.query.filter_by(user_id=user_id, is_read=False).count()


@app.context_processor
def inject_global_notification_state():
    """Inject notification badge count in templates for logged-in users."""
    user_id = session.get('user_id')
    data = {'unread_notification_count': 0}
    if user_id:
        data['unread_notification_count'] = get_unread_notification_count(user_id)
    data['current_year'] = datetime.utcnow().year
    return data


def get_chat_room_id(patient_id, doctor_id):
    """Generate deterministic room id for patient-doctor chat."""
    return f'chat_{min(patient_id, doctor_id)}_{max(patient_id, doctor_id)}'


def get_appointment_reminders(user_id):
    """Build reminder notifications for upcoming appointments."""
    now = datetime.now()
    upcoming_limit = now + timedelta(hours=48)

    appointments = Appointment.query.filter(
        Appointment.user_id == user_id,
        Appointment.status.in_(['Approved', 'Rescheduled'])
    ).order_by(Appointment.appointment_datetime.asc()).all()

    reminders = []
    for appointment in appointments:
        appt_time = appointment.appointment_datetime
        if appt_time < now:
            continue

        if appt_time <= upcoming_limit:
            delta = appt_time - now
            hours_left = int(delta.total_seconds() // 3600)
            if hours_left < 1:
                time_label = 'in less than 1 hour'
            elif hours_left == 1:
                time_label = 'in 1 hour'
            else:
                time_label = f'in {hours_left} hours'

            reminders.append({
                'appointment_id': appointment.id,
                'doctor_name': appointment.doctor_name,
                'hospital': appointment.hospital,
                'mode': appointment.mode,
                'status': appointment.status,
                'time_label': time_label,
                'formatted_time': appt_time.strftime('%b %d, %Y at %I:%M %p')
            })

    return reminders

def _sanitize_text(value):
    """Normalize user text inputs before validation."""
    if value is None:
        return None
    text_value = str(value).strip().lower()
    return text_value if text_value else None


def _parse_float_field(form_data, field_name, min_value=None, max_value=None):
    """Parse and validate float inputs from the request payload."""
    raw_value = form_data.get(field_name)
    if raw_value is None or str(raw_value).strip() == '':
        raise ValueError(f'Missing required field: {field_name}')

    try:
        value = float(raw_value)
    except (TypeError, ValueError):
        raise ValueError(f'Invalid numeric value for {field_name}')

    if min_value is not None and value < min_value:
        raise ValueError(f'{field_name} must be at least {min_value}')
    if max_value is not None and value > max_value:
        raise ValueError(f'{field_name} must be at most {max_value}')

    return value


def _parse_int_field(form_data, field_name, min_value=None, max_value=None):
    """Parse and validate integer inputs from the request payload."""
    float_value = _parse_float_field(form_data, field_name, min_value=min_value, max_value=max_value)
    if float_value != int(float_value):
        raise ValueError(f'{field_name} must be a whole number')
    return int(float_value)


def _parse_choice_field(form_data, field_name, mapping, aliases=None):
    """Validate categorical input and return numeric model value + canonical label."""
    raw_value = _sanitize_text(form_data.get(field_name))
    if raw_value is None:
        raise ValueError(f'Missing required field: {field_name}')

    canonical_value = aliases.get(raw_value, raw_value) if aliases else raw_value
    if canonical_value not in mapping:
        raise ValueError(f'Invalid value for {field_name}')

    return mapping[canonical_value], canonical_value

def prepare_prediction_data(form_data):
    """
    Convert and validate form data for ML prediction.
    Returns model-ready features and canonical categorical values.
    """
    if not isinstance(form_data, dict):
        raise ValueError('Invalid request payload')

    rbc_mapping = {'normal': 1, 'abnormal': 0}
    pc_mapping = {'normal': 1, 'abnormal': 0}
    pcc_mapping = {'present': 1, 'notpresent': 0}
    ba_mapping = {'present': 1, 'notpresent': 0}
    binary_mapping = {'yes': 1, 'no': 0}
    appet_mapping = {'good': 1, 'poor': 0}
    binary_aliases = {
        'true': 'yes', 'false': 'no',
        '1': 'yes', '0': 'no',
        'y': 'yes', 'n': 'no'
    }

    rbc_value, rbc_label = _parse_choice_field(form_data, 'rbc', rbc_mapping)
    pc_value, pc_label = _parse_choice_field(form_data, 'pc', pc_mapping)
    pcc_value, pcc_label = _parse_choice_field(form_data, 'pcc', pcc_mapping)
    ba_value, ba_label = _parse_choice_field(form_data, 'ba', ba_mapping)
    htn_value, htn_label = _parse_choice_field(form_data, 'htn', binary_mapping, binary_aliases)
    dm_value, dm_label = _parse_choice_field(form_data, 'dm', binary_mapping, binary_aliases)
    cad_value, cad_label = _parse_choice_field(form_data, 'cad', binary_mapping, binary_aliases)
    pe_value, pe_label = _parse_choice_field(form_data, 'pe', binary_mapping, binary_aliases)
    ane_value, ane_label = _parse_choice_field(form_data, 'ane', binary_mapping, binary_aliases)
    appet_value, appet_label = _parse_choice_field(form_data, 'appet', appet_mapping)

    data_dict = {
        'id': 0,
        'age': _parse_float_field(form_data, 'age', min_value=1, max_value=120),
        'bp': _parse_float_field(form_data, 'bp', min_value=40, max_value=260),
        'sg': _parse_float_field(form_data, 'sg', min_value=1.0, max_value=1.04),
        'al': _parse_int_field(form_data, 'al', min_value=0, max_value=5),
        'su': _parse_int_field(form_data, 'su', min_value=0, max_value=5),
        'rbc': rbc_value,
        'pc': pc_value,
        'pcc': pcc_value,
        'ba': ba_value,
        'bgr': _parse_float_field(form_data, 'bgr', min_value=20, max_value=700),
        'bu': _parse_float_field(form_data, 'bu', min_value=1, max_value=400),
        'sc': _parse_float_field(form_data, 'sc', min_value=0.1, max_value=25),
        'sod': _parse_float_field(form_data, 'sod', min_value=90, max_value=190),
        'pot': _parse_float_field(form_data, 'pot', min_value=1, max_value=12),
        'hemo': _parse_float_field(form_data, 'hemo', min_value=3, max_value=25),
        'pcv': _parse_float_field(form_data, 'pcv', min_value=10, max_value=65),
        'wc': _parse_float_field(form_data, 'wc', min_value=1, max_value=60),
        'rc': _parse_float_field(form_data, 'rc', min_value=1, max_value=8),
        'htn': htn_value,
        'dm': dm_value,
        'cad': cad_value,
        'appet': appet_value,
        'pe': pe_value,
        'ane': ane_value,
    }

    categorical_data = {
        'rbc': rbc_label,
        'pc': pc_label,
        'pcc': pcc_label,
        'ba': ba_label,
        'htn': htn_label,
        'dm': dm_label,
        'cad': cad_label,
        'appet': appet_label,
        'pe': pe_label,
        'ane': ane_label,
    }

    return data_dict, categorical_data


def generate_prediction_explanation(data_dict, categorical_data, risk_level):
    """Create a concise explanation from clinically relevant signals."""
    factors = []
    alert_codes = []

    if data_dict['bp'] >= 140:
        factors.append(f"Blood pressure is elevated ({data_dict['bp']:.1f} mmHg).")
        alert_codes.append('high_bp')
    if data_dict['sc'] > 1.2:
        factors.append(f"Serum creatinine is above the usual range ({data_dict['sc']:.2f} mg/dL).")
        alert_codes.append('high_sc')
    if data_dict['bu'] > 40:
        factors.append(f"Blood urea is elevated ({data_dict['bu']:.1f} mg/dL).")
        alert_codes.append('high_bu')
    if data_dict['hemo'] < 12:
        factors.append(f"Hemoglobin is low ({data_dict['hemo']:.1f} g/dL).")
        alert_codes.append('low_hemo')
    if data_dict['al'] >= 2:
        factors.append(f"Albumin in urine is increased (grade {data_dict['al']}).")
        alert_codes.append('high_albumin')
    if data_dict['su'] >= 2:
        factors.append(f"Urine sugar is elevated (grade {data_dict['su']}).")
        alert_codes.append('high_sugar')
    if categorical_data['htn'] == 'yes':
        factors.append('History of hypertension can increase kidney disease risk.')
        alert_codes.append('htn')
    if categorical_data['dm'] == 'yes':
        factors.append('Diabetes is an important CKD risk factor.')
        alert_codes.append('dm')

    if not factors:
        factors.append('Most submitted values are in expected ranges for CKD screening features.')

    if risk_level == 'High Risk':
        summary = 'The model predicts high CKD risk primarily because several kidney-related indicators are outside healthy ranges.'
    else:
        summary = 'The model predicts low CKD risk because the overall feature pattern is closer to lower-risk profiles.'

    return {
        'summary': summary,
        'factors': factors[:6],
        'alert_codes': list(dict.fromkeys(alert_codes))
    }


def build_smart_suggestions(risk_level, alert_codes):
    """Generate action-oriented health suggestions using prediction context."""
    suggestions = []

    if risk_level == 'High Risk':
        suggestions.extend([
            'Consult a Doctor: book a nephrologist appointment within the next 1-2 weeks.',
            'Repeat kidney function labs (serum creatinine, urea, urine protein) as advised by your doctor.',
            'Avoid over-the-counter painkillers like NSAIDs unless prescribed.'
        ])
    else:
        suggestions.extend([
            'Continue annual kidney screening and maintain healthy daily habits.',
            'Stay hydrated and avoid excessive processed or high-sodium foods.'
        ])

    targeted = {
        'high_bp': 'Track blood pressure at home and discuss blood pressure targets with your physician.',
        'high_sc': 'Review medicines and hydration status with your clinician because creatinine is elevated.',
        'high_bu': 'Ask for follow-up renal function tests and diet review if blood urea remains high.',
        'low_hemo': 'Discuss anemia workup with your doctor, including iron and nutrition assessment.',
        'high_albumin': 'Request a urine albumin/protein follow-up test to confirm kidney involvement.',
        'high_sugar': 'Improve glucose control and monitor HbA1c with your diabetes care plan.',
        'htn': 'Follow a low-salt diet and medication plan to control hypertension.',
        'dm': 'Maintain tighter diabetes control to reduce long-term kidney damage risk.'
    }

    for code in alert_codes:
        if code in targeted:
            suggestions.append(targeted[code])

    # De-duplicate while preserving order.
    return list(dict.fromkeys(suggestions))


def parse_stored_suggestions(prediction):
    """Read stored suggestion JSON safely for detail/report views."""
    if not prediction.suggestions:
        return []

    try:
        parsed = json.loads(prediction.suggestions)
        if isinstance(parsed, list):
            return [str(item) for item in parsed]
    except (TypeError, ValueError):
        pass

    return [line.strip() for line in prediction.suggestions.split('\n') if line.strip()]

def get_risk_recommendation(risk_level):
    """Get medical recommendations based on risk level"""
    if risk_level.lower() == 'high risk':
        return {
            'title': '⚠️ High Risk of Chronic Kidney Disease',
            'message': 'Based on your health metrics, you may be at high risk of CKD.',
            'recommendations': [
                'Schedule an appointment with a nephrologist',
                'Monitor blood pressure regularly',
                'Maintain a low-sodium diet',
                'Stay hydrated (consult doctor for fluid intake)',
                'Avoid NSAIDs unless prescribed',
                'Regular exercise (consult doctor first)',
                'Get periodic kidney function tests'
            ],
            'icon': '🔴'
        }
    else:
        return {
            'title': '✓ Low Risk of Chronic Kidney Disease',
            'message': 'Your health metrics indicate low risk of CKD.',
            'recommendations': [
                'Continue maintaining healthy lifestyle',
                'Regular health check-ups (annually)',
                'Maintain balanced diet',
                'Stay physically active',
                'Control blood pressure and diabetes if present',
                'Limit salt and processed foods',
                'Stay well-hydrated'
            ],
            'icon': '🟢'
        }


# ==================== ROUTES ====================

@app.route('/')
def index():
    """Splash page route - shows splash and redirects"""
    return render_template('splash.html')


@app.route('/role-select')
def role_select():
    """Role selection screen after splash."""
    return render_template('role_select.html')

@app.route('/static-test')
def static_test():
    """Test static file serving"""
    return """
    <html>
    <head>
        <link rel="stylesheet" href="/static/css/dashboard.css">
    </head>
    <body>
        <h1>Static Test Page</h1>
        <p>If CSS loaded, this page should be styled.</p>
        <div class="navbar" style="color: white; padding: 20px;">
            <p>Navbar test - gradient should be purple-blue</p>
        </div>
        <script src="/static/js/dashboard.js"></script>
        <p>JS loaded. Check console for "Dashboard initialized".</p>
    </body>
    </html>
    """

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Patient signup route"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not all([name, email, password, confirm_password]):
            return render_template('signup.html', error='All fields are required')
        
        if password != confirm_password:
            return render_template('signup.html', error='Passwords do not match')
        
        if len(password) < 6:
            return render_template('signup.html', error='Password must be at least 6 characters')
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            return render_template('signup.html', error='Email already registered')
        
        # Create new patient user
        try:
            user = User(name=name, email=email, role='patient')
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            
            # Log the user in
            set_user_session(user)
            
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            return render_template('signup.html', error=f'Error creating account: {str(e)}')
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Patient login route"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            return render_template('login.html', error='Email and password are required')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            if user.role != 'patient':
                return render_template('login.html', error='Please use Doctor Login for doctor accounts')
            set_user_session(user)
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid email or password')
    
    return render_template('login.html')


@app.route('/doctor/register', methods=['GET', 'POST'])
def doctor_register():
    """Doctor registration with basic criteria fields."""
    if request.method == 'POST':
        name = (request.form.get('name') or '').strip()
        email = (request.form.get('email') or '').strip().lower()
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        specialization = (request.form.get('specialization') or '').strip()
        experience_years = request.form.get('experience_years', type=int)
        hospital_name = (request.form.get('hospital_name') or '').strip()
        license_number = (request.form.get('license_number') or '').strip()
        phone = (request.form.get('phone') or '').strip()
        preferred_video_platform = (request.form.get('preferred_video_platform') or '').strip()
        platform_email = (request.form.get('platform_email') or '').strip()
        payment_provider = (request.form.get('payment_provider') or '').strip()
        payment_account = (request.form.get('payment_account') or '').strip()

        required_values = [name, email, password, confirm_password, specialization, hospital_name, license_number, phone]
        if not all(required_values) or experience_years is None:
            return render_template('doctor_register.html', error='All fields are required')
        if password != confirm_password:
            return render_template('doctor_register.html', error='Passwords do not match')
        if len(password) < 6:
            return render_template('doctor_register.html', error='Password must be at least 6 characters')
        if experience_years < 0 or experience_years > 70:
            return render_template('doctor_register.html', error='Experience must be between 0 and 70 years')
        if User.query.filter_by(email=email).first():
            return render_template('doctor_register.html', error='Email already registered')

        # Only allow kidney specialists (nephrology) to register as doctors
        allowed_specializations = ['nephrology', 'nephrologist', 'kidney', 'renal']
        if not any(term in specialization.lower() for term in allowed_specializations):
            return render_template(
                'doctor_register.html',
                error='Only kidney specialists (e.g., Nephrology) can register as doctors.'
            )

        try:
            doctor = User(
                name=name,
                email=email,
                role='doctor',
                specialization=specialization,
                experience_years=experience_years,
                hospital_name=hospital_name,
                license_number=license_number,
                phone=phone,
                is_doctor_profile_active=True,
                preferred_video_platform=preferred_video_platform,
                platform_email=platform_email,
                payment_provider=payment_provider,
                payment_account=payment_account
            )
            doctor.set_password(password)
            db.session.add(doctor)
            db.session.commit()

            set_user_session(doctor)
            return redirect(url_for('doctor_dashboard'))
        except Exception as e:
            db.session.rollback()
            return render_template('doctor_register.html', error=f'Registration failed: {str(e)}')

    return render_template('doctor_register.html')


@app.route('/doctor/login', methods=['GET', 'POST'])
def doctor_login():
    """Doctor login route."""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            return render_template('doctor_login.html', error='Email and password are required')

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            if user.role != 'doctor':
                return render_template('doctor_login.html', error='This email is not registered as a doctor account')
            set_user_session(user)
            return redirect(url_for('doctor_dashboard'))

        return render_template('doctor_login.html', error='Invalid email or password')

    return render_template('doctor_login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard route after successful login."""
    if session.get('user_role') == 'doctor':
        return redirect(url_for('doctor_dashboard'))

    user_name = session.get('user_name', 'User')
    user_id = session.get('user_id')
    
    print(f"[DEBUG] Dashboard accessed - user_id={user_id}, user_name={user_name}")
    
    try:
        result = render_template(
            'dashboard.html',
            user_name=user_name
        )
        print(f"[DEBUG] Template rendered successfully")
        return result
    
    except Exception as e:
        print(f"[ERROR] Dashboard error: {str(e)}")
        import traceback
        traceback.print_exc()
        return render_template('500.html'), 500


@app.route('/doctor/dashboard')
@login_required
@role_required('doctor')
def doctor_dashboard():
    """Doctor dashboard with appointment requests."""
    doctor_id = session.get('user_id')
    pending_requests = Appointment.query.filter_by(doctor_id=doctor_id, status='Requested').order_by(Appointment.created_at.desc()).all()
    approved_appointments = Appointment.query.filter(
        Appointment.doctor_id == doctor_id,
        Appointment.status.in_(['Approved', 'Rescheduled'])
    ).order_by(Appointment.appointment_datetime.asc()).limit(8).all()

    return render_template(
        'doctor_dashboard.html',
        doctor_name=session.get('user_name'),
        pending_requests=pending_requests,
        approved_appointments=approved_appointments
    )

@app.route('/predict-page')
@login_required
@role_required('patient')
def predict_page():
    """Render the CKD prediction form page"""
    return render_template('predict.html')


@app.route('/doctors')
@login_required
@role_required('patient')
def doctors():
    """Show kidney specialist listing page."""
    prediction_id = request.args.get('prediction_id', type=int)
    doctors_data = get_available_doctors()
    return render_template('doctors.html', doctors=doctors_data, prediction_id=prediction_id)


@app.route('/book-appointment/<int:doctor_id>', methods=['GET', 'POST'])
@login_required
@role_required('patient')
def book_appointment(doctor_id):
    """Create appointment request with selected doctor."""
    doctor = get_doctor_by_id(doctor_id)
    if not doctor:
        return redirect(url_for('doctors'))

    prediction_id = request.args.get('prediction_id', type=int)

    if request.method == 'POST':
        appointment_date = request.form.get('appointment_date')
        appointment_time = request.form.get('appointment_time')
        mode = (request.form.get('mode') or 'In-person').strip()
        meeting_platform = request.form.get('meeting_platform') if mode == 'Online' else None
        reason = (request.form.get('reason') or '').strip()
        posted_prediction_id = request.form.get('prediction_id', type=int)

        # Keep prediction_id from query when form value is missing
        if posted_prediction_id is None:
            posted_prediction_id = prediction_id

        if not appointment_date or not appointment_time:
            return render_template(
                'book_appointment.html',
                doctor=doctor,
                prediction_id=prediction_id,
                error='Please select both date and time for the appointment.'
            )

        try:
            appointment_dt = datetime.strptime(f'{appointment_date} {appointment_time}', '%Y-%m-%d %H:%M')
        except ValueError:
            return render_template(
                'book_appointment.html',
                doctor=doctor,
                prediction_id=prediction_id,
                error='Invalid date/time format. Please try again.'
            )

        if appointment_dt <= datetime.now():
            return render_template(
                'book_appointment.html',
                doctor=doctor,
                prediction_id=prediction_id,
                error='Please choose a future appointment time.'
            )

        mode_value = mode if mode in ['In-person', 'Online'] else 'In-person'
        status_value = 'Requested'
        payment_status = 'Not required'

        if mode_value == 'Online':
            status_value = 'Requested'
            payment_status = 'Pending'

        appointment = Appointment(
            user_id=session.get('user_id'),
            prediction_id=posted_prediction_id,
            doctor_id=doctor['id'],
            doctor_name=doctor['name'],
            doctor_experience=doctor['experience'],
            hospital=doctor['hospital'],
            patient_email=session.get('user_email'),
            appointment_datetime=appointment_dt,
            mode=mode_value,
            meeting_platform=meeting_platform,
            reason=reason,
            status=status_value,
            payment_status=payment_status
        )

        db.session.add(appointment)
        create_notification(
            doctor['id'],
            'New Appointment Request',
            f"{session.get('user_name')} requested an appointment on {appointment_dt.strftime('%b %d, %Y at %I:%M %p')}.",
            notification_type='warning',
            link=url_for('doctor_appointments')
        )

        send_email_notification(
            doctor.get('email'),
            'New CKD Consultation Request',
            f"You have a new appointment request from {session.get('user_name')} scheduled for {appointment_dt.strftime('%Y-%m-%d %H:%M')} ({mode_value})."
        )
        db.session.commit()

        return render_template('appointment_confirmation.html', appointment=appointment)

    return render_template('book_appointment.html', doctor=doctor, prediction_id=prediction_id)


@app.route('/appointments')
@login_required
@role_required('patient')
def appointments():
    """View logged-in user's booked appointments."""
    user_id = session.get('user_id')
    booked = Appointment.query.filter_by(user_id=user_id).order_by(Appointment.appointment_datetime.desc()).all()
    reminders = get_appointment_reminders(user_id)
    message = request.args.get('message', '')
    return render_template('appointments.html', appointments=booked, reminders=reminders, message=message)


@app.route('/appointment/<int:appointment_id>/cancel', methods=['POST'])
@login_required
@role_required('patient')
def cancel_appointment(appointment_id):
    """Cancel a booked or rescheduled appointment for the logged-in user."""
    user_id = session.get('user_id')
    appointment = Appointment.query.filter_by(id=appointment_id, user_id=user_id).first()

    if not appointment:
        return redirect(url_for('appointments', message='Appointment not found.'))

    if appointment.status == 'Cancelled':
        return redirect(url_for('appointments', message='Appointment is already cancelled.'))

    appointment.status = 'Cancelled'
    db.session.commit()

    create_notification(
        appointment.doctor_id,
        'Appointment Cancelled',
        f"{session.get('user_name')} cancelled the appointment scheduled for {appointment.appointment_datetime.strftime('%b %d, %Y at %I:%M %p')}",
        notification_type='warning',
        link=url_for('doctor_appointments')
    )
    send_email_notification(
        User.query.get(appointment.doctor_id).email,
        'Appointment Cancelled by Patient',
        f"Patient {session.get('user_name')} has cancelled the appointment scheduled for {appointment.appointment_datetime.strftime('%Y-%m-%d %H:%M')}."
    )

    return redirect(url_for('appointments', message='Appointment cancelled successfully.'))


@app.route('/appointment/<int:appointment_id>/reschedule', methods=['GET', 'POST'])
@login_required
@role_required('patient')
def reschedule_appointment(appointment_id):
    """Reschedule an existing appointment."""
    user_id = session.get('user_id')
    appointment = Appointment.query.filter_by(id=appointment_id, user_id=user_id).first()

    if not appointment:
        return redirect(url_for('appointments', message='Appointment not found.'))

    if appointment.status == 'Cancelled':
        return redirect(url_for('appointments', message='Cancelled appointments cannot be rescheduled.'))

    if request.method == 'POST':
        appointment_date = request.form.get('appointment_date')
        appointment_time = request.form.get('appointment_time')
        mode = (request.form.get('mode') or appointment.mode or 'In-person').strip()

        if not appointment_date or not appointment_time:
            return render_template(
                'reschedule_appointment.html',
                appointment=appointment,
                error='Please select both date and time.'
            )

        try:
            new_datetime = datetime.strptime(f'{appointment_date} {appointment_time}', '%Y-%m-%d %H:%M')
        except ValueError:
            return render_template(
                'reschedule_appointment.html',
                appointment=appointment,
                error='Invalid date or time format.'
            )

        if new_datetime <= datetime.now():
            return render_template(
                'reschedule_appointment.html',
                appointment=appointment,
                error='Please choose a future time for rescheduling.'
            )

        appointment.appointment_datetime = new_datetime
        appointment.mode = mode if mode in ['In-person', 'Online'] else 'In-person'
        appointment.status = 'Rescheduled'
        create_notification(
            appointment.doctor_id,
            'Appointment Rescheduled',
            f"{session.get('user_name')} rescheduled to {new_datetime.strftime('%b %d, %Y at %I:%M %p')}.",
            notification_type='info',
            link=url_for('doctor_appointments')
        )
        db.session.commit()

        return redirect(url_for('appointments', message='Appointment rescheduled successfully.'))

    return render_template('reschedule_appointment.html', appointment=appointment)


@app.route('/appointment/<int:appointment_id>/delete', methods=['POST'])
@login_required
@role_required('patient')
def delete_appointment(appointment_id):
    """Delete an appointment record from patient's history."""
    user_id = session.get('user_id')
    appointment = Appointment.query.filter_by(id=appointment_id, user_id=user_id).first()

    if not appointment:
        return redirect(url_for('appointments', message='Appointment not found.'))

    db.session.delete(appointment)
    db.session.commit()
    return redirect(url_for('appointments', message='Appointment deleted from history.'))


@app.route('/doctor/appointments')
@login_required
@role_required('doctor')
def doctor_appointments():
    """Doctor view to manage incoming appointment requests."""
    doctor_id = session.get('user_id')
    pending_requests = Appointment.query.filter_by(doctor_id=doctor_id, status='Requested').order_by(Appointment.created_at.desc()).all()
    reviewed = Appointment.query.filter(
        Appointment.doctor_id == doctor_id,
        Appointment.status.in_(['Approved', 'Paid', 'Confirmed', 'Rejected', 'Cancelled', 'Rescheduled'])
    ).order_by(Appointment.created_at.desc()).limit(20).all()
    notifications = get_recent_notifications(doctor_id)
    return render_template('doctor_appointments.html', pending_requests=pending_requests, reviewed=reviewed, notifications=notifications)


@app.route('/doctor/appointment/<int:appointment_id>/approve', methods=['POST'])
@login_required
@role_required('doctor')
def approve_appointment(appointment_id):
    """Doctor approves a patient appointment request."""
    doctor_id = session.get('user_id')
    appointment = Appointment.query.filter_by(id=appointment_id, doctor_id=doctor_id).first()
    if not appointment:
        return redirect(url_for('doctor_appointments'))

    if appointment.mode == 'Online':
        appointment.status = 'Approved'
        appointment.payment_status = 'Pending'
    else:
        appointment.status = 'Confirmed'
        appointment.payment_status = 'Not required'

    appointment.approved_at = datetime.utcnow()
    appointment.rejected_at = None
    appointment.decision_note = (request.form.get('decision_note') or '').strip() or None

    create_notification(
        appointment.user_id,
        'Appointment Approved',
        f"Dr. {session.get('user_name')} approved your appointment for {appointment.appointment_datetime.strftime('%b %d, %Y at %I:%M %p')}.",
        notification_type='success',
        link=url_for('appointments')
    )
    send_email_notification(
        appointment.patient_email or User.query.get(appointment.user_id).email,
        'CKD Appointment Approved',
        f"Your appointment with Dr. {session.get('user_name')} is approved for {appointment.appointment_datetime.strftime('%Y-%m-%d %H:%M')} ({appointment.mode})."
    )
    db.session.commit()
    return redirect(url_for('doctor_appointments'))


@app.route('/doctor/appointment/<int:appointment_id>/cancel', methods=['POST'])
@login_required
@role_required('doctor')
def doctor_cancel_appointment(appointment_id):
    doctor_id = session.get('user_id')
    appointment = Appointment.query.filter_by(id=appointment_id, doctor_id=doctor_id).first()
    if not appointment:
        return redirect(url_for('doctor_appointments', message='Appointment not found.'))

    if appointment.status in ['Cancelled', 'Rejected']:
        return redirect(url_for('doctor_appointments', message='Appointment is already cancelled or rejected.'))

    appointment.status = 'Cancelled'
    appointment.rejected_at = datetime.utcnow()
    db.session.commit()

    create_notification(
        appointment.user_id,
        'Appointment Cancelled by Doctor',
        f"Dr. {session.get('user_name')} cancelled your appointment scheduled for {appointment.appointment_datetime.strftime('%b %d, %Y at %I:%M %p')}.",
        notification_type='warning',
        link=url_for('appointments')
    )

    send_email_notification(
        appointment.patient_email or User.query.get(appointment.user_id).email,
        'CKD Appointment Cancelled',
        f"Your appointment with Dr. {appointment.doctor_name} on {appointment.appointment_datetime.strftime('%Y-%m-%d %H:%M')} has been cancelled by the doctor."
    )

    return redirect(url_for('doctor_appointments', message='Appointment cancelled successfully.'))


@app.route('/doctor/appointment/<int:appointment_id>/reject', methods=['POST'])
@login_required
@role_required('doctor')
def reject_appointment(appointment_id):
    """Doctor rejects a patient appointment request."""
    doctor_id = session.get('user_id')
    appointment = Appointment.query.filter_by(id=appointment_id, doctor_id=doctor_id).first()
    if not appointment:
        return redirect(url_for('doctor_appointments'))

    appointment.status = 'Rejected'
    appointment.rejected_at = datetime.utcnow()
    appointment.approved_at = None
    appointment.decision_note = (request.form.get('decision_note') or '').strip() or None

    rejection_note = f" Dr. note: {appointment.decision_note}" if appointment.decision_note else ''
    create_notification(
        appointment.user_id,
        'Appointment Request Rejected',
        f"Your appointment request with Dr. {session.get('user_name')} was rejected.{rejection_note}",
        notification_type='warning',
        link=url_for('appointments')
    )
    send_email_notification(
        appointment.patient_email or User.query.get(appointment.user_id).email,
        'CKD Appointment Request Update',
        f"Your appointment request with Dr. {session.get('user_name')} was rejected.{rejection_note}"
    )
    db.session.commit()
    return redirect(url_for('doctor_appointments'))


@app.route('/appointment/<int:appointment_id>/pay', methods=['POST'])
@login_required
@role_required('patient')
def pay_appointment(appointment_id):
    """Mock payment route for online appointment approval step."""
    patient_id = session.get('user_id')
    appointment = Appointment.query.filter_by(id=appointment_id, user_id=patient_id).first()
    if not appointment:
        return redirect(url_for('appointments', message='Appointment not found.'))

    if appointment.mode != 'Online' or appointment.status != 'Approved' or appointment.payment_status != 'Pending':
        return redirect(url_for('appointments', message='Payment is not required for this appointment.'))

    # Mock payment processing success
    appointment.payment_status = 'Paid'
    appointment.status = 'Paid'
    appointment.payment_reference = f'PAY-{appointment.id}-{int(datetime.utcnow().timestamp())}'

    db.session.commit()

    # Notify doctor that patient has paid and link sending is required.
    create_notification(
        appointment.doctor_id,
        'Patient Paid',
        f"{User.query.get(appointment.user_id).name} has paid for online appointment #{appointment.id}. Please send meeting link.",
        notification_type='info',
        link=url_for('doctor_appointments')
    )

    create_notification(
        appointment.user_id,
        'Payment Completed',
        f'Payment received for your online appointment with Dr. {appointment.doctor_name}. Waiting for meeting link.',
        notification_type='success',
        link=url_for('appointments')
    )

    send_email_notification(
        appointment.patient_email or User.query.get(appointment.user_id).email,
        'CKD Appointment Payment Confirmed',
        f"Your payment for online appointment with Dr. {appointment.doctor_name} was successful.\nDoctor will send meeting link shortly."
    )

    return redirect(url_for('appointments', message='Payment successful. Doctor will send the meeting link soon.'))


@app.route('/doctor/appointment/<int:appointment_id>/send_link', methods=['POST'])
@login_required
@role_required('doctor')
def send_appointment_link(appointment_id):
    doctor_id = session.get('user_id')
    appointment = Appointment.query.filter_by(id=appointment_id, doctor_id=doctor_id).first()
    if not appointment:
        return redirect(url_for('doctor_appointments', message='Appointment not found.'))

    if appointment.mode != 'Online' or appointment.payment_status != 'Paid':
        return redirect(url_for('doctor_appointments', message='Meeting link cannot be sent for this appointment.'))

    if not appointment.meeting_link:
        doctor = User.query.filter_by(id=doctor_id).first()
        platform = appointment.meeting_platform or (doctor.preferred_video_platform if doctor else None) or 'Zoom'
        appointment.meeting_platform = platform
        appointment.meeting_link = generate_meeting_link(appointment)
    appointment.status = 'Confirmed'
    db.session.commit()

    create_notification(
        appointment.user_id,
        'Meeting Link Sent',
        f'Dr. {session.get("user_name")} has sent your meeting link for online consultation.',
        notification_type='success',
        link=url_for('appointments')
    )
    send_email_notification(
        appointment.patient_email or User.query.get(appointment.user_id).email,
        'Your Online Appointment Link',
        f"Your appointment with Dr. {appointment.doctor_name} is confirmed. Join link: {appointment.meeting_link}"
    )

    return redirect(url_for('doctor_appointments', message='Meeting link sent to patient.'))


@app.route('/consultation-chat/<int:doctor_id>')
@login_required
@role_required('patient')
def patient_chat(doctor_id):
    """Patient chat window with selected doctor."""
    doctor = User.query.filter_by(id=doctor_id, role='doctor').first()
    if not doctor:
        return redirect(url_for('doctors'))

    patient_id = session.get('user_id')
    messages = ChatMessage.query.filter_by(patient_id=patient_id, doctor_id=doctor_id).order_by(ChatMessage.created_at.asc()).all()
    room_id = get_chat_room_id(patient_id, doctor_id)
    return render_template('consult_chat.html', room_id=room_id, chat_with=doctor, messages=messages, viewer_role='patient')


@app.route('/chat/upload-attachment', methods=['POST'])
@login_required
def upload_chat_attachment():
    if 'attachment' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['attachment']
    if not file or file.filename == '':
        return jsonify({'error': 'Invalid file provided'}), 400

    allowed_ext = {'jpg', 'jpeg', 'png', 'gif', 'pdf', 'doc', 'docx', 'txt', 'mp3', 'wav', 'ogg', 'm4a', 'webm'}
    filename = secure_filename(file.filename)
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    if ext not in allowed_ext:
        return jsonify({'error': 'File type not allowed'}), 400

    upload_path = os.path.join(app.root_path, 'static', 'uploads', 'chat')
    os.makedirs(upload_path, exist_ok=True)

    unique_name = f"{uuid.uuid4().hex}_{filename}"
    save_path = os.path.join(upload_path, unique_name)
    file.save(save_path)

    file_url = url_for('static', filename=f'uploads/chat/{unique_name}')
    return jsonify({'url': file_url}), 200


@app.route('/chat/message/<int:message_id>/delete', methods=['POST'])
@login_required
def delete_chat_message(message_id):
    """Delete a single chat message by its owner."""
    user_id = session.get('user_id')
    user_role = session.get('user_role')

    message = ChatMessage.query.get(message_id)
    if not message:
        return jsonify({'error': 'Message not found'}), 404

    if user_id != message.patient_id and user_id != message.doctor_id:
        return jsonify({'error': 'Unauthorized'}), 403

    try:
        db.session.delete(message)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

    return jsonify({'success': True, 'message_id': message_id}), 200


@app.route('/doctor/chat')
@login_required
@role_required('doctor')
def doctor_chat_hub():
    """Doctor chat inbox with patients."""
    doctor_id = session.get('user_id')
    patient_ids = db.session.query(ChatMessage.patient_id).filter_by(doctor_id=doctor_id).distinct().all()
    patients = []
    for row in patient_ids:
        patient = User.query.get(row[0])
        if patient:
            patients.append(patient)
    return render_template('doctor_chat_hub.html', patients=patients)


@app.route('/doctor/chat/<int:patient_id>')
@login_required
@role_required('doctor')
def doctor_chat(patient_id):
    """Doctor opens chat with a patient."""
    doctor_id = session.get('user_id')
    patient = User.query.filter_by(id=patient_id, role='patient').first()
    if not patient:
        return redirect(url_for('doctor_chat_hub'))

    messages = ChatMessage.query.filter_by(patient_id=patient_id, doctor_id=doctor_id).order_by(ChatMessage.created_at.asc()).all()
    room_id = get_chat_room_id(patient_id, doctor_id)
    return render_template('consult_chat.html', room_id=room_id, chat_with=patient, messages=messages, viewer_role='doctor')

@app.route('/api/predict', methods=['POST'])
@login_required
@role_required('patient')
def predict():
    """
    CKD prediction API endpoint
    Accepts form data, converts to dataframe, and makes prediction using loaded model
    """
    try:
        user_id = session.get('user_id')
        
        # Check if model is loaded
        if not ml_model:
            return jsonify({'error': 'Prediction model not available. Please contact administrator.'}), 500
        
        form_data = request.get_json(silent=True) or {}

        data_dict, categorical_data = prepare_prediction_data(form_data)
        
        try:
            df = pd.DataFrame([data_dict], columns=FEATURES_ORDER)
            
            prediction = int(ml_model.predict(df)[0])
            
            high_risk_probability = float(prediction)
            if hasattr(ml_model, 'predict_proba'):
                probabilities = ml_model.predict_proba(df)[0]
                if len(probabilities) >= 2:
                    high_risk_probability = float(probabilities[1])
                else:
                    high_risk_probability = float(np.max(probabilities))

            confidence = (high_risk_probability if prediction == 1 else (1 - high_risk_probability)) * 100
            
            risk_level = 'High Risk' if prediction == 1 else 'Low Risk'
            risk_color = '#dc3545' if prediction == 1 else '#28a745'

            explanation = generate_prediction_explanation(data_dict, categorical_data, risk_level)
            smart_suggestions = build_smart_suggestions(risk_level, explanation['alert_codes'])
            
            prediction_record = PredictionHistory(
                user_id=user_id,
                age=int(data_dict['age']),
                bp=data_dict['bp'],
                sg=data_dict['sg'],
                al=data_dict['al'],
                su=data_dict['su'],
                rbc=categorical_data['rbc'],
                pc=categorical_data['pc'],
                pcc=categorical_data['pcc'],
                ba=categorical_data['ba'],
                bgr=data_dict['bgr'],
                bu=data_dict['bu'],
                sc=data_dict['sc'],
                sod=data_dict['sod'],
                pot=data_dict['pot'],
                hemo=data_dict['hemo'],
                pcv=data_dict['pcv'],
                wc=data_dict['wc'],
                rc=data_dict['rc'],
                htn=categorical_data['htn'],
                dm=categorical_data['dm'],
                cad=categorical_data['cad'],
                appet=categorical_data['appet'],
                pe=categorical_data['pe'],
                ane=categorical_data['ane'],
                prediction_result=int(prediction),
                risk_level=risk_level,
                confidence=confidence,
                explanation=explanation['summary'],
                suggestions=json.dumps(smart_suggestions)
            )
            
            db.session.add(prediction_record)
            db.session.commit()
            
            # Get recommendations
            recommendations = get_risk_recommendation(risk_level)
            doctors_data = get_available_doctors()
            first_doctor_id = doctors_data[0]['id'] if doctors_data else None
            
            return jsonify({
                'success': True,
                'prediction': int(prediction),
                'risk_level': risk_level,
                'confidence': round(confidence, 2),
                'risk_color': risk_color,
                'high_risk_probability': round(high_risk_probability * 100, 2),
                'explanation': explanation,
                'smart_suggestions': smart_suggestions,
                'recommendations': recommendations,
                'prediction_id': prediction_record.id,
                'pdf_report_url': url_for('download_prediction_report', prediction_id=prediction_record.id),
                'consult_doctor_url': url_for('doctors', prediction_id=prediction_record.id),
                'consult_booking_url': url_for('book_appointment', doctor_id=first_doctor_id, prediction_id=prediction_record.id) if first_doctor_id else None,
                'show_consult_suggestion': prediction == 1
            })
        
        except Exception as model_error:
            db.session.rollback()
            print(f"Model prediction error: {model_error}")
            return jsonify({'success': False, 'error': f'Prediction error: {str(model_error)}'}), 200

    except ValueError as validation_error:
        return jsonify({'success': False, 'error': str(validation_error)}), 200
    
    except Exception as e:
        print(f"API error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 200


@app.route('/prediction/<int:prediction_id>/report.pdf')
@login_required
@role_required('patient')
def download_prediction_report(prediction_id):
    """Generate and download a PDF report for a prediction result."""
    user_id = session.get('user_id')
    prediction = PredictionHistory.query.filter_by(id=prediction_id, user_id=user_id).first()

    if not prediction:
        return render_template('404.html'), 404

    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
    except ImportError:
        return jsonify({'error': 'PDF support is unavailable. Please install reportlab.'}), 500

    recommendations = parse_stored_suggestions(prediction)
    if not recommendations:
        recommendations = get_risk_recommendation(prediction.risk_level).get('recommendations', [])

    explanation_text = prediction.explanation or 'No additional explanation available for this record.'

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 50

    def write_wrapped_line(text_value, font_name='Helvetica', font_size=11, indent=0, spacing=16):
        nonlocal y
        if text_value is None:
            return

        wrapped_lines = textwrap.wrap(str(text_value), width=95)
        if not wrapped_lines:
            wrapped_lines = ['']

        for line in wrapped_lines:
            if y < 55:
                pdf.showPage()
                y = height - 50
            pdf.setFont(font_name, font_size)
            pdf.drawString(40 + indent, y, line)
            y -= spacing

    pdf.setTitle(f'CKD Care Report #{prediction.id}')
    write_wrapped_line('CKD Care Report', font_name='Helvetica-Bold', font_size=18, spacing=24)
    write_wrapped_line(f'Report ID: {prediction.id}', font_name='Helvetica', font_size=10)
    write_wrapped_line(f'Date: {prediction.created_at.strftime("%Y-%m-%d %H:%M")}', font_name='Helvetica', font_size=10)
    write_wrapped_line(f'Risk Result: {prediction.risk_level}', font_name='Helvetica-Bold', font_size=12)
    write_wrapped_line(f'Confidence: {prediction.confidence:.2f}%', font_name='Helvetica', font_size=11, spacing=22)

    write_wrapped_line('Clinical Summary', font_name='Helvetica-Bold', font_size=13)
    write_wrapped_line(explanation_text, font_name='Helvetica', font_size=11, spacing=22)

    write_wrapped_line('Input Values', font_name='Helvetica-Bold', font_size=13)
    metric_lines = [
        f'Age: {prediction.age if prediction.age is not None else "N/A"} years',
        f'Blood Pressure: {prediction.bp} mmHg | Specific Gravity: {prediction.sg}',
        f'Blood Glucose (Random): {prediction.bgr} mg/dL | Blood Urea: {prediction.bu} mg/dL',
        f'Serum Creatinine: {prediction.sc} mg/dL | Sodium: {prediction.sod} mEq/L | Potassium: {prediction.pot} mEq/L',
        f'Hemoglobin: {prediction.hemo} g/dL | PCV: {prediction.pcv}% | WBC: {prediction.wc} K/uL | RBC: {prediction.rc} M/uL',
        f'Hypertension: {prediction.htn} | Diabetes: {prediction.dm} | CAD: {prediction.cad} | Appetite: {prediction.appet}',
        f'Pedal Edema: {prediction.pe} | Anemia: {prediction.ane}'
    ]
    for metric in metric_lines:
        write_wrapped_line(metric, font_name='Helvetica', font_size=10)

    y -= 8
    write_wrapped_line('Suggested Next Steps', font_name='Helvetica-Bold', font_size=13)
    for idx, recommendation in enumerate(recommendations, start=1):
        write_wrapped_line(f'{idx}. {recommendation}', font_name='Helvetica', font_size=11)

    y -= 8
    write_wrapped_line('Important: This AI-generated report is informational only and does not replace medical diagnosis.', font_name='Helvetica-Oblique', font_size=9)

    pdf.save()
    buffer.seek(0)

    filename = f'ckd_prediction_report_{prediction.id}.pdf'
    return send_file(buffer, as_attachment=True, download_name=filename, mimetype='application/pdf')

@app.route('/prediction-history')
@login_required
@role_required('patient')
def prediction_history():
    """View user's prediction history"""
    user_id = session.get('user_id')
    user_name = session.get('user_name')
    
    predictions = PredictionHistory.query.filter_by(user_id=user_id).order_by(
        PredictionHistory.created_at.desc()
    ).all()

    flash_messages = get_flashed_messages()
    display_message = flash_messages[0] if flash_messages else ''
    
    return render_template(
        'history.html',
        predictions=predictions,
        user_name=user_name,
        flash_message=display_message
    )

@app.route('/prediction/<int:prediction_id>')
@login_required
@role_required('patient')
def view_prediction(prediction_id):
    """View details of a specific prediction"""
    user_id = session.get('user_id')
    
    prediction = PredictionHistory.query.filter_by(id=prediction_id, user_id=user_id).first()
    
    if not prediction:
        return redirect(url_for('prediction_history'))
    
    recommendations = get_risk_recommendation(prediction.risk_level)
    smart_suggestions = parse_stored_suggestions(prediction)
    if not smart_suggestions:
        smart_suggestions = recommendations.get('recommendations', [])
    
    return render_template(
        'prediction_detail.html',
        prediction=prediction,
        recommendations=recommendations,
        smart_suggestions=smart_suggestions
    )

@app.route('/prediction/<int:prediction_id>/delete', methods=['POST'])
@login_required
@role_required('patient')
def delete_prediction(prediction_id):
    """Delete a prediction history record for the signed-in user."""
    user_id = session.get('user_id')
    prediction = PredictionHistory.query.filter_by(id=prediction_id, user_id=user_id).first()
    if not prediction:
        return redirect(url_for('prediction_history', message='Prediction not found.'))

    db.session.delete(prediction)
    db.session.commit()
    flash('Prediction record deleted successfully.')
    return redirect(url_for('prediction_history'))

@app.route('/logout')
def logout():
    """User logout route"""
    session.clear()
    return redirect(url_for('index'))


@app.route('/notifications/mark-read/<int:notification_id>', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    """Mark in-app notification as read for current user."""
    note = Notification.query.filter_by(id=notification_id, user_id=session.get('user_id')).first()
    if note:
        note.is_read = True
        db.session.commit()

    if session.get('user_role') == 'doctor':
        return redirect(url_for('doctor_dashboard'))
    return redirect(url_for('dashboard'))


@app.route('/notifications/mark-all-read', methods=['POST'])
@login_required
def mark_all_notifications_read():
    """Mark all notifications as read for current user."""
    user_id = session.get('user_id')
    Notification.query.filter_by(user_id=user_id, is_read=False).update({'is_read': True})
    db.session.commit()
    return redirect(url_for('notifications_page'))


@app.route('/notifications/delete/<int:notification_id>', methods=['POST'])
@login_required
def delete_notification(notification_id):
    """Delete a single notification for current user."""
    user_id = session.get('user_id')
    note = Notification.query.filter_by(id=notification_id, user_id=user_id).first()
    if note:
        db.session.delete(note)
        db.session.commit()
    return redirect(url_for('notifications_page'))


@app.route('/notifications/delete-all', methods=['POST'])
@login_required
def delete_all_notifications():
    """Delete all notifications for current user."""
    user_id = session.get('user_id')
    Notification.query.filter_by(user_id=user_id).delete()
    db.session.commit()
    return redirect(url_for('notifications_page'))


@app.route('/notifications')
@login_required
def notifications_page():
    """Show all notifications with read/unread status."""
    user_id = session.get('user_id')
    notifications = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).all()
    return render_template('notifications.html', notifications=notifications)


@socketio.on('join_room')
def handle_join_room(data):
    """Join patient-doctor private room with role validation."""
    if not data:
        return

    room_id = data.get('room_id')
    patient_id = data.get('patient_id')
    doctor_id = data.get('doctor_id')

    current_user_id = session.get('user_id')
    current_role = session.get('user_role')
    if not current_user_id or not current_role:
        return

    if current_role == 'patient' and int(current_user_id) != int(patient_id):
        return
    if current_role == 'doctor' and int(current_user_id) != int(doctor_id):
        return

    join_room(room_id)
    user_rooms[request.sid] = room_id

    emit('presence_update', {
        'room_id': room_id,
        'user_id': current_user_id,
        'status': 'online',
        'user_name': session.get('user_name')
    }, to=room_id, include_self=False)


@socketio.on('disconnect')
def handle_disconnect():
    sid = request.sid
    room_id = user_rooms.pop(sid, None)
    current_user_id = session.get('user_id')

    if room_id:
        emit('presence_update', {
            'room_id': room_id,
            'user_id': current_user_id,
            'status': 'offline',
            'user_name': session.get('user_name')
        }, to=room_id, include_self=False)


@socketio.on('typing')
def handle_typing(data):
    if not data:
        return

    room_id = data.get('room_id')
    user_id = data.get('user_id')
    user_name = data.get('user_name', 'Someone')
    is_typing = data.get('is_typing', False)

    if not room_id or not user_id:
        return

    emit('typing', {
        'room_id': room_id,
        'user_id': user_id,
        'user_name': user_name,
        'is_typing': is_typing
    }, to=room_id, include_self=False)


@socketio.on('send_message')
def handle_send_message(data):
    """Persist and broadcast realtime chat message."""
    if not data:
        return

    room_id = data.get('room_id')
    patient_id = data.get('patient_id')
    doctor_id = data.get('doctor_id')
    text_value = (data.get('message') or '').strip()
    attachment_url = data.get('attachment_url') or None
    sender_id = session.get('user_id')
    sender_role = session.get('user_role')

    if not room_id or not patient_id or not doctor_id or not sender_id or not sender_role:
        return

    if not text_value and not attachment_url:
        return

    if sender_role == 'patient' and int(sender_id) != int(patient_id):
        return
    if sender_role == 'doctor' and int(sender_id) != int(doctor_id):
        return

    message_record = ChatMessage(
        patient_id=int(patient_id),
        doctor_id=int(doctor_id),
        sender_id=int(sender_id),
        sender_role=sender_role,
        message=text_value or '',
        attachment_url=attachment_url
    )
    db.session.add(message_record)
    db.session.commit()

    emit('receive_message', {
        'id': message_record.id,
        'patient_id': message_record.patient_id,
        'doctor_id': message_record.doctor_id,
        'sender_id': message_record.sender_id,
        'sender_role': message_record.sender_role,
        'message': message_record.message,
        'attachment_url': message_record.attachment_url,
        'created_at': message_record.created_at.strftime('%Y-%m-%d %H:%M:%S')
    }, to=room_id)


@socketio.on('delete_message')
def handle_delete_message(data):
    """Remove a chat message and broadcast removal."""
    if not data:
        return

    room_id = data.get('room_id')
    message_id = data.get('message_id')
    sender_id = session.get('user_id')

    if not room_id or not message_id or not sender_id:
        return

    message = ChatMessage.query.get(message_id)
    if not message:
        return

    # allow patient/doctor only on their own chat conversation
    if int(sender_id) != int(message.patient_id) and int(sender_id) != int(message.doctor_id):
        return

    try:
        db.session.delete(message)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return

    emit('message_deleted', {'message_id': message_id}, to=room_id)


@app.route('/chat/message/<int:message_id>/edit', methods=['POST'])
@login_required
def edit_chat_message(message_id):
    payload = request.get_json() or {}
    new_text = (payload.get('message') or '').strip()

    if not new_text:
        return jsonify({'success': False, 'error': 'Empty message content'}), 400

    current_user_id = session.get('user_id')
    message = ChatMessage.query.get(message_id)

    if not message:
        return jsonify({'success': False, 'error': 'Message not found'}), 404

    if int(current_user_id) != int(message.sender_id):
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403

    message.message = new_text
    db.session.commit()

    socketio.emit('message_edited', {
        'room_id': get_chat_room_id(message.patient_id, message.doctor_id),
        'message_id': message_id,
        'message': new_text
    }, to=get_chat_room_id(message.patient_id, message.doctor_id))

    return jsonify({'success': True, 'message_id': message_id})


@app.route('/chat/transcript/<room_id>/report.pdf')
@login_required
def download_chat_transcript(room_id):
    if not room_id or not room_id.startswith('chat_'):
        return jsonify({'error': 'Invalid room format'}), 400

    try:
        _, first, second = room_id.split('_')
        patient_id = int(first)
        doctor_id = int(second)
    except Exception:
        return jsonify({'error': 'Invalid room format'}), 400

    messages = ChatMessage.query.filter_by(patient_id=patient_id, doctor_id=doctor_id).order_by(ChatMessage.created_at.asc()).all()

    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
    except ImportError:
        return jsonify({'error': 'PDF support unavailable. Please install reportlab.'}), 500

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 50

    pdf.setTitle(f'Chat Transcript {room_id}')
    pdf.setFont('Helvetica-Bold', 16)
    pdf.drawString(40, y, 'CKD Chat Transcript')
    y -= 28

    pdf.setFont('Helvetica', 10)
    pdf.drawString(40, y, f'Room: {room_id}')
    y -= 18

    for msg in messages:
        sender_label = 'Doctor' if msg.sender_role == 'doctor' else 'Patient'
        text_line = f"[{msg.created_at.strftime('%Y-%m-%d %H:%M')}] {sender_label}: {msg.message or ''}"
        if msg.attachment_url:
            text_line += f" [Attachment: {msg.attachment_url}]"

        wrapped_lines = textwrap.wrap(text_line, 110)
        for line in wrapped_lines:
            if y < 60:
                pdf.showPage()
                y = height - 50
            pdf.drawString(40, y, line)
            y -= 14

        y -= 6

    pdf.save()
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name=f'chat_transcript_{room_id}.pdf', mimetype='application/pdf')

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return render_template('500.html'), 500

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
