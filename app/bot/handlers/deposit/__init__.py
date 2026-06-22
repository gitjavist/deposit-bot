from .add import router as add_router
from .edit import router as edit_router
from .delete import router as delete_router
from .list import router as list_router
from .settings import router as settings_router
from .wizard import router as wizard_router
from .analytics import router as analytics_router
from .admin import router as admin_router
from .cards import router as cards_router

routers = [
    add_router,
    edit_router,
    delete_router,
    list_router,
    settings_router,
    wizard_router,
    analytics_router,
    admin_router,
    cards_router
]