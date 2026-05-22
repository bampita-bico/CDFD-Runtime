"""python -m domains list | demo <name> [--json] [--payload FILE.json]"""
import argparse
import json
import sys

from domains.demo_runner import run_domain_demo
from domains.registry import DomainRegistry


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="python -m domains")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list", help="Print sorted registered domain names")

    demo_p = sub.add_parser("demo", help="Run engine-backed demo for one domain")
    demo_p.add_argument("domain", help="Registry key, e.g. medicine, ecology")
    demo_p.add_argument("--json", action="store_true", help="Print JSON result")
    demo_p.add_argument("--payload", metavar="FILE.json", help="Optional JSON object for map_to_engine")
    demo_p.add_argument("--nx", type=int, default=16)
    demo_p.add_argument("--ny", type=int, default=16)
    demo_p.add_argument("--steps", type=int, default=24)

    args = p.parse_args(argv)

    if args.cmd == "list":
        for name in sorted(DomainRegistry.default().list_domains()):
            print(name)
        return 0

    payload = None
    if args.payload:
        with open(args.payload) as f:
            payload = json.load(f)
        if not isinstance(payload, dict):
            print("Payload JSON must be an object", file=sys.stderr)
            return 1

    out = run_domain_demo(args.domain, payload, nx=args.nx, ny=args.ny, steps=args.steps)
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        print(json.dumps(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
