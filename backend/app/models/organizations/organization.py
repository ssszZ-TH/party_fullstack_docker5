from app.config.database import database
from app.config.settings import BCRYPT_SALT
from app.schemas.organization import OrganizationCreate, OrganizationUpdate, OrganizationOut
from app.models.users.user import create_user, log_user_history
import bcrypt
import logging
from typing import Optional, List
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ค้นหา organization ด้วย ID
async def get_organization(organization_id: int) -> Optional[OrganizationOut]:
    query = """
        SELECT u.id, u.username, u.email, o.federal_tax_id, o.name_en, o.name_th, o.organization_type_id, 
               o.industry_type_id, o.employee_count, o.slogan, o.created_at, o.updated_at
        FROM users u
        JOIN organizations o ON u.id = o.id
        WHERE u.id = :id
    """
    result = await database.fetch_one(query=query, values={"id": organization_id})
    logger.info(f"Retrieved organization: id={organization_id}")
    return OrganizationOut(**result._mapping) if result else None

# ค้นหา organization ด้วย federal_tax_id
async def get_organization_by_federal_tax_id(federal_tax_id: str) -> Optional[dict]:
    query = """
        SELECT u.id, u.username, u.email, o.federal_tax_id, o.name_en, o.name_th, o.organization_type_id, 
               o.industry_type_id, o.employee_count, o.slogan, o.created_at, o.updated_at
        FROM users u
        JOIN organizations o ON u.id = o.id
        WHERE o.federal_tax_id = :federal_tax_id
    """
    result = await database.fetch_one(query=query, values={"federal_tax_id": federal_tax_id})
    logger.info(f"Queried organization with federal_tax_id {federal_tax_id}: {result}")
    return result

# ดึงข้อมูล organization ทั้งหมด
async def get_all_organizations() -> List[OrganizationOut]:
    query = """
        SELECT u.id, u.username, u.email, o.federal_tax_id, o.name_en, o.name_th, o.organization_type_id, 
               o.industry_type_id, o.employee_count, o.slogan, o.created_at, o.updated_at
        FROM users u
        JOIN organizations o ON u.id = o.id
        ORDER BY u.id ASC
    """
    results = await database.fetch_all(query=query)
    logger.info(f"Retrieved {len(results)} organizations")
    return [OrganizationOut(**result._mapping) for result in results]

# บันทึกประวัติการกระทำของ organization
async def log_organization_history(organization_id: int, federal_tax_id: Optional[str], name_en: str, 
                                  name_th: Optional[str], organization_type_id: Optional[int], 
                                  industry_type_id: Optional[int], employee_count: Optional[int], 
                                  slogan: Optional[str], action: str, action_by: Optional[int] = None):
    query = """
        INSERT INTO organization_history (organization_id, federal_tax_id, name_en, name_th, organization_type_id, 
                                        industry_type_id, employee_count, slogan, action, action_by, action_at)
        VALUES (:organization_id, :federal_tax_id, :name_en, :name_th, :organization_type_id, 
                :industry_type_id, :employee_count, :slogan, :action, :action_by, :action_at)
    """
    values = {
        "organization_id": organization_id,
        "federal_tax_id": federal_tax_id,
        "name_en": name_en,
        "name_th": name_th,
        "organization_type_id": organization_type_id,
        "industry_type_id": industry_type_id,
        "employee_count": employee_count,
        "slogan": slogan,
        "action": action,
        "action_by": action_by,
        "action_at": datetime.utcnow()
    }
    await database.execute(query=query, values=values)
    logger.info(f"Logged organization history: organization_id={organization_id}, action={action}, action_by={action_by}")

# สร้าง organization ใหม่
async def create_organization(organization: OrganizationCreate, action_by: Optional[int] = None) -> Optional[OrganizationOut]:
    async with database.transaction():
        try:
            user = UserCreate(username=organization.username, email=organization.email, password=organization.password, role="organization_user")
            user_result = await create_user(user, action_by)
            if not user_result:
                logger.warning(f"Failed to create user for organization: {organization.email}")
                return None

            if organization.federal_tax_id:
                existing_organization = await get_organization_by_federal_tax_id(organization.federal_tax_id)
                if existing_organization:
                    logger.warning(f"Attempt to create organization with existing federal_tax_id: {organization.federal_tax_id}")
                    return None

            query = """
                INSERT INTO organizations (id, federal_tax_id, name_en, name_th, organization_type_id, industry_type_id, 
                                         employee_count, slogan, created_at)
                VALUES (:id, :federal_tax_id, :name_en, :name_th, :organization_type_id, :industry_type_id, 
                        :employee_count, :slogan, :created_at)
                RETURNING id, federal_tax_id, name_en, name_th, organization_type_id, industry_type_id, 
                          employee_count, slogan, created_at, updated_at
            """
            values = {
                "id": user_result.id,
                "federal_tax_id": organization.federal_tax_id,
                "name_en": organization.name_en,
                "name_th": organization.name_th,
                "organization_type_id": organization.organization_type_id,
                "industry_type_id": organization.industry_type_id,
                "employee_count": organization.employee_count,
                "slogan": organization.slogan,
                "created_at": datetime.utcnow()
            }
            result = await database.fetch_one(query=query, values=values)
            if result:
                await log_organization_history(
                    organization_id=user_result.id,
                    federal_tax_id=organization.federal_tax_id,
                    name_en=organization.name_en,
                    name_th=organization.name_th,
                    organization_type_id=organization.organization_type_id,
                    industry_type_id=organization.industry_type_id,
                    employee_count=organization.employee_count,
                    slogan=organization.slogan,
                    action="create",
                    action_by=action_by
                )
                logger.info(f"Created organization: id={user_result.id}")
                return OrganizationOut(
                    id=user_result.id,
                    username=user_result.username,
                    email=user_result.email,
                    **result._mapping
                )
            return None
        except Exception as e:
            logger.error(f"Error creating organization: {str(e)}")
            raise

# อัปเดตข้อมูล organization
async def update_organization(organization_id: int, organization: OrganizationUpdate, action_by: Optional[int] = None) -> Optional[OrganizationOut]:
    async with database.transaction():
        values = {"id": organization_id, "updated_at": datetime.utcnow()}
        query_parts = []

        if organization.federal_tax_id is not None:
            query_parts.append("federal_tax_id = :federal_tax_id")
            values["federal_tax_id"] = organization.federal_tax_id
        if organization.name_en is not None:
            query_parts.append("name_en = :name_en")
            values["name_en"] = organization.name_en
        if organization.name_th is not None:
            query_parts.append("name_th = :name_th")
            values["name_th"] = organization.name_th
        if organization.organization_type_id is not None:
            query_parts.append("organization_type_id = :organization_type_id")
            values["organization_type_id"] = organization.organization_type_id
        if organization.industry_type_id is not None:
            query_parts.append("industry_type_id = :industry_type_id")
            values["industry_type_id"] = organization.industry_type_id
        if organization.employee_count is not None:
            query_parts.append("employee_count = :employee_count")
            values["employee_count"] = organization.employee_count
        if organization.slogan is not None:
            query_parts.append("slogan = :slogan")
            values["slogan"] = organization.slogan

        if not query_parts:
            logger.info(f"No fields to update for organization id={organization_id}")
            return None

        old_data = await get_organization(organization_id)
        if not old_data:
            return None

        query = f"""
            UPDATE organizations
            SET {', '.join(query_parts)}, updated_at = :updated_at
            WHERE id = :id
            RETURNING id, federal_tax_id, name_en, name_th, organization_type_id, industry_type_id, 
                      employee_count, slogan, created_at, updated_at
        """
        result = await database.fetch_one(query=query, values=values)
        if result:
            await log_organization_history(
                organization_id=organization_id,
                federal_tax_id=old_data.federal_tax_id,
                name_en=old_data.name_en,
                name_th=old_data.name_th,
                organization_type_id=old_data.organization_type_id,
                industry_type_id=old_data.industry_type_id,
                employee_count=old_data.employee_count,
                slogan=old_data.slogan,
                action="update",
                action_by=action_by
            )
            logger.info(f"Updated organization: id={organization_id}")
            return OrganizationOut(
                id=organization_id,
                username=old_data.username,
                email=old_data.email,
                **result._mapping
            )
        return None

# ลบ organization
async def delete_organization(organization_id: int, action_by: Optional[int] = None) -> Optional[int]:
    async with database.transaction():
        old_data = await get_organization(organization_id)
        if not old_data:
            return None

        query = "DELETE FROM organizations WHERE id = :id RETURNING id"
        result = await database.fetch_one(query=query, values={"id": organization_id})
        if result:
            await log_organization_history(
                organization_id=organization_id,
                federal_tax_id=old_data.federal_tax_id,
                name_en=old_data.name_en,
                name_th=old_data.name_th,
                organization_type_id=old_data.organization_type_id,
                industry_type_id=old_data.industry_type_id,
                employee_count=old_data.employee_count,
                slogan=old_data.slogan,
                action="delete",
                action_by=action_by
            )
            logger.info(f"Deleted organization: id={organization_id}")
            return result["id"]
        return None