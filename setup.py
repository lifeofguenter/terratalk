import re
import setuptools
from distutils.util import convert_path


def find_version():
    with open(convert_path('terratalk/__init__.py')) as fh:
        version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                                  fh.read(), re.M)

        if version_match:
            return version_match.group(1)

    raise RuntimeError("Unable to find version string.")


def find_description():
    with open(convert_path('README.md')) as fh:
        return fh.read()


setuptools.setup(
    name='terratalk',
    version=find_version(),
    author='Günter Grodotzki',
    author_email='gunter@grodotzki.com',
    description='A Terraform commentator.',
    long_description=find_description(),
    long_description_content_type='text/markdown',
    url='https://github.com/lifeofguenter/terratalk',
    packages=setuptools.find_packages(exclude=['tests*']),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3',
    install_requires=[
        'click',
        'requests',
    ],
    extras_require={
        'GitHub': ['PyGithub'],
    },
    entry_points={
        'console_scripts': [
            'terratalk = terratalk.__main__:cli',
        ],
    },
)
