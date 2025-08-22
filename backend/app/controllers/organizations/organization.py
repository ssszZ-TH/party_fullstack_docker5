from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from typing import List
import logging
from app.models.organizations.organization import create_organization, get_organization, update_organization, delete_organization, get_all_organizations
from app.schemas.organization import OrganizationCreate, OrganizationUpdate, OrganizationOut
from app.controllers.users.user import get_current_user

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/organizations", tags=["organizations"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# สร้าง organization ใหม่ (organization_admin เท่านั้น)
@router.post("/", response_model=OrganizationOut)
async def create_organization_endpoint(organization: OrganizationCreate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "organization_admin":
        logger.warning(f"Unauthorized attempt to create organization by user: id={current_user['id']}, role={current_user['role']}")
        raise HTTPException(status_code=403, detail="Organization admin access required")
    result = await create_organization(organization, action_by=current_user["id"])
    if not result:
        logger.warning(f"Failed to create organization: {organization.email}")
        raise HTTPException(status_code=400, detail="Email or federal tax ID already exists")
    logger.info(f"Created organization: id={result.id}")
    return result

# สร้าง organization ใหม่ผ่าน backdoor (ไม่ต้องใช้ token)
@router.post("/register", response_model=OrganizationOut)
async def register_organization_endpoint(organization: OrganizationCreate):
    result = await create_organization(organization, action_by=None)
    if not result:
        logger.warning(f"Failed to register organization: {organization.email}")
        raise HTTPException(status_code=400, detail="Email or federal tax ID already exists")
    logger.info(f"Registered organization: id={result.id}")
    return result

# ดึงข้อมูล organization ปัจจุบัน
@router.get("/me", response_model=OrganizationOut)
async def get_current_organization_endpoint(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "organization_user":
        logger.warning(f"Unauthorized attempt to get organization by user: id={current_user['id']}, role={current_user['role']}")
        raise HTTPException(status_code=403, detail="Organization user access required")
    organization_id = current_user["id"]
    result = await get_organization(organization_id)
    if not result:
        logger.warning(f"Organization not found: id={organization_id}")
        raise HTTPException(status_code=404, detail="Organization not found")
    logger.info(f"Retrieved organization: id={organization_id}")
    return result

# ดึงข้อมูล organization ตาม ID (organization_admin เท่านั้น)
@router.get("/{organization_id}", response_model=OrganizationOut)
async def get_organization_endpoint(organization_id: int, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "organization_admin":
        logger.warning(f"Unauthorized attempt to get organization by id={organization_id} by user: id={current_user['id']}, role={current_user['role']}")
        raise HTTPException(status_code=403, detail="Organization admin access required")
    result = await get_organization(organization_id)
    if not result:
        logger.warning(f"Organization not found: id={organization_id}")
        raise HTTPException(status_code=404, detail="Organization not found")
    logger.info(f"Retrieved organization: id={organization_id}")
    return result

# ดึงข้อมูล organization ทั้งหมด (organization_admin เท่านั้น)
@router.get("/", response_model=List[OrganizationOut])
async def get_all_organizations_endpoint(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "organization_admin":
        logger.warning(f"Unauthorized attempt to list all organizations by user: id={current_user['id']}, role={current_user['role']}")
        raise HTTPException(status_code=403, detail="Organization admin access required")
    results = await get_all_organizations()
    logger.info(f"Retrieved {len(results)} organizations")
    return results

# อัปเดตข้อมูล organization ปัจจุบัน
@router.put("/me", response_model=OrganizationOut)
async def update_organization_endpoint(organization: OrganizationUpdate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "organization_user":
        logger.warning(f"Unauthorized attempt to update organization by user: id={current_user['id']}, role={current_user['role']}")
        raise HTTPException(status_code=403, detail="Organization user access required")
    organization_id = current_user["id"]
    result = await update_organization(organization_id, organization, action_by=organization_id)
    if not result:
        logger.warning(f"Organization not found for update: id={organization_id}")
        raise HTTPException(status_code=404, detail="Organization not found")
    logger.info(f"Updated organization: id={organization_id}")
    return result

# อัปเดต organization อื่น (organization_admin เท่านั้น)
@router.put("/{organization_id}", response_model=OrganizationOut)
async def update_other_organization_endpoint(organization_id: int, organization: OrganizationUpdate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "organization_admin":
        logger.warning(f"Unauthorized attempt to update organization by id={organization_id} by user: id={current_user['id']}, role={current_user['role']}")
        raise HTTPException(status_code=403, detail="Organization admin access required")
    result = await update_organization(organization_id, organization, action_by=current_user["id"])
    if not result:
        logger.warning(f"Organization not found for update: id={organization_id}")
        raise HTTPException(status_code=404, detail="Organization not found")
    logger.info(f"Updated organization: id={organization_id}")
    return result

# ลบ organization ปัจจุบัน
@router.delete("/me")
async def delete_self_organization_endpoint(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "organization_user":
        logger.warning(f"Unauthorized attempt to delete organization by user: id={current_user['id']}, role={current_user['role']}")
        raise HTTPException(status_code=403, detail="Organization user access required")
    organization_id = current_user["id"]
    result = await delete_organization(organization_id, action_by=organization_id)
    if not result:
        logger.warning(f"Organization not found for self-deletion: id={organization_id}")
        raise HTTPException(status_code=404, detail="Organization not found")
    logger.info(f"Self-deleted organization: id={organization_id}")
    return {"message": "Organization deleted"}

# ลบ organization อื่น (organization_admin เท่านั้น)
@router.delete("/{organization_id}")
async def delete_organization_endpoint(organization_id: int, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "organization_admin":
        logger.warning(f"Unauthorized attempt to delete organization by id={organization_id} by user: id={current_user['id']}, role={current_user['role']}")
        raise HTTPException(status_code=403, detail="Organization admin access required")
    result = await delete_organization(organization_id, action_by=current_user["id"])
    if not result:
        logger.warning(f"Organization not found for deletion: id={organization_id}")
        raise HTTPException(status_code=404, detail="Organization not found")
    logger.info(f"Deleted organization: id={organization_id}")
    return {"message": "Organization deleted"}