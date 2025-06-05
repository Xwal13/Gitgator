
# GitGator

**GitGator** is a command-line tool for automating security enumeration and secrets scanning across GitHub organizations. It leverages open-source tools like Gitleaks, Trufflehog, and Dorky to quickly find secrets, sensitive files, and interesting patterns in repositories belonging to one or more target organizations.

---

## Features

- **Enumerate repositories** for one or multiple GitHub organizations.
- **Scan for secrets** using both [Gitleaks](https://github.com/gitleaks/gitleaks) and [Trufflehog](https://github.com/trufflesecurity/trufflehog).
- **Perform keyword-based OSINT searches** with [Dorky](https://github.com/codingo/dorky) (Go-based, not the Python package!).
- Organizes all findings into a structured `results/` folder.
- Supports custom dork wordlists.
- Real-time progress feedback.

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOURUSERNAME/GitGator.git
cd GitGator
```

### 2. Install Python dependencies

Make sure you have Python 3 and pip installed. Then run:

```bash
pip3 install -r requirements.txt
```

### 3. Install Tools

A helper script is provided for Ubuntu/Debian systems to install all required tools:

```bash
chmod +x install_tools.sh
./install_tools.sh
```

This will:
- Install Python 3, pip, Go (if not already installed)
- Install Python dependencies from `requirements.txt`
- Install [Gitleaks](https://github.com/gitleaks/gitleaks)
- Install [Trufflehog](https://github.com/trufflesecurity/trufflehog) via pip
- Clone and build [Dorky](https://github.com/codingo/dorky) from source (requires Go)

#### Manual installation (if you prefer)

- **Gitleaks:**  
  See [gitleaks releases](https://github.com/gitleaks/gitleaks/releases), download and move the binary to `/usr/local/bin/`.

- **Trufflehog:**  
  ```bash
  pip3 install trufflehog
  ```

- **Dorky (Go CLI):**  
  ```bash
  git clone https://github.com/codingo/dorky.git
  cd dorky
  go get
  go build -o dorky
  sudo mv dorky /usr/local/bin/
  ```

- Make sure `/usr/local/bin` is in your `$PATH`.

---

## Configuration

Create a `config.ini` file in the root directory:

```ini
[API_KEYS]
GITHUB = your_github_api_token
```

- The GitHub token must have permissions to read public (and private, if desired) repos in the target orgs.

---

## Usage

### Basic: Scan a single organization

```bash
python3 main.py -Org <organization_name>
```

### Multiple organizations

```bash
python3 main.py -mOrg org1 org2 org3
```

### Custom Dorks

- Place `.txt` files with custom dork keywords inside a `dorks/` folder in the project root.
- These will be included in the Dorky scan wordlist.

---

## Output

- All results are saved under the `results/` directory:
  ```
  results/
    orgname/
      gitleaks/
      trufflehog/
      dorky/
      custom_dorks/
  ```
- Each tool's scan results are timestamped and organized by repository.

---

## Example

```bash
python3 main.py -Org mycompany
```

You will see real-time progress and a summary of output locations.

---

## Troubleshooting

- **No `dorky` command found:**  
  Ensure you built the Go-based Dorky CLI and that `/usr/local/bin` is in your `$PATH`.
- **Missing dependencies:**  
  Rerun `./install_tools.sh` or manually install any missing tools.
- **Permission errors:**  
  Some installations may require `sudo` (especially when moving binaries).
- **GitHub API rate limits:**  
  Use a personal access token with sufficient permissions.

---

## License

MIT License (see LICENSE file).

---

## Credits

- [Gitleaks](https://github.com/gitleaks/gitleaks)
- [Trufflehog](https://github.com/trufflesecurity/trufflehog)
- [Dorky](https://github.com/codingo/dorky)
