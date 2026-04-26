"""
Run this ONCE after first deploy on Railway console:
  python setup_production.py

Seeds admin user, badges, surveys, quizzes and games.
Safe to run multiple times - skips existing data.
"""
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'earnwave.settings')
django.setup()

from django.core.management import call_command
print("🌊 Setting up EarnWave production data...")
call_command('seed_data')
call_command('seed_content')
print("✅ Setup complete!")
