import random
import os
from typing import Any

from fastapi import APIRouter, Depends

from auth import get_current_user
from models import AIAdRequest, AIAdResponse

# Feature flags
USE_SUPABASE = os.getenv("USE_SUPABASE", "true").lower() in ("true", "1", "yes")
PARALLEL_WRITE = os.getenv("PARALLEL_WRITE", "true").lower() in ("true", "1", "yes")

router = APIRouter(prefix="/api/ai", tags=["ai"])


# AI-powered ad generation (mocked)
@router.post("/generate-ad", response_model=AIAdResponse)
async def generate_ad(request: AIAdRequest, user_id: str = Depends(get_current_user)) -> AIAdResponse:
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
        request.category.lower(),
        ["General", "For Sale", "Miscellaneous"],
    )

    # Generate keywords
    keywords = [
        product.lower(),
        f"{product.lower()} for sale",
        f"buy {product.lower()}",
        f"cheap {product.lower()}",
        request.category.lower(),
    ]

    response = AIAdResponse(
        title=title,
        description=description,
        suggested_categories=suggested_categories,
        keywords=keywords,
    )

    # Log AI usage to Supabase
    if USE_SUPABASE:
        try:
            from supabase_db import get_supabase
            client = get_supabase()
            if client:
                bi_data = {
                    "user_id": user_id,
                    "event_type": "ai_ad_generated",
                    "event_data": {
                        "request": request.dict(),
                        "response": response.dict(),
                        "model": "mock_ai_v1"
                    }
                }
                client.table("business_intelligence").insert(bi_data).execute()
        except Exception as e:
            # Log error but don't fail the request
            print(f"Failed to log AI usage to Supabase: {e}")

    return response


# AI ad optimization suggestions
@router.post("/optimize-ad")
async def optimize_ad(title: str, description: str, user_id: str = Depends(get_current_user)) -> dict[str, Any]:
    suggestions = [
        "Add more specific details about the product condition",
        "Include measurements or dimensions",
        "Add a clear call-to-action",
        "Mention delivery/pickup options",
        "Use bullet points for better readability",
    ]

    result = {
        "score": random.randint(60, 95),
        "suggestions": random.sample(suggestions, k=random.randint(2, 4)),
        "estimated_views": random.randint(200, 800),
        "estimated_leads": random.randint(5, 25),
    }

    # Log AI usage to Supabase
    if USE_SUPABASE:
        try:
            from supabase_db import get_supabase
            client = get_supabase()
            if client:
                bi_data = {
                    "user_id": user_id,
                    "event_type": "ai_ad_optimized",
                    "event_data": {
                        "title": title,
                        "description_length": len(description),
                        "score": result["score"],
                        "suggestions_count": len(result["suggestions"])
                    }
                }
                client.table("business_intelligence").insert(bi_data).execute()
        except Exception as e:
            print(f"Failed to log AI optimization to Supabase: {e}")

    return result


# AI title optimization
@router.post("/optimize-title")
async def optimize_title(title: str, category: str = None, user_id: str = Depends(get_current_user)) -> dict[str, Any]:
    """Optimize ad title for better performance."""
    # Mock title optimization
    optimized_titles = [
        f"🔥 {title} - Best Deal!",
        f"Premium {title} - Excellent Condition",
        f"{title} - Must See!",
        f"⭐ {title} - Top Quality",
        f"💯 {title} - Perfect Condition"
    ]

    result = {
        "original_title": title,
        "optimized_title": random.choice(optimized_titles),
        "improvement_score": random.randint(15, 40),
        "estimated_click_increase": f"{random.randint(20, 50)}%",
        "reasoning": "Added engaging emoji and power words to increase visibility"
    }

    # Log AI usage to Supabase
    if USE_SUPABASE:
        try:
            from supabase_db import get_supabase
            client = get_supabase()
            if client:
                bi_data = {
                    "user_id": user_id,
                    "event_type": "ai_title_optimized",
                    "event_data": {
                        "original_title": title,
                        "category": category,
                        "improvement_score": result["improvement_score"]
                    }
                }
                client.table("business_intelligence").insert(bi_data).execute()
        except Exception as e:
            print(f"Failed to log AI title optimization to Supabase: {e}")

    return result


# AI price suggestions
@router.post("/suggest-price")
async def suggest_price(
    product_name: str,
    category: str,
    condition: str = "good",
    market_location: str = None,
    user_id: str = Depends(get_current_user)
) -> dict[str, Any]:
    """Suggest optimal pricing for a product."""
    # Mock price suggestions based on category
    base_prices = {
        "electronics": {"poor": 50, "good": 150, "excellent": 300},
        "furniture": {"poor": 100, "good": 300, "excellent": 600},
        "vehicles": {"poor": 2000, "good": 8000, "excellent": 15000},
        "appliances": {"poor": 75, "good": 200, "excellent": 400},
        "real estate": {"poor": 50000, "good": 150000, "excellent": 300000},
    }

    base_price = base_prices.get(category.lower(), {"poor": 25, "good": 75, "excellent": 150})[condition.lower()]

    # Add some randomization
    suggested_price = base_price * random.uniform(0.8, 1.2)

    result = {
        "product": product_name,
        "category": category,
        "condition": condition,
        "suggested_price": round(suggested_price, 2),
        "price_range": {
            "min": round(suggested_price * 0.8, 2),
            "max": round(suggested_price * 1.2, 2)
        },
        "confidence": random.randint(70, 95),
        "market_comparison": f"Based on {random.randint(50, 200)} similar listings",
        "recommendations": [
            "Consider condition when setting final price",
            "Check local market rates",
            "Price slightly below market for faster sale"
        ]
    }

    # Log AI usage to Supabase
    if USE_SUPABASE:
        try:
            from supabase_db import get_supabase
            client = get_supabase()
            if client:
                bi_data = {
                    "user_id": user_id,
                    "event_type": "ai_price_suggested",
                    "event_data": {
                        "product": product_name,
                        "category": category,
                        "condition": condition,
                        "suggested_price": result["suggested_price"],
                        "confidence": result["confidence"]
                    }
                }
                client.table("business_intelligence").insert(bi_data).execute()
        except Exception as e:
            print(f"Failed to log AI price suggestion to Supabase: {e}")

    return result
