import pathlib

from setuptools import setup

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

setup(
    name="didcomm-demo",
    version="0.1.0",
    description="DIDComm Demo CLI for Python",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/sicpa-dlab/didcomm-demo/didcomm-python-cli",
    author="SICPA",
    author_email="DLCHOpenSourceContrib@sicpa.com",
    license="Apache-2.0",
    python_requires=">=3.7",
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    install_requires=[
        "didcomm",
        "peerdid",
        "click"
    ],
    extras_require={
        "tests": [
            "pytest==6.2.5",
            "pytest-asyncio==0.15.1",
        ]
    },
    entry_points={
        'console_scripts': [
            'didcomm-cli = didcomm_demo.didcomm_cli:cli',
        ],
    },
)
