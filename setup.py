import os

from setuptools import setup


def path_in_project(*path):
    return os.path.join(os.path.dirname(__file__), *path)


def read_file(filename):
    with open(path_in_project(filename)) as f:
        return f.read()


def read_requirements(filename):
    contents = read_file(filename).strip('\n')
    return contents.split('\n') if contents else []

setup(
    name="yaws_integration_tests",
    version="0.0.1",
    author="Maciej Walerczuk",
    author_email="mwalerczuk@gmail.com",
    license="BSD",
    include_package_data=True,
    tests_require=read_requirements('requirements.txt'),
    zip_safe=False,
)
