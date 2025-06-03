#!/bin/bash

set -e

echo "Installing dependencies..."

# Install Go if not present
if ! command -v go >/dev/null 2>&1; then
    echo "Go not found. Installing golang..."
    if command -v apt-get >/dev/null 2>&1; then
        sudo apt-get update
        sudo apt-get install -y golang
    else
        echo "Please install Go manually from https://golang.org/dl/"
        exit 1
    fi
fi

# Install Python and pip if not present
if ! command -v python3 >/dev/null 2>&1; then
    echo "Python3 not found. Installing..."
    sudo apt-get install -y python3
fi

if ! command -v pip3 >/dev/null 2>&1; then
    echo "pip3 not found. Installing..."
    sudo apt-get install -y python3-pip
fi

# Install required Python packages
if [ -f requirements.txt ]; then
    echo "Installing Python packages from requirements.txt..."
    pip3 install -r requirements.txt
fi

# Install gitleaks if not present
if ! command -v gitleaks >/dev/null 2>&1; then
    echo "Installing gitleaks..."
    curl -s https://api.github.com/repos/gitleaks/gitleaks/releases/latest |
        grep "browser_download_url.*linux.*amd64\.tar\.gz" |
        cut -d : -f 2,3 |
        tr -d \" |
        wget -qi -
    tar -xvf gitleaks_*.tar.gz
    sudo mv gitleaks /usr/local/bin/
    rm gitleaks_*.tar.gz
fi

# Install trufflehog if not present
if ! command -v trufflehog >/dev/null 2>&1; then
    echo "Installing trufflehog via pip..."
    pip3 install trufflehog
fi

# Install Dorky (Go binary build)
if ! command -v dorky >/dev/null 2>&1; then
    echo "Installing dorky from source..."
    if [ ! -d "dorky" ]; then
        git clone https://github.com/codingo/dorky.git
    fi
    cd dorky
    go get
    go build -o dorky
    sudo mv dorky /usr/local/bin/
    cd ..
fi

echo "All tools installed!"
