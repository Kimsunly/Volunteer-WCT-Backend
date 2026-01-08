# Image Upload Setup Guide

## Overview
This guide will help you set up image uploading for organizers to post opportunity images stored in Supabase Storage.

## ✅ What Was Fixed

1. **Updated main.py** - Now uses `opportunity_with_images` router with full image support
2. **Enhanced image_upload.py** - Uses configuration from settings, better error handling
3. **Added storage bucket config** - Bucket name is now configurable via environment variables
4. **Created setup script** - Tool to verify and create storage bucket

## 📋 Prerequisites

1. **Supabase Project** with:
   - Valid `SUPABASE_URL` 
   - Valid `SUPABASE_KEY` (service_role key recommended for storage operations)

2. **Python packages** installed:
   ```bash
   cd Backend
   pip install -r requirements.txt
   ```

## 🚀 Setup Steps

### Step 1: Check Storage Configuration

Run the setup script to verify your storage bucket:

```bash
cd Backend
python -m app.setup_storage
```

This will:
- Check if the `opportunity-images` bucket exists
- Optionally create it if missing
- Show you configuration details

### Step 2: Create Bucket Manually (if needed)

If automatic creation fails, create the bucket in Supabase Dashboard:

1. Go to https://app.supabase.com
2. Select your project
3. Navigate to **Storage** in the left sidebar
4. Click **Create a new bucket**
5. Settings:
   - **Name**: `opportunity-images`
   - **Public bucket**: ✅ **YES** (required for public image URLs)
   - **File size limit**: 5242880 (5MB)
   - **Allowed MIME types**: `image/jpeg,image/png,image/gif,image/webp`
6. Click **Create bucket**

### Step 3: Set Up Storage Policies (Important!)

For organizers to upload images, you need RLS policies:

```sql
-- Allow authenticated users to upload images
CREATE POLICY "Allow authenticated uploads"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (bucket_id = 'opportunity-images');

-- Allow authenticated users to update their own images
CREATE POLICY "Allow authenticated updates"
ON storage.objects FOR UPDATE
TO authenticated
USING (bucket_id = 'opportunity-images');

-- Allow authenticated users to delete their own images
CREATE POLICY "Allow authenticated deletes"
ON storage.objects FOR DELETE
TO authenticated
USING (bucket_id = 'opportunity-images');

-- Allow public read access (so images can be viewed)
CREATE POLICY "Allow public reads"
ON storage.objects FOR SELECT
TO public
USING (bucket_id = 'opportunity-images');
```

Run these in your Supabase SQL Editor.

### Step 4: Start the Backend Server

```bash
cd Backend
uvicorn app.main:app --reload
```

The server should start on `http://localhost:8000`

## 📡 API Endpoints

### 1. Create Opportunity with Images

**Endpoint**: `POST /api/opportunities/with-images`

**Headers**:
```
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: multipart/form-data
```

**Body** (form-data):
```
title: "Beach Cleanup Volunteer"
category_slug: "environment"
category_label: "Environment"
location_slug: "sihanoukville"
location_label: "Sihanoukville"
description: "Help clean the beach"
full_details: "Full event details here..."
organization: "Green Cambodia"
date_range: "2026-02-01 to 2026-02-03"
time_range: "08:00 - 12:00"
capacity: 50
transport: "Provided"
housing: "Not provided"
meals: "Lunch provided"
images: [file1.jpg, file2.jpg, file3.jpg]  // Up to 5 images
```

**Response**:
```json
{
  "id": "uuid",
  "title": "Beach Cleanup Volunteer",
  "images": "https://...url1,https://...url2,https://...url3",
  ...other fields
}
```

### 2. Upload Images to Existing Opportunity

**Endpoint**: `POST /api/opportunities/{opportunity_id}/upload-images`

**Headers**:
```
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: multipart/form-data
```

**Body** (form-data):
```
images: [file1.jpg, file2.jpg]  // Up to 5 images per request
```

**Response**:
```json
{
  "message": "Uploaded 2 image(s) successfully",
  "uploaded_urls": ["https://...url1", "https://...url2"],
  "total_images": 5,
  "all_image_urls": ["https://...url1", "https://...url2", ...]
}
```

### 3. Delete Image from Opportunity

**Endpoint**: `DELETE /api/opportunities/{opportunity_id}/images`

**Headers**:
```
Authorization: Bearer YOUR_JWT_TOKEN
```

**Query Parameters**:
```
image_url: https://hyidxiytjwxknerdrpua.supabase.co/storage/v1/object/public/opportunity-images/organizer_1/image.jpg
```

**Response**:
```json
{
  "message": "Image deleted successfully",
  "remaining_images": 3
}
```

## 🧪 Testing with curl

### Test 1: Create with images
```bash
curl -X POST http://localhost:8000/api/opportunities/with-images \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "title=Beach Cleanup" \
  -F "category_slug=environment" \
  -F "category_label=Environment" \
  -F "location_slug=sihanoukville" \
  -F "location_label=Sihanoukville" \
  -F "description=Help clean the beach" \
  -F "images=@/path/to/image1.jpg" \
  -F "images=@/path/to/image2.jpg"
```

### Test 2: Upload images to existing
```bash
curl -X POST http://localhost:8000/api/opportunities/YOUR_OPP_ID/upload-images \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "images=@/path/to/image.jpg"
```

## 🎨 Frontend Integration (Next.js Example)

```javascript
// Create opportunity with images
const createOpportunityWithImages = async (formData) => {
  const form = new FormData();
  
  // Add text fields
  form.append('title', formData.title);
  form.append('category_slug', formData.category_slug);
  form.append('category_label', formData.category_label);
  form.append('location_slug', formData.location_slug);
  form.append('location_label', formData.location_label);
  form.append('description', formData.description);
  form.append('full_details', formData.full_details);
  form.append('organization', formData.organization);
  form.append('date_range', formData.date_range);
  form.append('time_range', formData.time_range);
  form.append('capacity', formData.capacity);
  form.append('transport', formData.transport);
  form.append('housing', formData.housing);
  form.append('meals', formData.meals);
  
  // Add image files
  formData.images.forEach(file => {
    form.append('images', file);
  });
  
  const response = await fetch('http://localhost:8000/api/opportunities/with-images', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      // Don't set Content-Type - browser will set it with boundary
    },
    body: form
  });
  
  return await response.json();
};

// Upload additional images
const uploadImages = async (opportunityId, files) => {
  const form = new FormData();
  files.forEach(file => form.append('images', file));
  
  const response = await fetch(
    `http://localhost:8000/api/opportunities/${opportunityId}/upload-images`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      body: form
    }
  );
  
  return await response.json();
};
```

## 🔧 Troubleshooting

### Error: "Bucket not found"
- Run `python -m app.setup_storage` to check bucket status
- Create bucket manually in Supabase Dashboard
- Verify bucket name is `opportunity-images`

### Error: "Permission denied"
- Check RLS policies are set up (see Step 3)
- Verify you're using a valid JWT token
- Make sure user is a verified organizer

### Error: "File too large"
- Max file size is 5MB per image
- Compress images before uploading
- Check browser console for specific error

### Images upload but URLs don't work
- Ensure bucket is set to **PUBLIC**
- Check bucket permissions in Supabase Dashboard
- Verify RLS policy allows public SELECT

### Error: "Invalid image URL"
- URL format should be: `https://[project].supabase.co/storage/v1/object/public/opportunity-images/...`
- Check the `images` field in database is storing full URLs

## 📊 Image Storage Structure

Images are stored in this structure:
```
opportunity-images/
  └── organizer_1/
      ├── 20260108_abc123_beach_cleanup.jpg
      ├── 20260108_def456_volunteers.jpg
      └── ...
  └── organizer_2/
      ├── 20260108_ghi789_event_photo.jpg
      └── ...
```

Each filename includes:
- Timestamp (prevents collisions)
- Unique ID (8 characters)
- Original filename (sanitized, max 50 chars)

## ✨ Features

- ✅ Upload up to 5 images per request
- ✅ Max 10 images total per opportunity
- ✅ Automatic file validation (type, size)
- ✅ Unique filename generation
- ✅ Organized by organizer ID
- ✅ Public URLs for images
- ✅ Secure (only organizer can modify their images)
- ✅ Automatic cleanup on opportunity deletion

## 🔐 Security Notes

1. **Authentication Required**: All upload/delete operations require valid JWT
2. **Organizer Verification**: Only verified organizers can create opportunities
3. **Ownership Check**: Users can only modify their own opportunities
4. **File Validation**: Only allowed image types and sizes
5. **RLS Policies**: Supabase enforces row-level security

## 📝 Next Steps

1. ✅ Run `python -m app.setup_storage` to verify setup
2. ✅ Create the storage bucket (manual or automatic)
3. ✅ Set up RLS policies in Supabase
4. ✅ Test API endpoints with curl or Postman
5. ✅ Integrate with your frontend application

## 💡 Tips

- Use WebP format for better compression
- Resize images on the frontend before upload
- Show upload progress to users
- Preview images before uploading
- Handle errors gracefully in UI
- Consider image optimization service for production

---

**Need help?** Check the console logs or API error messages for specific details.
