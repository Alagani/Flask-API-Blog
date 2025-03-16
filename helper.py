from auth import *

@app.after_request
def add_no_cache(response):
    response.headers["Cache-Control"] = "no-store"
    return response