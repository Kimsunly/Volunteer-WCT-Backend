# 📚 API Data Reference & Schema Guide

This document provides a detailed breakdown of the **data structures**, **fields**, and **types** used in the Admin Backend API. Use this as your reference when building the frontend to know exactly what data to send and what to expect in response.

---

## 📋 Table of Contents
1. [Common Types & Enums](#1-common-types--enums)
2. [Dashboard Metrics](#2-dashboard-metrics)
3. [Organizers Data](#3-organizers-data)
4. [Categories Data](#4-categories-data)
5. [Opportunities Data](#5-opportunities-data)
6. [Users Data](#6-users-data)
7. [Blogs & Community](#7-blogs--community)
8. [Pagination Wrapper](#8-pagination-wrapper)

---

## 1. Common Types & Enums

These string values are used across multiple endpoints.

| Enum Name | Values | Description |
|-----------|--------|-------------|
| **Visibility** | `public`, `private` | Controls who can see the content. |
| **OrganizerStatus** | `pending`, `verified`, `rejected`, `suspended` | Status of an organization application. |
| **OpportunityStatus** | `active`, `pending`, `closed` | Lifecycle of a volunteer opportunity. |
| **UserRole** | `user`, `organizer`, `admin` | Permission level of a user. |
| **UserStatus** | `active`, `inactive`, `suspended`, `pending` | Account status. |
| **CommentStatus** | `visible`, `hidden`, `flagged` | Moderation status for comments. |

---

## 2. Dashboard Metrics

**Endpoint:** `GET /admin/metrics`

**Response Object:** `DashboardMetrics`
| Field | Type | Description |
|-------|------|-------------|
| `donations_total` | `float` | Total amount of donations (all time). |
| `opportunities_count` | `Map<string, number>` | Count of opportunities by status (e.g., `{"active": 10, "closed": 5}`). |
| `organizers_count` | `Map<string, number>` | Count of organizers by status. |
| `users_count` | `integer` | Total number of registered users. |

---

## 3. Organizers Data

**Endpoint:** `GET /admin/organizers`

**Response Object:** `OrganizerListItem`
| Field | Type | Nullable? | Description |
|-------|------|-----------|-------------|
| `id` | `UUID` (string) | No | Unique ID of the organizer profile. |
| `organization_name` | `string` | No | Name of the organization. |
| `contact_person` | `string` | Yes | Name of the primary contact. |
| `email` | `string` (email) | No | Contact email. |
| `phone` | `string` | Yes | Contact phone number. |
| `registration_number` | `string` | Yes | Official registration/tax ID. |
| `address` | `string` | Yes | Physical address. |
| `website` | `string` | Yes | Website URL. |
| `description` | `string` | Yes | Brief description of the org. |
| `submitted_at` | `datetime` | Yes | When the application was submitted. |
| `status` | `OrganizerStatus` | No | Current status (`pending`, etc.). |
| `rejection_reason` | `string` | Yes | Reason provided if rejected or suspended. |

**Actions:**
- **Approve:** `POST /admin/organizers/{id}/approve` (No body)
- **Reject:** `POST /admin/organizers/{id}/reject`
  - Body: `{ "reason": "string (min 10 chars)" }`
- **Suspend:** `POST /admin/organizers/{id}/suspend`
  - Body: `{ "reason": "string (min 10 chars)" }`

---

## 4. Categories Data

**Endpoint:** `GET /admin/categories`

**Response Object:** `CategoryResponse`
| Field | Type | Nullable? | Description |
|-------|------|-----------|-------------|
| `id` | `UUID` (string) | No | Unique Category ID. |
| `name` | `string` | No | e.g., "Education", "Health". |
| `description` | `string` | Yes | Short explanation. |
| `icon` | `string` | Yes | Emoji or icon URL. |
| `color` | `string` | Yes | Hex color code (e.g., `#FF5733`). |
| `active` | `boolean` | No | If `true`, visible in app. |
| `created_at` | `datetime` | No | Creation timestamp. |

**Create/Update Body:**
- `name` (required for create)
- `active` (default: true)
- `description`, `icon`, `color` (optional)

---

## 5. Opportunities Data

**Endpoint:** `GET /admin/opportunities`

**Response Object:** `OpportunityListItem`
| Field | Type | Nullable? | Description |
|-------|------|-----------|-------------|
| `id` | `UUID` (string) | No | Unique Opportunity ID. |
| `title` | `string` | No | Event title. |
| `organizer` | `string` | No | Name of the organizer. |
| `organizer_id` | `integer` | No | ID reference to organizer. |
| `category` | `string` | Yes | Category name. |
| `location` | `string` | Yes | City or address. |
| `start_date` | `date` | Yes | YYYY-MM-DD. |
| `end_date` | `date` | Yes | YYYY-MM-DD. |
| `visibility` | `Visibility` | No | `public` or `private`. |
| `status` | `OpportunityStatus` | No | `active`, `closed`, etc. |
| `registered` | `integer` | No | Number of volunteers signed up. |
| `created_at` | `datetime` | Yes | Post timestamp. |

**Create Body (`POST`):**
- Required: `title`
- Optional: `category`, `location`, `start_date`, `end_date`, `description`, `visibility`, `status`

---

## 6. Users Data

**Endpoint:** `GET /admin/users`

**Response Object:** `UserListItem`
| Field | Type | Nullable? | Description |
|-------|------|-----------|-------------|
| `id` | `UUID` (string) | No | Unique User ID. |
| `name` | `string` | Yes | Display name. |
| `email` | `string` | No | User email. |
| `role` | `UserRole` | No | `user`, `organizer`, or `admin`. |
| `status` | `UserStatus` | No | Account status. |
| `avatar` | `string` | Yes | Profile picture URL. |
| `created_at` | `datetime` | No | Registration date. |

**Actions:**
- **Change Role:** `POST /admin/users/{id}/role`
  - Body: `{ "role": "organizer" }`
- **Deactivate:** `POST /admin/users/{id}/deactivate`
  - Body: `{ "reason": "optional string" }`

---

## 7. Blogs & Community

### Blogs (`/admin/blogs`)
- **Fields**: `id`, `title`, `category`, `image` (URL), `content` (HTML/Markdown), `author`, `published` (bool), `created_at`.
- **Note**: Main content is in the `content` field.

### Community Posts (`/admin/community`)
- **Fields**: `id`, `organizer_name`, `title`, `content`, `images` (Array of URLs), `likes` (int), `comments` (int), `status`.
- **Moderation**:
  - `POST /approve` (No body)
  - `POST /reject` (Body: `{ "reason": "string" }`)

---

## 8. Pagination Wrapper

List endpoints (Users, Organizers, etc.) return this standard wrapper structure:

```json
{
  "data": [ ... ],   // Array of the objects defined above
  "total": 100,      // Total records (ignoring limit)
  "limit": 50,       // Current page size
  "offset": 0        // Current offset
}
```

### Common Query Parameters
Almost all list endpoints support these:
- `limit` (default 50)
- `offset` (default 0)
- `search` (text search)
- `status` (filter by status enum)
- `order` (`asc` or `desc`)
- `sort` (field name to sort by)
