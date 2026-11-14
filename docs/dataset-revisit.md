# Dataset draft: decisions to revisit

This register covers the Dataset, core, and agents work on the `dataset-class`
branch. It records provisional choices that need more evidence or coordination
with another schema branch. It does not replace the [Measurements open questions](measurements-hackathon-2026-09-30.md#open-questions-for-the-group).

Keep each ID stable. When a choice is settled, change its status to **Resolved**
and link the deciding PR or issue; do not remove the row. Open a
[repository issue](https://github.com/ber-data/bridge-central-schema/issues)
when an item is ready for independent work, and add its link here. Review this
list when integrating another schema branch or mapping a new source dataset.

| ID | Schema element | Current choice | Revisit when | Status | Issue or decision |
| --- | --- | --- | --- | --- | --- |
| DS-01 | `dataset.yaml` `essdive` prefix and mappings | Use the provisional ESS-DIVE elements URL for `close_mappings`. | The ESS-DIVE schema has a configured, stable term URL; check whether the mappings should use it. | Open | — |
| DS-02 | `Dataset.associated_studies` | Store study identifiers as `uriorcurie` values. | The Study/Project model merges; choose its class range and relationship semantics. | Open | — |
| DS-04 | `Agent`, `Person`, `Organization` | Define these once in `agents.yaml`; Dataset refers to them by identifier. | The credit/umbrella branch merges; reconcile. | Open | — |
| DS-05 | `Dataset.contact`, `creators`, `contributors` | Use non-inlined `Agent` references; contact email is optional. | Revisit with credit/umbrella approach. | Open | — |
| DS-06 | `Dataset.funders` | Keep funder identifiers as `uriorcurie` values. | Attribution is revisited; decide whether to range this slot to `Organization` or other approach. Not all funders have ORCIDs. | Open | — |
| DS-07 | `PartialDateTime` | Accept year, year-month, date, or offset date-time using a pattern that does not check calendar-valid days. | A consumer needs calendar-valid dates or a shared date policy is agreed. This issue is noted somewhere in the Measurements dev | Open | — |
| DS-08 | `NamedThing` and `PartialDateTime` | Temporarily put in core.yaml | Reconcile when PR#39 is merged | Open | — |
| DS-10 | `Dataset.spatial_coverage` | Store one or more Location URI/CURIE identifiers when the optional slot is present; no Location class is defined yet. | When Location is defined, revisit to make sure still works and review the `schema:spatialCoverage` | Open | — |
| DS-11 | `Dataset.variable_measured`, `variable_measured_label` | Keep BRIDGE property IDs and unmatched free-text names in separate optional lists; entries are not paired by position. | This approach is similar to Measurements. Do people like it? | Open | — |
