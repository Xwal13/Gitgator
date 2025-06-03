from setuptools import setup, find_packages
from setuptools.command.install import install
import subprocess
import os
import sys

class PostInstallCommand(install):
    """Custom setup command to install dependencies via pip install ."""
    def run(self):
        # Install system dependencies (best-effort, warn if sudo or apt is not available)
        try:
            print("\n\033[94mInstalling system dependencies (requires sudo privileges)...\033[0m")
            # Check if apt-get exists
            if subprocess.call(['which', 'apt-get'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
                subprocess.check_call(['sudo', 'apt-get', 'update'])
                subprocess.check_call(['sudo', 'apt-get', 'install', '-y', 'figlet', 'ruby'])
            else:
                print("\033[93mSkipping apt-get install: not a Debian/Ubuntu system or apt-get not available.\033[0m")

            # Check if gem exists
            if subprocess.call(['which', 'gem'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
                subprocess.check_call(['sudo', 'gem', 'install', 'lolcat'])
            else:
                print("\033[93mSkipping gem install: 'gem' not found.\033[0m")

            # Install Delta Corps Priest font
            font_url = 'https://raw.githubusercontent.com/xero/figlet-fonts/master/delta_corps_priest_1.flf'
            font_dir = '/usr/share/figlet/'
            font_name = 'delta_corps_priest_1.flf'
            # Download font only if wget exists
            if subprocess.call(['which', 'wget'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
                subprocess.check_call(['wget', font_url, '-O', font_name])
                subprocess.check_call(['sudo', 'mv', font_name, font_dir])
            else:
                print("\033[93mSkipping font download: 'wget' not found.\033[0m")

            print("\n\033[92mSystem dependencies installation attempted. If errors occurred, please install them manually.\033[0m")
        except Exception as e:
            print(f"\n\033[91mError installing dependencies: {str(e)}\033[0m")
            print("You may need to manually install:")
            print("- figlet (sudo apt-get install figlet)")
            print("- lolcat (sudo gem install lolcat)")
            print("- Delta Corps Priest font in /usr/share/figlet/")

        # Run standard pip install process
        super().run()

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
        ('config', ['gitgator/config.ini.example']),
        ('dorks', ['gitgator/dorks/custom_dorks.txt']),
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Security'
    ],
    python_requires='>=3.8',
)

