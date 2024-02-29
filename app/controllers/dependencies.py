from typing import List, Generator

from fastapi import Depends, HTTPException, status
from fastapi.responses import JSONResponse

from fastapi_another_jwt_auth import AuthJWT

from app.api.v1.role.operations import ReadRole
from app.services.oauth2 import protected_route


class RoleChecker:
    def __init__(self, allowed_roles: List):
        self.allowed_roles = allowed_roles

    async def __call__(
        self,
        user_id: str = Depends(protected_route),
        read_operation: ReadRole = Depends(ReadRole),
    ):
        role = await read_operation.execute(user_id)
        if role not in self.allowed_roles:
            raise HTTPException(status_code=403, detail="Operation not permitted")

        return user_id
