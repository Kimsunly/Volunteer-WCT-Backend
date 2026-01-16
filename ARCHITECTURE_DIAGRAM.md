# Admin Backend Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Next.js)                       │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌──────────┐ │
│  │  Dashboard │  │ Organizers │  │Categories  │  │   ...    │ │
│  │   Admin    │  │   Admin    │  │   Admin    │  │   More   │ │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘  └────┬─────┘ │
└────────┼───────────────┼────────────────┼──────────────┼───────┘
         │               │                │              │
         │   HTTP Requests (JWT Token in Authorization header)
         │               │                │              │
┌────────▼───────────────▼────────────────▼──────────────▼───────┐
│                    FASTAPI BACKEND                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Authentication Middleware                    │  │
│  │  ┌──────────────────────────────────────────────────┐   │  │
│  │  │ require_admin(current_user)                       │   │  │
│  │  │  ✓ Verify JWT token                              │   │  │
│  │  │  ✓ Extract user_id                               │   │  │
│  │  │  ✓ Check role = admin in user_profiles           │   │  │
│  │  │  ✗ Return 403 if not admin                       │   │  │
│  │  └──────────────────────────────────────────────────┘   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              /admin Routes (28 endpoints)                 │  │
│  │                                                           │  │
│  │  GET  /admin/metrics                                     │  │
│  │                                                           │  │
│  │  GET  /admin/organizers                                  │  │
│  │  POST /admin/organizers/{id}/approve                     │  │
│  │  POST /admin/organizers/{id}/reject                      │  │
│  │  POST /admin/organizers/{id}/suspend                     │  │
│  │                                                           │  │
│  │  GET    /admin/categories                                │  │
│  │  POST   /admin/categories                                │  │
│  │  PUT    /admin/categories/{id}                           │  │
│  │  DELETE /admin/categories/{id}                           │  │
│  │                                                           │  │
│  │  GET    /admin/opportunities                             │  │
│  │  POST   /admin/opportunities                             │  │
│  │  PUT    /admin/opportunities/{id}                        │  │
│  │  DELETE /admin/opportunities/{id}                        │  │
│  │                                                           │  │
│  │  GET    /admin/blogs                                     │  │
│  │  POST   /admin/blogs                                     │  │
│  │  PUT    /admin/blogs/{id}                                │  │
│  │  DELETE /admin/blogs/{id}                                │  │
│  │                                                           │  │
│  │  GET    /admin/community                                 │  │
│  │  POST   /admin/community/{id}/approve                    │  │
│  │  POST   /admin/community/{id}/reject                     │  │
│  │  DELETE /admin/community/{id}                            │  │
│  │                                                           │  │
│  │  GET  /admin/users                                       │  │
│  │  POST /admin/users/{id}/role                             │  │
│  │  POST /admin/users/{id}/deactivate                       │  │
│  │                                                           │  │
│  │  GET  /admin/comments                                    │  │
│  │  POST /admin/comments/{id}/hide                          │  │
│  │  POST /admin/comments/{id}/approve                       │  │
│  │                                                           │  │
│  │  GET  /admin/donations                                   │  │
│  │                                                           │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Admin Action Logger                          │  │
│  │  log_admin_action(admin_id, action, target, details)     │  │
│  │    → Writes to admin_activity_log table                  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Supabase Client                              │  │
│  │  get_supabase() → Returns authenticated client            │  │
│  └──────────────────────────────────────────────────────────┘  │
└──────────────────────────┬───────────────────────────────────────┘
                           │
                           │ PostgreSQL Queries
                           │
┌──────────────────────────▼───────────────────────────────────────┐
│                   SUPABASE (PostgreSQL)                          │
│                                                                   │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────────┐  │
│  │ user_profiles  │  │   categories   │  │  opportunities   │  │
│  │ ──────────────│  │ ──────────────│  │ ──────────────  │  │
│  │ • user_id      │  │ • id           │  │ • id             │  │
│  │ • email        │  │ • name         │  │ • title          │  │
│  │ • role         │  │ • description  │  │ • organizer_id   │  │
│  │ • status       │  │ • icon         │  │ • status         │  │
│  │ • created_at   │  │ • color        │  │ • visibility     │  │
│  └────────────────┘  │ • active       │  │ • created_at     │  │
│                      └────────────────┘  └──────────────────┘  │
│                                                                   │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────────┐  │
│  │ organizer_     │  │     blogs      │  │  community_      │  │
│  │ applications   │  │ ──────────────│  │    posts         │  │
│  │ ──────────────│  │ • id           │  │ ──────────────  │  │
│  │ • id           │  │ • title        │  │ • id             │  │
│  │ • user_id      │  │ • content      │  │ • organizer_id   │  │
│  │ • org_name     │  │ • category     │  │ • title          │  │
│  │ • status       │  │ • published    │  │ • content        │  │
│  │ • reviewed_at  │  │ • author       │  │ • status         │  │
│  │ • reviewed_by  │  │ • created_at   │  │ • visibility     │  │
│  │ • rejection_   │  └────────────────┘  │ • likes          │  │
│  │   reason       │                      │ • comments       │  │
│  └────────────────┘                      └──────────────────┘  │
│                                                                   │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────────┐  │
│  │   comments     │  │   donations    │  │ admin_activity_  │  │
│  │ ──────────────│  │ ──────────────│  │      log         │  │
│  │ • id           │  │ • id           │  │ ──────────────  │  │
│  │ • user_id      │  │ • donor_name   │  │ • admin_id       │  │
│  │ • entity_type  │  │ • amount       │  │ • action         │  │
│  │ • entity_id    │  │ • currency     │  │ • target_type    │  │
│  │ • content      │  │ • created_at   │  │ • target_id      │  │
│  │ • status       │  └────────────────┘  │ • details        │  │
│  │ • created_at   │                      │ • created_at     │  │
│  └────────────────┘                      └──────────────────┘  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           Row Level Security (RLS) Policies              │  │
│  │  • Public: Read approved/published content only          │  │
│  │  • Organizers: Manage their own content                  │  │
│  │  • Admin: Full access to everything                      │  │
│  └──────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────────┘


DATA FLOW EXAMPLE: Approve Organizer
═══════════════════════════════════════

1. Frontend: Admin clicks "Approve" button
   ↓
2. API Call: POST /admin/organizers/{id}/approve
   Headers: { Authorization: "Bearer jwt_token" }
   ↓
3. Backend: require_admin() middleware
   • Verify JWT token
   • Extract user_id from token
   • Query user_profiles WHERE user_id = extracted_id
   • Check if role = 'admin'
   • ✓ Allow if admin, ✗ 403 if not
   ↓
4. Backend: approve_organizer() handler
   • Get application from organizer_applications
   • Check status (only approve if pending)
   • Update organizer_applications.status = 'approved'
   • Update user_profiles.role = 'organizer'
   • Update user_profiles.status = 'active'
   • Insert/Update organizer_profiles
   • Log to admin_activity_log
   ↓
5. Response: 200 OK
   {
     "message": "Organizer approved successfully",
     "organizer_id": "uuid",
     "organization_name": "Green Earth Foundation"
   }
   ↓
6. Frontend: Display success message, refresh list


SECURITY LAYERS
════════════════

Layer 1: JWT Authentication
├─ Verify token signature
├─ Check expiration
└─ Extract user claims

Layer 2: Role Authorization
├─ Query user_profiles for role
├─ Verify role = 'admin'
└─ Reject if not admin (403)

Layer 3: Row Level Security (RLS)
├─ Supabase enforces at database level
├─ Even with service key, follows policies
└─ Admin has full access via RLS policy

Layer 4: Input Validation
├─ Pydantic models validate all inputs
├─ Type checking, min/max length
└─ Custom validators for business rules

Layer 5: Audit Logging
├─ All actions logged to admin_activity_log
├─ Who, what, when, target, details
└─ Immutable audit trail


PAGINATION PATTERN
══════════════════

Request:
GET /admin/organizers?status=pending&limit=10&offset=0

Backend Processing:
1. Parse query params (limit, offset, filters)
2. Build Supabase query
3. Apply filters (.eq, .ilike)
4. Apply pagination (.range(offset, offset+limit-1))
5. Get count (.select("*", count="exact"))
6. Execute query

Response:
{
  "data": [...],      // Array of items
  "total": 100,       // Total count (for pagination UI)
  "limit": 10,        // Items per page
  "offset": 0         // Current offset
}

Frontend:
• Calculate total pages: Math.ceil(total / limit)
• Current page: Math.floor(offset / limit) + 1
• Next page: offset + limit
• Previous page: offset - limit


ERROR HANDLING FLOW
═══════════════════

Try:
  ├─ Authenticate admin
  ├─ Validate input (Pydantic)
  ├─ Execute database operation
  ├─ Log admin action
  └─ Return success response

Catch HTTPException:
  └─ Re-raise (already formatted)

Catch Generic Exception:
  ├─ Log error to console
  ├─ Create HTTPException with details
  └─ Return formatted error response

Response Format:
{
  "detail": "Error message here"
}
```

---

## File Structure

```
Backend/
├── app/
│   ├── models/
│   │   └── admin.py                    # ✨ NEW: All admin models
│   ├── routers/
│   │   ├── admin.py                    # Existing organizer approval
│   │   └── admin_comprehensive.py      # ✨ NEW: All admin endpoints
│   ├── main.py                         # ✨ UPDATED: Added new router
│   └── database.py                     # Supabase client
│
├── database_migration_admin.sql        # ✨ NEW: SQL schema + RLS
├── ADMIN_BACKEND_README.md            # ✨ NEW: Implementation guide
├── API_DOCUMENTATION.md               # ✨ NEW: Complete API reference
├── IMPLEMENTATION_SUMMARY.md          # ✨ NEW: This summary
├── test_admin_backend.sh              # ✨ NEW: Bash test script
└── test_admin_api.py                  # ✨ NEW: Python test script
```

---

**Legend:**
- ✨ NEW: Newly created file
- 🔄 UPDATED: Modified existing file
- 📦 EXISTING: Already present (no changes)
