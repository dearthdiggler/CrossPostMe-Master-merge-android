from services.diagram import generate_ad_mermaid


def test_generate_basic_mermaid():
    ad = {"id": "ad1", "title": "Test Ad", "owner_id": "user1"}
    posted = []
    mermaid = generate_ad_mermaid(ad, posted)
    assert "flowchart TB" in mermaid
    assert "Create Ad" in mermaid


def test_generate_with_marketplace_nodes():
    ad = {"id": "ad2", "title": "Market Ad", "owner_id": "user2"}
    posted = [
        {"platform": "eBay", "ad_id": "ad2"},
        {"platform": "Craigslist", "ad_id": "ad2"},
    ]
    mermaid = generate_ad_mermaid(ad, posted)
    # Expect eBay and Craigslist nodes
    assert "eBay" in mermaid
    assert "Craigslist" in mermaid
