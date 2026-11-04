"""Every bridge_property: ID used in examples or mappings must be defined in the term list."""

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TERMS = ROOT / "src" / "ber_central_schema" / "terms" / "bridge_property.tsv"
MAPPINGS = ROOT / "src" / "ber_central_schema" / "mappings" / "observed_property.sssom.tsv"
DATA_DIR = Path(__file__).parent / "data"


def defined_ids():
    with TERMS.open() as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    assert all(r["label"] and r["definition"] for r in rows), "every term needs a label and a definition"
    return {r["id"] for r in rows}


def test_example_ids_are_defined():
    used = set()
    for path in DATA_DIR.rglob("*.yaml"):
        used.update(re.findall(r"observed_property:\s*(bridge_property:\S+)", path.read_text()))
    assert used, "no observed_property values found, so this check could not fail"
    assert used - defined_ids() == set()


def test_mapping_subjects_are_defined():
    with MAPPINGS.open() as f:
        lines = [line for line in f if not line.startswith("#")]
    subjects = {row["subject_id"] for row in csv.DictReader(lines, delimiter="\t")}
    assert subjects - defined_ids() == set()
