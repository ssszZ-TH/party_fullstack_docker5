from app.config.database import database
from app.config.settings import BCRYPT_SALT
from app.schemas.user import UserCreate, UserUpdate, UserOut
import bcrypt
import logging
from typing import Optional, List
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Role permissions:
# system_admin: CRUD all users
# basetype_admin: CRUD person and organization data (via respective endpoints)
# hr_admin: CRUD person-related data
# organization_admin: CRUD organization-related data

# Get user by email
async def get_user_by_email(email: str) -> Optional[dict]:
    query = "SELECT id, username, email, password, role, created_at, updated_at FROM users WHERE email = :email"
    result = await database.fetch_one(query=query, values={"email": email})
    logger.info(f"Queried user with email {email}: {result}")
    return result

# Create new user
async def create_user(user: UserCreate) -> Optional[UserOut]:
    try:
        existing_user = await get_user_by_email(user.email)
        if existing_user:
            logger.warning(f"Attempt to create user with existing email: {user.email}")
            return None
        hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), BCRYPT_SALT.encode('utf-8')).decode('utf-8')
        now = datetime.utcnow()
        query = """
            INSERT INTO users (username, email, password, role, created_at)
            VALUES (:username, :email, :password, :role, :created_at)
            RETURNING id, username, email, role, created_at, updated_at
        """
        values = {
            "username": user.username,
            "email": user.email,
            "password": hashed_password,
            "role": user.role or "hr_admin",  # Default role if not specified
            "created_at": now
        }
        async with database.transaction():
            result = await database.fetch_one(query=query, values=values)
            if result:
                # Log to users_history
                history_query = """
                    INSERT INTO users_history (user_id, username, email, password, role, action, action_by)
                    VALUES (:user_id, :username, :email, :password, :role, 'CREATE', :action_by)
                """
                history_values = {
                    "user_id": result["id"],
                    "username": user.username,
                    "email": user.email,
                    "password": hashed_password,
                    "role": user.role or "hr_admin",
                    "action_by": result["id"]  # Assuming creator is the user itself
                }
                await database.execute(query=history_query, values=history_values)
        logger.info(f"Created user: {user.email}, role: {user.role}")
        return UserOut(**result._mapping) if result else None
    except ValueError as e:
        logger.error(f"Error hashing password for {user.email}: {str(e)}")
        raise

# Get user by ID
async def get_user(user_id: int) -> Optional[UserOut]:
    query = "SELECT id, username, email, role, created_at, updated_at FROM users WHERE id = :id"
    result = await database.fetch_one(query=query, values={"id": user_id})
    logger.info(f"Retrieved user: id={user_id}")
    return UserOut(**result._mapping) if result else None

# Get all users
async def get_all_users() -> List[UserOut]:
    query = "SELECT id, username, email, role, created_at, updated_at FROM users ORDER BY id ASC"
    results = await database.fetch_all(query=query)
    logger.info(f"Retrieved {len(results)} users")
    return [UserOut(**result._mapping) for result in results]

# Update user data
async def update_user(user_id: int, user: UserUpdate, action_by: int) -> Optional[UserOut]:
    values = {"id": user_id, "updated_at": datetime.utcnow()}
    query_parts = []
    
    if user.username is not None:
        query_parts.append("username = :username")
        values["username"] = user.username
    if user.email is not None:
        query_parts.append("email = :email")
        values["email"] = user.email
    if user.password is not None:
        hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), BCRYPT_SALT.encode('utf-8')).decode('utf-8')
        query_parts.append("password = :password")
        values["password"] = hashed_password

    if not query_parts:
        logger.info(f"No fields to update for user id={user_id}")
        return None

    query = f"""
        UPDATE users
        SET {', '.join(query_parts)}, updated_at = :updated_at
        WHERE id = :id
        RETURNING id, username, email, role, created_at, updated_at
    """
    async with database.transaction():
        result = await database.fetch_one(query=query, values=values)
        if result:
            # Log to users_history
            history_query = """
                INSERT INTO users_history (user_id, username, email, password, role, action, action_by)
                VALUES (:user_id, :username, :email, :password, :role, 'UPDATE', :action_by)
            """
            history_values = {
                "user_id": user_id,
                "username": user.username or result["username"],
                "email": user.email or result["email"],
                "password": hashed_password if user.password else None,
                "role": result["role"],
                "action_by": action_by
            }
            await database.execute(query=history_query, values=history_values)
    logger.info(f"Updated user: id={user_id}")
    return UserOut(**result._mapping) if result else None

# Delete user
async def delete_user(user_id: int, action_by: int) -> Optional[int]:
    async with database.transaction():
        query = "SELECT id, username, email, password, role FROM users WHERE id = :id"
        user_data = await database.fetch_one(query=query, values={"id": user_id})
        if user_data:
            # Log to users_history
            history_query = """
                INSERT INTO users_history (user_id, username, email, password, role, action, action_by)
                VALUES (:user_id, :username, :email, :password, :role, 'DELETE', :action_by)
            """
            history_values = {
                "user_id": user_id,
                "username": user_data["username"],
                "email": user_data["email"],
                "password": user_data["password"],
                "role": user_data["role"],
                "action_by": action_by
            }
            await database.execute(query=history_query, values=history_values)
            
            # Delete user
            delete_query = "DELETE FROM users WHERE id = :id RETURNING id"
            result = await database.fetch_one(query=delete_query, values={"id": user_id})
            logger.info(f"Deleted user: id={user_id}")
            return result["id"] if result else None
    return None

# Verify user password
async def verify_user_password(user_id: int, password: str) -> bool:
    query = "SELECT password FROM users WHERE id = :id"
    result = await database.fetch_one(query=query, values={"id": user_id})
    if not result:
        logger.warning(f"User not found for password verification: id={user_id}")
        return False
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), BCRYPT_SALT.encode('utf-8')).decode('utf-8')
    logger.info(f"Verified password for user id={user_id}")
    return hashed_password == result["password"]