#!/usr/bin/env python3
import argparse
import subprocess
import os
import sys
import shutil
import requests
from pathlib import Path
import configparser
import time

def show_banner():
    """Display awesome banner with fallback"""
    try:
        has_figlet = shutil.which('figlet') is not None
        has_lolcat = shutil.which('lolcat') is not None

        if has_figlet and has_lolcat:
            figlet = subprocess.Popen(
                ['figlet', '-w', '100', '-f', 'standard', 'GitGator'],
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
            print("\n\033[95mGitGator - GitHub Enumeration Tool\033[0m\n")
    except Exception:
        print("\n\033[95mGitGator - GitHub Enumeration Tool\033[0m\n")

# Determine BASE_DIR robustly
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    BASE_DIR = Path(__file__).resolve().parent

# Configuration setup (look for config.ini in the project root or current dir)
config_file = None
possible_confs = [
    BASE_DIR / 'config.ini',
    BASE_DIR.parent / 'config.ini',
    Path.cwd() / 'config.ini'
]
for conf in possible_confs:
    if conf.exists():
        config_file = conf
        break

if not config_file:
    print("\033[91mError: config.ini not found!\033[0m")
    sys.exit(1)

config = configparser.ConfigParser()
config.read(config_file)

# Set API key from config
GITHUB_API_KEY = config.get('API_KEYS', 'GITHUB', fallback=None)
if not GITHUB_API_KEY:
    print("\033[91mError: GitHub API key not found in config.ini\033[0m")
    sys.exit(1)

# Path configuration (dorks directory detection)
DORKS_DIR = None
for dork_path in [
    BASE_DIR / 'dorks',
    BASE_DIR.parent / 'dorks',
    Path.cwd() / 'dorks'
]:
    if dork_path.exists():
        DORKS_DIR = dork_path
        break

if not DORKS_DIR:
    print("\033[91mError: dorks directory not found!\033[0m")
    sys.exit(1)

def create_directory_structure(org_name):
    """Create organized directory structure for outputs in results/{org_name}/tool"""
    base_path = BASE_DIR / "results" / org_name
    dirs = ['gitleaks', 'trufflehog', 'dorky', 'custom_dorks']

    for d in dirs:
        (base_path / d).mkdir(parents=True, exist_ok=True)
    return base_path

def get_org_repos(org, token):
    """Fetch all public repositories for an organization using the GitHub API."""
    headers = {"Authorization": f"token {token}"}
    repos = []
    page = 1
    while True:
        url = f"https://api.github.com/orgs/{org}/repos?per_page=100&page={page}"
        resp = requests.get(url, headers=headers)
        if not resp.ok:
            print(f"\033[91mGitHub API error: {resp.status_code} {resp.text}\033[0m")
            sys.stdout.flush()
            break
        data = resp.json()
        if not data:
            break
        repos.extend([r['clone_url'] for r in data])
        page += 1
    return repos

def run_gitleaks_on_repos(org_name, output_dir, github_token):
    """Clone and scan all repos in the org with gitleaks, live progress."""
    print("Fetching repo list from GitHub...")
    sys.stdout.flush()
    repos = get_org_repos(org_name, github_token)
    print(f"Repo list fetched. {len(repos)} repos.")
    sys.stdout.flush()
    if not repos:
        print(f"\033[93mNo repositories found for org '{org_name}', or permission denied.\033[0m")
        sys.stdout.flush()
        return
    print(f"\033[96m[+] Found {len(repos)} repositories in {org_name}.\033[0m")
    sys.stdout.flush()
    for idx, repo_url in enumerate(repos, 1):
        repo_name = repo_url.split('/')[-1].replace('.git', '')
        repo_dir = BASE_DIR / f"{org_name}_{repo_name}"
        try:
            print(f"\033[94m[GITLEAKS {idx}/{len(repos)}] Cloning {repo_url}...\033[0m")
            sys.stdout.flush()
            subprocess.run(['git', 'clone', '--depth=1', repo_url, str(repo_dir)], check=True)
            timestamp = int(time.time())
            output_file = output_dir / 'gitleaks' / f'results_{repo_name}_{timestamp}.json'
            print(f"\033[94m[GITLEAKS {idx}/{len(repos)}] Running gitleaks on {repo_name}...\033[0m")
            sys.stdout.flush()
            subprocess.run([
                'gitleaks', 'detect',
                '--source', str(repo_dir),
                '--report-format', 'json',
                '--report-path', str(output_file)
            ], check=True, timeout=600, env=os.environ.copy())
            print(f"\033[92m[GITLEAKS {idx}/{len(repos)}] Gitleaks scan completed for {repo_name}.\033[0m")
            sys.stdout.flush()
        except subprocess.CalledProcessError as e:
            print(f"\033[91m[GITLEAKS {idx}/{len(repos)}] Gitleaks error on {repo_name}: {e}\033[0m")
            sys.stdout.flush()
        except subprocess.TimeoutExpired:
            print(f"\033[91m[GITLEAKS {idx}/{len(repos)}] Gitleaks scan for {repo_name} timed out after 10 minutes.\033[0m")
            sys.stdout.flush()
        finally:
            if repo_dir.exists():
                print(f"\033[90m[GITLEAKS {idx}/{len(repos)}] Cleaning up {repo_name}...\033[0m")
                sys.stdout.flush()
                shutil.rmtree(repo_dir)

def run_trufflehog_on_repos(org_name, output_dir, github_token):
    """Run trufflehog (v2.x CLI) on all repos in the org, live progress, handle secrets found vs error."""
    repos = get_org_repos(org_name, github_token)
    if not repos:
        print(f"\033[93mNo repositories found for org '{org_name}', or permission denied.\033[0m")
        sys.stdout.flush()
        return
    print(f"\033[96m[+] Running trufflehog on {len(repos)} repositories in {org_name}.\033[0m")
    sys.stdout.flush()
    for idx, repo_url in enumerate(repos, 1):
        repo_name = repo_url.split('/')[-1].replace('.git', '')
        output_file = output_dir / 'trufflehog' / f'results_{repo_name}.json'
        try:
            env = os.environ.copy()
            env['GITHUB_TOKEN'] = github_token
            print(f"\033[93m[TRUFFLEHOG {idx}/{len(repos)}] Scanning {repo_name} using trufflehog...\033[0m")
            sys.stdout.flush()
            with open(output_file, 'w') as outf:
                result = subprocess.run(
                    ['trufflehog', '--json', repo_url],
                    stdout=outf,
                    timeout=600,
                    env=env
                )
            # Now interpret the result code:
            if result.returncode == 0:
                print(f"\033[92m[TRUFFLEHOG {idx}/{len(repos)}] Trufflehog scan completed for {repo_name} (no secrets found).\033[0m")
            elif result.returncode == 1:
                # Check if output file contains results
                try:
                    with open(output_file, 'r') as f:
                        lines = f.readlines()
                        has_leaks = False
                        for line in lines:
                            if line.strip() and line.strip() != "[]":
                                has_leaks = True
                                break
                        if has_leaks:
                            print(f"\033[93m[TRUFFLEHOG {idx}/{len(repos)}] Trufflehog found secrets in {repo_name}!\033[0m")
                        else:
                            print(f"\033[91m[TRUFFLEHOG {idx}/{len(repos)}] Trufflehog scan error on {repo_name} (empty output, possible repo error).\033[0m")
                except Exception as e:
                    print(f"\033[91m[TRUFFLEHOG {idx}/{len(repos)}] Trufflehog scan error on {repo_name}: {e}\033[0m")
            else:
                print(f"\033[91m[TRUFFLEHOG {idx}/{len(repos)}] Trufflehog scan error on {repo_name}: Return code {result.returncode}\033[0m")
            sys.stdout.flush()
        except subprocess.TimeoutExpired:
            print(f"\033[91m[TRUFFLEHOG {idx}/{len(repos)}] Trufflehog scan for {repo_name} timed out.\033[0m")
            sys.stdout.flush()
        except FileNotFoundError:
            print("\033[91mTrufflehog not installed. Please install trufflehog.\033[0m")
            sys.stdout.flush()

def run_dorky_on_wordlist(wordlist, dorky_args, env, output_file):
    """Run dorky Go CLI on a wordlist piped via stdin."""
    try:
        with open(wordlist, 'rb') as infile, open(output_file, 'w') as outf:
            subprocess.run(
                ['dorky'] + dorky_args,
                stdin=infile,
                stdout=outf,
                check=True,
                env=env
            )
        print(f"\033[92m[DORKY] Dorky scan completed and saved to {output_file}.\033[0m")
    except subprocess.CalledProcessError as e:
        print(f"\033[91m[DORKY] Dorky error: {e}\033[0m")
    except FileNotFoundError:
        print("\033[91mDorky not installed or not in PATH. Please install dorky Go CLI.\033[0m")

def build_wordlist(org_name):
    """
    Build a wordlist file from org name and custom dorks.
    Returns the path to the wordlist file.
    """
    wordlist_path = BASE_DIR / "results" / f"{org_name}_wordlist.txt"
    with open(wordlist_path, "w") as f:
        f.write(f"{org_name}\n")
        # Add more words as needed (e.g., from custom dorks)
        if DORKS_DIR:
            for dork_file in DORKS_DIR.glob('*.txt'):
                with open(dork_file, 'r') as dfile:
                    for line in dfile:
                        if line.strip():
                            f.write(line.strip() + "\n")
    return wordlist_path

def run_dorky(org_name, output_dir):
    """Run dorky Go CLI with standard flags using a wordlist."""
    timestamp = int(time.time())
    output_file = output_dir / 'dorky' / f'results_{timestamp}.txt'

    env = os.environ.copy()
    env['GITHUB_ACCESS_TOKEN'] = GITHUB_API_KEY

    # Build a wordlist with org name and custom dorks
    wordlist_path = build_wordlist(org_name)

    # Standard flags: search orgs, repos, users, clean words, GitHub only
    dorky_args = ['-o', '-r', '-u', '-c', '-gh']

    print(f"\033[94m[DORKY] Running dorky Go CLI on {org_name} using wordlist {wordlist_path}...\033[0m")
    run_dorky_on_wordlist(str(wordlist_path), dorky_args, env, str(output_file))

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
        print("\033[91mNo organizations specified!\033[0m")
        sys.stdout.flush()
        sys.exit(1)

    for org in orgs:
        print(f"\n\033[1mProcessing organization: {org}\033[0m")
        sys.stdout.flush()
        output_dir = create_directory_structure(org)

        # Run security tools with real-time feedback
        if shutil.which('gitleaks'):
            run_gitleaks_on_repos(org, output_dir, GITHUB_API_KEY)
        else:
            print("\033[91mGitleaks not installed. Please install gitleaks.\033[0m")
            sys.stdout.flush()

        if shutil.which('trufflehog'):
            run_trufflehog_on_repos(org, output_dir, GITHUB_API_KEY)
        else:
            print("\033[91mTrufflehog not installed. Please install trufflehog.\033[0m")
            sys.stdout.flush()

        if shutil.which('dorky'):
            run_dorky(org, output_dir)
        else:
            print("\033[91mDorky not installed or not in PATH. Please install dorky Go CLI.\033[0m")
            sys.stdout.flush()

        print(f"\n\033[92mCompleted scanning for {org}\033[0m")
        print(f"Results saved to: {output_dir}\n")
        sys.stdout.flush()

if __name__ == '__main__':
    main()
