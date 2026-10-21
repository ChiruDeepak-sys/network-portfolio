"""Check a Cisco IOS-style sample configuration against basic lab standards."""

import argparse
import re
import sys
from pathlib import Path


REQUIRED_CHECKS = {
    "Hostname configured": re.compile(r"^hostname\s+\S+\s*$", re.MULTILINE | re.IGNORECASE),
    "NTP server configured": re.compile(r"^ntp server\s+\S+", re.MULTILINE | re.IGNORECASE),
    "Syslog destination configured": re.compile(r"^logging host\s+\S+", re.MULTILINE | re.IGNORECASE),
    "SSH version 2 enabled": re.compile(r"^ip ssh version 2\s*$", re.MULTILINE | re.IGNORECASE),
}


def audit_config(config_text):
    return [(label, bool(pattern.search(config_text))) for label, pattern in REQUIRED_CHECKS.items()]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path, help="Path to a local IOS-style configuration text file")
    args = parser.parse_args()

    try:
        config_text = args.config.read_text(encoding="utf-8")
    except OSError as exc:
        print("ERROR: Could not read configuration: {}".format(exc), file=sys.stderr)
        return 2

    results = audit_config(config_text)
    print("Configuration compliance report: {}".format(args.config.name))
    for label, passed in results:
        print("{} {}".format("PASS" if passed else "FAIL", label))

    passed_count = sum(passed for _, passed in results)
    print("Result: {}/{} checks passed".format(passed_count, len(results)))
    return 0 if passed_count == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
