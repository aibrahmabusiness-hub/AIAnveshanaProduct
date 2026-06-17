import sys
import os
sys.path.append('C:/Users/Admin/Documents/Agentic AI/backend')
from main import app

for route in app.routes:
    if hasattr(route, 'methods'):
        print(route.path, route.methods)
    else:
        print(route.path, 'Mount/Other')
