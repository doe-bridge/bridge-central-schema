# Dataset draft: decisions to revisit

This register covers the Dataset, core, and agents work on the `dataset-class`
branch. It records provisional choices that need more evidence or coordination
with another schema branch. It does not replace the [Measurements open questions](measurements-hackathon-2026-09-30.md#open-questions-for-the-group).

Keep each ID stable. When a choice is settled, change its status to **Resolved**
and link the deciding PR or issue; do not remove the row. Open a
[repository issue](https://github.com/doe-bridge/bridge-central-schema/issues)
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
| DS-10 | `Dataset.spatial_coverage` | Store one or more Location URI/CURIE identifiers when the optional slot is present; no Location class is defined yet. | When Location is defined, revisit to make sure still works b/c this will require a separate table (I think) and the ability to make locaiton ids unique | Open | — |
| DS-11 | `Dataset.variable_measured`, `variable_measured_label` | Keep BRIDGE property IDs and unmatched free-text names in separate optional lists; entries are not paired by position. | This approach is similar to Measurements. Do people like it? | Open | — |
| DS-12 | `Dataset` multivalued slots | Several Dataset slots currently allow multiple values (`multivalued: true`). | Confirm which slots should allow multiple values and whether any need a different cardinality. | Open | — |
| DS-13 | Dataset contents and files | Dataset currently does not expose its constituent files. | Decide whether to add a separate class linking a dataset ID to a filename, description, and possibly a file ID. Some datasets provide file descriptions; others have informative filenames. | Open | — |
| DS-14 | Study and Project concepts | `Dataset.associated_studies` currently allows identifiers for studies or projects without asserting that the concepts are equivalent. | Confirm whether Study and Project are more or less equivalent or should be modeled as separate classes when the Study/Project work is integrated. | Open | — |
| DS-15 | ESS-DIVE `Dataset.provider` and BRIDGE Study/Project | No ESS-DIVE provider mapping is assigned to `Dataset.associated_studies`. ESS-DIVE uses one primary DOE project as the dataset publisher. | Check whether that provider role fits the BRIDGE Study/Project concept and `associated_studies`, or needs a separate relationship. | Open | — |
| DS-16 | ESS-DIVE provider IDs in `Dataset.associated_studies` | ESS-DIVE provider projects should be listed as associated studies, but their stable local IDs are bare identifiers rather than URI/CURIE values; the current ESS-DIVE example omits the provider. | Decide whether to namespace [ESS-DIVE project](https://data.ess-dive.lbl.gov/projects) IDs as URI/CURIE values or map them to BRIDGE Study IDs without implying that they are PIDs, then populate the example. | Open | — |
| DS-17 | `Dataset.funders`, `Dataset.award` | Record funding organizations and award or contract numbers on Dataset. | When Study merges, decide whether funding fields belong on Dataset, Study, or both, and how overlapping values relate. | Open | — |
| DS-18 | `Dataset.license` | Require a license URI without restricting it to an enum. | Decide whether dataset license options should be governed by an enum and which licenses it should allow. | Open | — |
