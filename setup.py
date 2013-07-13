#!/usr/bin/env python
from setuptools import setup


setup(
    name="radio.core",
    version="0.1.0",
    license="BSD",
    description="Core modules for R/a/dio code base",
    author="Wesley Bitter",
    author_email="radio@wessie.info",
    url="http://github.com/R-a-dio/radio.core",
    namespace_packages=["radio"],
    tests_require=["pytest"],
)
