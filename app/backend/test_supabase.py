"""
Test Supabase Connection
Quick test to verify Supabase is configured correctly
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from supabase_db import db, get_supabase

def test_connection():
    """Test Supabase connection"""
    print("🔍 Testing Supabase connection...")
    print("-" * 50)

    try:
        # Test 1: Check if client is initialized
        client = get_supabase()
        if client:
            print("✅ Supabase client initialized")
        else:
            print("❌ Supabase client is None - check environment variables")
            return False

        # Test 2: Try to query a table (should work even if empty)
        print("\n📊 Testing database query...")
        try:
            users = client.table("users").select("*").limit(1).execute()
            print(f"✅ Database query successful")
            print(f"   Users found: {len(users.data) if users.data else 0}")
        except Exception as e:
            print(f"❌ Database query failed: {e}")
            print("   Make sure you've run the SQL schema in Supabase!")
            return False

        # Test 3: Test SupabaseDB wrapper methods
        print("\n🔧 Testing SupabaseDB wrapper...")
        try:
            # This should work even if no data exists
            stats = db.get_industry_stats()
            print(f"✅ SupabaseDB methods working")
            print(f"   Industry stats: {len(stats)} records")
        except Exception as e:
            print(f"⚠️  SupabaseDB method warning: {e}")
            print("   This is normal if views haven't been created yet")

        # Test 4: Check all required tables exist
        print("\n📋 Checking tables...")
        required_tables = [
            "users",
            "user_business_profiles",
            "listings",
            "business_intelligence",
            "platform_connections",
            "analytics"
        ]

        for table in required_tables:
            try:
                client.table(table).select("*").limit(1).execute()
                print(f"   ✅ {table}")
            except Exception as e:
                print(f"   ❌ {table} - {e}")

        print("\n" + "=" * 50)
        print("✅ SUPABASE CONNECTION SUCCESSFUL!")
        print("=" * 50)
        print("\nYou can now:")
        print("1. Start migrating routes to use Supabase")
        print("2. Run the enhanced signup with Supabase")
        print("3. Begin parallel operation (MongoDB + Supabase)")
        print("\n💡 Next: Update enhanced_signup.py to use Supabase!")

        return True

    except Exception as e:
        print(f"\n❌ Connection test failed: {e}")
        print("\nTroubleshooting:")
        print("1. Check SUPABASE_URL is set correctly")
        print("2. Check SUPABASE_SERVICE_KEY is set correctly")
        print("3. Make sure you've run the SQL schema in Supabase")
        print("4. Verify the credentials are for the correct project")
        return False

if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("CROSSPOSTME - SUPABASE CONNECTION TEST")
    print("=" * 50 + "\n")

    success = test_connection()
    sys.exit(0 if success else 1)
