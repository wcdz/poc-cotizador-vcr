from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from src.core.config import settings
from src.api.routes import cotizacion_router  # Router unificado para productos
from src.api.routes import expuestos_actuarial_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    debug=settings.DEBUG,
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, restringir a dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router unificado para productos
app.include_router(
    cotizacion_router.router,
    prefix=f"{settings.API_V1_STR}/productos",
    tags=["productos"],
)

# Router para cálculos actuariales de expuestos
app.include_router(
    expuestos_actuarial_router.router,
    prefix=f"{settings.API_V1_STR}/expuestos",
    tags=["expuestos"],
)

# Endpoint base para verificar que la API está funcionando
@app.get("/")
async def root():
    return {"message": "Bienvenido a la API de Cotizador VCR :D"}


if __name__ == "__main__":
    import uvicorn

    # Usar puerto de configuración o de variable de entorno
    port = int(os.getenv("PORT", settings.PORT))
    uvicorn.run("src.main:app", host="localhost", port=port, reload=True)
