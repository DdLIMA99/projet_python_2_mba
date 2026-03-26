"""Setup script for banking-transactions-api package.

This file is kept for compatibility with tools that do not yet
support PEP 517 / pyproject.toml-only workflows, as required
by the CI/CD pipeline specifications.
"""

from setuptools import find_packages, setup

setup(
    name="banking-transactions-api",
    version="1.0.0",
    description=(
        "API REST pour exposer les données de transactions bancaires fictives."
    ),
    author="MBA2 Student",
    python_requires=">=3.12",
    packages=find_packages(exclude=["tests*"]),
    install_requires=[
        "fastapi>=0.111.0",
        "uvicorn[standard]>=0.29.0",
        "pandas>=2.2.0",
        "numpy>=1.26.0",
        "pydantic>=2.7.0",
        "python-multipart>=0.0.9",
    ],
    extras_require={
        "dev": [
            "pytest>=8.0.0",
            "pytest-cov>=5.0.0",
            "httpx>=0.27.0",
            "flake8>=7.0.0",
            "mypy>=1.9.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "banking-api=banking_api.main:app",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3.12",
        "Framework :: FastAPI",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
