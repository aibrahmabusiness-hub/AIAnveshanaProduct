from backend.main import app
for route in app.routes:
    if hasattr(route, "methods"):
        print(route.path, route.methods, route.name)
    else:
        print(route.path, route.name)
