# Umbrella classes for samples, organisms, studies and processing (draft)

Working files for the BRIDGE umbrella schema group, 2026-10-14. Nothing here is agreed. The draft classes are in `src/ber_central_schema/schema/umbrella.yaml`, which the central schema imports so the docs site shows them, and their examples are in `tests/data/`, where `just test` checks them.

Sources read on 2026-10-14: nmdc-schema main at 03ba5a2 (https://github.com/microbiomedata/nmdc-schema), BASALT-Schema main at f41b7f4 (https://github.com/EMSL-Computing/BASALT-Schema), nmdc-lakehouse main at 3992849 (https://github.com/microbiomedata/nmdc-lakehouse) and BER-Schema-Mapper at 19072c7 (https://github.com/corilo/BER-Schema-Mapper).

## Files

| File | What it is |
|---|---|
| `nmdc-basalt-comparison.md` | What nmdc-schema and BASALT have today, side by side. Same content as the commentable Google Doc: https://docs.google.com/document/d/1ZF5mnfnauqJag8zM-YEZVq5BPa-jUyoKOOHChi5xtd4/edit |
| `src/ber_central_schema/schema/umbrella.yaml` | A LinkML proposal for shared `Study`, `Site`, `Organism`, `Sample`, `PlannedProcess` and `MaterialProcessing` classes, plus `ProcessingSampleLink` |
| `mapper-notes.md` | What Yuri's BER Schema Mapper covers and lacks for this work |
| `tests/data/valid/` and `tests/data/invalid/` (files not named `Measurement-*`) | Small valid and invalid instances, including the two `ProcessingSampleLink` rows that one NMDC Extraction step becomes |

## Use together

- Start from `nmdc-basalt-comparison.md`. Each umbrella class in `umbrella.yaml` lists, in `exact_mappings` or `close_mappings`, the nmdc-schema and BASALT classes from that table that it stands for.
- The umbrella classes are imported into this repo's schema as a draft, marked as not yet agreed. The measurements module (https://github.com/doe-bridge/bridge-central-schema/pull/9) has a `feature_of_interest` slot waiting for a Sample class.
- For what the processing graph looks like as tables, nmdc-lakehouse is one worked example. Its flattening rules are in https://github.com/microbiomedata/nmdc-lakehouse/blob/main/docs/architecture.md ("Normalization decisions"), and the generated flat schema is itself LinkML (https://github.com/microbiomedata/nmdc-lakehouse-schema).

## Alternatives for the same job

### Storing sample-to-processing links as tables

- NMDC flattened: two tables, `material_processing_set_has_input` and `material_processing_set_has_output`, with the direction in the table name (https://github.com/microbiomedata/nmdc-lakehouse/blob/main/docs/trino_recursive_graph_traversal.md).
- BASALT: one `ProcessingSampleLink` table with a `role` column, plus `step_number` and `in_run`.

The two hold the same facts; BASALT's table is the union of NMDC's two. `umbrella.yaml` keeps `has_input` and `has_output` on `PlannedProcess` (limited to samples on `MaterialProcessing`) and uses BASALT's shape for the flat form. Whether `step_number` and `in_run` belong in the umbrella is open.

### Writing down mappings

These do different jobs. Each fact should have one home.

- LinkML mapping slots (`exact_mappings`, `close_mappings`, `related_mappings`) in the umbrella schema, as in `umbrella.yaml`. Proposed as the main record.
- SSSOM (https://mapping-commons.github.io/sssom/): the same mappings as a table, with room for justification, author and confidence. It can be generated from the LinkML mapping slots (`gen-sssom umbrella_classes.yaml` with linkml 1.11.1, run before the file moved to `umbrella.yaml`, gives one row per mapping on classes and slots, 45 rows; mappings on enum values are not exported), so it is another view of the same facts, not a second source.
- linkml-map (https://github.com/linkml/linkml-map): transformation specs for converting NMDC or BASALT data into umbrella form, for example turning `has_input` lists into `ProcessingSampleLink` rows. Needed for loading data, not for agreeing on classes.

### Placing classes

- BER Schema Mapper (https://corilo.github.io/BER-Schema-Mapper/) places whole classes from 19 BER schemas into process-flow groups. It does not record slot mappings.
- `umbrella.yaml` maps classes and slots, for NMDC and BASALT only.

The mapper suits a first pass across many schemas; what the group agrees can then be recorded in the LinkML mapping slots.

## Checking the draft

`just test` loads every file in `tests/data/valid/`. `linkml-validate -s src/ber_central_schema/schema/ber_central_schema.yaml -C <Class> <file>` reports no issues for every file in `tests/data/valid/` and an error for every file in `tests/data/invalid/`.

## Known gaps

- Identifiers: BASALT ids are bare UUIDs and the umbrella `id` range is `uriorcurie`. The BASALT example writes them as `urn:uuid:` URIs. `linkml-validate` 1.11.1 also accepted a bare UUID in a `uriorcurie` slot, so the draft does not yet enforce any id form; that needs a decision (`urn:uuid:`, a BASALT prefix, or a pattern).
- Records held in more than one system: much NMDC metadata redistributes records that EMSL and JGI (GOLD) also hold. `external_identifiers` on `NamedThing` records the original system's identifier so the copies can be matched. It is one generic list, as in BASALT; nmdc-schema instead has one slot per system and entity type (`gold_biosample_identifiers`, `emsl_biosample_identifiers`, ...). Whether the umbrella needs to say which system holds the original record is open.
- Sample categories: `sample_category` (`SampleCategoryEnum`) is one option for the request for more sample categories (plants and others). It says where the material came from (culture, engineered strain, environment). Three BASALT Sample subclasses name a program rather than a material (`AMP2UserSample`, `TerraformSample`, `FieldDeployedTerraformSample`) and have no category value. Values have no ontology meanings yet.
- `PlannedProcess` and `MaterialProcessing` are abstract and the draft has no concrete subclasses, so the processing examples use `ProcessingSampleLink`.

- James Carr's BASALT-to-Parquet work was not found, so the BASALT flat form above comes from the BASALT LinkML schema, not its Parquet output.
- See `mapper-notes.md` for gaps in the mapper's catalog.
