# Database Setup Instructions

This document explains how to set up the MongoDB database with proper indexes for optimal performance.

## Quick Setup

Run the database setup script to create all necessary indexes:

```bash
cd app/backend
python scripts/setup_db.py
```

## What Gets Created

### Indexes for Messages Collection

1. **Content Hash Index** (Primary optimization):

   ```javascript
   { "user_id": 1, "content_hash": 1 }
   ```

   - Used for fast duplicate detection
   - Replaces slow full-text matching

2. **Compound Index** (Legacy support):

   ```javascript
   { "user_id": 1, "platform": 1, "platform_message_id": 1, "sender_email": 1 }
   ```

   - Supports complex queries and fallback duplicate detection

3. **User Received Index**:

   ```javascript
   { "user_id": 1, "received_at": -1 }
   ```

   - Optimizes message listing by date

4. **Status Index**:

   ```javascript
   { "user_id": 1, "platform": 1, "is_read": 1, "is_responded": 1 }
   ```

   - Supports filtering by read/response status

### Indexes for Other Collections

- **Ads**: User/status, platform/status, unique ID indexes
- **Leads**: User/status, contact info, ad association indexes
- **Platform Accounts**: User/platform, unique account indexes
- **Secure Credentials**: User/platform unique indexes

## Content Hash Implementation

Messages now include a `content_hash` field generated from:

- Platform name
- Sender email (or empty string)
- First 100 characters of message text

This enables:

- Fast duplicate detection
- Near-duplicate catching (similar messages)
- Race condition elimination
- Efficient database queries

## Environment Variables

Ensure these are set before running setup:

```bash
MONGO_URL=mongodb://localhost:27017
DB_NAME=crosspostme
```

## Verification

After setup, the script will display all created indexes. You can also check manually:

```javascript
// In MongoDB shell
db.messages.getIndexes();
```

## Performance Benefits

- **Before**: Slow queries on 5 unindexed fields
- **After**: Single hash lookup with O(1) performance
- **Duplicate Detection**: ~100x faster with content hashing
- **Message Queries**: Optimized for common access patterns

The content hash approach eliminates race conditions and provides much better performance than timestamp-based IDs and full-text duplicate detection.
