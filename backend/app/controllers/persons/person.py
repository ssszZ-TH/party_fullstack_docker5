from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from typing import List
import logging
from app.models.persons.person import create_person, get_person, update_person, delete_person, get_all_persons
from app.schemas.person import PersonCreate, PersonUpdate, PersonOut
from app.controllers.users.user import get_current_user

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/persons", tags=["persons"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# สร้าง person ใหม่ (hr_admin เท่านั้น)
@router.post("/", response_model=PersonOut)
async def create_person_endpoint(person: PersonCreate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "hr_admin":
        logger.warning(f"Unauthorized attempt to create person by user: id={current_user['id']}, role={current_user['role']}")
        raise HTTPException(status_code=403, detail="HR admin access required")
    result = await create_person(person, action_by=current_user["id"])
    if not result:
        logger.warning(f"Failed to create person: {person.email}")
        raise HTTPException(status_code=400, detail="Email or personal ID number already exists")
    logger.info(f"Created person: id={result.id}")
    return result

# สร้าง person ใหม่ผ่าน backdoor (ไม่ต้องใช้ token)
@router.post("/register", response_model=PersonOut)
async def register_person_endpoint(person: PersonCreate):
    result = await create_person(person, action_by=None)
    if not result:
        logger.warning(f"Failed to register person: {person.email}")
        raise HTTPException(status_code=400, detail="Email or personal ID number already exists")
    logger.info(f"Registered person: id={result.id}")
    return result

# ดึงข้อมูล person ปัจจุบัน
@router.get("/me", response_model=PersonOut)
async def get_current_person_endpoint(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "person_user":
        logger.warning(f"Unauthorized attempt to get person by user: id={current_user['id']}, role={current_user['role']}")
        raise HTTPException(status_code=403, detail="Person user access required")
    person_id = current_user["id"]
    result = await get_person(person_id)
    if not result:
        logger.warning(f"Person not found: id={person_id}")
        raise HTTPException(status_code=404, detail="Person not found")
    logger.info(f"Retrieved person: id={person_id}")
    return result

# ดึงข้อมูล person ตาม ID (hr_admin เท่านั้น)
@router.get("/{person_id}", response_model=PersonOut)
async def get_person_endpoint(person_id: int, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "hr_admin":
        logger.warning(f"Unauthorized attempt to get person by id={person_id} by user: id={current_user['id']}, role={current_user['role']}")
        raise HTTPException(status_code=403, detail="HR admin access required")
    result = await get_person(person_id)
    if not result:
        logger.warning(f"Person not found: id={person_id}")
        raise HTTPException(status_code=404, detail="Person not found")
    logger.info(f"Retrieved person: id={person_id}")
    return result

# ดึงข้อมูล person ทั้งหมด (hr_admin เท่านั้น)
@router.get("/", response_model=List[PersonOut])
async def get_all_persons_endpoint(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "hr_admin":
        logger.warning(f"Unauthorized attempt to list all persons by user: id={current_user['id']}, role={current_user['role']}")
        raise HTTPException(status_code=403, detail="HR admin access required")
    results = await get_all_persons()
    logger.info(f"Retrieved {len(results)} persons")
    return results

# อัปเดตข้อมูล person ปัจจุบัน
@router.put("/me", response_model=PersonOut)
async def update_person_endpoint(person: PersonUpdate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "person_user":
        logger.warning(f"Unauthorized attempt to update person by user: id={current_user['id']}, role={current_user['role']}")
        raise HTTPException(status_code=403, detail="Person user access required")
    person_id = current_user["id"]
    result = await update_person(person_id, person, action_by=person_id)
    if not result:
        logger.warning(f"Person not found for update: id={person_id}")
        raise HTTPException(status_code=404, detail="Person not found")
    logger.info(f"Updated person: id={person_id}")
    return result

# อัปเดต person อื่น (hr_admin เท่านั้น)
@router.put("/{person_id}", response_model=PersonOut)
async def update_other_person_endpoint(person_id: int, person: PersonUpdate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "hr_admin":
        logger.warning(f"Unauthorized attempt to update person by id={person_id} by user: id={current_user['id']}, role={current_user['role']}")
        raise HTTPException(status_code=403, detail="HR admin access required")
    result = await update_person(person_id, person, action_by=current_user["id"])
    if not result:
        logger.warning(f"Person not found for update: id={person_id}")
        raise HTTPException(status_code=404, detail="Person not found")
    logger.info(f"Updated person: id={person_id}")
    return result

# ลบ person ปัจจุบัน
@router.delete("/me")
async def delete_self_person_endpoint(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "person_user":
        logger.warning(f"Unauthorized attempt to delete person by user: id={current_user['id']}, role={current_user['role']}")
        raise HTTPException(status_code=403, detail="Person user access required")
    person_id = current_user["id"]
    result = await delete_person(person_id, action_by=person_id)
    if not result:
        logger.warning(f"Person not found for self-deletion: id={person_id}")
        raise HTTPException(status_code=404, detail="Person not found")
    logger.info(f"Self-deleted person: id={person_id}")
    return {"message": "Person deleted"}

# ลบ person อื่น (hr_admin เท่านั้น)
@router.delete("/{person_id}")
async def delete_person_endpoint(person_id: int, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "hr_admin":
        logger.warning(f"Unauthorized attempt to delete person by id={person_id} by user: id={current_user['id']}, role={current_user['role']}")
        raise HTTPException(status_code=403, detail="HR admin access required")
    result = await delete_person(person_id, action_by=current_user["id"])
    if not result:
        logger.warning(f"Person not found for deletion: id={person_id}")
        raise HTTPException(status_code=404, detail="Person not found")
    logger.info(f"Deleted person: id={person_id}")
    return {"message": "Person deleted"}