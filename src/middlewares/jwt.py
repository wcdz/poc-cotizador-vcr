from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import time

# Configuración JWT - Idealmente estos valores deberían venir de config.py
JWT_SECRET_KEY = "tu_clave_secreta_debe_ser_larga_y_aleatoria"  # Reemplazar por una clave segura
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class JWTBearer(HTTPBearer):
    """
    Middleware para JWT que verifica el token en las solicitudes
    """
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)
    
    async def __call__(self, request: Request) -> Optional[Dict[str, Any]]:
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No se proporcionaron credenciales"
            )
            
        if credentials.scheme != "Bearer":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Esquema de autenticación inválido"
            )
            
        payload = self.verify_jwt(credentials.credentials)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Token inválido o expirado"
            )
            
        return payload
    
    def verify_jwt(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verifica un token JWT y devuelve su payload si es válido
        """
        try:
            payload = jwt.decode(
                token, 
                JWT_SECRET_KEY, 
                algorithms=[JWT_ALGORITHM]
            )
            
            # Verificar si el token ha expirado
            expiration = payload.get("exp")
            if expiration is None:
                return None
                
            if datetime.utcfromtimestamp(expiration) < datetime.utcnow():
                return None
                
            return payload
        except JWTError:
            return None


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un token JWT con los datos proporcionados
    """
    to_encode = data.copy()
    
    # Establecer tiempo de expiración
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire})
    
    # Generar token
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def get_current_user(token: str) -> Dict[str, Any]:
    """
    Decodifica un token JWT y devuelve la información del usuario
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudo validar las credenciales",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Instancia del middleware para usar en dependencias
jwt_auth = JWTBearer() 