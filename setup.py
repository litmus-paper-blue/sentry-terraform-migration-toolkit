#!/usr/bin/env python3
"""
Setup configuration for sentry-terraform-discovery
"""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="sentry-terraform-discovery",
    version="1.0.0",
    author="Ogonna Nnamani",
    author_email="ogonna.devops@gmail.com",
    description="Discover Sentry resources and generate Terraform configurations",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/litmus-paper-blue/sentry-terraform-discovery",
    project_urls={
        "Bug Reports": "https://github.com/litmus-paper-blue/sentry-terraform-discovery/issues",
        "Source": "https://github.com/litmus-paper-blue/sentry-terraform-discovery",
        "Documentation": "https://github.com/litmus-paper-blue/sentry-terraform-discovery/blob/main/docs/",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Systems Administration",
        "Topic :: Software Development :: Code Generators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.10.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
            "pre-commit>=2.20.0",
            "twine>=4.0.0",
        ],
        "test": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.10.0",
            "responses>=0.22.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "sentry-discovery=sentry_discovery.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "sentry_discovery": [
            "templates/*.j2",
            "templates/**/*.j2",
        ],
    },
    keywords="sentry terraform infrastructure-as-code devops migration",
    zip_safe=False,
)