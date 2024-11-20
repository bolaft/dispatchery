from setuptools import setup, find_packages

setup(
    name="dispatchery",
    version="0.3.2",
    description="A Python package for advanced function dispatching based on complex, nested, and parameterized types. Inspired by singledispatch.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Soufian Salim",
    author_email="soufian.salim@gmail.com",
    url="https://github.com/bolaft/dispatchery",
    packages=find_packages(),
    keywords="dispatch, type-safety, singledispatch, functools, typing, types",
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
)
