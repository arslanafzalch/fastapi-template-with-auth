# This file is used to resolve the circular imports in the models package.


def __resolve_base_user_class__():
    """
    Return the child class of BaseUser based on the type.
    """
    from app.models.base_users import BaseUser

    return BaseUser


def __resolve_user_class__():
    """
    Return the child class of User based on the type.
    """
    from app.models.users import User

    return User
