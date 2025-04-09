#!/usr/bin/env python3
"""
Script to check for outdated dependencies and generate a report.
"""

import json
import subprocess
import sys
from datetime import datetime


def get_outdated_packages():
    """Get a list of outdated packages using pip list --outdated."""
    try:
        result = subprocess.run(
            ["pip", "list", "--outdated", "--format=json"],
            capture_output=True,
            text=True,
            check=True,
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error checking dependencies: {e}")
        return []


def generate_report(packages):
    """Generate a markdown report of outdated packages."""
    report = f"# Dependency Update Report\n\nGenerated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    if not packages:
        report += "All dependencies are up to date! 🎉\n"
        return report

    report += "## Outdated Packages\n\n"
    report += "| Package | Current Version | Latest Version | Type |\n"
    report += "|---------|----------------|----------------|------|\n"

    for pkg in packages:
        report += f"| {pkg['name']} | {pkg['version']} | {pkg['latest_version']} | {pkg.get('type', 'unknown')} |\n"

    report += "\n## Recommendations\n\n"
    report += "To update a specific package:\n```bash\npip install --upgrade package_name\n```\n\n"
    report += "To update all packages:\n```bash\npip install --upgrade -r requirements.txt\n```\n"

    return report


def main():
    """Main function to check dependencies and generate report."""
    print("Checking for outdated dependencies...")
    packages = get_outdated_packages()
    report = generate_report(packages)

    # Write report to file
    with open("dependency_report.md", "w") as f:
        f.write(report)

    print(f"Report generated: dependency_report.md")
    if packages:
        print(f"Found {len(packages)} outdated package(s)")
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
