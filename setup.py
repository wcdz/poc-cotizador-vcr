from setuptools import setup, find_packages

setup(
    name="cotizador-vcr",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0",
        "pydantic>=2.4.2",
        "pydantic-settings>=2.0.3",
        "python-dotenv>=1.0.0",
        "scipy>=1.15.2",
    ],
) 