"""Compare local JSON health snapshots before and after a lab change."""

import argparse
import json
import sys
from pathlib import Path


def load_snapshot(path):
    with path.open("r", encoding="utf-8") as stream:
        data = json.load(stream)
    for key in ("interfaces", "bgp_neighbors", "counters"):
        if key not in data or not isinstance(data[key], dict):
            raise ValueError("{} must contain an object named '{}'".format(path, key))
    return data


def compare(before, after):
    checks = []

    for name, state in after["interfaces"].items():
        checks.append(("Interface {} is up".format(name), str(state).lower() == "up"))

    for neighbor, state in after["bgp_neighbors"].items():
        checks.append(("BGP neighbor {} is Established".format(neighbor), str(state).lower() == "established"))

    for interface, new_counts in after["counters"].items():
        old_counts = before.get("counters", {}).get(interface, {})
        for counter in ("crc", "fec"):
            if counter not in new_counts:
                continue
            old_value = int(old_counts.get(counter, 0))
            new_value = int(new_counts[counter])
            checks.append(("{} {} counter did not increase ({} -> {})".format(interface, counter.upper(), old_value, new_value), new_value <= old_value))

    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--before", required=True, type=Path, help="JSON snapshot captured before the change")
    parser.add_argument("--after", required=True, type=Path, help="JSON snapshot captured after the change")
    args = parser.parse_args()

    try:
        before = load_snapshot(args.before)
        after = load_snapshot(args.after)
        checks = compare(before, after)
    except (OSError, json.JSONDecodeError, ValueError, TypeError) as exc:
        print("ERROR: Could not validate snapshots: {}".format(exc), file=sys.stderr)
        return 2

    if not checks:
        print("ERROR: No checks were available in the after snapshot.", file=sys.stderr)
        return 2

    print("Post-change validation report")
    for label, passed in checks:
        print("{} {}".format("PASS" if passed else "REVIEW", label))

    passed_count = sum(passed for _, passed in checks)
    print("Result: {}/{} checks passed".format(passed_count, len(checks)))
    return 0 if passed_count == len(checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
