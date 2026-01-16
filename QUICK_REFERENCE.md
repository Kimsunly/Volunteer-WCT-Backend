# 🚀 Admin Backend - Quick Reference Card

## 📋 Essential Information

**Base URL:** `http://localhost:8000/admin`  
**Auth:** `Authorization: Bearer <jwt_token>`  
**Role Required:** `admin`

---

## 🔥 Most Used Endpoints

### 1. Dashboard Metrics
```bash
GET /admin/metrics
# Returns: donations_total, opportunities_count, organizers_count, users_count
```

### 2. Pending Organizers
```bash
GET /admin/organizers?status=pending
# Returns: List of pending organizer applications
```

### 3. Approve Organizer
```bash
POST /admin/organizers/{id}/approve
# Effect: Changes role to organizer, status to active
```

### 4. Reject Organizer
```bash
POST /admin/organizers/{id}/reject
Body: { "reason": "Your reason here" }
# Effect: Sets status to rejected, stores reason
```

### 5. List Categories
```bash
GET /admin/categories
# Returns: All categories with name, icon, color, active status
```

### 6. Create Category
```bash
POST /admin/categories
Body: {
  "name": "Category Name",
  "description": "Description",
  "icon": "🎯",
  "color": "#3B82F6",
  "active": true
}
```

### 7. List Opportunities (with filters)
```bash
GET /admin/opportunities?status=active&limit=20&offset=0
# Filters: search, category, status, visibility
```

### 8. Community Moderation
```bash
GET /admin/community?status=pending
POST /admin/community/{id}/approve
POST /admin/community/{id}/reject
```

### 9. List Users
```bash
GET /admin/users?role=organizer&limit=50
# Filters: search, role
```

### 10. Change User Role
```bash
POST /admin/users/{id}/role
Body: { "role": "organizer" }
# Roles: user, organizer, admin
```

---

## 📝 Common Query Parameters

| Parameter | Type | Values | Default |
|-----------|------|--------|---------|
| `limit` | int | 1-100 | 50 |
| `offset` | int | 0+ | 0 |
| `status` | string | Varies by endpoint | null |
| `search` | string | Any text | null |
| `category` | string | Category name | null |
| `visibility` | string | public, private | null |
| `role` | string | user, organizer, admin | null |

---

## 🎯 Response Formats

### List Response
```json
{
  "data": [...],
  "total": 100,
  "limit": 50,
  "offset": 0
}
```

### Success Response
```json
{
  "message": "Operation successful",
  "id": "uuid",
  "...": "additional data"
}
```

### Error Response
```json
{
  "detail": "Error message here"
}
```

---

## ⚡ Quick Testing

### Test Server Health
```bash
curl http://localhost:8000/health
```

### Test Admin Access
```bash
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  http://localhost:8000/admin/metrics
```

### Test Create Category
```bash
curl -X POST \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","description":"Test category","active":true}' \
  http://localhost:8000/admin/categories
```

---

## 🔐 Authentication Flow

1. **Login:**
```bash
POST /api/auth/login
Body: { "email": "admin@example.com", "password": "..." }
Response: { "token": "jwt_token_here", ... }
```

2. **Set Token:**
```bash
export ADMIN_TOKEN="jwt_token_here"
```

3. **Use Token:**
```bash
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  http://localhost:8000/admin/...
```

---

## 🐛 Quick Debugging

### Check if server is running:
```bash
curl http://localhost:8000/health
```

### Check if you're admin:
```sql
SELECT user_id, email, role 
FROM user_profiles 
WHERE email = 'your-email@example.com';
```

### Check admin activity log:
```sql
SELECT * FROM admin_activity_log 
ORDER BY created_at DESC 
LIMIT 10;
```

### Check RLS policies:
```sql
SELECT tablename, policyname 
FROM pg_policies 
WHERE schemaname = 'public';
```

---

## 📦 Tables Quick Reference

| Table | Purpose | Key Fields |
|-------|---------|------------|
| `categories` | Opportunity categories | name, icon, color, active |
| `blogs` | Blog posts | title, content, published |
| `community_posts` | Organizer posts | title, status, visibility |
| `comments` | User comments | content, status |
| `donations` | Donation records | amount, donor_name |
| `admin_activity_log` | Audit trail | admin_id, action, target |

---

## 🚨 Common Issues & Fixes

### 403 Forbidden
```bash
# Check token
echo $ADMIN_TOKEN

# Check user role
SELECT role FROM user_profiles WHERE user_id = 'your-id';
```

### 404 Not Found
```bash
# Check endpoint URL (should be /admin/...)
# Verify backend is running
ps aux | grep uvicorn
```

### 422 Validation Error
```json
// Check required fields
// Verify data types match
// Review API_DOCUMENTATION.md
```

---

## 📞 Where to Find More

| Question | Document |
|----------|----------|
| How do I set up? | `CHECKLIST.md` |
| What endpoints exist? | `API_DOCUMENTATION.md` |
| How does it work? | `ARCHITECTURE_DIAGRAM.md` |
| Implementation details? | `ADMIN_BACKEND_README.md` |
| What's complete? | `IMPLEMENTATION_SUMMARY.md` |

---

## ⚡ Power User Tips

### Batch Testing
```bash
# Test all endpoints at once
./test_admin_backend.sh
```

### Watch Logs in Real-time
```bash
# Terminal 1: Run backend with logs
uvicorn app.main:app --reload --log-level debug

# Terminal 2: Make requests
curl ...
```

### Quick Data Check
```bash
# Count pending items
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  "http://localhost:8000/admin/organizers?status=pending" \
  | jq '.total'
```

### Auto-refresh Token
```bash
# Add to ~/.bashrc or ~/.zshrc
alias admin_login='export ADMIN_TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login -H "Content-Type: application/json" -d "{\"email\":\"admin@example.com\",\"password\":\"your-pass\"}" | jq -r .token)'
```

---

## 🎉 Success Checklist

- [ ] Backend running on port 8000
- [ ] Database migration completed
- [ ] Admin user created
- [ ] JWT token obtained
- [ ] `/admin/metrics` returns data
- [ ] Can approve/reject organizers
- [ ] Can CRUD categories
- [ ] Frontend can call endpoints

---

**Print this card and keep it handy! 🚀**

**Last Updated:** January 10, 2026  
**Version:** 1.0.0
