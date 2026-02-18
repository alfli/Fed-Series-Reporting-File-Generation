#!/usr/bin/env python3
from __future__ import annotations

import argparse
import random
import string
from datetime import datetime, timedelta
from typing import Optional, List, Set, Dict

import xmlschema


# ============================================================
# Group Definitions (FRIENDLY itemGroup@ref values)
# ============================================================

# Friendly refs per your mapping
SCHEDULE2_REF = "Schedule2"
SCHEDULE3_REF = "Schedule3"
BUSINESS_REF  = "BusContact"
SERVICE_REF   = "ServiceProvider"
VALTECH_REF   = "ValTechnique"

# Key rs_id within each group (still the real rs_id)
SCHEDULE2_SEQ_RSID = "SHCDN186"
SCHEDULE3_SEQ_RSID = "SHCCN186"
BUSINESS_SEQ_RSID  = "SHCAR069"
SERVICE_SEQ_RSID   = "SHCAR070"
VALTECH_KEY_RSID   = "SHCAN448"

# Group contents (rs_id lists)
SCHEDULE2_RSIDS = [
    "SHCDN186",
    "SHCAN448", "SHCDN460", "SHCDN461", "SHCDN462", "SHCDN463", "SHCDN464",
    "SHCDN465", "SHCDN466", "SHCDN467", "SHCDN468", "SHCDN486",
    "SHCDN470", "SHCDN471", "SHCDN487", "SHCDN490", "SHCDN472",
    "SHCDN473", "SHCDN474", "SHCDN475", "SHCDN477", "SHCD9914",
]

SCHEDULE3_RSIDS = [
    "SHCCN186",
    "SHCCN478", "SHCCN456", "SHCCN457", "SHCCN458", "SHCCN459",
    "SHCCN479", "SHCCN480", "SHCCN481", "SHCCN482",
    "SHCCN483", "SHCCN484", "SHCCN485",
]

BUSINESS_RSIDS = [
    "SHCAR069",
    "SHCAC495", "SHCAC496", "SHCA8902", "SHCA4086",
]

SERVICE_RSIDS = [
    "SHCAR070",
    "SHCAN263",
]

VALTECH_RSIDS = [
    "SHCAN448",
    "SHCAN449",
]

SEQ_KEY_VALUE = "yes"


# ============================================================
# Value Generators (basic; extend as needed)
# ============================================================

US_STATES = ["NY", "CA", "TX", "IL", "WA"]
CURRENCIES = ["USD", "EUR", "JPY", "GBP", "CAD"]
COMPANIES = ["Big Bank", "Acme Financial", "Northstar Credit"]
NAMES = ["Alex Kim", "Jordan Lee", "Taylor Chen"]
TITLES = ["Manager", "Director", "VP"]
CITIES = ["New York", "Chicago", "San Francisco", "Seattle"]
STREETS = ["Main St", "Market St", "Broadway", "1st Ave", "2nd Ave"]

def digits(n: int) -> str:
    return "".join(random.choice(string.digits) for _ in range(n))

def rand_alnum(n: int) -> str:
    return "".join(random.choice(string.ascii_letters + string.digits) for _ in range(n))

def yyyymmdd() -> str:
    dt = datetime.utcnow() - timedelta(days=random.randint(0, 365))
    return dt.strftime("%Y%m%d")

def mmddyy() -> str:
    dt = datetime.utcnow() - timedelta(days=random.randint(0, 365 * 3))
    return dt.strftime("%m%d%y")

def phone10() -> str:
    return random.choice("123456789") + digits(9)

def zip5() -> str:
    return digits(5)

def whole_dollars(max_digits: int) -> str:
    length = random.randint(1, max_digits)
    first = random.choice("123456789")
    return first + digits(length - 1) if length > 1 else first

def make_value(rs_id: str, seq_value: Optional[int] = None, override: Optional[str] = None) -> str:
    if override is not None:
        return override

    # Sequence drivers (key items)
    if rs_id in ("SHCDN186", "SHCCN186", "SHCAR069", "SHCAR070"):
        return str(seq_value if seq_value is not None else 1)

    # Standalone schedule-1 items
    if rs_id == "SHCA9017":  # Organization Name
        return random.choice(COMPANIES)
    if rs_id == "SHCA9028":  # Street Address
        return f"{random.randint(1,99999)} {random.choice(STREETS)}"
    if rs_id == "SHCA9130":  # City
        return random.choice(CITIES)
    if rs_id == "SHCA9200":  # State
        return random.choice(US_STATES)
    if rs_id == "SHCA9220":  # Zip
        return zip5()
    if rs_id == "SHCAN261":  # Reporting Status 1-4
        return str(random.randint(1, 4))
    if rs_id == "SHCAN262":  # Reporter Type 1-9
        return str(random.randint(1, 9))

    # Service provider contact standalone items
    if rs_id == "SHCAN444":  # Name
        return random.choice(NAMES)
    if rs_id == "SHCAN445":  # Title
        return random.choice(TITLES)
    if rs_id == "SHCAN446":  # Telephone
        return phone10()
    if rs_id == "SHCAN447":  # Email
        return "contact@example.com"

    # Business contact group items
    if rs_id == "SHCAC495":
        return random.choice(NAMES)
    if rs_id == "SHCAC496":
        return random.choice(TITLES)
    if rs_id == "SHCA8902":
        return phone10()
    if rs_id == "SHCA4086":
        return "user@example.com"

    # Service provider group item
    if rs_id == "SHCAN263":
        return random.choice(COMPANIES)

    # Schedule 2 items
    if rs_id == "SHCAN448":  # reporting unit
        return "".join(random.choice(string.ascii_uppercase) for _ in range(3))
    if rs_id == "SHCDN470":
        return random.choice(CURRENCIES)
    if rs_id in ("SHCDN490", "SHCDN472"):
        return whole_dollars(12)
    if rs_id == "SHCDN473":
        return whole_dollars(11)
    if rs_id in ("SHCDN474", "SHCDN475"):
        return whole_dollars(13)
    if rs_id in ("SHCDN477", "SHCD9914"):
        return mmddyy()

    # Schedule 3 items
    if rs_id in ("SHCCN456", "SHCCN457", "SHCCN458", "SHCCN459"):
        return whole_dollars(13)
    if rs_id == "SHCCN483":
        return random.choice(US_STATES)

    # Val technique
    if rs_id == "SHCAN449":
        return "Valuation description"

    return rand_alnum(10)


# ============================================================
# XML Helpers (manual writing; old-lxml compatible)
# ============================================================

def esc(s: str) -> str:
    return (s.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;")
             .replace('"', "&quot;")
             .replace("'", "&apos;"))

def w(fh, s: str) -> None:
    fh.write(s.encode("utf-8"))

def start(fh, tag: str, **attrs) -> None:
    if attrs:
        a = " ".join(f'{k}="{esc(str(v))}"' for k, v in attrs.items())
        w(fh, f"<{tag} {a}>")
    else:
        w(fh, f"<{tag}>")

def end(fh, tag: str) -> None:
    w(fh, f"</{tag}>")

def text_tag(fh, tag: str, value: str, **attrs) -> None:
    start(fh, tag, **attrs)
    w(fh, esc(value))
    end(fh, tag)

def write_report_item(fh, rs_id: str, value: str, key_attr: Optional[str] = None) -> None:
    if key_attr:
        start(fh, "reportItem", key=key_attr)
    else:
        start(fh, "reportItem")
    text_tag(fh, "rs_id", rs_id, type="mdrm")
    text_tag(fh, "itemValue", value)
    end(fh, "reportItem")


# ============================================================
# Group Writer + Accumulation
# ============================================================

def write_group_instance(
    fh,
    *,
    group_ref: str,
    rs_ids: List[str],
    key_rsid: str,
    seq_value: Optional[int] = None,
    overrides: Optional[Dict[str, str]] = None,
    sums: Optional[Dict[str, int]] = None,
) -> None:
    overrides = overrides or {}
    sums = sums if sums is not None else {}

    start(fh, "itemGroup", ref=group_ref)

    for rid in rs_ids:
        val = make_value(rid, seq_value=seq_value, override=overrides.get(rid))

        if rid == key_rsid:
            write_report_item(fh, rid, val, key_attr=SEQ_KEY_VALUE)
        else:
            write_report_item(fh, rid, val)

        # accumulation rules
        if rid == "SHCDN490":
            try:
                sums["S2_SUM_SHCDN490"] = sums.get("S2_SUM_SHCDN490", 0) + int(val)
            except ValueError:
                pass

        if rid in ("SHCCN456", "SHCCN457", "SHCCN458", "SHCCN459"):
            try:
                sums[rid] = sums.get(rid, 0) + int(val)
            except ValueError:
                pass

    end(fh, "itemGroup")


# ============================================================
# Main Generator
# ============================================================

def generate(
    xsd_path: str,
    output_path: str,
    schedule2_groups: int,
    schedule3_groups: int,
    business_groups: int,
    service_groups: int,
    validate: bool,
) -> None:
    sums: Dict[str, int] = {}

    # For ValTechnique: unique SHCAN448 values used in Schedule2
    schedule2_units: List[str] = []
    schedule2_units_set: Set[str] = set()

    def new_unique_unit() -> str:
        while True:
            v = make_value("SHCAN448")
            if v not in schedule2_units_set:
                schedule2_units_set.add(v)
                schedule2_units.append(v)
                return v

    with open(output_path, "wb") as fh:
        w(fh, '<?xml version="1.0" encoding="UTF-8"?>\n')

        start(fh, "financialDataFile")

        # fileDescription
        start(fh, "fileDescription")
        text_tag(fh, "createDate", datetime.utcnow().strftime("%Y%m%d"))
        text_tag(fh, "createTime", datetime.utcnow().strftime("%H%M%S"))
        text_tag(fh, "dataTypeIndicator", "Production")
        text_tag(fh, "requestType", "Scheduler")
        text_tag(fh, "receivingSite", "New York")
        text_tag(fh, "seriesName", "SHCA")
        text_tag(fh, "reportingForm", "SHCA")
        end(fh, "fileDescription")

        # asofDate (ONLY ONE)
        start(fh, "asofDate", date=yyyymmdd())
        start(fh, "financialData")

        # ONE reportingEntity
        start(fh, "reportingEntity")
        text_tag(fh, "reportingEntityIdentifier", str(random.randint(1, 9_999_999_999)))
        text_tag(fh, "transferType", "Initial")
        text_tag(fh, "sendingSiteReportKey", "STAR Internal Key")
        text_tag(fh, "processingDistrict", "02")
        text_tag(fh, "confidentiality", "None", status="1")
        text_tag(fh, "estimation", "None")

        # -----------------------------------------------------
        # Standalone Schedule 1 items (NOT in any itemGroup)
        # Must appear BEFORE itemGroups and BEFORE summaries
        # -----------------------------------------------------
        standalone_items = [
            "SHCA9017", "SHCA9028", "SHCA9130", "SHCA9200", "SHCA9220",
            "SHCAN261", "SHCAN262",
            "SHCAN444", "SHCAN445", "SHCAN446", "SHCAN447",
        ]
        for rid in standalone_items:
            write_report_item(fh, rid, make_value(rid))

        # ----------------- itemGroups -----------------

        # Business Contact groups
        for seq in range(1, business_groups + 1):
            write_group_instance(
                fh,
                group_ref=BUSINESS_REF,
                rs_ids=BUSINESS_RSIDS,
                key_rsid=BUSINESS_SEQ_RSID,
                seq_value=seq,
                sums=sums,
            )

        # Service Provider groups
        for seq in range(1, service_groups + 1):
            write_group_instance(
                fh,
                group_ref=SERVICE_REF,
                rs_ids=SERVICE_RSIDS,
                key_rsid=SERVICE_SEQ_RSID,
                seq_value=seq,
                sums=sums,
            )

        # Schedule 2 groups (also collect unique SHCAN448)
        for seq in range(1, schedule2_groups + 1):
            unit = new_unique_unit()
            write_group_instance(
                fh,
                group_ref=SCHEDULE2_REF,
                rs_ids=SCHEDULE2_RSIDS,
                key_rsid=SCHEDULE2_SEQ_RSID,
                seq_value=seq,
                overrides={"SHCAN448": unit},
                sums=sums,
            )

        # ValTechnique groups (one per unique Schedule2 SHCAN448)
        for unit in schedule2_units:
            write_group_instance(
                fh,
                group_ref=VALTECH_REF,
                rs_ids=VALTECH_RSIDS,
                key_rsid=VALTECH_KEY_RSID,
                overrides={"SHCAN448": unit},
                sums=sums,
            )

        # Schedule 3 groups
        for seq in range(1, schedule3_groups + 1):
            write_group_instance(
                fh,
                group_ref=SCHEDULE3_REF,
                rs_ids=SCHEDULE3_RSIDS,
                key_rsid=SCHEDULE3_SEQ_RSID,
                seq_value=seq,
                sums=sums,
            )

        # ----------------- Summary (standalone reportItems) -----------------

        # Summary of Schedule 2
        write_report_item(fh, "SHCAN450", str(schedule2_groups))
        write_report_item(fh, "SHCAN451", str(sums.get("S2_SUM_SHCDN490", 0)))
        write_report_item(fh, "SHCAN452", "0")
        write_report_item(fh, "SHCAN453", "0")
        write_report_item(fh, "SHCAN454", "0")

        # Summary of Schedule 3
        write_report_item(fh, "SHCAN455", str(schedule3_groups))
        write_report_item(fh, "SHCAN456", str(sums.get("SHCCN456", 0)))
        write_report_item(fh, "SHCAN457", str(sums.get("SHCCN457", 0)))
        write_report_item(fh, "SHCAN458", str(sums.get("SHCCN458", 0)))
        write_report_item(fh, "SHCAN459", str(sums.get("SHCCN459", 0)))

        end(fh, "reportingEntity")
        end(fh, "financialData")
        end(fh, "asofDate")
        end(fh, "financialDataFile")

    if validate:
        schema = xmlschema.XMLSchema(xsd_path)
        schema.validate(output_path)


def main() -> None:
    ap = argparse.ArgumentParser(description="SHCA XML generator (single reportingEntity).")
    ap.add_argument("--xsd", required=True, help="Path to shca.xsd")
    ap.add_argument("--out", default="shca_output.xml", help="Output XML")
    ap.add_argument("--schedule2", type=int, default=1, help="Number of Schedule2 itemGroups")
    ap.add_argument("--schedule3", type=int, default=1, help="Number of Schedule3 itemGroups")
    ap.add_argument("--business", type=int, default=1, help="Number of BusContact itemGroups")
    ap.add_argument("--service", type=int, default=1, help="Number of ServiceProvider itemGroups")
    ap.add_argument("--no-validate", action="store_true", help="Skip XSD validation")
    ap.add_argument("--seed", type=int, default=None, help="Random seed")
    args = ap.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    generate(
        xsd_path=args.xsd,
        output_path=args.out,
        schedule2_groups=args.schedule2,
        schedule3_groups=args.schedule3,
        business_groups=args.business,
        service_groups=args.service,
        validate=not args.no_validate,
    )

    print("Generated:", args.out)


if __name__ == "__main__":
    main()
