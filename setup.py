#!/usr/bin/env python3
"""
Setup script for Streamlined NANDA Adapter
"""

from setuptools import setup, find_packages
import os


def read_requirements():
    """Read requirements from file"""
    requirements = [
        "flask",
        "anthropic",
        "requests",
        "python-a2a==0.5.6",
        "mcp",
        "python-dotenv",
        "flask-cors",
        "psutil"  # For system monitoring
    ]
    return requirements


def read_readme():
    """Read README file for long description"""
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Streamlined NANDA Adapter - Efficient AI Agent Communication System"


setup(
    name="streamlined-nanda-adapter",
    version="2.0.0",
    description="Streamlined AI Agent Communication Framework with intelligent discovery and telemetry",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="NANDA Team",
    author_email="support@nanda.ai",
    url="https://github.com/projnanda/streamlined-adapter.git",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": ["pytest", "pytest-asyncio", "black", "flake8"],
        "monitoring": ["prometheus-client", "grafana-api"],
    },
    entry_points={
        "console_scripts": [
            "streamlined-adapter=nanda_core.core.adapter:main",
            "nanda-discover=nanda_core.discovery.agent_discovery:main"
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="nanda ai agent framework streamlined discovery telemetry",
    include_package_data=True,
    zip_safe=False,
)