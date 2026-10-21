# Data Center Network Engineering Portfolio

Three small, dependency-free Python projects for practicing data center network operations. They use sample data only and do not connect to real devices.

## Projects

1. **Network configuration compliance checker** — checks a Cisco IOS-style configuration text file against a few sample operational standards.
2. **Pre/post change validator** — compares JSON snapshots of interface, BGP, and CRC/FEC status and reports changes that need attention.
3. **Leaf-spine topology validator** — checks a small topology design for redundant leaf-to-spine links, unique subnets, and reciprocal BGP peer definitions.

These are portfolio labs. They do not prove production experience. Understand and adapt each project before describing it on a resume.

## Requirements

- Python 3.9 or newer
- Windows PowerShell, Command Prompt, macOS Terminal, or Linux shell
- No third-party Python packages are required

Check Python is available:

```powershell
python --version
```

On Windows, if `python` is not recognized, try `py -3 --version` and replace `python` with `py -3` in the commands below.

## Run the examples

Open a terminal in this folder, then run:

```powershell
python config-compliance/audit_config.py --config config-compliance/sample_config.cfg
python change-validation/validate_change.py --before change-validation/samples/before.json --after change-validation/samples/after-healthy.json
python leaf-spine/validate_topology.py --topology leaf-spine/topology.json
```

The first and third examples should report `PASS`. The healthy change snapshot should report all checks passing. To see a detected issue, run:

```powershell
python change-validation/validate_change.py --before change-validation/samples/before.json --after change-validation/samples/after-issue.json
```

That final example intentionally returns exit code 1 because the sample contains a down interface, a non-established BGP neighbor, and increased error counters.

## Project folders

- `config-compliance/` — sample IOS configuration and compliance checker.
- `change-validation/` — example pre/post snapshots and validator.
- `leaf-spine/` — example topology JSON and design validator.

## Safety and scope

- All examples read local sample files and make no network connections.
- Do not commit company configurations, IP plans, credentials, customer names, or private operational details.
- The IOS sample is fictional and is not a production-ready security baseline.
- The topology checker validates design data; it does not emulate switches or prove packet forwarding.

## Resume wording after you run and understand the projects

Use project language and keep the scope clear. For example:

- “Built a Python tool to compare pre- and post-change interface, BGP, and CRC/FEC snapshots and flag failed checks.”
- “Created a leaf-spine topology validator to check redundant uplinks, subnet uniqueness, and reciprocal BGP peer definitions.”
- “Developed a Python checker for sample Cisco IOS configurations to identify missing NTP, syslog, and SSH settings.”

Only include results you personally reproduced and can explain in an interview.
