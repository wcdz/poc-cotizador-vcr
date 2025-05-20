# Cotizador VCR

Aplicación de cotización para seguros con funcionalidades de cálculo actuarial y proyecciones financieras.

## Descripción del Proyecto

El Cotizador VCR es una aplicación web desarrollada con FastAPI que permite la gestión de cotizaciones de seguros con capacidades avanzadas de cálculo actuarial. La aplicación proporciona una API para crear, actualizar, eliminar y consultar cotizaciones, así como para realizar cálculos complejos basados en modelos financieros y actuariales.

## Arquitectura

La aplicación sigue una arquitectura de capas orientada al dominio (DDD):

```
src/
├── api/                # Capa de API REST
│   └── routes/         # Endpoints organizados por funcionalidad
│
├── models/             # Modelos de datos
│   ├── domain/         # Modelos de dominio con lógica de negocio
│   └── schemas/        # Esquemas Pydantic para validación de datos
│
├── services/           # Servicios de orquestación
│   ├── cotizador_service.py    # Servicio unificado para cotizaciones
│   └── expuestos_mes_service.py # Servicio para cálculos de exposición
│
├── repositories/       # Acceso a datos
│
├── core/               # Configuración y elementos core
│   └── middlewares/    # Middlewares (JWT, logging, etc.)
│
├── middlewares/        # Middlewares a nivel de aplicación
│
├── utils/              # Utilidades genéricas 
│
└── helpers/            # Funciones auxiliares específicas
    └── goalseek.py     # Herramientas de cálculo financiero
```

### Módulos de Cálculo

La aplicación incluye módulos especializados para cálculos actuariales y financieros, siguiendo una arquitectura DDD donde la lógica de negocio reside en los modelos de dominio:

- **Expuestos_mes**: Cálculo de exposición mensual al riesgo
- **Gastos**: Proyección y cálculo de gastos
- **Margen_solvencia**: Cálculo de requisitos de solvencia
- **Reserva**: Estimación de reservas técnicas
- **Flujo_resultado**: Proyección de flujos de resultados

### Endpoints Principales

- **`/api/v1/productos/cotizar`**: Endpoint unificado para cotizaciones de diferentes productos (RUMBO, ENDOSOS)
- **`/api/v1/expuestos/calcular`**: Cálculo de exposición mensual
- **`/api/v1/expuestos/proyectar`**: Proyección de exposición mensual

## Requisitos

- Python 3.8+
- FastAPI
- Uvicorn
- Pydantic
- SciPy (para cálculos matemáticos complejos)

## Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/wcdz/poc-cotizador-vcr.git
cd poc-cotizador-vcr
```

2. Crear y activar un entorno virtual:
```bash
python -m venv venv
# En Windows
venv\Scripts\activate
# En macOS/Linux
source venv/bin/activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Instalar el proyecto en modo desarrollo:
```bash
pip install -e .
```

## Uso

### Iniciar la aplicación

```bash
# Método recomendado
python src/main.py

# Alternativamente
python -m uvicorn src.main:app --reload
```

La API estará disponible en `http://localhost:8080`

### Documentación de la API

Una vez iniciada la aplicación, puedes acceder a la documentación interactiva:

- Swagger UI: `http://localhost:8080/docs`
- ReDoc: `http://localhost:8080/redoc`

## Desarrollo

Para extender la funcionalidad o modificar el comportamiento de la aplicación, se recomienda seguir la estructura de módulos existente y mantener la separación de responsabilidades según los principios de Domain-Driven Design.

### Nuevos Cálculos

Para añadir nuevos modelos de cálculo:

1. Crear un modelo de dominio en `src/models/domain/` con toda la lógica de negocio
2. Implementar un servicio correspondiente en `src/services/` que orqueste operaciones
3. Crear esquemas Pydantic en `src/models/schemas/` para la validación de datos
4. Exponer la funcionalidad mediante endpoints en `src/api/routes/`

## Licencia

Este proyecto está bajo licencia MIT.

## Autor

William Elisban Chávez Díaz
- Email: wcdz.dev@gmail.com
- GitHub: [@wcdz](https://github.com/wcdz)
