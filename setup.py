"""
Setup configuration for WebScraperPortable
"""

from setuptools import setup, find_packages

setup(
    name="WebScraperPortable",
    version="2.0.0",
    description="A self-contained, portable web scraper with session-based output",
    package_dir={"WebScraperPortable": "src"},
    packages=["WebScraperPortable"],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.0",
        "beautifulsoup4>=4.11.0",
        "pandas>=1.5.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "full": [
            "ollama>=0.1.0",
            "numpy>=1.21.0",
            "rich>=13.0.0",
            "python-docx>=0.8.11",
            "PyMuPDF>=1.21.0",
        ],
        "dev": [
            "pytest>=8.0.0",
            "pytest-mock>=3.10.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "webscraper=WebScraperPortable.__main__:main",
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
