from setuptools import setup, find_packages
from distutils.util import convert_path


def find_description():
    with open(convert_path('README.md')) as fh:
        return fh.read()


setup(
    name='terratalk',
    version='0.4.1',
    py_modules=['cli'],
    author='Günter Grodotzki',
    author_email='gunter@grodotzki.com',
    description='A Terraform commentator.',
    long_description=find_description(),
    long_description_content_type='text/markdown',
    url='https://github.com/lifeofguenter/terratalk',
    packages=find_packages(exclude=['tests*']),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3',
    install_requires=[
        'Click',
        'requests',
    ],
    extras_require={
        'GitHub': ['PyGithub'],
        'GitLab': ['python-gitlab'],
    },
    entry_points={
        'console_scripts': [
            'terratalk = terratalk.__main__:cli',
        ],
    },
)
