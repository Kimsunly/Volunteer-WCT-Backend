# 🎯 Admin Backend API Reference

**Version:** 1.0.0  
**Base URL:** `http://localhost:8000/admin`  
**Authentication:** Bearer Token (Admin role required)

---

## 📋 Table of Contents

1. [Authentication](#authentication)
2. [Dashboard](#dashboard)
3. [Organizers](#organizers)
4. [Categories](#categories)
5. [Opportunities](#opportunities)
6. [Blogs](#blogs)
7. [Community](#community)
8. [Users](#users)
9. [Comments](#comments)
10. [Donations](#donations)
11. [Error Responses](#error-responses)

---

## 🔐 Authentication

All admin endpoints require authentication with admin role.

### Request Headers
```http
Authorization: Bearer <jwt_token>
```

### How to Get Token
```bash
# Login as admin user
POST /api/auth/login
Content-Type: application/json

{
  "email": "admin@example.com",
  "password": "your-password"
}

# Response includes token in cookie or body
```

---

## 📊 Dashboard

### Get Metrics

```http
GET /admin/metrics
```

**Description:** Get dashboard aggregates (donations total, counts by status)

**Response 200:**
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

## 👥 Organizers

### List Organizers

```http
GET /admin/organizers?status={status}&search={search}&limit={limit}&offset={offset}
```

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| status | string | No | Filter: `pending`, `verified`, `rejected`, `suspended` |
| search | string | No | Search by organization name or email |
| limit | integer | No | Page size (1-100, default: 50) |
| offset | integer | No | Offset for pagination (default: 0) |

**Response 200:**
```json
{
  "data": [
    {
      "id": "uuid",
      "organization_name": "Green Earth Foundation",
      "contact_person": "John Doe",
      "email": "john@greenearth.org",
      "phone": "+855123456789",
      "registration_number": "ORG-2026-001",
      "address": "Phnom Penh, Cambodia",
      "website": "https://greenearth.org",
      "description": "Environmental conservation",
      "submitted_at": "2026-01-01T00:00:00Z",
      "status": "pending",
      "verified_at": null,
      "verified_by": null,
      "rejection_reason": null
    }
  ],
  "total": 100,
  "limit": 50,
  "offset": 0
}
```

### Approve Organizer

```http
POST /admin/organizers/{organizer_id}/approve
```

**Description:** Approve organizer application (changes user role to organizer, status to active)

**Response 200:**
```json
{
  "message": "Organizer approved successfully",
  "organizer_id": "uuid",
  "organization_name": "Green Earth Foundation"
}
```

**Side Effects:**
- Application status → `approved`
- User role → `organizer`
- User status → `active`
- Creates organizer profile
- Logs admin action

### Reject Organizer

```http
POST /admin/organizers/{organizer_id}/reject
```

**Request Body:**
```json
{
  "reason": "Incomplete documentation provided"
}
```

**Response 200:**
```json
{
  "message": "Organizer rejected",
  "organizer_id": "uuid",
  "reason": "Incomplete documentation provided"
}
```

### Suspend Organizer

```http
POST /admin/organizers/{organizer_id}/suspend
```

**Request Body:**
```json
{
  "reason": "Violation of terms of service"
}
```

**Response 200:**
```json
{
  "message": "Organizer suspended",
  "organizer_id": "uuid",
  "reason": "Violation of terms of service"
}
```

---

## 🏷️ Categories

### List Categories

```http
GET /admin/categories?active_only={boolean}
```

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| active_only | boolean | No | Show only active categories |

**Response 200:**
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

### Create Category

```http
POST /admin/categories
```

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

**Response 201:**
```json
{
  "id": "uuid",
  "name": "Technology",
  "description": "Tech volunteering opportunities",
  "icon": "💻",
  "color": "#8B5CF6",
  "active": true,
  "created_at": "2026-01-10T12:00:00Z",
  "updated_at": null
}
```

### Update Category

```http
PUT /admin/categories/{category_id}
```

**Request Body (all fields optional):**
```json
{
  "name": "Technology & Innovation",
  "description": "Updated description",
  "icon": "🚀",
  "color": "#7C3AED",
  "active": true
}
```

**Response 200:**
```json
{
  "id": "uuid",
  "name": "Technology & Innovation",
  "description": "Updated description",
  "icon": "🚀",
  "color": "#7C3AED",
  "active": true,
  "created_at": "2026-01-10T12:00:00Z",
  "updated_at": "2026-01-10T13:00:00Z"
}
```

### Delete Category

```http
DELETE /admin/categories/{category_id}
```

**Response:** `204 No Content`

---

## 🎯 Opportunities

### List Opportunities

```http
GET /admin/opportunities?search={search}&category={category}&status={status}&visibility={visibility}&limit={limit}&offset={offset}
```

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| search | string | No | Search by title |
| category | string | No | Filter by category |
| status | string | No | Filter: `active`, `pending`, `closed` |
| visibility | string | No | Filter: `public`, `private` |
| limit | integer | No | Page size (1-100, default: 50) |
| offset | integer | No | Offset for pagination (default: 0) |

**Response 200:**
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
      "description": "Join us for beach cleanup",
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

### Public Opportunities (client-facing)

Use this endpoint to let users browse opportunities with filters and search:

```
GET /api/opportunities?limit=20&offset=0&category_slug=environment&location_slug=phnom-penh&q=beach&visibility=public
```

Query parameters supported:
- `limit` (int): page size (1-100)
- `offset` (int): number of items to skip
- `category_slug` (string): filter by category identifier
- `location_slug` (string): filter by location identifier
- `organization` (string): fuzzy match on organization name
- `q` (string, min 2 chars): search term searched against title, description, and organization
- `visibility` (string): `public` or `private` — filters on `is_private` column
- `status` (string): opportunity status (e.g., `active`, `pending`, `closed`)

Response: `OpportunityListResponse` (paginated list with total count)

Notes:
- The `q` parameter performs a case-insensitive partial match on title, description and organization using `ilike`.
- Combining filters and `q` will return rows that match all provided filters AND match the `q` expression.
- For private opportunities, users still need the access key to apply — see the Private Opportunities section for details.

### Create Opportunity

```http
POST /admin/opportunities
```

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

**Response 201:** _(Same as opportunity object)_

### Update Opportunity

```http
PUT /admin/opportunities/{opportunity_id}
```

**Request Body (all fields optional):**
```json
{
  "title": "Updated Title",
  "status": "closed",
  "visibility": "private"
}
```

**Response 200:** _(Updated opportunity object)_

### Delete Opportunity

```http
DELETE /admin/opportunities/{opportunity_id}
```

**Response:** `204 No Content`

---

## � Private Opportunities & CV upload

This project now supports "private" (restricted) opportunities and an optional applicant CV upload flow.

Database changes
- Run the SQL migration in `migrations/001_add_private_opportunities_and_cvs.sql` to add the required columns:
  - `opportunities.is_private boolean DEFAULT false`
  - `opportunities.access_key_hash text` (stores hashed access key)
  - `applications.cv_url text` (optional public URL to applicant CV)

Private opportunity behaviour
- Organizers may create opportunities that are private by setting `is_private` to true and providing a plain `access_key` when creating the opportunity. The API will store only a hashed value in `access_key_hash`.
- Users must provide the correct access key when applying to a private opportunity. The server compares the SHA-256 hash of the provided key to the stored `access_key_hash` and rejects the application if it doesn't match.

Organizer endpoints (create/update)
- The create opportunity route (organizer-authenticated, multipart/form-data) accepts two optional privacy fields:
  - `is_private` (form boolean) — set true to make the opportunity private
  - `access_key` (form string) — plain-text key required when making the opportunity private on create/update

Application / Registration endpoints
- Apply (JSON)

```
POST /api/applications/
Content-Type: application/json
Authorization: Bearer <token>

{
  "opportunity_id": 123,
  "name": "Jane Doe",
  "skills": "Event Coordination",
  "availability": "Weekends",
  "email": "jane@example.com",
  "phone_number": "+855 12 345 678",
  "sex": "female",
  "message": "Happy to help",
  "access_key": "if-required-for-private",    # optional unless opportunity is private
  "cv_url": "https://.../user_uuid/.../cv.pdf"   # optional
}
```

- Apply (multipart + optional CV upload in one request)

```
POST /api/applications/multipart
Authorization: Bearer <token>
Content-Type: multipart/form-data

Fields:
- opportunity_id (int)
- name (string)
- skills (string)
- availability (string)
- email (string)
- phone_number (string)
- sex (string)
- message (string, optional)
- access_key (string, optional) -- required if opportunity is private
- file (file, optional) -- applicant CV (PDF/DOC/DOCX/TXT)

Response: application object (201 Created) or 403 if access_key missing/invalid for private opportunities.
```

- Upload CV only

```
POST /api/applications/upload-cv
Authorization: Bearer <token>
Content-Type: multipart/form-data

Fields:
- file: (file) PDF/DOC/DOCX/TXT

Response (200):
{
  "cv_url": "https://.../user_uuid/.../cv.pdf"
}

Usage notes
- Two-step approach (if frontend cannot multipart in one request):
  1. POST `/api/applications/upload-cv` with the CV file → get `cv_url`.
  2. POST `/api/applications/` with JSON including `cv_url`.
- Storage: the default CV bucket is `user-cvs` (configurable via `CV_BUCKET` env var). Ensure the bucket exists and has the appropriate public/signed URL policy for your needs.
- Security: access keys are hashed (SHA-256) in the DB. For stronger protection consider HMAC or bcrypt/argon2 and rate-limiting attempts.


---

## �📝 Blogs

### List Blogs

```http
GET /admin/blogs?published_only={boolean}
```

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| published_only | boolean | No | Show only published blogs |

**Response 200:**
```json
[
  {
    "id": "uuid",
    "title": "10 Ways to Make a Difference",
    "category": "Tips",
    "image": "https://example.com/image.jpg",
    "content": "Blog content here...",
    "author": "Admin Team",
    "published": true,
    "created_at": "2026-01-01T00:00:00Z",
    "updated_at": "2026-01-05T00:00:00Z"
  }
]
```

### Create Blog

```http
POST /admin/blogs
```

**Request Body:**
```json
{
  "title": "10 Ways to Make a Difference",
  "category": "Tips",
  "image": "https://example.com/image.jpg",
  "content": "Blog content here...",
  "author": "Admin Team",
  "published": false
}
```

**Response 201:** _(Blog object)_

### Update Blog

```http
PUT /admin/blogs/{blog_id}
```

**Request Body (all fields optional):**
```json
{
  "title": "Updated Title",
  "published": true
}
```

**Toggle Publish Example:**
```json
{
  "published": true
}
```

**Response 200:** _(Updated blog object)_

### Delete Blog

```http
DELETE /admin/blogs/{blog_id}
```

**Response:** `204 No Content`

---

## 💬 Community

### List Community Posts

```http
GET /admin/community?status={status}&limit={limit}&offset={offset}
```

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| status | string | No | Filter: `all`, `pending`, `approved`, `rejected` |
| limit | integer | No | Page size (1-100, default: 50) |
| offset | integer | No | Offset for pagination (default: 0) |

**Response 200:**
```json
{
  "data": [
    {
      "id": "uuid",
      "organizer_id": "uuid",
      "organizer_name": "Green Earth Foundation",
      "title": "Our Latest Impact Report",
      "title_kh": "របាយការណ៍ផលប៉ះពាល់ចុងក្រោយរបស់យើង",
      "content": "We're excited to share...",
      "content_kh": "យើងរំភើបក្នុងការចែករំលែក...",
      "category": "update",
      "images": ["url1", "url2"],
      "visibility": "public",
      "likes": 125,
      "comments": 23,
      "status": "pending",
      "tags": ["impact", "report"],
      "created_at": "2026-01-10T00:00:00Z",
      "rejection_reason": null
    }
  ],
  "total": 50,
  "limit": 50,
  "offset": 0
}
```

### Approve Community Post

```http
POST /admin/community/{post_id}/approve
```

**Response 200:**
```json
{
  "message": "Community post approved",
  "post_id": "uuid"
}
```

### Reject Community Post

```http
POST /admin/community/{post_id}/reject
```

**Request Body:**
```json
{
  "reason": "Content violates community guidelines"
}
```

**Response 200:**
```json
{
  "message": "Community post rejected",
  "post_id": "uuid",
  "reason": "Content violates community guidelines"
}
```

### Delete Community Post

```http
DELETE /admin/community/{post_id}
```

**Response:** `204 No Content`

---

## 👤 Users

### List Users

```http
GET /admin/users?search={search}&role={role}&limit={limit}&offset={offset}
```

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| search | string | No | Search by name or email |
| role | string | No | Filter: `user`, `organizer`, `admin` |
| limit | integer | No | Page size (1-100, default: 50) |
| offset | integer | No | Offset for pagination (default: 0) |

**Response 200:**
```json
[
  {
    "id": "uuid",
    "name": "Jane Smith",
    "email": "jane@example.com",
    "role": "user",
    "status": "active",
    "avatar": "https://example.com/avatar.jpg",
    "created_at": "2026-01-01T00:00:00Z"
  }
]
```

### Change User Role

```http
POST /admin/users/{user_id}/role
```

**Request Body:**
```json
{
  "role": "organizer"
}
```

**Allowed Roles:** `user`, `organizer`, `admin`

**Response 200:**
```json
{
  "message": "User role updated",
  "user_id": "uuid",
  "new_role": "organizer"
}
```

### Deactivate User

```http
POST /admin/users/{user_id}/deactivate
```

**Request Body:**
```json
{
  "reason": "User requested account closure"
}
```

**Response 200:**
```json
{
  "message": "User deactivated",
  "user_id": "uuid"
}
```

---

## 💭 Comments

### List Comments

```http
GET /admin/comments?status={status}&limit={limit}&offset={offset}
```

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| status | string | No | Filter: `visible`, `hidden`, `flagged` |
| limit | integer | No | Page size (1-100, default: 50) |
| offset | integer | No | Offset for pagination (default: 0) |

**Response 200:**
```json
[
  {
    "id": "uuid",
    "user_id": "uuid",
    "user_name": "John Doe",
    "opportunity_id": "uuid",
    "community_post_id": null,
    "content": "Great initiative!",
    "status": "visible",
    "created_at": "2026-01-10T00:00:00Z"
  }
]
```

### Hide Comment

```http
POST /admin/comments/{comment_id}/hide
```

**Response 200:**
```json
{
  "message": "Comment hidden",
  "comment_id": "uuid"
}
```

### Approve Comment

```http
POST /admin/comments/{comment_id}/approve
```

**Response 200:**
```json
{
  "message": "Comment approved",
  "comment_id": "uuid"
}
```

---

## 💰 Donations

### List Donations

```http
GET /admin/donations?limit={limit}&offset={offset}
```

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| limit | integer | No | Page size (1-100, default: 50) |
| offset | integer | No | Offset for pagination (default: 0) |

**Response 200:**
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

## ❌ Error Responses

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
  "detail": "Resource conflict: duplicate entry"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error: [error details]"
}
```

---

## 📌 Notes

### Date/Time Format
All timestamps use ISO 8601 format:
```
2026-01-10T12:30:45Z
```

### Pagination
Standard pagination using `limit` and `offset`:
- Default limit: 50
- Max limit: 100
- Offset starts at 0

### Sorting
Most list endpoints sort by `created_at DESC` by default.

### Filtering
Use query parameters for filtering. Multiple filters are combined with AND logic.

### Search
Search is case-insensitive and uses partial matching (ILIKE in PostgreSQL).

---

**Last Updated:** January 10, 2026  
**Maintained By:** Backend Team
