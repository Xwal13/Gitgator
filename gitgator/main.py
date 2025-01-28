import argparse
import subprocess
import os
import json
import shutil
import sys
from pathlib import Path
import configparser

# Banner configuration
BANNER_TEXT = """
 ██████  ██ ████████  ██████   █████  ████████  ██████  ██████  
██       ██    ██    ██    ██ ██   ██    ██    ██    ██ ██   ██ 
██   ███ ██    ██    ██    ██ ███████    ██    ██    ██ ██████  
██    ██ ██    ██    ██    ██ ██   ██    ██    ██    ██ ██   ██ 
 ██████  ██    ██     ██████  ██   ██    ██     ██████  ██   ██ 
"""

def show_banner():
    """Display awesome banner with fallback"""
    try:
        has_figlet = shutil.which('figlet') is not None
        has_lolcat = shutil.which('lolcat') is not None
        
        if has_figlet and has_lolcat:
            figlet = subprocess.Popen(
                ['figlet', '-w', '100', '-f', 'Delta_Corps_Priest_1', 'GitGator'],
                stdout=subprocess.PIPE
            )
            lolcat = subprocess.Popen(
                ['lolcat'],
                stdin=figlet.stdout,
                stdout=subprocess.PIPE
            )
            output, _ = lolcat.communicate()
            print(output.decode('utf-8'))
        else:
            print("\033[95m" + BANNER_TEXT + "\033[0m")
            
    except Exception as e:
        print(f"\n\033[93mSimple Banner:\033[0m")
        print("\033[95m" + BANNER_TEXT + "\033[0m")

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

def run_gitleaks(org_name, output_dir):
    """Run gitleaks and save results"""
    output_file = output_dir / 'gitleaks' / 'results.json'
    try:
        subprocess.run([
            'gitleaks',
            'detect',
            '--source', f'https://github.com/{org_name}',
            '--report-format', 'json',
            '--report-path', str(output_file)
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Gitleaks error: {e}")

def run_trufflehog(org_name, output_dir):
    """Run trufflehog and save results"""
    output_file = output_dir / 'trufflehog' / 'results.txt'
    try:
        result = subprocess.run([
            'trufflehog',
            'github',
            '--org', org_name,
            '--token', GITHUB_API_KEY,
            '--json'
        ], capture_output=True, text=True, check=True)
        
        with open(output_file, 'w') as f:
            f.write(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Trufflehog error: {e}")

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

def main():
    show_banner()
    
    parser = argparse.ArgumentParser(description='GitHub Enumeration Tool')
    parser.add_argument('-Org', help='Single organization name')
    parser.add_argument('-mOrg', nargs='+', help='Multiple organization names')
    
    args = parser.parse_args()
    orgs = []
    
    if args.Org:
        orgs.append(args.Org)
    if args.mOrg:
        orgs.extend(args.mOrg)
    
    if not orgs:
        print("No organizations specified!")
        return
    
    custom_dorks = load_custom_dorks()
    
    for org in orgs:
        print(f"\n\033[1mProcessing organization: {org}\033[0m")
        output_dir = create_directory_structure(org)
        
        # Run security tools
        run_gitleaks(org, output_dir)
        run_trufflehog(org, output_dir)
        run_dorky(org, output_dir, custom_dorks)
        
        print(f"\n\033[92mCompleted scanning for {org}\033[0m")
        print(f"Results saved to: {output_dir}\n")

if __name__ == '__main__':
    main()
