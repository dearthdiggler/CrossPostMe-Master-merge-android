"""
Listing Assistant API Routes

AI-powered assistant for generating platform-specific listing content.
Helps users post to platforms without APIs by generating optimized,
ready-to-copy content.
"""

import logging
import os
from typing import Any, Dict, List

import openai
from auth import get_current_user
from db import get_typed_db
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Initialize OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    logger.warning("OPENAI_API_KEY not set. AI features will not work.")

router = APIRouter(prefix="/api/assistant", tags=["assistant"])
db = get_typed_db()


# ============================================================================
# Models
# ============================================================================


class ListingInput(BaseModel):
    """Input for generating listing content."""

    title: str = Field(..., description="Product title", max_length=200)
    description: str | None = Field(None, description="Product description")
    price: float = Field(..., description="Price in USD", gt=0)
    category: str | None = Field(None, description="Product category")
    condition: str = Field(default="new", description="new, used, refurbished")
    brand: str | None = Field(None, description="Brand name")
    images: List[str] = Field(default=[], description="Image URLs")
    tags: List[str] = Field(default=[], description="Keywords/tags")


class PlatformRequirements(BaseModel):
    """Platform-specific requirements and constraints."""

    platform: str = Field(..., description="Platform name")
    title_max_length: int = Field(default=80)
    description_max_length: int = Field(default=5000)
    description_style: str = Field(
        default="conversational",
        description="formal, conversational, bullet-points",
    )
    required_fields: List[str] = Field(default=[])
    emoji_allowed: bool = Field(default=True)
    html_allowed: bool = Field(default=False)


class GeneratedContent(BaseModel):
    """Generated content ready for copy/paste."""

    platform: str
    title: str
    description: str
    price_formatted: str
    suggested_tags: List[str]
    seo_keywords: List[str]
    character_counts: Dict[str, int]
    tips: List[str]


class BulkGenerateRequest(BaseModel):
    """Request to generate content for multiple platforms."""

    listing: ListingInput
    platforms: List[str] = Field(
        default=["offerup", "poshmark", "facebook", "craigslist"],
        description="Platforms to generate for",
    )


# ============================================================================
# Platform Configurations
# ============================================================================

PLATFORM_CONFIGS = {
    "offerup": PlatformRequirements(
        platform="OfferUp",
        title_max_length=80,
        description_max_length=1000,
        description_style="conversational",
        emoji_allowed=True,
        html_allowed=False,
        required_fields=["title", "price", "category"],
    ),
    "poshmark": PlatformRequirements(
        platform="Poshmark",
        title_max_length=80,
        description_max_length=500,
        description_style="bullet-points",
        emoji_allowed=True,
        html_allowed=False,
        required_fields=["title", "price", "brand", "size"],
    ),
    "facebook": PlatformRequirements(
        platform="Facebook Marketplace",
        title_max_length=100,
        description_max_length=10000,
        description_style="conversational",
        emoji_allowed=True,
        html_allowed=False,
        required_fields=["title", "price", "location"],
    ),
    "craigslist": PlatformRequirements(
        platform="Craigslist",
        title_max_length=70,
        description_max_length=4096,
        description_style="formal",
        emoji_allowed=False,
        html_allowed=True,
        required_fields=["title", "price"],
    ),
    "mercari": PlatformRequirements(
        platform="Mercari",
        title_max_length=80,
        description_max_length=1000,
        description_style="conversational",
        emoji_allowed=True,
        html_allowed=False,
        required_fields=["title", "price", "category", "brand"],
    ),
    "ebay": PlatformRequirements(
        platform="eBay",
        title_max_length=80,
        description_max_length=32000,
        description_style="formal",
        emoji_allowed=False,
        html_allowed=True,
        required_fields=["title", "price", "category"],
    ),
}


# ============================================================================
# AI Generation Functions
# ============================================================================


async def generate_optimized_title(
    original_title: str,
    platform_config: PlatformRequirements,
    brand: str | None = None,
    tags: List[str] | None = None,
) -> str:
    """Generate platform-optimized title using AI."""

    if not openai.api_key:
        # Fallback: Simple truncation
        return original_title[: platform_config.title_max_length]

    max_length = platform_config.title_max_length
    platform = platform_config.platform

    prompt = f"""Generate an optimized product title for {platform}.

Original title: {original_title}
Brand: {brand or 'N/A'}
Tags: {', '.join(tags or [])}

Requirements:
- Maximum {max_length} characters
- Include brand if provided
- Include key selling points
- SEO-friendly
- No emoji: {not platform_config.emoji_allowed}

Return ONLY the optimized title, nothing else."""

    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0.7,
        )

        generated_title = str(response.choices[0].message.content).strip()
        return str(generated_title[: platform_config.title_max_length])

    except Exception as e:
        logger.error(f"AI title generation failed: {e}")
        return original_title[: platform_config.title_max_length]


async def generate_optimized_description(
    title: str,
    original_description: str | None,
    platform_config: PlatformRequirements,
    condition: str = "new",
    brand: str | None = None,
    price: float = 0,
) -> str:
    """Generate platform-optimized description using AI."""

    if not openai.api_key:
        # Fallback: Return original or placeholder
        return original_description or f"For sale: {title}. Price: ${price:.2f}"

    max_length = platform_config.description_max_length
    platform = platform_config.platform
    style = platform_config.description_style

    prompt = f"""Generate a compelling product description for {platform}.

Product: {title}
Brand: {brand or 'Generic'}
Condition: {condition}
Price: ${price:.2f}
Original description: {original_description or 'None provided'}

Requirements:
- Maximum {max_length} characters
- Style: {style}
- Condition: {condition}
- Emoji allowed: {platform_config.emoji_allowed}
- HTML allowed: {platform_config.html_allowed}
- Highlight key features and benefits
- Create urgency (limited availability, great deal)
- End with call-to-action

Return ONLY the description, nothing else."""

    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.8,
        )

        generated_desc = str(response.choices[0].message.content).strip()
        return str(generated_desc[: platform_config.description_max_length])

    except Exception as e:
        logger.error(f"AI description generation failed: {e}")
        return (original_description or f"For sale: {title}")[
            : platform_config.description_max_length
        ]


async def generate_tags(
    title: str, description: str | None, category: str | None
) -> List[str]:
    """Generate SEO tags using AI."""

    if not openai.api_key:
        # Fallback: Extract from title
        return title.lower().split()[:10]

    prompt = f"""Generate 10-15 SEO-friendly tags/keywords for this product:

Title: {title}
Description: {description or 'N/A'}
Category: {category or 'N/A'}

Requirements:
- Relevant search terms
- Mix of general and specific
- Include brand/model if applicable
- Common misspellings if relevant
- Lowercase, comma-separated

Return ONLY the tags, nothing else."""

    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.6,
        )

        tags_text = response.choices[0].message.content.strip()
        tags = [tag.strip() for tag in tags_text.split(",")]
        return tags[:15]

    except Exception as e:
        logger.error(f"AI tag generation failed: {e}")
        return title.lower().split()[:10]


def format_price_for_platform(price: float, platform: str) -> str:
    """Format price according to platform conventions."""

    price_map = {
        "offerup": f"${price:.0f}",  # No decimals
        "poshmark": f"${price:.2f}",
        "facebook": f"${price:.0f}",
        "craigslist": f"${price:.0f}",
        "mercari": f"${price:.2f}",
        "ebay": f"${price:.2f}",
    }

    return price_map.get(platform, f"${price:.2f}")


def generate_platform_tips(platform: str, listing: ListingInput) -> List[str]:
    """Generate platform-specific posting tips."""

    tips_map = {
        "offerup": [
            "✅ Post during peak hours (6-9 PM local time)",
            "📸 Use well-lit photos with plain background",
            "💬 Respond to messages within 1 hour",
            "📍 Set accurate location for local pickup",
            "🏷️ Mark 'Firm on Price' if not negotiable",
        ],
        "poshmark": [
            "👗 Include brand name in title",
            "📏 List exact measurements (not just size)",
            "🏷️ Tag with brand, size, color, style",
            "📦 Offer bundle discounts",
            "🎉 Share to parties for visibility",
        ],
        "facebook": [
            "📍 List in relevant Buy & Sell groups",
            "✅ Mark availability: 'Available' or 'Pending'",
            "📞 Enable messaging for quick responses",
            "🚗 Specify if shipping or local only",
            "⭐ Link to your FB profile (builds trust)",
        ],
        "craigslist": [
            "🔒 Never share personal email in listing",
            "💰 State 'Cash only' if preferred",
            "🏪 Meet in public place for safety",
            "📅 Repost every 48 hours for visibility",
            "❌ Watch out for scams (fake checks)",
        ],
    }

    return tips_map.get(platform, ["✅ Take clear photos", "💬 Respond quickly"])


# ============================================================================
# API Endpoints
# ============================================================================


@router.post("/generate/{platform}", response_model=GeneratedContent)
async def generate_for_platform(
    platform: str,
    listing: ListingInput,
    current_user: str = Depends(get_current_user),
) -> GeneratedContent:
    """
    Generate optimized listing content for a specific platform.

    Uses AI to create platform-specific titles, descriptions, and tags
    that are ready to copy and paste.
    """

    platform_key = platform.lower()
    if platform_key not in PLATFORM_CONFIGS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Platform '{platform}' not supported. Available: {list(PLATFORM_CONFIGS.keys())}",
        )

    config = PLATFORM_CONFIGS[platform_key]

    # Generate optimized content
    title = await generate_optimized_title(
        listing.title, config, listing.brand, listing.tags
    )

    description = await generate_optimized_description(
        title,
        listing.description,
        config,
        listing.condition,
        listing.brand,
        listing.price,
    )

    tags = await generate_tags(title, description, listing.category)

    price_formatted = format_price_for_platform(listing.price, platform_key)

    tips = generate_platform_tips(platform_key, listing)

    return GeneratedContent(
        platform=config.platform,
        title=title,
        description=description,
        price_formatted=price_formatted,
        suggested_tags=tags[:10],
        seo_keywords=tags,
        character_counts={
            "title": len(title),
            "description": len(description),
            "title_max": config.title_max_length,
            "description_max": config.description_max_length,
        },
        tips=tips,
    )


@router.post("/generate/bulk", response_model=List[GeneratedContent])
async def generate_bulk(
    request: BulkGenerateRequest,
    current_user: str = Depends(get_current_user),
) -> List[GeneratedContent]:
    """
    Generate optimized content for multiple platforms at once.

    Perfect for cross-posting - generates all listings in one API call.
    """

    results = []

    for platform in request.platforms:
        try:
            generated = await generate_for_platform(
                platform, request.listing, current_user
            )
            results.append(generated)
        except HTTPException:
            # Skip unsupported platforms
            continue
        except Exception as e:
            logger.error(f"Failed to generate for {platform}: {e}")
            continue

    if not results:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to generate content for any platform",
        )

    return results


@router.get("/platforms")
async def get_supported_platforms() -> Dict[str, Any]:
    """
    Get list of supported platforms and their requirements.
    """

    platforms = {}
    for key, config in PLATFORM_CONFIGS.items():
        platforms[key] = {
            "name": config.platform,
            "title_max_length": config.title_max_length,
            "description_max_length": config.description_max_length,
            "description_style": config.description_style,
            "emoji_allowed": config.emoji_allowed,
            "html_allowed": config.html_allowed,
            "required_fields": config.required_fields,
        }

    return {"platforms": platforms, "total": len(platforms)}


@router.post("/optimize-price")
async def optimize_price(
    title: str,
    current_price: float,
    category: str | None = None,
    condition: str = "new",
    current_user: str = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Get AI-powered pricing suggestions based on market data.
    """

    if not openai.api_key:
        return {
            "suggested_price": current_price,
            "confidence": "low",
            "reason": "AI not configured",
        }

    prompt = f"""Analyze this product and suggest optimal pricing:

Product: {title}
Category: {category or 'General'}
Condition: {condition}
Current Price: ${current_price:.2f}

Provide:
1. Suggested price (be realistic)
2. Price range (min-max)
3. Reasoning

Format as JSON."""

    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.5,
        )

        # Parse AI response (simplified - would need better parsing)
        suggestion_text = response.choices[0].message.content

        return {
            "current_price": current_price,
            "suggestion": suggestion_text,
            "confidence": "medium",
        }

    except Exception as e:
        logger.error(f"Price optimization failed: {e}")
        return {
            "suggested_price": current_price,
            "confidence": "low",
            "error": str(e),
        }
