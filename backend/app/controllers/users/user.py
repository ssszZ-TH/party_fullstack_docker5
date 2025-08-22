from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from typing import List, Optional
from datetime import datetime, timedelta
import logging
from app.models.users.user import create_user, get_user, update_user, delete_user, get_all_users
from app.schemas.user import UserCreate, UserUpdate, UserOut
from app.config.settings import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["users"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# ตรวจสอบผู้ใช้จาก JWT token
async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.info(f"Decoded JWT payload: {payload}")
        user_id: str = payload.get("sub")
        role: str = payload.get("role")
        if user_id is None:
            logger.error("Invalid token: missing 'sub'")
            raise HTTPException(status_code=401, detail="Invalid token")
        logger.info(f"Authenticated user: id={user_id}, role={role}")
        return {"id": int(user_id), "role": role}
    except JWTError as e:
        logger.error(f"JWT decode failed: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid token")

# สร้างผู้ใช้ใหม่ (system_admin เท่านั้น)
@router.post("/", response_model=UserOut)
async def create_user_endpoint(user: UserCreate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "system_admin":
        logger.warning(f"Unauthorized attempt to create user by user: id={current_user['id']}, role={current_user['role']}")
        raise HTTPException(status_code=403, detail="System admin access required")
    valid_roles = ["system_admin", "hr_admin", "organization_admin"]
    if user.role is not None and user.role not in valid_roles:
        logger.warning(f"Invalid role provided: {user.role}")
        raise HTTPException(status_code=422, detail=f"Role must be one of {valid_roles}")
    result = await create_user(user, action_by=current_user["id"])
    if not result:
        logger.warning(f"Failed to create user: {user.email}")
        raise HTTPException(status_code=400, detail="Email already exists")
    logger.info(f"Created user: {user.email}, role={result.role}")
    return result

# สร้างผู้ใช้ใหม่ผ่าน backdoor (ไม่ต้องใช้ token)
@router.post("/register", response_model=UserOut)
async def register_user_endpoint(user: UserCreate):
    valid_roles = ["system_admin", "hr_admin", "organization_admin"]
    if user.role is not None and user.role not in valid_roles:
        logger.warning(f"Invalid role provided: {user.role}")
        raise HTTPException(status_code=422, detail=f"Role must be one of {valid_roles}")
    result = await create_user(user, action_by=None)
    if not result:
        logger.warning(f"Failed to register user: {user.email}")
        raise HTTPException(status_code=400, detail="Email already exists")
    logger.info(f"Registered user: {user.email}, role={result.role}")
    return result

# ดึงข้อมูลผู้ใช้ปัจจุบัน
@router.get("/me", response_model=UserOut)
async def get_current_user_endpoint(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    result = await get_user(user_id)
    if not result:
        logger.warning(f"User not found: id={user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    logger.info(f"Retrieved current user: id={user_id}, role={result.role}")
    return result

# ดึงข้อมูลผู้ใช้ตาม ID (system_admin เท่านั้น)
@router.get("/{user_id}", response_model=UserOut)
async def get_user_endpoint(user_id: int, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "system_admin":
        logger.warning(f"Unauthorized attempt to get user by id={user_id} by user: id={current_user['id']}, role={current_user['role']}")
        raise HTTPException(status_code=403, detail="System admin access required")
    result = await get_user(user_id)
    if not result:
        logger.warning(f"User not found: id={user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    if result.role not in ["system_admin", "hr_admin", "organization_admin"]:
        logger.warning(f"Unauthorized attempt to access user with role={result.role} by user: id={current_user['id']}")
        raise HTTPException(status_code=403, detail="Cannot access this user")
    logger.info(f"Retrieved user: id={user_id}, role={result.role}")
    return result

# ดึงข้อมูลผู้ใช้ทั้งหมด (system_admin เท่านั้น)
@router.get("/", response_model=List[UserOut])
async def get_all_users_endpoint(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "system_admin":
        logger.warning(f"Unauthorized attempt to list all users by user: id={current_user['id']}, role={current_user['role']}")
        raise HTTPException(status_code=403, detail="System admin access required")
    results = await get_all_users()
    filtered_results = [user for user in results if user.role in ["system_admin", "hr_admin", "organization_admin"]]
    logger.info(f"Retrieved {len(filtered_results)} users")
    return filtered_results

# อัปเดตข้อมูลผู้ใช้ปัจจุบัน
@router.put("/me", response_model=UserOut)
async def update_user_endpoint(user: UserUpdate, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    if user.role is not None:
        logger.warning(f"Unauthorized attempt to change role by user: id={user_id}")
        raise HTTPException(status_code=403, detail="Cannot change role")
    result = await update_user(user_id, user, action_by=user_id)
    if not result:
        logger.warning(f"User not found for update: id={user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    logger.info(f"Updated user: id={user_id}, role={result.role}")
    return result

# อัปเดตผู้ใช้อื่น (system_admin เท่านั้น)
@router.put("/{user_id}", response_model=UserOut)
async def update_other_user_endpoint(user_id: int, user: UserUpdate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "system_admin":
        logger.warning(f"Unauthorized attempt to update user by id={user_id} by user: id={current_user['id']}, role={current_user['role']}")
        raise HTTPException(status_code=403, detail="System admin access required")
    target_user = await get_user(user_id)
    if not target_user:
        logger.warning(f"User not found for update: id={user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    if target_user.role not in ["system_admin", "hr_admin", "organization_admin"]:
        logger.warning(f"Unauthorized attempt to update user with role={target_user.role} by user: id={current_user['id']}")
        raise HTTPException(status_code=403, detail="Cannot update this user")
    valid_roles = ["system_admin", "hr_admin", "organization_admin"]
    if user.role is not None and user.role not in valid_roles:
        logger.warning(f"Invalid role provided: {user.role}")
        raise HTTPException(status_code=422, detail=f"Role must be one of {valid_roles}")
    result = await update_user(user_id, user, action_by=current_user["id"])
    if not result:
        logger.warning(f"User not found for update: id={user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    logger.info(f"Updated user: id={user_id}, role={result.role}")
    return result

# ลบผู้ใช้ปัจจุบัน
@router.delete("/me")
async def delete_self_endpoint(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    result = await delete_user(user_id, action_by=user_id)
    if not result:
        logger.warning(f"User not found for self-deletion: id={user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    logger.info(f"Self-deleted user: id={user_id}")
    return {"message": "User deleted"}

# ลบผู้ใช้อื่น (system_admin เท่านั้น)
@router.delete("/{user_id}")
async def delete_user_endpoint(user_id: int, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "system_admin":
        logger.warning(f"Unauthorized attempt to delete user by id={user_id} by user: id={current_user['id']}, role={current_user['role']}")
        raise HTTPException(status_code=403, detail="System admin access required")
    target_user = await get_user(user_id)
    if not target_user:
        logger.warning(f"User not found for deletion: id={user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    if target_user.role not in ["system_admin", "hr_admin", "organization_admin"]:
        logger.warning(f"Unauthorized attempt to delete user with role={target_user.role} by user: id={current_user['id']}")
        raise HTTPException(status_code=403, detail="Cannot delete this user")
    result = await delete_user(user_id, action_by=current_user["id"])
    if not result:
        logger.warning(f"User not found for deletion: id={user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    logger.info(f"Deleted user: id={user_id}")
    return {"message": "User deleted"}

# สร้าง JWT access token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt