from setuptools import setup, find_packages

setup(
    name="simple_model",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "pydantic>=2.0.0",
        "email-validator>=1.1.3",
        "strawberry-graphql[fastapi]>=0.138.0",
        "motor>=3.3.0",
    ],
    package_dir={"": "."},
)
