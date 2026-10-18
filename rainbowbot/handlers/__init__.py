from aiogram import Router

from .akinator import router as akinator_router
from .inline_help import router as inline_help_router
from .rps import router as rps_router
from .start import router as start_router

router = Router()

# команда /start
router.include_router(start_router)

# игры
router.include_router(akinator_router)
router.include_router(rps_router)

# инлайн хелп
router.include_router(inline_help_router)
