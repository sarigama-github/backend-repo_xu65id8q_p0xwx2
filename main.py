import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import create_document, get_documents, db
from schemas import Property, Inquiry

app = FastAPI(title="Asylen Ventures API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Asylen Ventures Backend Running"}

@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = getattr(db, 'name', None) or "✅ Set"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response

# ---------------- Real Estate Endpoints ----------------

class InquiryRequest(Inquiry):
    pass

@app.get("/api/properties", response_model=List[Property])
def list_properties(city: Optional[str] = None, featured: Optional[bool] = None):
    if db is None:
        # Return curated demo properties when DB not available
        return _demo_properties()

    query = {}
    if city:
        query["city"] = {"$regex": f"^{city}$", "$options": "i"}
    if featured is not None:
        query["featured"] = featured

    docs = get_documents("property", query, limit=50)
    if not docs:
        # Seed a few when empty for the first time
        for p in _demo_properties():
            try:
                create_document("property", p.dict())
            except Exception:
                pass
        docs = get_documents("property", query, limit=50)

    # Serialize mongo docs to Property
    properties: List[Property] = []
    for d in docs:
        try:
            properties.append(Property(**{k: d.get(k) for k in Property.model_fields.keys()}))
        except Exception:
            continue
    return properties

@app.get("/api/properties/featured", response_model=List[Property])
def featured_properties():
    return list_properties(featured=True)

@app.post("/api/inquiries")
def create_inquiry(payload: InquiryRequest):
    try:
        if db is None:
            # Accept but not persist; emulate success
            return {"status": "accepted", "persisted": False}
        _id = create_document("inquiry", payload)
        return {"status": "ok", "id": _id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------------- Utilities ----------------

def _demo_properties() -> List[Property]:
    return [
        Property(
            title="Dal Lake Waterfront Villa",
            description="Elegant lakefront retreat with panoramic Himalayan views and private shikara access.",
            address="Boulevard Road, Dal Lake",
            city="Srinagar",
            state="Jammu & Kashmir",
            country="India",
            price=12500000,
            bedrooms=4,
            bathrooms=4.5,
            area_sqft=3800,
            images=[
                "https://images.unsplash.com/photo-1548013146-72479768bada?q=80&w=1600&auto=format&fit=crop",
                "https://images.unsplash.com/photo-1558981806-ec527fa84c39?q=80&w=1600&auto=format&fit=crop"
            ],
            featured=True,
            status="For Sale"
        ),
        Property(
            title="Gulmarg Alpine Chalet",
            description="Cozy ski-in chalet nestled among pines, minutes from gondola.",
            address="Near Gulmarg Gondola",
            city="Gulmarg",
            state="Jammu & Kashmir",
            country="India",
            price=8500000,
            bedrooms=3,
            bathrooms=3.0,
            area_sqft=2200,
            images=[
                "https://images.unsplash.com/photo-1519681393784-d120267933ba?q=80&w=1600&auto=format&fit=crop",
                "https://images.unsplash.com/photo-1519682577862-22b62b24e493?q=80&w=1600&auto=format&fit=crop"
            ],
            featured=True,
            status="For Sale"
        ),
        Property(
            title="Lidder River Retreat",
            description="Modern riverside home with sunlit interiors and cedar finishes.",
            address="Aru Valley Road",
            city="Pahalgam",
            state="Jammu & Kashmir",
            country="India",
            price=4200000,
            bedrooms=2,
            bathrooms=2.0,
            area_sqft=1400,
            images=[
                "https://images.unsplash.com/photo-1501183638710-841dd1904471?q=80&w=1600&auto=format&fit=crop",
                "https://images.unsplash.com/photo-1521401292936-0a2129a30b22?q=80&w=1600&auto=format&fit=crop"
            ],
            featured=False,
            status="For Sale"
        ),
    ]

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
