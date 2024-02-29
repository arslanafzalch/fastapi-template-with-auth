from app.api.v1.operation import BaseOperation
from app.models import Role


class ReadRole(BaseOperation):
    async def execute(self, user_id: str) -> int | None:
        """
        Read user role

        :param user_id: ``(str)``: The unique identifier of the user to retrieve.

        :return: int | None: Role object if found, otherwise None.
        """
        role = await Role.read_user_roles(self.session, user_id)
        return role.id if role else None
