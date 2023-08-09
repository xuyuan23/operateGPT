"""wutils: handy tools
"""
from codecs import open
from os import path

from setuptools import find_packages, setup


here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

with open(path.join(here, "requirements.txt"), encoding="utf-8") as f:
    requirements = [line.strip() for line in f if line]

setup(
    name="operategpt",
    version="0.0.1",
    description="Automatic Operations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="operategpt.cn",
    author="xuyuan23",
    author_email="643854343@qq.com",
    license="Apache 2.0",
    keywords="automatic operations gpt llms",
    packages=find_packages(exclude=["contrib", "docs", "examples"]),
    python_requires=">=3.9",
    install_requires=requirements,
)
