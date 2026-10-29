# Wide polymorphic tables (draft)

This note answers a question I raised at the Samples, Projects and Processes squad meeting on 2026-10-28: do we want a small number of wide tables with a `type` column, or a large number of narrow tables? I use NMDC as the worked example because I was able to measure it. Nothing here is agreed.

## Two decisions, not one

NMDC's design is two decisions that get discussed as one. The first is how many classes the schema declares. nmdc-schema declares abstract parents (`Sample`, `MaterialProcessing`, `WorkflowExecution`), concrete subclasses, and per-subclass `slot_usage`, so each rule is stated once. The second is how many tables the store has. NMDC uses two storage projections at once in Mongo, and nmdc-lakehouse adds a third.

| Projection | Where NMDC uses it | Discriminator | Notes |
|---|---|---|---|
| One collection per family, subclasses mixed | `material_processing_set`, `workflow_execution_set`, `data_generation_set`, `configuration_set` | a required `type` slot | JSON Schema validates each document as `anyOf` the subclass schemas, and each branch pins `type` to one class. |
| One collection per concrete class | `biosample_set`, `processed_sample_set`, `organism_sample_set` | the id prefix (`bsm`, `procsm`, `osm`) | The prefixes are written into the `has_input` and `has_output` patterns of the process classes. |
| One wide table per collection, holding the union of all subclass columns | nmdc-lakehouse flattened Parquet and Iceberg | a `type` column | `QuantityValue` slots become several columns each. |

The hierarchy itself costs nothing. The costs appear in the projection, and they differ by target.

## What the width is today

I measured these widths with LinkML SchemaView on nmdc-schema main at 76fa03024 on 2026-10-28, comparing the induced slots of the concrete subclasses.

| Collection | Concrete subclasses | Slots in the union | Slots common to all | Slots held by exactly one subclass | Fewest slots on one subclass | Most slots on one subclass | Notes |
|---|---|---|---|---|---|---|---|
| `material_processing_set` | 13 | 55 | 15 | 35 | 15 | 30 | |
| `workflow_execution_set` | 11 | 77 | 22 | 22 | 22 | 50 | |
| `data_generation_set` | 2 | 28 | 20 | 8 | 24 | 24 | |
| the three sample collections, if merged | 3 | 560 | 5 | 535 | 14 | 548 | All 535 belong to `Biosample` alone. |

I ran DuckDB over the flattened Parquet of the local nmdc-lakehouse export of 2026-08-21, counting non-null values per column by `type`. The processing table has 86 columns and 35,234 rows; Extraction and FiltrationProcess, the widest types, each fill 23 of the columns in at least one row, and five subclasses had no rows at all. The biosample table has 1,402 columns, of which 300 are non-null in at least one of its 27,352 rows and 22 are non-null in at least half of them.

## The per-type constraints are smaller than the worry

Across the 13 `MaterialProcessing` subclasses there are 0 `rules`. The `slot_usage` differences come down to three kinds: every class has its own id pattern, `has_input` and `has_output` are required on 8 of the 13, and those two slots are narrowed to `OrganismSample` on Culturing (both) and Isolation (output only), with id patterns saying which sample classes are allowed. The JSON Schema `anyOf` branch for each type handles all three, so Mongo enforces the per-type constraints at write time.

The cost is on the read side. In a wide table, "required for Extraction only" cannot become NOT NULL, and "OrganismSample for Culturing only" cannot become a foreign key. Both turn into conditions on `type` that Parquet cannot carry. A reader has to know which columns apply to which type, and `has_input` allows different targets in different rows of the same table.

## The precedent NMDC already ran

`Biosample` is 548 slots wide because NMDC flattened the MIxS vocabulary into one class. MIxS itself declares 331 combination classes (a checklist crossed with an environment) with a union of 834 slots, and the required slots per class run from 2 (HumanGut and others) to 60 (MisagAgriculture and MiuvigAgriculture); I measured that with SchemaView on the MIxS clone at 6a2a6edd6. NMDC put all of that on one class with 7 required slots, 0 `rules`, and a free-text `env_package` that nothing checks. That bought one table and one id space, and it paid with every per-extension required list. LinkML offers a middle path, conditional `rules` keyed on `env_package` or `type`, but I have not checked which generators enforce them.

## Costs and benefits of the type-discriminated wide table

The wide table with a `type` column has benefits that one table per class loses.

- Polymorphic references have one target. `has_input: Sample` resolves to one table; with three sample collections it resolves by a regex on the id prefix.
- Walking provenance from Biosample to NucleotideSequencing crosses one process table instead of picking a table at every hop.
- Adding a subtype does not change the set of tables that clients have to know about.
- The `type` column makes a mixed table legible, and it is what makes `anyOf` validation deterministic.

The costs are these.

- Width is the union, and sparsity grows with the number of subtypes times the vocabulary per subtype. The sample family's shared core is 5 slots.
- Per-type required slots, ranges and patterns become conditions on `type` that columnar stores do not enforce.
- The same column can carry a narrower range, or a different meaning, in different rows.
- A slot added for one subtype changes everyone's table.
- A 1,402-column table is unusable by a person without a per-type view.

## What I propose

Keep the class hierarchy, with per-subclass `slot_usage` as the single place where a rule is stated. Validate each document on write against its subclass schema, as Mongo plus JSON Schema already does for NMDC. Project to type-discriminated wide tables for the analytic store, and generate a per-type view and column list from the schema so a reader never has to guess which of 86 or 1,402 columns apply to a row. Keep the subtypes few and material.

That last point is where this note meets `what-is-a-sample.md`. The MIxS extensions overlap heavily, which is how 331 classes fit in 834 slots. Plant observation units, atmospheric stations and MAG rows overlap with MIxS hardly at all, though I have not measured that. If I am right, each added subtype adds nearly its whole vocabulary to the union while the shared core stays at an id, a type, a name, a source and a date. Keeping subjects, observation contexts, stations and information artifacts out of `Sample` is therefore both the right definition and the cheap storage choice.

## Sources

- nmdc-schema main at 76fa03024, https://github.com/microbiomedata/nmdc-schema, measured with LinkML SchemaView on 2026-10-28.
- MIxS clone at 6a2a6edd6 (2026-08-12, 8 commits after v7.0.1), https://github.com/GenomicsStandardsConsortium/mixs, measured with LinkML SchemaView on 2026-10-28.
- nmdc-lakehouse local export of 2026-08-21 (27,352 biosamples), measured with DuckDB on 2026-10-28. The flattening rules are at https://github.com/microbiomedata/nmdc-lakehouse/blob/main/docs/architecture.md and the generated flat schema is at https://github.com/microbiomedata/nmdc-lakehouse-schema.
