from setuptools import setup, find_packages

setup(
    name='Gitgator',
    version='0.1',
    description='Comprehensive GitHub Enumeration Toolkit',
    long_description='Advanced GitHub organization scanning tool with integrated secret detection and custom dork capabilities',
    author='xMusashi13',
    author_email='your.email@example.com',  # Update with your email
    url='https://github.com/xMusashi13/Gitgator/tree/main',
    license='MIT',
    packages=find_packages(),
    package_dir={'gitgator': 'gitgator'},
    include_package_data=True,
    install_requires=[
        'configparser>=5.3.0',
        'pathlib>=1.0.1',
    ],
    entry_points={
        'console_scripts': [
            'gitgator = gitgator.main:main',
        ],
    },
    package_data={
        'gitgator': [
            'dorks/*.txt',
            'config.ini.example'
        ],
    },
    data_files=[
        ('config', ['config.ini.example']),
        ('dorks', ['dorks/custom_dorks.txt']),
        ('', ['LICENSE']),  # Add your LICENSE file
    ],
    keywords='security github enumeration secrets-detection devsecops',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Security',
        'Topic :: Utilities'
    ],
    python_requires='>=3.8',
    project_urls={
        'Private Repository': 'https://github.com/xMusashi13/Gitgator/tree/main',
    },
)
