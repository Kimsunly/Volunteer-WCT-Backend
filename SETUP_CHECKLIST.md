# 📋 Image Upload Setup Checklist

Use this checklist to ensure everything is properly set up for image uploads.

## ✅ Backend Setup

- [ ] **1. Install Dependencies**
  ```bash
  cd Backend
  pip install -r requirements.txt
  ```

- [ ] **2. Configure Environment**
  - [ ] Copy `.env.example` to `.env`
  - [ ] Set `SUPABASE_URL` with your project URL
  - [ ] Set `SUPABASE_KEY` with your service role key
  - [ ] Set `JWT_SECRET` to a secure value

- [ ] **3. Run Setup Check**
  ```bash
  python -m app.setup_storage
  ```

## ✅ Supabase Storage Setup

- [ ] **4. Create Storage Bucket**
  - [ ] Go to Supabase Dashboard → Storage
  - [ ] Create bucket: `opportunity-images`
  - [ ] Set as **PUBLIC** ✓
  - [ ] File size limit: 5MB
  - [ ] Allowed types: image/jpeg, image/png, image/gif, image/webp

- [ ] **5. Set Up RLS Policies**
  - [ ] Go to SQL Editor
  - [ ] Run the SQL commands from `IMAGE_UPLOAD_GUIDE.md`
  - [ ] Verify policies are created

## ✅ Testing

- [ ] **6. Start Backend Server**
  ```bash
  uvicorn app.main:app --reload
  ```
  - [ ] Server starts without errors
  - [ ] Visit http://localhost:8000 - should see "online"
  - [ ] Visit http://localhost:8000/docs - API docs load

- [ ] **7. Test with Test Page**
  - [ ] Open http://localhost:8000/static/test-image-upload.html
  - [ ] Login and copy JWT token
  - [ ] Try creating opportunity with images
  - [ ] Verify images upload successfully
  - [ ] Check images are stored in Supabase Storage
  - [ ] Verify public URLs work

- [ ] **8. Test API Endpoints**
  - [ ] POST `/api/opportunities/with-images` works
  - [ ] POST `/api/opportunities/{id}/upload-images` works
  - [ ] DELETE `/api/opportunities/{id}/images` works
  - [ ] Image URLs are accessible

## ✅ Verification

- [ ] **9. Check Storage**
  - [ ] Images appear in Supabase Storage dashboard
  - [ ] Files organized in `organizer_{id}` folders
  - [ ] Filenames include timestamp and unique ID

- [ ] **10. Check Database**
  - [ ] Opportunity records have `images` field populated
  - [ ] Image URLs are comma-separated strings
  - [ ] URLs are publicly accessible

## ✅ Frontend Integration (Next.js)

- [ ] **11. Update Frontend API Service**
  - [ ] Add FormData support for image uploads
  - [ ] Include Authorization header with JWT
  - [ ] Handle multipart/form-data correctly

- [ ] **12. Create Upload UI**
  - [ ] File input component (accept images)
  - [ ] Image preview before upload
  - [ ] Upload progress indicator
  - [ ] Error handling and display

- [ ] **13. Display Images**
  - [ ] Parse comma-separated URLs from `images` field
  - [ ] Render image gallery
  - [ ] Handle missing images gracefully

## 🔧 Troubleshooting Checklist

If something doesn't work:

- [ ] Check console logs in terminal
- [ ] Check browser console for errors
- [ ] Verify JWT token is valid and not expired
- [ ] Confirm user is a verified organizer
- [ ] Check Supabase Storage permissions
- [ ] Verify bucket is set to PUBLIC
- [ ] Confirm RLS policies are created
- [ ] Check file size (max 5MB)
- [ ] Verify file type is allowed
- [ ] Test with curl to isolate frontend issues

## 📝 Common Issues & Solutions

### "Bucket not found"
**Solution**: Run `python -m app.setup_storage` or create manually

### "Permission denied" 
**Solution**: Set up RLS policies in Supabase SQL Editor

### "Image URLs don't work"
**Solution**: Make sure bucket is PUBLIC in Supabase

### "Token expired"
**Solution**: Login again to get a fresh JWT token

### "File too large"
**Solution**: Compress images, max 5MB per file

### "Only 403 errors"
**Solution**: Verify user is verified organizer with `verified_at` set

## ✨ Success Indicators

You'll know it's working when:

✅ Images upload without errors  
✅ Public URLs are returned  
✅ Images visible in Supabase Storage dashboard  
✅ Image URLs work in browser  
✅ Database records contain image URLs  
✅ Images display on frontend  

## 📚 Resources

- **Full Guide**: `IMAGE_UPLOAD_GUIDE.md`
- **Fix Summary**: `FIX_SUMMARY.md`
- **Test Page**: http://localhost:8000/static/test-image-upload.html
- **API Docs**: http://localhost:8000/docs
- **Setup Script**: `python -m app.setup_storage`

---

**Last Updated**: January 8, 2026  
**Status**: Ready for testing 🚀
