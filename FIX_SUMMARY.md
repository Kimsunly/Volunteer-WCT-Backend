# 🎉 Image Upload Fix Summary

## What Was Fixed

### 1. **Main Application Router** ([main.py](Backend/app/main.py))
   - ✅ Changed from `opportunity` to `opportunity_with_images` router
   - ✅ Now includes full image upload support

### 2. **Image Upload Utilities** ([image_upload.py](Backend/app/utils/image_upload.py))
   - ✅ Added configuration import from settings
   - ✅ Uses `STORAGE_OPPORTUNITY_BUCKET` from config
   - ✅ Better error handling with proper bucket references

### 3. **Configuration** ([config.py](Backend/app/config.py))
   - ✅ Added `STORAGE_OPPORTUNITY_BUCKET` setting
   - ✅ Configurable via `OPPORTUNITY_BUCKET` environment variable
   - ✅ Defaults to `"opportunity-images"`

### 4. **New Files Created**

   **a) Setup Script** (`Backend/app/setup_storage.py`)
   - Check if storage bucket exists
   - Create bucket automatically
   - Verify configuration
   - **Run it**: `python -m app.setup_storage`

   **b) Setup Guide** (`Backend/IMAGE_UPLOAD_GUIDE.md`)
   - Complete setup instructions
   - API endpoint documentation
   - Frontend integration examples
   - Troubleshooting guide

   **c) Test Page** (`Backend/app/static/test-image-upload.html`)
   - Interactive test interface
   - Create opportunities with images
   - Upload images to existing opportunities
   - **Access at**: `http://localhost:8000/static/test-image-upload.html`

## 🚀 Quick Start

### 1. Run Setup Check
```bash
cd Backend
python -m app.setup_storage
```

### 2. Create Storage Bucket

**Option A: Automatic**
- Follow prompts from setup script

**Option B: Manual**
1. Go to [Supabase Dashboard](https://app.supabase.com)
2. Navigate to Storage
3. Create bucket named: `opportunity-images`
4. Make it **PUBLIC** ✅
5. Set file size limit: 5MB

### 3. Set Up Storage Policies

Run this SQL in Supabase SQL Editor:

```sql
-- Allow authenticated users to upload
CREATE POLICY "Allow authenticated uploads"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (bucket_id = 'opportunity-images');

-- Allow authenticated users to update
CREATE POLICY "Allow authenticated updates"
ON storage.objects FOR UPDATE
TO authenticated
USING (bucket_id = 'opportunity-images');

-- Allow authenticated users to delete
CREATE POLICY "Allow authenticated deletes"
ON storage.objects FOR DELETE
TO authenticated
USING (bucket_id = 'opportunity-images');

-- Allow public to view images
CREATE POLICY "Allow public reads"
ON storage.objects FOR SELECT
TO public
USING (bucket_id = 'opportunity-images');
```

### 4. Start Backend Server
```bash
cd Backend
uvicorn app.main:app --reload
```

### 5. Test It!
- Open: `http://localhost:8000/static/test-image-upload.html`
- Login to get JWT token
- Upload some test images

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/opportunities/with-images` | Create opportunity with images |
| POST | `/api/opportunities/{id}/upload-images` | Add images to opportunity |
| DELETE | `/api/opportunities/{id}/images` | Delete specific image |
| GET | `/api/opportunities` | List all opportunities |
| GET | `/api/opportunities/{id}` | Get single opportunity |
| PATCH | `/api/opportunities/{id}` | Update opportunity |
| DELETE | `/api/opportunities/{id}` | Delete opportunity |

## 📝 Usage Example

```javascript
// Frontend code to upload images
const createOpportunity = async (data, images) => {
  const formData = new FormData();
  
  // Add all text fields
  Object.keys(data).forEach(key => {
    formData.append(key, data[key]);
  });
  
  // Add image files
  images.forEach(file => {
    formData.append('images', file);
  });
  
  const response = await fetch('/api/opportunities/with-images', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
    },
    body: formData
  });
  
  return await response.json();
};
```

## 🎨 Image Storage Structure

```
opportunity-images/
  ├── organizer_1/
  │   ├── 20260108_abc123_beach_cleanup.jpg
  │   └── 20260108_def456_volunteers.jpg
  ├── organizer_2/
  │   └── 20260108_ghi789_event.jpg
  └── ...
```

## ✅ Features

- ✅ Upload up to 5 images per request
- ✅ Max 10 images total per opportunity
- ✅ File type validation (jpg, png, gif, webp)
- ✅ File size limit (5MB per image)
- ✅ Unique filename generation (prevents collisions)
- ✅ Organized by organizer ID
- ✅ Public image URLs
- ✅ Automatic cleanup on opportunity deletion
- ✅ Only organizer can modify their images

## 🔧 Troubleshooting

**Bucket not found?**
→ Run `python -m app.setup_storage` or create manually

**Permission denied?**
→ Check RLS policies are set up correctly

**Images don't display?**
→ Make sure bucket is PUBLIC

**File too large?**
→ Max 5MB per image, compress before upload

## 📚 Documentation

- Full guide: [IMAGE_UPLOAD_GUIDE.md](Backend/IMAGE_UPLOAD_GUIDE.md)
- Test page: http://localhost:8000/static/test-image-upload.html
- API docs: http://localhost:8000/docs

## 🎯 Next Steps

1. ✅ Run setup script to verify configuration
2. ✅ Create storage bucket in Supabase
3. ✅ Add RLS policies
4. ✅ Test with the test page
5. ✅ Integrate with your frontend

---

Everything is now set up for organizers to upload images to Supabase! 🎉
