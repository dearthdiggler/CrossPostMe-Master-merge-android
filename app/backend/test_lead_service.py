"""Test script for LeadService
Tests lead creation, matching, and deduplication
"""

import asyncio
from datetime import datetime
from typing import Any

from backend.services.lead_service import LeadService
from motor.motor_asyncio import AsyncIOMotorClient


async def test_lead_service() -> None:
    print("=" * 60)
    print("Testing LeadService")
    print("=" * 60)

    # Connect to MongoDB
    client: Any = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.crosspostme

    try:
        # Test connection
        await client.admin.command("ping")
        print("✅ Connected to MongoDB")

        # Create service
        lead_service = LeadService(db)
        print("✅ LeadService initialized")

        # Test 1: Create new lead
        print("\n" + "=" * 60)
        print("Test 1: Create new lead from message")
        print("=" * 60)

        message_data = {
            "id": "msg_test_123",
            "user_id": "user_test",
            "platform": "craigslist",
            "sender_email": "test@example.com",
            "sender_name": "Test User",
            "sender_phone": "+1-555-1234",
            "message_text": "Is this still available?",
            "received_at": datetime.now().isoformat(),
            "ad_id": "ad_test_001",
        }

        lead_id = await lead_service.find_or_create_lead(message_data)
        print(f"✅ Lead created: {lead_id}")

        # Verify lead was created
        lead = await db.leads.find_one({"id": lead_id})
        if lead:
            print(f"   - Contact Name: {lead.get('contact_name')}")
            print(f"   - Contact Email: {lead.get('contact_email')}")
            print(f"   - Contact Phone: {lead.get('contact_phone')}")
            print(f"   - Platform: {lead.get('platform')}")
            print(f"   - Status: {lead.get('status')}")

        # Test 2: Match existing lead by email (Tier 1)
        print("\n" + "=" * 60)
        print("Test 2: Match existing lead by exact email")
        print("=" * 60)

        message_data2 = {
            "id": "msg_test_456",
            "user_id": "user_test",
            "platform": "craigslist",
            "sender_email": "test@example.com",
            "sender_name": "Different Name",  # Different name, same email
            "message_text": "What's your best price?",
            "received_at": datetime.now().isoformat(),
            "ad_id": "ad_test_001",
        }

        lead_id2 = await lead_service.find_or_create_lead(message_data2)
        print(f"✅ Lead matched: {lead_id2}")
        print(f"✅ Same lead as before? {lead_id == lead_id2}")

        if lead_id == lead_id2:
            print("   ✓ Tier 1 matching (exact email) works!")

        # Test 3: Match by phone (Tier 2)
        print("\n" + "=" * 60)
        print("Test 3: Match existing lead by phone")
        print("=" * 60)

        message_data3 = {
            "id": "msg_test_789",
            "user_id": "user_test",
            "platform": "craigslist",
            "sender_phone": "+1-555-1234",
            "sender_name": "Phone User",
            "message_text": "Still available?",
            "received_at": datetime.now().isoformat(),
            "ad_id": "ad_test_001",
        }

        lead_id3 = await lead_service.find_or_create_lead(message_data3)
        print(f"✅ Lead matched: {lead_id3}")
        print(f"✅ Same lead as before? {lead_id == lead_id3}")

        if lead_id == lead_id3:
            print("   ✓ Tier 2 matching (exact phone) works!")

        # Test 4: Create different lead
        print("\n" + "=" * 60)
        print("Test 4: Create different lead (different contact)")
        print("=" * 60)

        message_data4 = {
            "id": "msg_test_999",
            "user_id": "user_test",
            "platform": "craigslist",
            "sender_email": "different@example.com",
            "sender_name": "Another User",
            "sender_phone": "+1-555-9999",
            "message_text": "Interested!",
            "received_at": datetime.now().isoformat(),
            "ad_id": "ad_test_001",
        }

        lead_id4 = await lead_service.find_or_create_lead(message_data4)
        print(f"✅ New lead created: {lead_id4}")
        print(f"✅ Different from first lead? {lead_id != lead_id4}")

        if lead_id != lead_id4:
            print("   ✓ Creates separate lead for different contact!")

        # Test 5: Fuzzy matching
        print("\n" + "=" * 60)
        print("Test 5: Fuzzy name matching (same domain, similar name)")
        print("=" * 60)

        message_data5 = {
            "id": "msg_test_555",
            "user_id": "user_test",
            "platform": "craigslist",
            "sender_email": "john.doe@acme.com",
            "sender_name": "John Doe",
            "message_text": "Hello!",
            "received_at": datetime.now().isoformat(),
            "ad_id": "ad_test_002",
        }

        lead_id5 = await lead_service.find_or_create_lead(message_data5)
        print(f"✅ Lead created: {lead_id5}")

        message_data6 = {
            "id": "msg_test_666",
            "user_id": "user_test",
            "platform": "craigslist",
            "sender_email": "jdoe@acme.com",  # Same domain, different prefix
            "sender_name": "Doe, John",  # Name reversed
            "message_text": "Follow up",
            "received_at": datetime.now().isoformat(),
            "ad_id": "ad_test_002",
        }

        lead_id6 = await lead_service.find_or_create_lead(message_data6)
        print(f"✅ Lead matched/created: {lead_id6}")
        print(f"✅ Fuzzy matched? {lead_id5 == lead_id6}")

        if lead_id5 == lead_id6:
            print("   ✓ Tier 3 fuzzy matching works!")
        else:
            print(
                "   ℹ Fuzzy match didn't reach threshold (expected for different emails)",
            )

        # Summary
        print("\n" + "=" * 60)
        print("Summary")
        print("=" * 60)

        # Count leads created
        lead_count = await db.leads.count_documents({"user_id": "user_test"})
        print(f"✅ Total leads created for test user: {lead_count}")

        # List all test leads
        print("\n📋 All test leads:")
        test_leads = await db.leads.find({"user_id": "user_test"}).to_list(100)
        for i, lead in enumerate(test_leads, 1):
            print(f"   {i}. {lead['id']}")
            print(f"      - Email: {lead.get('contact_email', 'N/A')}")
            print(f"      - Phone: {lead.get('contact_phone', 'N/A')}")
            print(f"      - Name: {lead.get('contact_name', 'N/A')}")
            print(f"      - Messages: {len(lead.get('message_ids', []))}")

        print("\n" + "=" * 60)
        print("✅ All tests completed!")
        print("=" * 60)

        # Cleanup option (commented out by default)
        # Uncomment to remove test data:
        # print("\n🧹 Cleaning up test data...")
        # await db.leads.delete_many({"user_id": "user_test"})
        # print("✅ Test data removed")

    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback

        traceback.print_exc()
    finally:
        client.close()
        print("\n👋 Connection closed")


if __name__ == "__main__":
    # This script is executed directly for manual testing; return type is None
    asyncio.run(test_lead_service())
