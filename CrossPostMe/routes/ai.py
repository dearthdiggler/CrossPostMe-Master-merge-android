import random

from fastapi import APIRouter
from models import AIAdRequest, AIAdResponse

router = APIRouter(prefix="/api/ai", tags=["ai"])


# AI-powered ad generation (mocked)
@router.post("/generate-ad", response_model=AIAdResponse)
async def generate_ad(request: AIAdRequest):
    # Mock AI generation
    product = request.product_name
    price = request.price

    # Generate title based on tone
    if request.tone == "urgent":
        title = f"🔥 {product} - Limited Time ${price}!"
    elif request.tone == "casual":
        title = f"{product} for sale - ${price}"
    else:
        title = f"Premium {product} - ${price}"

    # Generate description
    description = f"{request.product_details}\n\n"
    description += f"Price: ${price}\n"
    description += "\n✓ Great condition\n"
    description += "✓ Ready for pickup/delivery\n"
    description += "✓ Serious inquiries only\n\n"
    description += "Contact me for more details or to schedule a viewing!"

    # Suggest categories
    category_map = {
        "furniture": ["Home & Garden", "Furniture", "Living Room"],
        "electronics": ["Electronics", "Computers & Tech", "Mobile Phones"],
        "vehicles": ["Vehicles", "Cars & Trucks", "Motorcycles"],
        "real estate": ["Real Estate", "Apartments", "Houses for Sale"],
        "appliances": ["Home & Garden", "Appliances", "Kitchen"],
    }

    suggested_categories = category_map.get(
        request.category.lower(), ["General", "For Sale", "Miscellaneous"]
    )

    # Generate keywords
    keywords = [
        product.lower(),
        f"{product.lower()} for sale",
        f"buy {product.lower()}",
        f"cheap {product.lower()}",
        request.category.lower(),
    ]

    return AIAdResponse(
        title=title,
        description=description,
        suggested_categories=suggested_categories,
        keywords=keywords,
    )


# AI ad optimization suggestions
@router.post("/optimize-ad")
async def optimize_ad(title: str, description: str):
    suggestions = [
        "Add more specific details about the product condition",
        "Include measurements or dimensions",
        "Add a clear call-to-action",
        "Mention delivery/pickup options",
        "Use bullet points for better readability",
    ]

    return {
        "score": random.randint(60, 95),
        "suggestions": random.sample(suggestions, k=random.randint(2, 4)),
        "estimated_views": random.randint(200, 800),
        "estimated_leads": random.randint(5, 25),
    }
