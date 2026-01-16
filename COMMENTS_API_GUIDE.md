# Comments API Guide

## Overview
The comments system allows **all authenticated users** (volunteers, organizers, admins) to comment on:
- **Opportunities** - Volunteer opportunities detail pages
- **Blogs** - Blog posts
- **Community Posts** - Community discussion posts

## Features
✅ **Public viewing** - Anyone can view comments (no auth required)  
✅ **Authenticated commenting** - Any logged-in user can comment  
✅ **Edit your comments** - Users can update their own comments  
✅ **Delete your comments** - Users can delete their own comments  
✅ **User information** - Comments show author name and avatar  
✅ **Pagination** - Efficient loading for large comment lists  
✅ **Admin moderation** - Admins can hide/approve comments via admin endpoints

## API Endpoints

### 1. View Comments (Public Access)
Get all comments for a specific opportunity, blog, or community post.

**Endpoint:** `GET /comments/entity/{entity_type}/{entity_id}`

**Parameters:**
- `entity_type`: `"opportunity"`, `"blog"`, or `"community_post"`
- `entity_id`: UUID of the entity
- `limit`: Number per page (default: 20, max: 100)
- `offset`: Skip count for pagination (default: 0)

**Example:**
```bash
# View comments on an opportunity (no auth required)
curl "http://localhost:8000/comments/entity/opportunity/123e4567-e89b-12d3-a456-426614174000?limit=20&offset=0"
```

**Response:**
```json
{
  "comments": [
    {
      "id": "comment-uuid",
      "user_id": "user-uuid",
      "user_name": "John Doe",
      "user_avatar": "https://example.com/avatar.jpg",
      "entity_type": "opportunity",
      "entity_id": "opportunity-uuid",
      "content": "This looks amazing! I'd love to participate.",
      "status": "visible",
      "created_at": "2024-01-10T10:30:00Z",
      "updated_at": null,
      "can_edit": false,
      "can_delete": false
    }
  ],
  "total": 15,
  "limit": 20,
  "offset": 0,
  "has_more": false
}
```

---

### 2. Create Comment (Authentication Required)
Post a new comment on an opportunity, blog, or community post.

**Endpoint:** `POST /comments/`

**Headers:**
```
Authorization: Bearer <jwt-token>
Content-Type: application/json
```

**Body:**
```json
{
  "entity_type": "opportunity",
  "entity_id": "123e4567-e89b-12d3-a456-426614174000",
  "content": "This looks like an amazing opportunity! Count me in!"
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/comments/" \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "entity_type": "opportunity",
    "entity_id": "123e4567-e89b-12d3-a456-426614174000",
    "content": "This looks amazing! I would love to participate."
  }'
```

**Response:** `201 Created`
```json
{
  "id": "new-comment-uuid",
  "user_id": "your-user-uuid",
  "user_name": "Your Name",
  "user_avatar": "https://example.com/your-avatar.jpg",
  "entity_type": "opportunity",
  "entity_id": "opportunity-uuid",
  "content": "This looks amazing! I would love to participate.",
  "status": "visible",
  "created_at": "2024-01-11T15:45:00Z",
  "updated_at": null,
  "can_edit": true,
  "can_delete": true
}
```

---

### 3. Update Your Comment (Authentication Required)
Edit your own comment.

**Endpoint:** `PUT /comments/{comment_id}`

**Headers:**
```
Authorization: Bearer <jwt-token>
Content-Type: application/json
```

**Body:**
```json
{
  "content": "Updated: This looks amazing! I'm definitely joining."
}
```

**Example:**
```bash
curl -X PUT "http://localhost:8000/comments/comment-uuid" \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{"content": "Updated comment text here"}'
```

**Response:** `200 OK` (returns updated comment)

---

### 4. Delete Your Comment (Authentication Required)
Remove your own comment.

**Endpoint:** `DELETE /comments/{comment_id}`

**Headers:**
```
Authorization: Bearer <jwt-token>
```

**Example:**
```bash
curl -X DELETE "http://localhost:8000/comments/comment-uuid" \
  -H "Authorization: Bearer eyJhbGc..."
```

**Response:** `204 No Content`

---

### 5. View Your Comments (Authentication Required)
Get all comments you've made across all entities.

**Endpoint:** `GET /comments/my-comments`

**Parameters:**
- `limit`: Number per page (default: 20, max: 100)
- `offset`: Skip count for pagination (default: 0)

**Headers:**
```
Authorization: Bearer <jwt-token>
```

**Example:**
```bash
curl "http://localhost:8000/comments/my-comments?limit=10&offset=0" \
  -H "Authorization: Bearer eyJhbGc..."
```

**Response:** Similar to entity comments list

---

## Frontend Integration

### React Example - Display Comments on Opportunity Page

```javascript
import { useState, useEffect } from 'react';
import axios from 'axios';

const OpportunityComments = ({ opportunityId }) => {
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState('');
  const [loading, setLoading] = useState(false);
  
  // Fetch comments (no auth needed for viewing)
  useEffect(() => {
    const fetchComments = async () => {
      try {
        const response = await axios.get(
          `http://localhost:8000/comments/entity/opportunity/${opportunityId}`
        );
        setComments(response.data.comments);
      } catch (error) {
        console.error('Failed to fetch comments:', error);
      }
    };
    
    fetchComments();
  }, [opportunityId]);
  
  // Post new comment (requires auth)
  const handleSubmitComment = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.post(
        'http://localhost:8000/comments/',
        {
          entity_type: 'opportunity',
          entity_id: opportunityId,
          content: newComment
        },
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );
      
      // Add new comment to the list
      setComments([response.data, ...comments]);
      setNewComment('');
    } catch (error) {
      console.error('Failed to post comment:', error);
      alert('Please log in to comment');
    } finally {
      setLoading(false);
    }
  };
  
  // Delete comment
  const handleDeleteComment = async (commentId) => {
    try {
      const token = localStorage.getItem('access_token');
      await axios.delete(
        `http://localhost:8000/comments/${commentId}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );
      
      // Remove from list
      setComments(comments.filter(c => c.id !== commentId));
    } catch (error) {
      console.error('Failed to delete comment:', error);
    }
  };
  
  return (
    <div className="comments-section">
      <h3>Comments ({comments.length})</h3>
      
      {/* Comment Form (show only if logged in) */}
      <form onSubmit={handleSubmitComment}>
        <textarea
          value={newComment}
          onChange={(e) => setNewComment(e.target.value)}
          placeholder="Share your thoughts..."
          maxLength={2000}
          required
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Posting...' : 'Post Comment'}
        </button>
      </form>
      
      {/* Comments List */}
      <div className="comments-list">
        {comments.map(comment => (
          <div key={comment.id} className="comment">
            <div className="comment-header">
              <img src={comment.user_avatar || '/default-avatar.png'} alt={comment.user_name} />
              <span>{comment.user_name}</span>
              <span className="comment-date">
                {new Date(comment.created_at).toLocaleDateString()}
              </span>
            </div>
            
            <p className="comment-content">{comment.content}</p>
            
            {comment.can_delete && (
              <button onClick={() => handleDeleteComment(comment.id)}>
                Delete
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default OpportunityComments;
```

---

## User Permissions

| Action | Volunteer | Organizer | Admin |
|--------|-----------|-----------|-------|
| View comments | ✅ (public) | ✅ (public) | ✅ (public) |
| Post comment | ✅ | ✅ | ✅ |
| Edit own comment | ✅ | ✅ | ✅ |
| Delete own comment | ✅ | ✅ | ✅ |
| Edit any comment | ❌ | ❌ | ✅ |
| Delete any comment | ❌ | ❌ | ✅ |
| Hide/approve comments | ❌ | ❌ | ✅ (via admin endpoints) |

---

## Database Schema

The `comments` table structure:

```sql
CREATE TABLE comments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES user_profiles(user_id) ON DELETE CASCADE,
    entity_type TEXT NOT NULL CHECK (entity_type IN ('opportunity', 'community_post', 'blog')),
    entity_id UUID NOT NULL,
    content TEXT NOT NULL,
    status TEXT DEFAULT 'visible' CHECK (status IN ('visible', 'hidden', 'flagged')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);
```

---

## Testing

### Quick Test Sequence

1. **View comments (no auth):**
   ```bash
   curl "http://localhost:8000/comments/entity/opportunity/YOUR-OPPORTUNITY-ID"
   ```

2. **Login and get token:**
   ```bash
   curl -X POST "http://localhost:8000/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"email": "user@example.com", "password": "password"}'
   ```

3. **Post a comment:**
   ```bash
   curl -X POST "http://localhost:8000/comments/" \
     -H "Authorization: Bearer YOUR-TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "entity_type": "opportunity",
       "entity_id": "YOUR-OPPORTUNITY-ID",
       "content": "Test comment!"
     }'
   ```

4. **View your comments:**
   ```bash
   curl "http://localhost:8000/comments/my-comments" \
     -H "Authorization: Bearer YOUR-TOKEN"
   ```

---

## API Documentation

Visit **http://localhost:8000/docs** to see interactive API documentation with Swagger UI where you can test all endpoints directly.

---

## Next Steps

1. ✅ **Comments API is ready** - All endpoints are live
2. 🔄 **Run database migration** - Execute `database_migration_admin.sql` if not done yet
3. 🎨 **Frontend integration** - Add comment components to your opportunity detail pages
4. 🧪 **Test the endpoints** - Use Swagger UI or curl to verify functionality
5. 🎯 **Style comments** - Design comment cards with user avatars and timestamps

---

## Support

For admin moderation of comments, see the admin endpoints documentation:
- `GET /admin/comments` - List all comments with filters
- `POST /admin/comments/{id}/hide` - Hide inappropriate comments
- `POST /admin/comments/{id}/approve` - Approve flagged comments
