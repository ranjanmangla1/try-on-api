import os
import uvicorn

if __name__ == "__main__":
    debug = os.getenv("DEBUG", "0") == "1"
    port = int(os.getenv("PORT", None) or "8000")
    uvicorn.run(
        "src.try_on_api.main:create_app",
        host="0.0.0.0",
        port=port,
        reload=debug,
        proxy_headers=True,
        forwarded_allow_ips="*",
        log_level="debug" if debug else "info",
    )

