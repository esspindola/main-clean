from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import auth, products, inventory

app = FastAPI(title='CSM API', description="Headless CSM for Zatobox", version="1.0.0")

# CORS config (adjust origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(inventory.router)

@app.get("/")
def root():
    return {"message": "CSM API is running", "docs":"/docs"}
