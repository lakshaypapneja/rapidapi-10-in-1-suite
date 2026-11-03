import os
from fastapi import Header, HTTPException, Request


async def verify_rapidapi_secret(
    request: Request,
    x_rapidapi_proxy_secret: str | None = Header(default=None),
):
    """
    Optional middleware/dependency to ensure requests only come through RapidAPI
    once you set RAPIDAPI_PROXY_SECRET in your production environment variables.
    During local testing or if RAPIDAPI_PROXY_SECRET is unset, all requests are allowed.
    """
    expected_secret = os.getenv("RAPIDAPI_PROXY_SECRET")
    if expected_secret and x_rapidapi_proxy_secret != expected_secret:
        raise HTTPException(
            status_code=403,
            detail="Forbidden: Invalid or missing X-RapidAPI-Proxy-Secret header.",
        )
    return True
