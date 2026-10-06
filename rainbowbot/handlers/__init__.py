from aiogram import Router

from .akinator import router as akinator_router
from .start import router as start_router

router = Router()
router.include_router(akinator_router)
router.include_router(start_router)
