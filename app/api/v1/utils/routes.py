from fastapi import APIRouter

from app.logger import logger

router = APIRouter()
log = logger.extendable_logger(log_name="Utils")
