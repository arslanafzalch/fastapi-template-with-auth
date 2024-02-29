from datetime import datetime, date as date_type

from fastapi import HTTPException, status
from passlib.context import CryptContext
import random

from app.core.constants import DATE_FORMAT, DATETIME_FORMAT

txt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_text(text: str):
    """
    Hash text

    :param text: ``(str)``: The text to hash.

    :return: ``(str)``: The hashed text.
    """
    return txt_context.hash(text)


def verify_hashed_text(text: str, hashed_text: str):
    """
    Verify text

    :param text: ``(str)``: The text to verify.
    :param hashed_text: ``(str)``: The hashed text to verify against.

    :return: ``(bool)``: True if the text matches the hashed text, otherwise False.
    """
    return txt_context.verify(text, hashed_text)


def generate_random_number(size: int = 4):
    """
    Generate random number

    :param size: ``(int)``: The size of the random number.

    :return:  ``(int)``: The random number.
    """
    min_size = pow(10, size - 1)
    max_size = pow(10, size) - 1

    return random.randint(min_size, max_size)


def get_current_timestamp() -> datetime:
    """
    Get current timestamp

    :return: ``(datetime)``: The current timestamp.
    """
    return datetime.now().replace(microsecond=0)


def convert_str_to_date_from_request(
    _date: str, date_format: str = DATE_FORMAT
) -> date_type:
    """
    Convert string to datetime

    :param _date: ``(str)``: The date string to convert.
    :param date_format: ``(str)``: The date format.

    :return: ``(date)``: The datetime object.

    :raises: HTTPException: If the date is not in the correct format.
    """
    try:
        _date = (
            datetime.strptime(_date, date_format)
            if _date is not None
            else datetime.today().date()
        )
        return _date
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect date entered. Date must be in YYYY-MM-DD format",
        )
