# Test Plan for Gender Type API

| Test Description | Method | Path | JWT Bearer | Body Payload | Expected Result |
|------------------|--------|------|------------|--------------|-----------------|
| Create gender type (success) | POST | /gender_types/ | Valid basetype_admin token | `{"description": "Male"}` | Returns GenderTypeOut with id, description="Male", HTTP 200 |
| Create gender type (duplicate description) | POST | /gender_types/ | Valid basetype_admin token | `{"description": "Male"}` | HTTP 400, "Description already exists" |
| Create gender type (unauthorized) | POST | /gender_types/ | Valid non-basetype_admin token | `{"description": "Female"}` | HTTP 403, "Basetype admin access required" |
| Get gender type by ID (success) | GET | /gender_types/1 | Valid basetype_admin token | None | Returns GenderTypeOut with id=1, HTTP 200 |
| Get gender type by ID (not found) | GET | /gender_types/999 | Valid basetype_admin token | None | HTTP 404, "Gender type not found" |
| Get gender type by ID (unauthorized) | GET | /gender_types/1 | Valid non-basetype_admin token | None | HTTP 403, "Basetype admin access required" |
| Get all gender types (success) | GET | /gender_types/ | Valid basetype_admin token | None | Returns list of GenderTypeOut, HTTP 200 |
| Get all gender types (unauthorized) | GET | /gender_types/ | Valid non-basetype_admin token | None | HTTP 403, "Basetype admin access required" |
| Update gender type (success) | PUT | /gender_types/1 | Valid basetype_admin token | `{"description": "Updated Male"}` | Returns updated GenderTypeOut, HTTP 200 |
| Update gender type (no fields) | PUT | /gender_types/1 | Valid basetype_admin token | {} | HTTP 404, "Gender type not found" |
| Update gender type (not found) | PUT | /gender_types/999 | Valid basetype_admin token | `{"description": "Updated"}` | HTTP 404, "Gender type not found" |
| Update gender type (unauthorized) | PUT | /gender_types/1 | Valid non-basetype_admin token | `{"description": "Updated"}` | HTTP 403, "Basetype admin access required" |
| Delete gender type (success) | DELETE | /gender_types/1 | Valid basetype_admin token | None | Returns {"message": "Gender type deleted"}, HTTP 200 |
| Delete gender type (not found) | DELETE | /gender_types/999 | Valid basetype_admin token | None | HTTP 404, "Gender type not found" |
| Delete gender type (unauthorized) | DELETE | /gender_types/1 | Valid non-basetype_admin token | None | HTTP 403, "Basetype admin access required" |