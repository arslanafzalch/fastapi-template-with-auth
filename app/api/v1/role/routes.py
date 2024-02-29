from fastapi import APIRouter

from app.logger import logger

log = logger.extendable_logger(log_name="Role")
router = APIRouter()
