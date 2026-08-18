"""Application entry point"""

import uvicorn
from .app import create_app
from .config import settings

app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "aurora.app:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info",
    )
