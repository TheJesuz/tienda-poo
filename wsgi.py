import sys, os

base = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(base, 'ecommerce'))
os.chdir(os.path.join(base, 'ecommerce'))

from app import app
