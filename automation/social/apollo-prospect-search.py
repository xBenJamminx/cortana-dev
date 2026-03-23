#!/usr/bin/env python3
"""
Apollo.io Prospect Search System for Parker & Taylor Outbound
==============================================================
Reusable CLI tool to search Apollo for prospects matching P&T ICPs.

Usage:
  python3 scripts/apollo-prospect-search.py --summary
  python3 scripts/apollo-prospect-search.py --icp 1 --limit 5
  python3 scripts/apollo-prospect-search.py --icp all --limit 10 --pull
  python3 scripts/apollo-prospect-search.py --create-labels

Note: Apollo free-tier API returns preview data (obfuscated last names,
no direct emails). Full data requires revealing contacts via the Apollo UI
or a paid API plan.
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import requests

# -- Constants -----------------------------------------------------------------

API_BASE = "https://api.apollo.io/api/v1"
PEOPLE_SEARCH_ENDPOINT = f"{API_BASE}/mixed_people/api_search"
LABELS_ENDPOINT = f"{API_BASE}/labels"
WORKSPACE = Path("/root/.openclaw/workspace")
OUTPUT_DIR = WORKSPACE / "output"
ENV_FILE = Path("/root/.openclaw/.env")

# -- ANSI Colors ---------------------------------------------------------------

class C:
    BOLD = "\033[1m"
    GREEN = "\033[92m"
    CYAN = "\033[96m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    MAGENTA = "\033[95m"
    DIM = "\033[2m"
    RESET = "\033[0m"

# -- ICP Configurations --------------------------------------------------------
#
# Each ICP defines search parameters sent directly to Apollo's
# /mixed_people/api_search endpoint. Industries are passed via
# q_organization_keyword_tags (the working param for free-tier API).

ICP_CONFIGS = {
    1: {
        "name": "Ops Overload",
        "label_name": "P&T ICP 1: Ops Hire Signal",
        "label_id": "69a0b3067bbc0800155fb484",
        "search_params": {
            "person_titles": [
                "Founder", "CEO", "COO", "Head of Operations",
                "VP Operations", "Director of Operations",
                "Operations Manager", "Managing Partner", "Owner"
            ],
            "person_seniorities": ["owner", "founder", "c_suite", "vp", "director"],
            "organization_num_employees_ranges": ["1,200"],
            "person_locations": ["United States"],
            "q_organization_keyword_tags": [
                "professional services", "marketing and advertising",
                "computer software", "e-commerce", "staffing and recruiting",
                "management consulting", "real estate"
            ],
        },
    },
    2: {
        "name": "Scaling Without Headcount",
        "label_name": "P&T ICP 2: Scaling Without Headcount",
        "label_id": "69a0b93dee44980019f7f780",
        "search_params": {
            "person_titles": [
                "Founder", "CEO", "COO", "CTO",
                "Director of Operations", "Chief of Staff"
            ],
            "person_seniorities": ["owner", "founder", "c_suite", "vp", "director"],
            "organization_num_employees_ranges": ["1,200"],
            "person_locations": ["United States"],
            "q_organization_keyword_tags": [
                "information technology and services", "financial services",
                "hospital & health care", "business supplies and equipment"
            ],
        },
    },
    3: {
        "name": "Tool Sprawl",
        "label_name": "P&T ICP 3: Tool Sprawl",
        "label_id": "69a0b93d326526000d968299",
        "search_params": {
            "person_titles": [
                "COO", "CTO", "VP Operations", "Head of Systems",
                "Operations Director", "Chief of Staff", "Founder", "CEO"
            ],
            "person_seniorities": ["owner", "founder", "c_suite", "vp", "director"],
            "organization_num_employees_ranges": ["1,200"],
            "person_locations": ["United States"],
            "q_organization_keyword_tags": [
                "logistics and supply chain", "staffing and recruiting",
                "management consulting", "marketing and advertising",
                "computer software"
            ],
        },
    },
}

# -- Helpers -------------------------------------------------------------------

def load_api_key() -> str:
    """Load APOLLO_API_KEY from /root/.openclaw/.env"""
    if not ENV_FILE.exists():
        print(f"{C.RED}ERROR: {ENV_FILE} not found{C.RESET}")
        sys.exit(1)

    with open(ENV_FILE) as f:
        for line in f:
            line = line.strip()
            if line.startswith("APOLLO_API_KEY="):
                key = line.split("=", 1)[1].strip().strip('"').strip("'")
                if key:
                    return key

    print(f"{C.RED}ERROR: APOLLO_API_KEY not found in {ENV_FILE}{C.RESET}")
    sys.exit(1)


def get_headers(api_key: str) -> dict:
    """Return headers for Apollo API requests."""
    return {
        "Content-Type": "application/json",
        "X-Api-Key": api_key,
    }


def search_prospects(api_key: str, icp_num: int, limit: int = 10, page: int = 1) -> dict:
    """
    Search Apollo for prospects matching an ICP config.
    Returns a normalized dict with keys: total_entries, people.
    """
    config = ICP_CONFIGS[icp_num]
    params = dict(config["search_params"])
    params["per_page"] = limit
    params["page"] = page

    try:
        resp = requests.post(
            PEOPLE_SEARCH_ENDPOINT,
            headers=get_headers(api_key),
            json=params,
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()

        # Apollo api_search returns total_entries at root, not under pagination
        return {
            "total_entries": data.get("total_entries", 0),
            "people": data.get("people", []),
        }
    except requests.exceptions.HTTPError:
        print(f"{C.RED}API Error ({resp.status_code}): {resp.text[:500]}{C.RESET}")
        return {"total_entries": 0, "people": []}
    except requests.exceptions.RequestException as e:
        print(f"{C.RED}Request failed: {e}{C.RESET}")
        return {"total_entries": 0, "people": []}


def format_person(person: dict) -> dict:
    """
    Extract clean fields from a person record.

    Apollo free-tier returns preview data:
      - first_name + last_name_obfuscated (no full last name)
      - has_email (bool), no actual email address
      - has_direct_phone instead of phone number
      - organization has has_* flags instead of actual values

    We extract what's available and mark restricted fields clearly.
    """
    org = person.get("organization", {}) or {}

    # Build name from available fields
    first = person.get("first_name", "")
    last_obf = person.get("last_name_obfuscated", "")
    # Some plans return full name
    full_name = person.get("name", "")
    name = full_name if full_name else f"{first} {last_obf}".strip()

    # Email: free tier gives has_email bool, paid gives actual email
    email = person.get("email")
    has_email = person.get("has_email", False)
    email_status = person.get("email_status", "unknown")

    # Employee count: free tier gives has_employee_count, paid gives actual
    emp_count = org.get("estimated_num_employees")
    if emp_count is None:
        emp_count = "yes" if org.get("has_employee_count") else "unknown"

    # Industry
    industry = org.get("industry")
    if industry is None:
        industry = "yes" if org.get("has_industry") else "unknown"

    return {
        "name": name or "N/A",
        "first_name": first,
        "title": person.get("title", "N/A"),
        "company": org.get("name", "N/A"),
        "has_email": has_email,
        "email": email,
        "email_status": email_status,
        "has_direct_phone": person.get("has_direct_phone", "No"),
        "linkedin_url": person.get("linkedin_url"),
        "city": person.get("city", ""),
        "state": person.get("state", ""),
        "has_city": person.get("has_city", False),
        "has_state": person.get("has_state", False),
        "employee_count": emp_count,
        "industry": industry,
        "apollo_id": person.get("id", ""),
        "last_refreshed": person.get("last_refreshed_at", ""),
    }


def print_person(p: dict, idx: int):
    """Pretty print a single prospect."""
    # Location from actual fields or flags
    loc_parts = []
    if p["city"]:
        loc_parts.append(p["city"])
    elif p.get("has_city"):
        loc_parts.append("[city available]")
    if p["state"]:
        loc_parts.append(p["state"])
    elif p.get("has_state"):
        loc_parts.append("[state available]")
    location = ", ".join(loc_parts)

    # Email display
    if p["email"]:
        email_display = p["email"]
    elif p["has_email"]:
        email_display = f"{C.YELLOW}available (reveal in Apollo){C.RESET}"
    else:
        email_display = f"{C.DIM}none{C.RESET}"

    # Phone
    phone_display = "yes" if p["has_direct_phone"] == "Yes" else "no"

    print(f"  {C.BOLD}{C.CYAN}{idx}. {p['name']}{C.RESET}")
    print(f"     Title:      {p['title']}")
    print(f"     Company:    {p['company']} ({p['employee_count']} employees)")
    print(f"     Industry:   {p['industry']}")
    print(f"     Email:      {email_display}")
    print(f"     Phone:      {phone_display}")
    if location:
        print(f"     Location:   {location}")
    if p.get("linkedin_url"):
        print(f"     LinkedIn:   {C.DIM}{p['linkedin_url']}{C.RESET}")
    print()


def create_label(api_key: str, name: str) -> dict:
    """Create a label in Apollo. Returns the label data."""
    payload = {
        "name": name,
        "modality": "contacts",
    }
    try:
        resp = requests.post(
            LABELS_ENDPOINT,
            headers=get_headers(api_key),
            json=payload,
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.HTTPError:
        print(f"{C.RED}Label creation failed ({resp.status_code}): {resp.text[:300]}{C.RESET}")
        return {}
    except requests.exceptions.RequestException as e:
        print(f"{C.RED}Request failed: {e}{C.RESET}")
        return {}


# -- CLI Commands --------------------------------------------------------------

def cmd_summary(api_key: str):
    """Show total prospect counts for each ICP (no full data pull)."""
    print(f"\n{C.BOLD}{C.MAGENTA}=== P&T Prospect Summary ==={C.RESET}\n")

    grand_total = 0
    for icp_num, config in ICP_CONFIGS.items():
        result = search_prospects(api_key, icp_num, limit=1)
        total = result["total_entries"]
        grand_total += total
        color = C.GREEN if total > 0 else C.YELLOW
        industries = config["search_params"].get("q_organization_keyword_tags", [])
        print(f"  {C.BOLD}ICP {icp_num}: {config['name']}{C.RESET}")
        print(f"    Total matches: {color}{total:,}{C.RESET}")
        print(f"    Industries: {', '.join(industries)}")
        print(f"    Label ID: {config.get('label_id', 'not created')}")
        print()

    print(f"  {C.BOLD}Grand total (all ICPs, may overlap): {C.GREEN}{grand_total:,}{C.RESET}")
    print(f"\n{C.DIM}Tip: Run with --icp N --limit 10 to see actual prospects{C.RESET}\n")


def cmd_search(api_key: str, icp_nums: list, limit: int, pull: bool):
    """Search and display prospects for specified ICPs."""
    all_results = {}

    for icp_num in icp_nums:
        config = ICP_CONFIGS[icp_num]
        print(f"\n{C.BOLD}{C.MAGENTA}=== ICP {icp_num}: {config['name']} ==={C.RESET}\n")

        result = search_prospects(api_key, icp_num, limit=limit)
        people = result["people"]
        total = result["total_entries"]

        print(f"  {C.GREEN}Showing {len(people)} of {total:,} total matches{C.RESET}")
        if total > 0:
            print(f"  {C.DIM}(Apollo free tier shows preview data. Reveal full details in the Apollo UI.){C.RESET}")
        print()

        formatted = []
        for i, person in enumerate(people, 1):
            p = format_person(person)
            print_person(p, i)
            formatted.append(p)

        all_results[f"icp_{icp_num}"] = {
            "name": config["name"],
            "label_id": config.get("label_id"),
            "total_matches": total,
            "returned": len(formatted),
            "prospects": formatted,
            "search_params": config["search_params"],
        }

    if pull:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        today = datetime.now().strftime("%Y-%m-%d")
        outfile = OUTPUT_DIR / f"apollo-prospects-{today}.json"

        with open(outfile, "w") as f:
            json.dump(all_results, f, indent=2, default=str)

        print(f"\n{C.GREEN}{C.BOLD}Saved to {outfile}{C.RESET}")

    return all_results


def cmd_create_labels(api_key: str):
    """Create the 3 ICP labels in Apollo (skips any that already have IDs)."""
    print(f"\n{C.BOLD}{C.MAGENTA}=== Creating Apollo Labels ==={C.RESET}\n")

    for icp_num, config in ICP_CONFIGS.items():
        label_name = config["label_name"]

        if config.get("label_id"):
            print(f"  {C.YELLOW}ICP {icp_num}: \"{label_name}\" already exists (ID: {config['label_id']}){C.RESET}")
            continue

        print(f"  Creating: \"{label_name}\"...", end=" ")
        result = create_label(api_key, label_name)

        if result:
            label_data = result.get("label", result)
            label_id = label_data.get("id", "unknown")
            print(f"{C.GREEN}Done! ID: {label_id}{C.RESET}")
        else:
            print(f"{C.RED}Failed{C.RESET}")

    print()


# -- Main ---------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Apollo.io Prospect Search for Parker & Taylor Outbound",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --summary                    Show prospect counts per ICP
  %(prog)s --icp 1 --limit 5           Search ICP 1, show 5 results
  %(prog)s --icp all --limit 10 --pull  Search all ICPs, save to JSON
  %(prog)s --create-labels              Create ICP labels in Apollo
        """,
    )
    parser.add_argument(
        "--icp",
        type=str,
        default=None,
        help="Which ICP to search: 1, 2, 3, or 'all' (default: all)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Number of results per ICP (default: 10)",
    )
    parser.add_argument(
        "--create-labels",
        action="store_true",
        help="Create ICP labels in Apollo",
    )
    parser.add_argument(
        "--pull",
        action="store_true",
        help="Save results to output/apollo-prospects-YYYY-MM-DD.json",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Show total counts per ICP (minimal API usage)",
    )

    args = parser.parse_args()

    # Load API key
    api_key = load_api_key()
    print(f"{C.DIM}Apollo API key loaded.{C.RESET}")

    # Route commands
    if args.create_labels:
        cmd_create_labels(api_key)

    if args.summary:
        cmd_summary(api_key)
        return

    if args.icp is not None:
        if args.icp.lower() == "all":
            icp_nums = [1, 2, 3]
        else:
            try:
                num = int(args.icp)
                if num not in ICP_CONFIGS:
                    print(f"{C.RED}Invalid ICP number: {num}. Use 1, 2, or 3.{C.RESET}")
                    sys.exit(1)
                icp_nums = [num]
            except ValueError:
                print(f"{C.RED}Invalid --icp value: {args.icp}. Use 1, 2, 3, or 'all'.{C.RESET}")
                sys.exit(1)

        cmd_search(api_key, icp_nums, args.limit, args.pull)
        return

    # Default: show help if no action specified
    if not args.create_labels:
        parser.print_help()


if __name__ == "__main__":
    main()
