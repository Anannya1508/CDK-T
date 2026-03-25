#!/usr/bin/env python
"""Test if app imports correctly"""
import sys
sys.path.insert(0, 'c:/CDK-T')

try:
    from app.app import app, ml_model
    print("✓ App imported successfully")
    print(f"✓ ML Model loaded: {ml_model is not None}")
    print("\n✓ Application is ready to run")
except Exception as e:
    print(f"✗ Import failed: {e}")
    import traceback
    traceback.print_exc()
