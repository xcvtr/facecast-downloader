from setuptools import setup, find_packages

setup(
    name="facecast-downloader",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0",
        "tqdm>=4.66.0",
    ],
    entry_points={
        "console_scripts": [
            "facecast-dl=src.cli:main",
        ],
    },
    python_requires=">=3.8",
)
