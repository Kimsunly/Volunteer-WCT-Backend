# Comprehensive Admin Backend - Implementation Guide

## 📋 Overview

This implementation provides a complete FastAPI backend for admin dashboard and management features, following the frontend specifications exactly.

## 🏗️ Architecture

### Components
- **Models**: `/app/models/admin.py` - Pydantic models for all admin operations
- **Router**: `/app/routers/admin_comprehensive.py` - All admin endpoints
- **Database**: `database_migration_admin.sql` - SQL schema and RLS policies
- **Authentication**: Role-based access control (admin only)

### Tech Stack
- **Framework**: FastAPI 0.100+
- **Database**: Supabase (PostgreSQL)
- **Auth**: JWT tokens with role claims
- **Validation**: Pydantic v2

## 📦 Installation

### 1. Install Dependencies
```bash
cd Backend
pip install -r requirements.txt
```

### 2. Run Database Migration
Execute the SQL migration in Supabase SQL Editor:
```bash
# Copy contents of database_migration_admin.sql to Supabase SQL Editor
# Or use Supabase CLI:
supabase db push
```

### 3. Verify Environment Variables
Ensure `.env` has:
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key
SUPABASE_JWT_SECRET=your-jwt-secret
```

### 4. Start Server
```bash
uvicorn app.main:app --reload --port 8000
```

## 📚 API Endpoints

### Base URL
```
http://localhost:8000/admin
```

### Authentication
All endpoints require:
- **Header**: `Authorization: Bearer <jwt_token>`
- **Role**: `admin` (verified in user_profiles table)

---

## 🔍 Dashboard Metrics

### GET /admin/metrics
Get dashboard aggregates

**Response:**
```json
{
  "donations_total": 15000.50,
  "opportunities_count": {
    "active": 25,
    "pending": 5,
    "closed": 10
  },
  "organizers_count": {
    "pending": 3,
    "verified": 15,
    "rejected": 2,
    "suspended": 1
  },
  "users_count": 1250
}
```

---

## 👥 Organizers Management

### GET /admin/organizers
List organizer applications

**Query Params:**
- `status`: `pending|verified|rejected|suspended`
- `search`: Search by organization name or email
- `limit`: Page size (1-100, default 50)
- `offset`: Offset for pagination (default 0)

**Response:**
```json
{
  "data": [
    {
      "id": "uuid",
      "organization_name": "Green Earth Foundation",
      "contact_person": "John Doe",
      "email": "john@greenearth.org",
      "phone": "+855123456789",
      "status": "pending",
      "submitted_at": "2026-01-01T00:00:00Z",
      "verified_at": null,
      "reject_reason": null
    }
  ],
  "total": 100,
  "limit": 50,
  "offset": 0
}
```

### POST /admin/organizers/{organizer_id}/approve
Approve organizer application

**Response:**
```json
{
  "message": "Organizer approved successfully",
  "organizer_id": "uuid",
  "organization_name": "Green Earth Foundation"
}
```

**Side Effects:**
- Updates application status to `approved`
- Changes user role to `organizer`
- Sets user status to `active`
- Creates `organizer_profiles` entry
- Logs admin action

### POST /admin/organizers/{organizer_id}/reject
Reject organizer application

**Request Body:**
```json
{
  "reason": "Incomplete documentation provided"
}
```

**Response:**
```json
{
  "message": "Organizer rejected",
  "organizer_id": "uuid",
  "reason": "Incomplete documentation provided"
}
```

### POST /admin/organizers/{organizer_id}/suspend
Suspend organizer account

**Request Body:**
```json
{
  "reason": "Violation of terms of service"
}
```

---

## 🏷️ Categories Management

### GET /admin/categories
List all categories

**Query Params:**
- `active_only`: boolean (default false)

**Response:**
```json
[
  {
    "id": "uuid",
    "name": "Education",
    "description": "Educational volunteer opportunities",
    "icon": "📚",
    "color": "#3B82F6",
    "active": true,
    "created_at": "2026-01-01T00:00:00Z",
    "updated_at": null
  }
]
```

### POST /admin/categories
Create new category

**Request Body:**
```json
{
  "name": "Technology",
  "description": "Tech volunteering opportunities",
  "icon": "💻",
  "color": "#8B5CF6",
  "active": true
}
```

### PUT /admin/categories/{category_id}
Update category (all fields optional)

**Request Body:**
```json
{
  "name": "Technology & Innovation",
  "active": true
}
```

### DELETE /admin/categories/{category_id}
Delete category

**Response:** `204 No Content`

---

## 🎯 Opportunities Management

### GET /admin/opportunities
List all opportunities

**Query Params:**
- `search`: Search by title
- `category`: Filter by category
- `status`: `active|pending|closed`
- `visibility`: `public|private`
- `limit`: Page size (1-100, default 50)
- `offset`: Offset for pagination

**Response:**
```json
{
  "data": [
    {
      "id": "uuid",
      "title": "Beach Cleanup Drive",
      "organizer": "Green Earth Foundation",
      "organizer_id": "uuid",
      "category": "Environment",
      "location": "Sihanoukville Beach",
      "start_date": "2026-02-15",
      "end_date": "2026-02-15",
      "visibility": "public",
      "status": "active",
      "registered": 45,
      "created_at": "2026-01-10T00:00:00Z"
    }
  ],
  "total": 100,
  "limit": 50,
  "offset": 0
}
```

### POST /admin/opportunities
Create opportunity (on behalf of organizer)

**Request Body:**
```json
{
  "title": "Tree Planting Event",
  "organizer_id": "uuid",
  "category": "Environment",
  "location": "Phnom Penh",
  "start_date": "2026-03-01",
  "end_date": "2026-03-01",
  "description": "Join us for tree planting",
  "visibility": "public",
  "status": "active"
}
```

### PUT /admin/opportunities/{opportunity_id}
Update opportunity (all fields optional)

### DELETE /admin/opportunities/{opportunity_id}
Delete opportunity

---

## 📝 Blogs Management

### GET /admin/blogs
List all blogs

**Query Params:**
- `published_only`: boolean (default false)

### POST /admin/blogs
Create blog

**Request Body:**
```json
{
  "title": "10 Ways to Make a Difference",
  "category": "Tips",
  "image": "https://...",
  "content": "Blog content here...",
  "author": "Admin Team",
  "published": false
}
```

### PUT /admin/blogs/{blog_id}
Update blog (all fields optional)

**Toggle Publish Example:**
```json
{
  "published": true
}
```

### DELETE /admin/blogs/{blog_id}
Delete blog

---

## 💬 Community Moderation

### GET /admin/community
List community posts for moderation

**Query Params:**
- `status`: `all|pending|approved|rejected`
- `limit`: Page size (1-100, default 50)
- `offset`: Offset for pagination

**Response:**
```json
{
  "data": [
    {
      "id": "uuid",
      "organizer_id": "uuid",
      "organizer_name": "Green Earth Foundation",
      "title": "Our Latest Impact Report",
      "content": "We're excited to share...",
      "category": "update",
      "images": ["url1", "url2"],
      "visibility": "public",
      "likes": 125,
      "comments": 23,
      "status": "pending",
      "tags": ["impact", "report"],
      "created_at": "2026-01-10T00:00:00Z"
    }
  ],
  "total": 50,
  "limit": 50,
  "offset": 0
}
```

### POST /admin/community/{post_id}/approve
Approve community post

**Response:**
```json
{
  "message": "Community post approved",
  "post_id": "uuid"
}
```

### POST /admin/community/{post_id}/reject
Reject community post

**Request Body:**
```json
{
  "reason": "Content violates community guidelines"
}
```

### DELETE /admin/community/{post_id}
Delete community post

---

## 👤 Users Management

### GET /admin/users
List all users

**Query Params:**
- `search`: Search by name or email
- `role`: Filter by role (`user|organizer|admin`)
- `limit`: Page size (1-100, default 50)
- `offset`: Offset for pagination

**Response:**
```json
[
  {
    "id": "uuid",
    "name": "Jane Smith",
    "email": "jane@example.com",
    "role": "user",
    "status": "active",
    "avatar": "https://...",
    "created_at": "2026-01-01T00:00:00Z"
  }
]
```

### POST /admin/users/{user_id}/role
Change user role

**Request Body:**
```json
{
  "role": "organizer"
}
```

**Allowed Roles:** `user`, `organizer`, `admin`

### POST /admin/users/{user_id}/deactivate
Deactivate user account

**Request Body:**
```json
{
  "reason": "User requested account closure"
}
```

---

## 💭 Comments Moderation

### GET /admin/comments
List comments for moderation

**Query Params:**
- `status`: `visible|hidden|flagged`
- `limit`: Page size (1-100, default 50)
- `offset`: Offset for pagination

**Response:**
```json
[
  {
    "id": "uuid",
    "user_id": "uuid",
    "user_name": "John Doe",
    "opportunity_id": "uuid",
    "content": "Great initiative!",
    "status": "visible",
    "created_at": "2026-01-10T00:00:00Z"
  }
]
```

### POST /admin/comments/{comment_id}/hide
Hide comment

### POST /admin/comments/{comment_id}/approve
Approve comment (unhide)

---

## 💰 Donations View

### GET /admin/donations
List all donations (read-only, for metrics)

**Query Params:**
- `limit`: Page size (1-100, default 50)
- `offset`: Offset for pagination

**Response:**
```json
[
  {
    "id": "uuid",
    "donor_name": "Anonymous",
    "amount": 100.00,
    "currency": "USD",
    "created_at": "2026-01-10T00:00:00Z"
  }
]
```

---

## 🔒 Security

### Authentication Flow
1. User logs in via `/api/auth/login`
2. Backend returns JWT token with role claim
3. Frontend stores token in cookie
4. Every admin request includes: `Authorization: Bearer <token>`
5. Backend verifies token and checks `role=admin` in database

### Row Level Security (RLS)
All tables have RLS policies:
- **Public access**: Only approved/published content
- **Organizer access**: Their own content
- **Admin access**: Full access to everything

### Admin Action Logging
All admin actions are logged to `admin_activity_log`:
- Who performed the action (admin_id)
- What action was performed
- What resource was affected
- When it happened
- Additional details

---

## 🧪 Testing

### Test Admin Endpoints
```bash
# Set admin token
export ADMIN_TOKEN="your-admin-jwt-token"

# Test metrics
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  http://localhost:8000/admin/metrics

# Test organizers list
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  "http://localhost:8000/admin/organizers?status=pending"

# Approve organizer
curl -X POST \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  http://localhost:8000/admin/organizers/{id}/approve

# Create category
curl -X POST \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Tech","description":"Tech volunteering","active":true}' \
  http://localhost:8000/admin/categories
```

### Test Admin Access Control
```bash
# Should return 403 with user token
export USER_TOKEN="your-user-jwt-token"
curl -H "Authorization: Bearer $USER_TOKEN" \
  http://localhost:8000/admin/metrics
# Expected: 403 Forbidden
```

---

## 📊 Database Schema

### Key Tables
- `categories` - Opportunity categories
- `blogs` - Blog posts and tips
- `community_posts` - Organizer community updates
- `comments` - User comments on content
- `donations` - Donation records
- `admin_activity_log` - Audit trail

### Key Relationships
- `community_posts.organizer_id` → `user_profiles.user_id`
- `comments.user_id` → `user_profiles.user_id`
- `opportunities.organizer_id` → `organizer_profiles.user_id`

---

## 🐛 Error Handling

All endpoints return consistent error responses:

### 400 Bad Request
```json
{
  "detail": "Failed to create category: name already exists"
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden
```json
{
  "detail": "Admin access required"
}
```

### 404 Not Found
```json
{
  "detail": "Organizer application not found"
}
```

### 409 Conflict
```json
{
  "detail": "Category name already exists"
}
```

---

## 🚀 Deployment

### Production Checklist
- [ ] Use service role key in `SUPABASE_KEY`
- [ ] Enable HTTPS for all endpoints
- [ ] Set up rate limiting
- [ ] Configure CORS for production domain
- [ ] Enable audit logging
- [ ] Set up monitoring (Sentry, DataDog)
- [ ] Configure backup for database
- [ ] Set up CI/CD pipeline

### Environment Variables
```env
# Production
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key  # NOT anon key!
SUPABASE_JWT_SECRET=your-jwt-secret
ALLOWED_ORIGINS=https://your-frontend.com
DEBUG=False
```

---

## 📖 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Supabase Documentation](https://supabase.com/docs)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [JWT Authentication](https://jwt.io/)

---

## 🤝 Support

For backend team questions:
1. Check this README first
2. Review the inline code comments
3. Test with provided curl commands
4. Check Supabase logs for database errors
5. Review admin_activity_log for action history

---

## ✅ Implementation Status

### Completed ✓
- [x] All models defined in `admin.py`
- [x] All endpoints implemented in `admin_comprehensive.py`
- [x] Database migration SQL with RLS
- [x] Admin authentication middleware
- [x] Action logging
- [x] Pagination support
- [x] Filtering and search
- [x] Error handling
- [x] Documentation

### Ready for Integration ✓
- [x] API contracts match frontend requirements
- [x] Response formats match frontend expectations
- [x] Authentication flow compatible with NextAuth
- [x] CORS configured for local development
- [x] Database ready with sample data

---

**Backend Team**: You're good to go! All endpoints are ready for frontend integration. 🎉
