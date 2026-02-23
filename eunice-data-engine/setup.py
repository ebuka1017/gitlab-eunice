from setuptools import setup, find_packages

setup(
    name="eunice-data-engine",
    version="1.0.0",
    description="technical debt analysis engine using real gitlab data",
    author="ebuka1017",
    url="https://github.com/ebuka1017/eunice",
    packages=find_packages(),
    install_requires=[
        "python-gitlab>=4.0.0",
        "pyyaml>=6.0",
        "requests>=2.31.0",
    ],
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
