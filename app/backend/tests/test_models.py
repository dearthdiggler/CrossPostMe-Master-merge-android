import os
import sys

# ruff: noqa: E402
# Ensure backend package path is on sys.path so tests can import local modules
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from backend.models import Ad, AIAdRequest, AIAdResponse, PlatformAccount, PostedAd


def test_ad_serialization_roundtrip() -> None:
    ad = Ad(
        title="Test",
        description="Desc",
        price=9.99,
        category="electronics",
        location="NYC",
    )
    d = ad.model_dump()
    assert d["title"] == "Test"
    # reconstruct and check defaults
    ad2 = Ad(**d)
    assert ad2.status == "draft"


def test_postedad_defaults() -> None:
    pa = PostedAd(ad_id="ad1", platform="facebook")
    d = pa.model_dump()
    assert d["views"] == 0
    assert pa.status == "active"


def test_platform_account_creation() -> None:
    acc = PlatformAccount(
        platform="facebook",
        account_name="acct",
        account_email="crosspostme@gmail.com",
    )
    assert acc.platform == "facebook"
    assert acc.status == "active"


def test_ai_models() -> None:
    req = AIAdRequest(
        product_name="Widget",
        product_details="Nice",
        price=19.99,
        category="gadgets",
    )
    resp = AIAdResponse(
        title="t",
        description="d",
        suggested_categories=["a"],
        keywords=["k"],
    )
    assert isinstance(req.price, float)
    assert isinstance(resp.suggested_categories, list)
