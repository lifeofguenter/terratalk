import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='terratalk',
    version='0.0.5',
    author='Gunter Grodotzki',
    author_email='gunter@grodotzki.co.za',
    description='Terraform commentator.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/lifeofguenter/terratalk',
    packages=setuptools.find_packages(),
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
    entry_points={
        'console_scripts': [
            'terratalk = terratalk.__main__:cli',
        ],
    },
)
