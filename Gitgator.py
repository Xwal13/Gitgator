import argparse
import subprocess
import os
import json
from pathlib import Path
import configparser

# Configuration setup
config = configparser.ConfigParser()
config.read('config.ini')

# Set API key from config
GITHUB_API_KEY = config.get('API_KEYS', 'GITHUB', fallback=None)

# Path configuration
BASE_DIR = Path(__file__).parent.resolve()
DORKS_DIR = BASE_DIR / 'dorks'
CUSTOM_DORKS_FILE = DORKS_DIR / 'custom_dorks.txt'

def create_directory_structure(org_name):
    """Create organized directory structure for outputs"""
    base_path = BASE_DIR / org_name / 'secrets'
    dirs = ['gitleaks', 'trufflehog', 'dorky', 'custom_dorks']
    
    for d in dirs:
        (base_path / d).mkdir(parents=True, exist_ok=True)
    return base_path

def run_dorky(org_name, output_dir, custom_dorks=None):
    """Run dorky with standard and custom dorks"""
    output_file = output_dir / 'dorky' / 'results.json'
    custom_output_file = output_dir / 'custom_dorks' / 'results.json'
    dorks = [
        'filename:.env',
        'filename:docker-compose.yml',
        'extension:pem private'
    ]
    
    # Run standard dorks
    try:
        subprocess.run([
            'dorky',
            'github',
            '-q', ' '.join(dorks),
            '-o', str(output_file),
            '-t', GITHUB_API_KEY,
            '--org', org_name
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Dorky error: {e}")

    # Run custom dorks separately if they exist
    if custom_dorks:
        try:
            subprocess.run([
                'dorky',
                'github',
                '-q', ' '.join(custom_dorks),
                '-o', str(custom_output_file),
                '-t', GITHUB_API_KEY,
                '--org', org_name
            ], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Custom dorks error: {e}")

def load_custom_dorks():
    """Load custom dorks from directory"""
    custom_dorks = []
    if DORKS_DIR.exists():
        for dork_file in DORKS_DIR.glob('*.txt'):
            with open(dork_file, 'r') as f:
                custom_dorks.extend([line.strip() for line in f if line.strip()])
    return custom_dorks

# ... (rest of the code remains same as previous version with foundapis removed)

if __name__ == '__main__':
    main()
