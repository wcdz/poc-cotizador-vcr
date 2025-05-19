# Cotizador VCR

Aplicación de cotización para seguros con funcionalidades de cálculo actuarial y proyecciones financieras.

## Descripción del Proyecto

El Cotizador VCR es una aplicación web desarrollada con FastAPI que permite la gestión de cotizaciones de seguros con capacidades avanzadas de cálculo actuarial. La aplicación proporciona una API para crear, actualizar, eliminar y consultar cotizaciones, así como para realizar cálculos complejos basados en modelos financieros y actuariales.

## Arquitectura

La aplicación sigue una arquitectura de capas orientada al dominio:

```
src/
├── api/                # Capa de API REST
│   └── routes/         # Endpoints organizados por funcionalidad
│
├── models/             # Modelos de datos
│   ├── domain/         # Modelos de dominio (entidades core)
│   └── schemas/        # Esquemas Pydantic para validación de datos
│
├── services/           # Servicios de negocio
│   ├── cotizador.py    # Servicio para cotizaciones
│   └── ...             # Otros servicios de cálculo
│
├── repositories/       # Acceso a datos
│
├── core/               # Configuración y elementos core
│
├── utils/              # Utilidades genéricas 
│
└── helpers/            # Funciones auxiliares específicas
    └── goalseek.py     # Herramientas de cálculo financiero
```

### Módulos de Cálculo

La aplicación incluye módulos especializados para cálculos actuariales y financieros:

- **Expuestos_mes**: Cálculo de exposición mensual al riesgo
- **Gastos**: Proyección y cálculo de gastos
- **Margen_solvencia**: Cálculo de requisitos de solvencia
- **Reserva**: Estimación de reservas técnicas
- **Flujo_resultado**: Proyección de flujos de resultados

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

## Uso

### Iniciar la aplicación

```bash
uvicorn src.main:app --reload
```

La API estará disponible en `http://localhost:8000`

### Documentación de la API

Una vez iniciada la aplicación, puedes acceder a la documentación interactiva:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Desarrollo

Para extender la funcionalidad o modificar el comportamiento de la aplicación, se recomienda seguir la estructura de módulos existente y mantener la separación de responsabilidades.

### Nuevos Cálculos

Para añadir nuevos modelos de cálculo:

1. Crear un modelo de dominio en `src/models/domain/`
2. Implementar el servicio correspondiente en `src/services/`
3. Exponer la funcionalidad mediante endpoints en `src/api/routes/`

## Licencia

Este proyecto está bajo licencia MIT.

## Autor

William Elisban Chávez Díaz
- Email: wcdz.dev@gmail.com
- GitHub: [@wcdz](https://github.com/wcdz)
