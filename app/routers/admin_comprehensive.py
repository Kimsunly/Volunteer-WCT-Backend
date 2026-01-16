"""
Comprehensive Admin Router - Full Implementation
Implements all admin endpoints per specification:
- Dashboard metrics
- Organizers management
- Categories CRUD
- Opportunities CRUD
- Blogs CRUD
- Community moderation
- Users management
- Comments moderation
- Donations view
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Optional, List
from datetime import datetime

from app.models.admin import (
    # Dashboard
    DashboardMetrics,
    
    # Organizers
    OrganizerListItem,
    OrganizerApproveRequest,
    OrganizerRejectRequest,
    OrganizerSuspendRequest,
    OrganizerStatusEnum,
    
    # Categories
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    
    # Opportunities
    OpportunityListItem,
    OpportunityCreate,
    OpportunityUpdate,
    
    # Blogs
    BlogCreate,
    BlogUpdate,
    BlogResponse,
    
    # Community
    CommunityPostListItem,
    CommunityPostCreate,
    CommunityApproveRequest,
    CommunityRejectRequest,
    
    # Users
    UserListItem,
    UserRoleChangeRequest,
    UserDeactivateRequest,
    
    # Comments
    CommentListItem,
    CommentHideRequest,
    CommentApproveRequest,
    
    # Donations
    DonationListItem,
    
    # Common
    PaginatedResponse,
    VisibilityEnum,
    OpportunityStatusEnum,
    CommunityStatusEnum,
)
from app.utils.security import get_current_user, extract_user_id
from app.database import get_supabase

router = APIRouter(prefix="/admin", tags=["Admin"])


# ============================================
# ADMIN AUTHENTICATION MIDDLEWARE
# ============================================

def require_admin(current_user = Depends(get_current_user)):
    """Verify user has admin role"""
    supabase = get_supabase()
    user_id = extract_user_id(current_user)
    
    try:
        user_profile = supabase.table("user_profiles")\
            .select("role")\
            .eq("user_id", user_id)\
            .single()\
            .execute()
        
        if not user_profile.data or user_profile.data.get('role') != 'admin':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        
        return current_user
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR: Admin check error: {e}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )


def log_admin_action(admin_id: str, action: str, target_type: str, target_id: str, details: str = None):
    """Log admin actions for audit trail"""
    supabase = get_supabase()
    try:
        log_data = {
            "admin_id": admin_id,
            "action": action,
            "target_type": target_type,
            "target_id": target_id,
            "details": details,
            "created_at": datetime.utcnow().isoformat()
        }
        supabase.table("admin_activity_log").insert(log_data).execute()
    except Exception as e:
        print(f"WARNING: Failed to log admin action: {e}")


# ============================================
# DASHBOARD METRICS
# ============================================

@router.get("/metrics", response_model=DashboardMetrics)
def get_dashboard_metrics(current_user = Depends(require_admin)):
    """
    GET /admin/metrics
    Returns dashboard aggregates: donations total, opportunities count, organizers count, users count
    """
    supabase = get_supabase()
    
    try:
        # Donations total
        donations_response = supabase.table("donations")\
            .select("amount")\
            .execute()
        donations_total = sum(d.get('amount', 0) for d in (donations_response.data or []))
        
        # Opportunities count by status
        opportunities_response = supabase.table("opportunities")\
            .select("status")\
            .execute()
        opportunities_count = {}
        for opp in (opportunities_response.data or []):
            status = opp.get('status', 'unknown')
            opportunities_count[status] = opportunities_count.get(status, 0) + 1
        
        # Organizers count by status
        organizers_response = supabase.table("organizer_applications")\
            .select("status")\
            .execute()
        organizers_count = {}
        for org in (organizers_response.data or []):
            status = org.get('status', 'unknown')
            organizers_count[status] = organizers_count.get(status, 0) + 1
        
        # Users count
        users_response = supabase.table("user_profiles")\
            .select("id", count="exact")\
            .execute()
        users_count = users_response.count or 0
        
        return DashboardMetrics(
            donations_total=donations_total,
            opportunities_count=opportunities_count,
            organizers_count=organizers_count,
            users_count=users_count
        )
        
    except Exception as e:
        print(f"ERROR: Metrics error: {e}")
        # Return empty metrics on error
        return DashboardMetrics()


# ============================================
# ORGANIZERS MANAGEMENT
# ============================================

@router.get("/organizers")
def list_organizers(
    status: Optional[OrganizerStatusEnum] = None,
    search: Optional[str] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user = Depends(require_admin)
):
    """
    GET /admin/organizers?status=pending|verified|rejected|suspended
    List all organizer applications with filtering
    """
    supabase = get_supabase()
    
    try:
        query = supabase.table("organizer_applications")\
            .select("*", count="exact")\
            .order("submitted_at", desc=True)
        
        # Filter by status
        if status:
            query = query.eq("status", status.value)
        
        # Search by organization name or email
        if search:
            # Note: Supabase doesn't support OR in Python client easily
            # So we do two queries and merge (or use RPC function)
            query = query.ilike("organization_name", f"%{search}%")
        
        # Pagination
        query = query.range(offset, offset + limit - 1)
        
        response = query.execute()
        
        return {
            "data": response.data or [],
            "total": response.count or 0,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        print(f"ERROR: List organizers error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to list organizers: {str(e)}"
        )


@router.post("/organizers/{organizer_id}/approve")
def approve_organizer(
    organizer_id: str,
    current_user = Depends(require_admin)
):
    """
    POST /admin/organizers/{id}/approve
    Approve organizer application
    """
    supabase = get_supabase()
    admin_id = extract_user_id(current_user)
    
    try:
        # Get application
        app_response = supabase.table("organizer_applications")\
            .select("*")\
            .eq("id", organizer_id)\
            .single()\
            .execute()
        
        if not app_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organizer application not found"
            )
        
        application = app_response.data
        
        # Check status
        if application['status'] == 'verified':
            return {
                "message": "Organizer already verified",
                "organizer_id": organizer_id
            }
        
        if application['status'] != 'pending':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot approve {application['status']} application"
            )
        
        # Update application
        supabase.table("organizer_applications")\
            .update({
                "status": "verified",
                "reviewed_at": datetime.utcnow().isoformat(),
                "reviewed_by": admin_id
            })\
            .eq("id", organizer_id)\
            .execute()
        
        # Update user profile
        supabase.table("user_profiles")\
            .update({
                "role": "organizer",
                "status": "active"
            })\
            .eq("user_id", application['user_id'])\
            .execute()
        
        # Create organizer profile
        organizer_profile_data = {
            "user_id": application['user_id'],
            "organization_name": application['organization_name'],
            "organizer_type": application['organizer_type'],
            "phone": application.get('phone'),
            "website": application.get('website'),
            "address": application.get('address'),
            "description": application.get('description'),
            "contact_person": application.get('contact_person'),
            "registration_number": application.get('registration_number'),
            "verified_at": datetime.utcnow().isoformat(),
            "is_active": True
        }
        
        # Check if profile exists
        existing_profile = supabase.table("organizer_profiles")\
            .select("id")\
            .eq("user_id", application['user_id'])\
            .execute()
        
        if existing_profile.data:
            supabase.table("organizer_profiles")\
                .update(organizer_profile_data)\
                .eq("user_id", application['user_id'])\
                .execute()
        else:
            supabase.table("organizer_profiles")\
                .insert(organizer_profile_data)\
                .execute()
        
        # Log action
        log_admin_action(
            admin_id,
            "approve_organizer",
            "organizer",
            organizer_id,
            f"Approved: {application['organization_name']}"
        )
        
        return {
            "message": "Organizer approved successfully",
            "organizer_id": organizer_id,
            "organization_name": application['organization_name']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR: Approve organizer error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to approve organizer: {str(e)}"
        )


@router.post("/organizers/{organizer_id}/reject")
def reject_organizer(
    organizer_id: str,
    request: OrganizerRejectRequest,
    current_user = Depends(require_admin)
):
    """
    POST /admin/organizers/{id}/reject
    Reject organizer application with reason
    """
    supabase = get_supabase()
    admin_id = extract_user_id(current_user)
    
    try:
        # Get application
        app_response = supabase.table("organizer_applications")\
            .select("*")\
            .eq("id", organizer_id)\
            .single()\
            .execute()
        
        if not app_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organizer application not found"
            )
        
        application = app_response.data
        
        if application['status'] != 'pending':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot reject {application['status']} application"
            )
        
        # Update application
        supabase.table("organizer_applications")\
            .update({
                "status": "rejected",
                "reviewed_at": datetime.utcnow().isoformat(),
                "reviewed_by": admin_id,
                "rejection_reason": request.reason
            })\
            .eq("id", organizer_id)\
            .execute()
        
        # Update user profile
        supabase.table("user_profiles")\
            .update({
                "status": "rejected"
            })\
            .eq("user_id", application['user_id'])\
            .execute()
        
        # Log action
        log_admin_action(
            admin_id,
            "reject_organizer",
            "organizer",
            organizer_id,
            f"Rejected: {application['organization_name']} - {request.reason}"
        )
        
        return {
            "message": "Organizer rejected",
            "organizer_id": organizer_id,
            "reason": request.reason
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR: Reject organizer error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to reject organizer: {str(e)}"
        )


@router.post("/organizers/{organizer_id}/suspend")
def suspend_organizer(
    organizer_id: str,
    request: OrganizerSuspendRequest,
    current_user = Depends(require_admin)
):
    """
    POST /admin/organizers/{id}/suspend
    Suspend organizer account
    """
    supabase = get_supabase()
    admin_id = extract_user_id(current_user)
    
    try:
        # Get application
        app_response = supabase.table("organizer_applications")\
            .select("*")\
            .eq("id", organizer_id)\
            .single()\
            .execute()
        
        if not app_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organizer not found"
            )
        
        application = app_response.data
        
        # Update application
        supabase.table("organizer_applications")\
            .update({
                "status": "suspended",
                "reviewed_at": datetime.utcnow().isoformat(),
                "reviewed_by": admin_id,
                "rejection_reason": request.reason
            })\
            .eq("id", organizer_id)\
            .execute()
        
        # Update user profile
        supabase.table("user_profiles")\
            .update({
                "status": "suspended"
            })\
            .eq("user_id", application['user_id'])\
            .execute()
        
        # Log action
        log_admin_action(
            admin_id,
            "suspend_organizer",
            "organizer",
            organizer_id,
            f"Suspended: {application['organization_name']} - {request.reason}"
        )
        
        return {
            "message": "Organizer suspended",
            "organizer_id": organizer_id,
            "reason": request.reason
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR: Suspend organizer error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to suspend organizer: {str(e)}"
        )


# ============================================
# CATEGORIES MANAGEMENT
# ============================================

@router.get("/categories", response_model=List[CategoryResponse])
def list_categories(
    active_only: bool = False,
    current_user = Depends(require_admin)
):
    """
    GET /admin/categories
    List all categories
    """
    supabase = get_supabase()
    
    try:
        query = supabase.table("categories").select("*")
        
        if active_only:
            query = query.eq("active", True)
        
        response = query.execute()
        return response.data or []
        
    except Exception as e:
        print(f"ERROR: List categories error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to list categories: {str(e)}"
        )


@router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    category: CategoryCreate,
    current_user = Depends(require_admin)
):
    """
    POST /admin/categories
    Create new category
    """
    supabase = get_supabase()
    admin_id = extract_user_id(current_user)
    
    try:
        category_data = category.model_dump()
        category_data['created_at'] = datetime.utcnow().isoformat()
        
        response = supabase.table("categories")\
            .insert(category_data)\
            .execute()
        
        if not response.data:
            raise Exception("Failed to create category")
        
        # Log action
        log_admin_action(
            admin_id,
            "create_category",
            "category",
            response.data[0]['id'],
            f"Created: {category.name}"
        )
        
        return response.data[0]
        
    except Exception as e:
        print(f"ERROR: Create category error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create category: {str(e)}"
        )


@router.put("/categories/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: str,
    category: CategoryUpdate,
    current_user = Depends(require_admin)
):
    """
    PUT /admin/categories/{id}
    Update category
    """
    supabase = get_supabase()
    admin_id = extract_user_id(current_user)
    
    try:
        # Check if exists
        existing = supabase.table("categories")\
            .select("id")\
            .eq("id", category_id)\
            .execute()
        
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        # Update
        update_data = category.model_dump(exclude_unset=True)
        update_data['updated_at'] = datetime.utcnow().isoformat()
        
        response = supabase.table("categories")\
            .update(update_data)\
            .eq("id", category_id)\
            .execute()
        
        # Log action
        log_admin_action(
            admin_id,
            "update_category",
            "category",
            category_id,
            f"Updated category"
        )
        
        return response.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR: Update category error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update category: {str(e)}"
        )


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: str,
    current_user = Depends(require_admin)
):
    """
    DELETE /admin/categories/{id}
    Delete category
    """
    supabase = get_supabase()
    admin_id = extract_user_id(current_user)
    
    try:
        # Check if exists
        existing = supabase.table("categories")\
            .select("id")\
            .eq("id", category_id)\
            .execute()
        
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        # Delete
        supabase.table("categories")\
            .delete()\
            .eq("id", category_id)\
            .execute()
        
        # Log action
        log_admin_action(
            admin_id,
            "delete_category",
            "category",
            category_id,
            f"Deleted category"
        )
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR: Delete category error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to delete category: {str(e)}"
        )


# ============================================
# OPPORTUNITIES MANAGEMENT
# ============================================

@router.get("/opportunities")
def list_opportunities(
    search: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[OpportunityStatusEnum] = None,
    visibility: Optional[VisibilityEnum] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user = Depends(require_admin)
):
    """
    GET /admin/opportunities?search=&category=&status=&visibility=
    List all opportunities with filters
    """
    supabase = get_supabase()
    
    try:
        query = supabase.table("opportunities")\
            .select("*, organizer:organizer_id(organization_name)", count="exact")\
            .order("created_at", desc=True)
        
        # Filters
        if search:
            query = query.ilike("title", f"%{search}%")
        if category:
            query = query.eq("category", category)
        if status:
            query = query.eq("status", status.value)
        if visibility:
            query = query.eq("visibility", visibility.value)
        
        # Pagination
        query = query.range(offset, offset + limit - 1)
        
        response = query.execute()
        
        return {
            "data": response.data or [],
            "total": response.count or 0,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        print(f"ERROR: List opportunities error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to list opportunities: {str(e)}"
        )


@router.post("/opportunities", status_code=status.HTTP_201_CREATED)
def create_opportunity(
    opportunity: OpportunityCreate,
    current_user = Depends(require_admin)
):
    """
    POST /admin/opportunities
    Create opportunity (admin can create on behalf of organizer)
    """
    supabase = get_supabase()
    admin_id = extract_user_id(current_user)
    
    try:
        opp_data = opportunity.model_dump()
        opp_data['created_at'] = datetime.utcnow().isoformat()

        # Ensure date/time are strings for JSON serialization
        # Admin model uses start_date / end_date
        if opp_data.get('start_date') is not None:
            try:
                opp_data['start_date'] = opp_data['start_date'].isoformat()
            except Exception:
                pass

        if opp_data.get('end_date') is not None:
            try:
                opp_data['end_date'] = opp_data['end_date'].isoformat()
            except Exception:
                pass

        # Also support older/newer fields if present
        if opp_data.get('date_range') is not None:
            try:
                opp_data['date_range'] = opp_data['date_range'].isoformat()
            except Exception:
                pass

        if opp_data.get('time_range') is not None:
            try:
                opp_data['time_range'] = opp_data['time_range'].isoformat()
            except Exception:
                pass

        # Map admin model fields to the opportunities table columns used elsewhere
        # The public/organizer endpoints use 'category_label' and 'location_label'
        # while the admin model uses 'category' and 'location'. Translate them.
        if 'category' in opp_data and opp_data.get('category') is not None:
            opp_data['category_label'] = opp_data.pop('category')

        if 'location' in opp_data and opp_data.get('location') is not None:
            opp_data['location_label'] = opp_data.pop('location')

        # Map start_date/end_date into the single 'date_range' column used elsewhere.
        # The DB's `date_range` column is a DATE (single date). Store the start
        # date (ISO string) there. If you want true start/end support, add
        # separate `start_date` and `end_date` columns in the DB via migration.
        start = opp_data.pop('start_date', None)
        end = opp_data.pop('end_date', None)
        if start:
            # store only the start date (ISO string) to match the existing schema
            opp_data['date_range'] = start
        
        # Admin creates opportunity directly - set organizer_id to NULL
        # and mark it as created by admin using created_by_admin field
        opp_data['organizer_id'] = None
        opp_data['created_by_admin'] = admin_id  # Track which admin created it
        
        response = supabase.table("opportunities")\
            .insert(opp_data)\
            .execute()
        
        if not response.data:
            raise Exception("Failed to create opportunity")
        
        # Log action
        log_admin_action(
            admin_id,
            "create_opportunity",
            "opportunity",
            response.data[0]['id'],
            f"Created: {opportunity.title}"
        )
        
        return response.data[0]
        
    except Exception as e:
        print(f"ERROR: Create opportunity error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create opportunity: {str(e)}"
        )


@router.put("/opportunities/{opportunity_id}")
def update_opportunity(
    opportunity_id: str,
    opportunity: OpportunityUpdate,
    current_user = Depends(require_admin)
):
    """
    PUT /admin/opportunities/{id}
    Update opportunity
    """
    supabase = get_supabase()
    admin_id = extract_user_id(current_user)
    
    try:
        # Check if exists
        existing = supabase.table("opportunities")\
            .select("id")\
            .eq("id", opportunity_id)\
            .execute()
        
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Opportunity not found"
            )
        
        # Update
        update_data = opportunity.model_dump(exclude_unset=True)
        update_data['updated_at'] = datetime.utcnow().isoformat()
        
        # Serialize date fields to ISO strings
        if update_data.get('start_date') is not None:
            try:
                update_data['start_date'] = update_data['start_date'].isoformat()
            except Exception:
                pass
        
        if update_data.get('end_date') is not None:
            try:
                update_data['end_date'] = update_data['end_date'].isoformat()
            except Exception:
                pass
        
        # Map admin field names to DB columns
        if 'category' in update_data and update_data.get('category') is not None:
            update_data['category_label'] = update_data.pop('category')
        
        if 'location' in update_data and update_data.get('location') is not None:
            update_data['location_label'] = update_data.pop('location')
        
        # Map start_date to date_range if provided
        start = update_data.pop('start_date', None)
        end = update_data.pop('end_date', None)
        if start:
            update_data['date_range'] = start
        
        response = supabase.table("opportunities")\
            .update(update_data)\
            .eq("id", opportunity_id)\
            .execute()
        
        # Log action
        log_admin_action(
            admin_id,
            "update_opportunity",
            "opportunity",
            opportunity_id,
            f"Updated opportunity"
        )
        
        return response.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR: Update opportunity error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update opportunity: {str(e)}"
        )


@router.delete("/opportunities/{opportunity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_opportunity(
    opportunity_id: str,
    current_user = Depends(require_admin)
):
    """
    DELETE /admin/opportunities/{id}
    Delete opportunity
    """
    supabase = get_supabase()
    admin_id = extract_user_id(current_user)
    
    try:
        # Check if exists
        existing = supabase.table("opportunities")\
            .select("id")\
            .eq("id", opportunity_id)\
            .execute()
        
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Opportunity not found"
            )
        
        # Delete
        supabase.table("opportunities")\
            .delete()\
            .eq("id", opportunity_id)\
            .execute()
        
        # Log action
        log_admin_action(
            admin_id,
            "delete_opportunity",
            "opportunity",
            opportunity_id,
            f"Deleted opportunity"
        )
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR: Delete opportunity error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to delete opportunity: {str(e)}"
        )


# ============================================
# BLOGS/TIPS MANAGEMENT
# ============================================

@router.get("/blogs", response_model=List[BlogResponse])
def list_blogs(
    published_only: bool = False,
    current_user = Depends(require_admin)
):
    """
    GET /admin/blogs
    List all blogs
    """
    supabase = get_supabase()
    
    try:
        query = supabase.table("blogs").select("*").order("created_at", desc=True)
        
        if published_only:
            query = query.eq("published", True)
        
        response = query.execute()
        return response.data or []
        
    except Exception as e:
        print(f"ERROR: List blogs error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to list blogs: {str(e)}"
        )


@router.post("/blogs", response_model=BlogResponse, status_code=status.HTTP_201_CREATED)
def create_blog(
    blog: BlogCreate,
    current_user = Depends(require_admin)
):
    """
    POST /admin/blogs
    Create new blog
    """
    supabase = get_supabase()
    admin_id = extract_user_id(current_user)
    
    try:
        blog_data = blog.model_dump()
        blog_data['created_at'] = datetime.utcnow().isoformat()
        
        response = supabase.table("blogs")\
            .insert(blog_data)\
            .execute()
        
        if not response.data:
            raise Exception("Failed to create blog")
        
        # Log action
        log_admin_action(
            admin_id,
            "create_blog",
            "blog",
            response.data[0]['id'],
            f"Created: {blog.title}"
        )
        
        return response.data[0]
        
    except Exception as e:
        print(f"ERROR: Create blog error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create blog: {str(e)}"
        )


@router.put("/blogs/{blog_id}", response_model=BlogResponse)
def update_blog(
    blog_id: str,
    blog: BlogUpdate,
    current_user = Depends(require_admin)
):
    """
    PUT /admin/blogs/{id}
    Update blog
    """
    supabase = get_supabase()
    admin_id = extract_user_id(current_user)
    
    try:
        # Check if exists
        existing = supabase.table("blogs")\
            .select("id")\
            .eq("id", blog_id)\
            .execute()
        
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Blog not found"
            )
        
        # Update
        update_data = blog.model_dump(exclude_unset=True)
        update_data['updated_at'] = datetime.utcnow().isoformat()
        
        response = supabase.table("blogs")\
            .update(update_data)\
            .eq("id", blog_id)\
            .execute()
        
        # Log action
        log_admin_action(
            admin_id,
            "update_blog",
            "blog",
            blog_id,
            f"Updated blog"
        )
        
        return response.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR: Update blog error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update blog: {str(e)}"
        )


@router.delete("/blogs/{blog_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_blog(
    blog_id: str,
    current_user = Depends(require_admin)
):
    """
    DELETE /admin/blogs/{id}
    Delete blog
    """
    supabase = get_supabase()
    admin_id = extract_user_id(current_user)
    
    try:
        # Check if exists
        existing = supabase.table("blogs")\
            .select("id")\
            .eq("id", blog_id)\
            .execute()
        
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Blog not found"
            )
        
        # Delete
        supabase.table("blogs")\
            .delete()\
            .eq("id", blog_id)\
            .execute()
        
        # Log action
        log_admin_action(
            admin_id,
            "delete_blog",
            "blog",
            blog_id,
            f"Deleted blog"
        )
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR: Delete blog error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to delete blog: {str(e)}"
        )


# ============================================
# COMMUNITY MODERATION
# ============================================

@router.get("/community")
def list_community_posts(
    post_status: Optional[CommunityStatusEnum] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user = Depends(require_admin)
):
    """
    GET /admin/community?post_status=pending|approved|rejected
    List community posts for moderation
    """
    supabase = get_supabase()
    
    try:
        # Simple query without join - organizer_id is just a UUID
        query = supabase.table("community_posts")\
            .select("*", count="exact")\
            .order("created_at", desc=True)
        
        # Filter by status
        if post_status:
            query = query.eq("status", post_status.value)
        
        # Pagination
        query = query.range(offset, offset + limit - 1)
        
        response = query.execute()
        
        return {
            "data": response.data or [],
            "total": response.count or 0,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        print(f"ERROR: List community posts error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to list community posts: {str(e)}"
        )


@router.post("/community")
def create_community_post(
    post: CommunityPostCreate,
    current_user = Depends(require_admin)
):
    """
    POST /admin/community
    Create community post (admin creates directly, auto-approved)
    """
    supabase = get_supabase()
    admin_id = extract_user_id(current_user)
    
    try:
        post_data = post.model_dump()
        post_data['organizer_id'] = admin_id  # Admin is the organizer
        post_data['created_at'] = datetime.utcnow().isoformat()
        post_data['status'] = 'approved'  # Auto-approve admin posts
        post_data['comments_count'] = 0
        post_data['likes'] = 0
        
        response = supabase.table("community_posts")\
            .insert(post_data)\
            .execute()
        
        if not response.data:
            raise Exception("Failed to create community post")
        
        # Log action
        log_admin_action(
            admin_id,
            "create_community_post",
            "community_post",
            response.data[0]['id'],
            f"Created: {post.title}"
        )
        
        return response.data[0]
        
    except Exception as e:
        print(f"ERROR: Create community post error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create community post: {str(e)}"
        )


@router.post("/community/{post_id}/approve")
def approve_community_post(
    post_id: str,
    current_user = Depends(require_admin)
):
    """
    POST /admin/community/{id}/approve
    Approve community post
    """
    supabase = get_supabase()
    admin_id = extract_user_id(current_user)
    
    try:
        # Check if exists
        existing = supabase.table("community_posts")\
            .select("*")\
            .eq("id", post_id)\
            .execute()
        
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Community post not found"
            )
        
        post = existing.data[0]
        
        # Update status
        supabase.table("community_posts")\
            .update({
                "status": "approved",
                "updated_at": datetime.utcnow().isoformat()
            })\
            .eq("id", post_id)\
            .execute()
        
        # Log action
        log_admin_action(
            admin_id,
            "approve_community_post",
            "community_post",
            post_id,
            f"Approved: {post.get('title', 'Untitled')}"
        )
        
        return {
            "message": "Community post approved",
            "post_id": post_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR: Approve community post error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to approve community post: {str(e)}"
        )


@router.post("/community/{post_id}/reject")
def reject_community_post(
    post_id: str,
    request: CommunityRejectRequest,
    current_user = Depends(require_admin)
):
    """
    POST /admin/community/{id}/reject
    Reject community post with reason
    """
    supabase = get_supabase()
    admin_id = extract_user_id(current_user)
    
    try:
        # Check if exists
        existing = supabase.table("community_posts")\
            .select("*")\
            .eq("id", post_id)\
            .execute()
        
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Community post not found"
            )
        
        post = existing.data[0]
        
        # Update status
        supabase.table("community_posts")\
            .update({
                "status": "rejected",
                "rejection_reason": request.reason,
                "updated_at": datetime.utcnow().isoformat()
            })\
            .eq("id", post_id)\
            .execute()
        
        # Log action
        log_admin_action(
            admin_id,
            "reject_community_post",
            "community_post",
            post_id,
            f"Rejected: {post.get('title', 'Untitled')} - {request.reason}"
        )
        
        return {
            "message": "Community post rejected",
            "post_id": post_id,
            "reason": request.reason
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR: Reject community post error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to reject community post: {str(e)}"
        )


@router.delete("/community/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_community_post(
    post_id: str,
    current_user = Depends(require_admin)
):
    """
    DELETE /admin/community/{id}
    Delete community post
    """
    supabase = get_supabase()
    admin_id = extract_user_id(current_user)
    
    try:
        # Check if exists
        existing = supabase.table("community_posts")\
            .select("id")\
            .eq("id", post_id)\
            .execute()
        
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Community post not found"
            )
        
        # Delete
        supabase.table("community_posts")\
            .delete()\
            .eq("id", post_id)\
            .execute()
        
        # Log action
        log_admin_action(
            admin_id,
            "delete_community_post",
            "community_post",
            post_id,
            f"Deleted community post"
        )
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR: Delete community post error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to delete community post: {str(e)}"
        )


# ============================================
# USERS MANAGEMENT
# ============================================

@router.get("/users", response_model=List[UserListItem])
def list_users(
    search: Optional[str] = None,
    role: Optional[str] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user = Depends(require_admin)
):
    """
    GET /admin/users?search=&role=
    List all users
    """
    supabase = get_supabase()
    
    try:
        query = supabase.table("user_profiles")\
            .select("*", count="exact")\
            .order("created_at", desc=True)
        
        # Filter by role
        if role:
            query = query.eq("role", role)
        
        # Search by name or email
        if search:
            query = query.or_(f"first_name.ilike.%{search}%,last_name.ilike.%{search}%,email.ilike.%{search}%")
        
        # Pagination
        query = query.range(offset, offset + limit - 1)
        
        response = query.execute()
        
        # Transform data with safe Unicode handling
        users = []
        for user in (response.data or []):
            try:
                # Safely build name, handling potential Unicode issues
                first_name = user.get('first_name', '') or ''
                last_name = user.get('last_name', '') or ''
                full_name = f"{first_name} {last_name}".strip()
                
                users.append({
                    "id": user.get("user_id"),
                    "name": full_name if full_name else "Unknown",
                    "email": user.get("email"),
                    "role": user.get("role", "user"),
                    "status": user.get("status", "active"),
                    "avatar": user.get("avatar"),
                    "created_at": user.get("created_at")
                })
            except Exception as user_err:
                # Skip problematic users rather than crashing
                import logging
                logging.error(f"Error processing user: {type(user_err).__name__}")
                continue
        
        return users
        
    except Exception as e:
        # Safe error logging - avoid printing user data with Unicode
        import logging
        logging.error(f"List users error: {type(e).__name__}: {str(e)[:100]}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list users"
        )


@router.post("/users/{user_id}/role")
def change_user_role(
    user_id: str,
    request: UserRoleChangeRequest,
    current_user = Depends(require_admin)
):
    """
    POST /admin/users/{id}/role
    Change user role
    """
    supabase = get_supabase()
    admin_id = extract_user_id(current_user)
    
    try:
        # Check if user exists
        existing = supabase.table("user_profiles")\
            .select("id")\
            .eq("user_id", user_id)\
            .execute()
        
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update role
        supabase.table("user_profiles")\
            .update({"role": request.role.value})\
            .eq("user_id", user_id)\
            .execute()
        
        # Log action
        log_admin_action(
            admin_id,
            "change_user_role",
            "user",
            user_id,
            f"Changed role to: {request.role.value}"
        )
        
        return {
            "message": "User role updated",
            "user_id": user_id,
            "new_role": request.role.value
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR: Change user role error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to change user role: {str(e)}"
        )


@router.post("/users/{user_id}/deactivate")
def deactivate_user(
    user_id: str,
    request: UserDeactivateRequest,
    current_user = Depends(require_admin)
):
    """
    POST /admin/users/{id}/deactivate
    Deactivate user account
    """
    supabase = get_supabase()
    admin_id = extract_user_id(current_user)
    
    try:
        # Check if user exists
        existing = supabase.table("user_profiles")\
            .select("id")\
            .eq("user_id", user_id)\
            .execute()
        
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Deactivate
        supabase.table("user_profiles")\
            .update({"status": "inactive"})\
            .eq("user_id", user_id)\
            .execute()
        
        # Log action
        log_admin_action(
            admin_id,
            "deactivate_user",
            "user",
            user_id,
            f"Deactivated: {request.reason or 'No reason provided'}"
        )
        
        return {
            "message": "User deactivated",
            "user_id": user_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR: Deactivate user error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to deactivate user: {str(e)}"
        )


# ============================================
# COMMENTS MODERATION
# ============================================

@router.get("/comments", response_model=List[CommentListItem])
def list_comments(
    status: Optional[str] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user = Depends(require_admin)
):
    """
    GET /admin/comments?status=
    List comments for moderation
    """
    supabase = get_supabase()
    
    try:
        query = supabase.table("comments")\
            .select("*", count="exact")\
            .order("created_at", desc=True)
        
        # Filter by status
        if status:
            query = query.eq("status", status)
        
        # Pagination
        query = query.range(offset, offset + limit - 1)
        
        response = query.execute()
        return response.data or []
        
    except Exception as e:
        print(f"ERROR: List comments error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to list comments: {str(e)}"
        )


@router.post("/comments/{comment_id}/hide")
def hide_comment(
    comment_id: str,
    current_user = Depends(require_admin)
):
    """
    POST /admin/comments/{id}/hide
    Hide comment
    """
    supabase = get_supabase()
    admin_id = extract_user_id(current_user)
    
    try:
        # Check if exists
        existing = supabase.table("comments")\
            .select("id")\
            .eq("id", comment_id)\
            .execute()
        
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found"
            )
        
        # Hide
        supabase.table("comments")\
            .update({"status": "hidden"})\
            .eq("id", comment_id)\
            .execute()
        
        # Log action
        log_admin_action(
            admin_id,
            "hide_comment",
            "comment",
            comment_id,
            f"Hidden comment"
        )
        
        return {
            "message": "Comment hidden",
            "comment_id": comment_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR: Hide comment error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to hide comment: {str(e)}"
        )


@router.post("/comments/{comment_id}/approve")
def approve_comment(
    comment_id: str,
    current_user = Depends(require_admin)
):
    """
    POST /admin/comments/{id}/approve
    Approve comment
    """
    supabase = get_supabase()
    admin_id = extract_user_id(current_user)
    
    try:
        # Check if exists
        existing = supabase.table("comments")\
            .select("id")\
            .eq("id", comment_id)\
            .execute()
        
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found"
            )
        
        # Approve
        supabase.table("comments")\
            .update({"status": "visible"})\
            .eq("id", comment_id)\
            .execute()
        
        # Log action
        log_admin_action(
            admin_id,
            "approve_comment",
            "comment",
            comment_id,
            f"Approved comment"
        )
        
        return {
            "message": "Comment approved",
            "comment_id": comment_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR: Approve comment error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to approve comment: {str(e)}"
        )


# ============================================
# DONATIONS VIEW
# ============================================

@router.get("/donations", response_model=List[DonationListItem])
def list_donations(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user = Depends(require_admin)
):
    """
    GET /admin/donations
    List all donations (for dashboard sum)
    """
    supabase = get_supabase()
    
    try:
        query = supabase.table("donations")\
            .select("*", count="exact")\
            .order("created_at", desc=True)\
            .range(offset, offset + limit - 1)
        
        response = query.execute()
        return response.data or []
        
    except Exception as e:
        print(f"ERROR: List donations error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to list donations: {str(e)}"
        )
