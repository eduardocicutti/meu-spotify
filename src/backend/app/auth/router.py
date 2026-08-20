# app/auth/router.py
from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import RedirectResponse

from app.auth.dependencies import get_current_user
from app.auth.service import get_authorize_url, handle_callback
from app.users.models import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/login")
async def login(request: Request):
    """Inicia fluxo OAuth - redireciona para Spotify."""
    state = request.session.get("oauth_state") if hasattr(request, "session") else None
    # Gerar state aleatório para segurança
    import secrets
    state = secrets.token_urlsafe(32)

    # Guardar state na sessão (simplificado - em produção usar Redis)
    # Para dev, vamos passar no redirect
    auth_url = get_authorize_url(state)
    return RedirectResponse(url=auth_url)


@router.get("/callback")
async def callback(request: Request, code: str, state: str):
    """Callback do OAuth - troca code por tokens e cria sessão."""
    session_token = await handle_callback(code, state)

    # Redirect para frontend com cookie
    response = RedirectResponse(url="/")
    response.set_cookie(
        key="session",
        value=session_token,
        httponly=True,
        secure=False,  # True em produção (HTTPS)
        samesite="lax",
        max_age=7 * 24 * 3600,  # 7 dias
        path="/",
    )
    return response


@router.post("/logout")
async def logout(response: Response):
    """Logout - invalida cookie de sessão."""
    response = Response(content="Logged out")
    response.delete_cookie(key="session", path="/", httponly=True, samesite="lax")
    return response


@router.get("/me")
async def get_me(user: User = Depends(get_current_user)):
    """Retorna dados do usuário autenticado."""
    return {
        "id": user.id,
        "display_name": user.display_name,
        "email": user.email,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }
