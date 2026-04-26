"""
Run this once to generate your SECRET_KEY for Railway:
  python generate_secret.py
Then paste the output into Railway environment variables.
"""
from django.core.management.utils import get_random_secret_key
print("Your SECRET_KEY:")
print(get_random_secret_key())
