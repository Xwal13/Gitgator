from setuptools import setup, find_packages

setup(
    name='gh-enum',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'configparser',
        'pathlib',
    ],
    entry_points={
        'console_scripts': [
            'gh-enum = ghenum.main:main',
        ],
    },
    package_data={
        'ghenum': [
            'dorks/*.txt',
            'config.ini.example'
        ],
    },
    data_files=[
        ('config', ['config.ini.example']),
        ('dorks', ['dorks/custom_dorks.txt']),
    ],
    author='xMusashi13',
    description='GitHub Enumeration Toolkit',
    keywords='security github enumeration',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
)
