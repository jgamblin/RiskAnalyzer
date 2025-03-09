# RiskAnalyzer
Risk Analyzer Game (game.cve.icu)

The Risk Analyzer Game is an educational tool designed to help users learn about Common Vulnerabilities and Exposures (CVEs). Players are presented with CVEs and must guess either the CVSS 3 Base Score or the CWE associated with each CVE. 

## GitHub Actions

This repository includes a GitHub Action that runs the `download_cves.py` script every night at 5 minutes after midnight and on every push to the `main` branch. This script downloads the latest CVEs from the specified source.

The workflow file is located at `.github/workflows/download_cves.yml`.

## What `download_cves.py` Does

The `download_cves.py` script is responsible for downloading the latest Common Vulnerabilities and Exposures (CVEs) from a specified source. It fetches the CVE data, processes it, and stores it in a format that can be used by the application. This ensures that the application always has the most up-to-date information about known vulnerabilities.

Specifically, the script picks 500 random CVEs that have both a CWE and a CVSS 3 Base Score, and that were published after January 1, 2022. These CVEs are then used in the game.
