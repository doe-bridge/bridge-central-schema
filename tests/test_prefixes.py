"""Check the prefix rules in docs/identifiers.md."""

import re
from pathlib import Path

import pytest
import yaml
from linkml_runtime.utils.schemaview import SchemaView

SCHEMA = (
    Path(__file__).parent.parent / "src" / "ber_central_schema" / "schema" / "ber_central_schema.yaml"
)
# Only valid examples: invalid ones may break other rules on purpose.
DATA_DIR = Path(__file__).parent / "data" / "valid"
ELEMENT_PREFIX = "bridge_central_schema"
# A full URI is not a CURIE. Any value with "://" after its scheme is one, and
# so is a URN. Schemes are case-insensitive (RFC 3986 section 3.1).
URN_SCHEME = "urn"
# A prefix is an NCName, so it may start with an underscore and contain hyphens.
CURIE = re.compile(r"^([A-Za-z_][A-Za-z0-9_.-]*):(\S+)$")


def _modules():
    """Each schema module in the import closure, except LinkML's own."""
    sv = SchemaView(str(SCHEMA))
    sv.imports_closure()
    return {
        name: schema
        for name, schema in sv.schema_map.items()
        if not name.startswith("linkml:")
    }


def _declared():
    """Every prefix declared in any module, mapped to the set of its expansions."""
    declared = {}
    for schema in _modules().values():
        for prefix in schema.prefixes.values():
            declared.setdefault(prefix.prefix_prefix, set()).add(prefix.prefix_reference)
    return declared


def _curie_slots():
    """Names of slots whose range is uriorcurie or curie, in any class.

    Only these are checked: other string slots may hold source text kept
    verbatim, such as a GenBank db_xref value.
    """
    sv = SchemaView(str(SCHEMA))
    names = set()
    for class_name in sv.all_classes():
        for slot in sv.class_induced_slots(class_name):
            if slot.range in {"uriorcurie", "curie"}:
                names.add(slot.name)
    return names


def _curie_values(node, slots):
    """Strings held in the given slots, anywhere in the document."""
    if isinstance(node, dict):
        for key, value in node.items():
            if key in slots:
                for item in value if isinstance(value, list) else [value]:
                    if isinstance(item, str):
                        yield item
            yield from _curie_values(value, slots)
    elif isinstance(node, list):
        for value in node:
            yield from _curie_values(value, slots)


def test_no_prefix_has_two_expansions():
    """A prefix means the same namespace in every module."""
    conflicts = {p: e for p, e in _declared().items() if len(e) > 1}
    assert not conflicts


def test_data_prefixes_are_declared():
    """Every CURIE in a uriorcurie or curie slot uses a prefix some module declares."""
    declared = _declared()
    slots = _curie_slots()
    undeclared = set()
    for path in DATA_DIR.rglob("*.yaml"):
        for value in _curie_values(yaml.safe_load(path.read_text()), slots):
            match = CURIE.match(value)
            if not match or match.group(2).startswith("//"):
                continue
            prefix = match.group(1)
            if prefix.lower() != URN_SCHEME and prefix not in declared:
                undeclared.add((path.name, match.group(1)))
    assert not undeclared


@pytest.mark.xfail(
    strict=True,
    reason="measurements.yaml on main uses default_prefix bridge; "
    "https://github.com/doe-bridge/bridge-central-schema/pull/9 moves it to bridge_central_schema",
)
def test_every_module_uses_the_element_prefix():
    """Classes, slots and enums BRIDGE defines all sit in one namespace."""
    others = {
        name: schema.default_prefix
        for name, schema in _modules().items()
        if schema.default_prefix != ELEMENT_PREFIX
    }
    assert not others


def _elements_without_uri():
    """Classes and slots, in any BRIDGE module, that leave their URI to the default prefix."""
    missing = set()
    for name, schema in _modules().items():
        for cls in schema.classes.values():
            if not cls.class_uri:
                missing.add((name, "class", cls.name))
            for att in (cls.attributes or {}).values():
                if not att.slot_uri:
                    missing.add((name, "attribute", f"{cls.name}.{att.name}"))
        for slot in schema.slots.values():
            if not slot.slot_uri:
                missing.add((name, "slot", slot.name))
    return missing


@pytest.mark.xfail(
    strict=True,
    reason="no module asserts every URI yet; "
    "https://github.com/doe-bridge/bridge-central-schema/issues/35",
)
def test_every_element_asserts_its_uri():
    """Each class and slot states its URI instead of inheriting it from default_prefix."""
    assert not _elements_without_uri()


@pytest.mark.xfail(
    strict=True,
    reason="no class has a type slot yet; "
    "https://github.com/doe-bridge/bridge-central-schema/issues/35",
)
def test_every_class_has_a_type_slot():
    """Each class has a slot with designates_type, so a row can say which class it is."""
    sv = SchemaView(str(SCHEMA))
    untyped = [
        c for c in sv.all_classes()
        if not any(s.designates_type for s in sv.class_induced_slots(c))
    ]
    assert not untyped
