from setuptools import setup

setup(
    name="rondan",
    version="0.1",
    py_modules=["rondan"],
    install_requires=[
        "kanaconv", 
        "requests", 
        "SPARQLWrapper", 
        "lxml",
        "beautifulsoup4"],
)