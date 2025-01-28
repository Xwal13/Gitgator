from setuptools import setup, find_packages
from setuptools.command.install import install
import subprocess
import os

class PostInstallCommand(install):
    """Custom setup command to install dependencies"""
    def run(self):
        # Install system dependencies
        try:
            print("\n\033[94mInstalling system dependencies...\033[0m")
            subprocess.check_call(['sudo', 'apt-get', 'install', '-y', 'figlet', 'ruby'])
            subprocess.check_call(['sudo', 'gem', 'install', 'lolcat'])
            
            # Install Delta Corps Priest font
            font_url = 'https://github.com/xero/figlet-fonts/raw/master/delta_corps_priest_1.flf'
            font_dir = '/usr/share/figlet/'
            subprocess.check_call(['wget', font_url])
            subprocess.check_call(['sudo', 'mv', 'delta_corps_priest_1.flf', font_dir])
            print("\n\033[92mDependencies installed successfully!\033[0m")
        except Exception as e:
            print(f"\n\033[91mError installing dependencies: {str(e)}\033[0m")
            print("You may need to manually install:")
            print("- figlet (sudo apt-get install figlet)")
            print("- lolcat (sudo gem install lolcat)")
            print("- Delta Corps Priest font in /usr/share/figlet/")

        install.run(self)

setup(
    name='Gitgator',
    version='0.3',
    description='Advanced GitHub Enumeration Toolkit',
    long_description='Comprehensive GitHub scanning tool with secret detection and custom dork capabilities',
    author='xMusashi13',
    author_email='your.email@example.com',
    url='https://github.com/xMusashi13/Gitgator/tree/main',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'configparser>=5.3.0',
        'pathlib>=1.0.1',
        'shutilwhich>=1.1.0'
    ],
    cmdclass={
        'install': PostInstallCommand
    },
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
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8+',
        'Topic :: Security'
    ],
    python_requires='>=3.8',
)
