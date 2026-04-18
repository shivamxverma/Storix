from fastapi import APIRouter, Depends, HTTPException, Request
import logging
from starlette.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.session import get_session
from app.api.auth.service import get_or_create_google_user, create_access_token
import json

router = APIRouter()
logger = logging.getLogger(__name__)

oauth = OAuth()
oauth.register(
    name='google',
    client_id=settings.google_client_id,
    client_secret=settings.google_client_secret,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

@router.get('/google/login')
async def login(request: Request):
    redirect_uri = settings.google_redirect_uri
    logger.info(f"Initiating Google Login")
    logger.info(f"Configured Redirect URI: {redirect_uri}")
    logger.info(f"Request Headers: {dict(request.headers)}")
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get('/google/callback')
async def auth_callback(request: Request, db: Session = Depends(get_session)):

    try:
        token = await oauth.google.authorize_access_token(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Authentication failed: {str(e)}")
    
    user_info = token.get('userinfo')
    if not user_info:
        raise HTTPException(status_code=400, detail="Failed to get user info from Google")
    
    user = get_or_create_google_user(db, user_info)
    
    access_token = create_access_token(
        data={"sub": user.email}
    )
    
    response = RedirectResponse(url=f"{settings.frontend_url}/dashboard?token={access_token}")
    return response

@router.get('/me')
async def get_me(request: Request, db: Session = Depends(get_session)):
    # This would normally use a dependency to get the current user from JWT
    pass
