# Wide polymorphic tables (draft)

This note answers a question @turbomam raised at the Samples, Projects and Processes squad meeting on 2026-10-28: do we want a small number of wide tables, each holding several kinds of record and telling them apart with a `type` column, or a large number of narrow tables, one per kind? It is a proposal to argue with, not an agreed position. NMDC (the National Microbiome Data Collaborative) is the worked example because @turbomam was able to measure both its schema and its data. Each point is made in plain words first and then backed by a measurement, with the method and the date.

## The short version

A schema can declare many classes and still store them in few tables. NMDC declares a hierarchy of classes and stores it three different ways at once, so it shows what each way costs. The class hierarchy itself costs nothing. The wide tables cost width: a single NMDC table holding all three kinds of sample would need 560 columns, of which 5 are shared by all three, and the flattened biosample table in the lakehouse has 1,402 columns, of which 22 are filled on at least half of the rows. The rules that tell one subtype from another are few, and they are enforced when a record is written, not by the tables. So the proposal is to keep the class hierarchy, check each record against its own subclass when it is written, lay the records out as wide tables for analysis, and generate a per-type view of each wide table so nobody has to guess which columns apply. Keeping the subtypes few and material keeps the width down, which is where this note meets `what-is-a-sample.md`.

## Two decisions, not one

The first decision is how many classes the schema declares. nmdc-schema declares abstract parent classes (`Sample`, `MaterialProcessing`, `WorkflowExecution`), concrete subclasses under each, and per-subclass `slot_usage`, which is how LinkML tightens a slot for one class (making it required, narrowing its range, or adding a pattern). Each rule is stated once, on the subclass it applies to.

The second decision is how many tables the store has. NMDC lays the same classes out in three ways.

| Table layout | Where NMDC uses it | How a reader tells the kinds apart | Notes |
|---|---|---|---|
| One MongoDB collection per class family, subclasses mixed | `material_processing_set`, `workflow_execution_set`, `data_generation_set`, `configuration_set` | a required `type` slot | On write, JSON Schema checks each document against the list of subclass schemas (`anyOf`), and each branch pins `type` to one class. |
| One MongoDB collection per concrete class | `biosample_set`, `processed_sample_set`, `organism_sample_set` | the id prefix (`bsm`, `procsm`, `osm`) | The prefixes are written into the `has_input` and `has_output` patterns of the process classes. |
| One wide table per collection, holding every column any subclass has | nmdc-lakehouse flattened Parquet and Iceberg tables | a `type` column | A `QuantityValue` slot becomes several columns. |

The hierarchy itself costs nothing. The costs appear in the table layout, and they differ by store.

## What the width is today

Width here means the number of columns a table needs in order to hold every subclass. @turbomam measured it with LinkML SchemaView on nmdc-schema main at 76fa03024 on 2026-10-28, counting for each concrete subclass every slot it has, inherited ones included.

| Collection | Concrete subclasses | Slots in the union | Slots common to all | Slots held by exactly one subclass | Fewest slots on one subclass | Most slots on one subclass | Notes |
|---|---|---|---|---|---|---|---|
| `material_processing_set` | 13 | 55 | 15 | 35 | 15 | 30 | |
| `workflow_execution_set` | 11 | 77 | 22 | 22 | 22 | 50 | |
| `data_generation_set` | 2 | 28 | 20 | 8 | 24 | 24 | |
| the three sample collections, if merged | 3 | 560 | 5 | 535 | 14 | 548 | All 535 belong to `Biosample` alone. |

Most of those columns are empty most of the time. The row counts come from DuckDB over the flattened Parquet of @turbomam's local nmdc-lakehouse export of 2026-08-21, counting non-null values per column by `type`. The processing table has 86 columns and 35,234 rows; Extraction and FiltrationProcess, the widest types, each fill 23 of the columns in at least one row, and five subclasses had no rows at all. The biosample table has 1,402 columns, of which 300 are non-null in at least one of its 27,352 rows and 22 are non-null in at least half of them.

## The per-type rules are smaller than the worry

The fear is that each subtype carries its own rules and a shared table cannot enforce them. In NMDC the rules are few. Across the 13 `MaterialProcessing` subclasses there are 0 `rules` (LinkML's conditional constraints). The `slot_usage` differences come down to three kinds: every class has its own id pattern, `has_input` and `has_output` are required on 8 of the 13, and those two slots are narrowed to `OrganismSample` on Culturing (both) and Isolation (output only), with id patterns saying which sample classes are allowed. The JSON Schema `anyOf` branch for each type checks all three, so Mongo enforces the per-type rules when a document is written.

The cost falls on readers. In a wide table, "required for Extraction only" cannot become a NOT NULL constraint, and "OrganismSample for Culturing only" cannot become a foreign key, because both are conditions on `type`, and a Parquet file carries neither. A reader has to know which columns apply to which type, and the same `has_input` column can point at different kinds of sample in different rows.

## The precedent NMDC already ran

NMDC has run the wide-union experiment once already, on `Biosample`, which is 548 slots wide because NMDC flattened the MIxS vocabulary into one class. MIxS (Minimum Information about any (x) Sequence, the Genomic Standards Consortium's checklists) itself declares 331 combination classes (a checklist crossed with an environment) with a union of 834 slots, and the required slots per class run from 2 (HumanGut and others) to 60 (MisagAgriculture and MiuvigAgriculture); @turbomam measured that with SchemaView on a local MIxS clone at 6a2a6edd6. NMDC put all of that on one class with 7 required slots, 0 `rules`, and a free-text `env_package` that nothing checks. That bought one table and one id space, and the price was every per-extension required list. LinkML offers a middle path, conditional `rules` keyed on `env_package` or `type`, but which generators enforce them has not been checked.

## Costs and benefits of the wide table with a `type` column

The wide table has benefits that one table per class loses.

- A reference that may point at any subtype has one target. `has_input: Sample` resolves to one table; with three sample collections it resolves by a regular expression on the id prefix.
- Following a sample through extraction, library preparation and sequencing crosses one process table instead of picking a table at every step.
- Adding a subtype does not change the set of tables that clients have to know about.
- The `type` column makes a mixed table legible, and it is what lets `anyOf` validation pick one branch.

The costs are these.

- Width is the union, and the share of empty cells grows with the number of subtypes times the vocabulary of each. The sample family's shared core is 5 slots.
- Per-type required slots, ranges and patterns become conditions on `type` that columnar stores do not enforce.
- The same column can carry a narrower range, or a different meaning, in different rows.
- A slot added for one subtype changes everyone's table.
- A 1,402-column table is unusable by a person without a per-type view.

One more concern came up at the squad meeting on 2026-10-28: a long table needs an index on every column that people are likely to search, such as Pfam family names in a gene annotation table, and a wide union table makes that list of columns long. Indexes are a property of the table layout, not of the schema. They can be added or changed after the data are loaded without touching a class or a slot, so this note does not treat the concern as a blocker for the schema decision. It does belong on the list of things to generate per type, next to the per-type views and column lists proposed below. What the lakehouse does in place of indexes was not checked for this note.

## Proposal

Keep the class hierarchy, with per-subclass `slot_usage` as the single place where a rule is stated. Check each record on write against its own subclass, as Mongo plus JSON Schema already does for NMDC. Lay the records out as wide tables with a `type` column for the analytic store, and generate from the schema a per-type view and column list for each wide table, so a reader never has to guess which of 86 or 1,402 columns apply to a row. Keep the subtypes few and material.

That last point is where this note meets `what-is-a-sample.md`. The MIxS extensions overlap heavily, which is how 331 classes fit in 834 slots. Plant observation units, atmospheric stations and MAG rows overlap with MIxS hardly at all, though that has not been measured. If that holds, each added subtype adds nearly its whole vocabulary to the union while the shared core stays at an id, a type, a name, a source and a date. Keeping subjects, observations, stations and information artifacts out of `Sample` is therefore both the right definition and the cheap storage choice.

## What this means in practice

| Who | What the proposal asks of them | Notes |
|---|---|---|
| schema authors | State each per-subtype rule once, as `slot_usage` on that subclass. | NMDC needed 0 `rules` across 13 processing subclasses. |
| loaders and submitters | Check each record against its subclass before writing it. | This is where required slots, ranges and patterns are enforced. The tables will not do it. |
| lakehouse builders | Generate a per-type view and column list for each wide table from the schema, and index the columns people search. | Views and indexes are added after loading and need no schema change. |
| query writers | Query the per-type view and expect empty cells outside it. | 22 of the 1,402 biosample columns are filled on at least half of the rows. |

## Sources

- nmdc-schema main at 76fa03024, https://github.com/microbiomedata/nmdc-schema, measured with LinkML SchemaView on 2026-10-28.
- @turbomam's local MIxS clone at 6a2a6edd6 (2026-08-12, 8 commits after v7.0.1), https://github.com/GenomicsStandardsConsortium/mixs, measured with LinkML SchemaView on 2026-10-28.
- @turbomam's local nmdc-lakehouse export of 2026-08-21 (27,352 biosamples), measured with DuckDB on 2026-10-28. The flattening rules are at https://github.com/microbiomedata/nmdc-lakehouse/blob/main/docs/architecture.md and the generated flat schema is at https://github.com/microbiomedata/nmdc-lakehouse-schema.
