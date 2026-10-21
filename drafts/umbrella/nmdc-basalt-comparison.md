# nmdc-schema and BASALT: sample, organism, study and processing classes

Mark Miller, 2026-10-14. Starting point for the BRIDGE umbrella schema group. Corrections welcome, especially on the BASALT side.

Versions read: nmdc-schema main at 03ba5a2 (https://github.com/microbiomedata/nmdc-schema) and BASALT-Schema main at f41b7f4, 2026-09-28 (https://github.com/EMSL-Computing/BASALT-Schema).

## Side by side

| concept | nmdc-schema | BASALT | same or different |
|---|---|---|---|
| abstract sample | `Sample`, abstract, is_a `MaterialEntity` | `Sample`, abstract, no parent; slots `name`, `description`, `emsl_activity`, `lims_barcode` | same name, both abstract |
| concrete samples | one wide `Biosample` with MIxS slots and `env_broad_scale`, `env_local_scale`, `env_medium`; a separate `OrganismSample` | 18 subclasses of `Sample`, mostly by sample type (`SoilSample`, `WaterSample`, `PlantSample`, `PureCultureSample`, ...) | different: one class vs one class per type |
| processed sample | `ProcessedSample` is_a `Sample` | `ProcessedSample` is_a `Sample` | same |
| sampling event | collection slots such as `collection_date` are on `Biosample` | separate `SamplingActivity` class; samples point to it with `sampled_during` | different |
| site | `FieldResearchSite`, linked from the sample by `collected_from` | `Site`, linked from `SamplingActivity` by `sampled_at_site` | both have a site class, linked from different places |
| organism | `Organism`: the biological identity of what is in a sample, not the sample; taxon in `classified_as` (range `NcbiTaxon`) | `organism`: a biological identity that many physical samples can instantiate; replaced the former `Strain` class; `taxonomy_id` is a string | close in meaning; taxon is a class in one and a string in the other |
| sample to organism | `expected_organism` on `OrganismSample` | `organism_ref` on sample and culture classes | same idea, different slot names |
| study or project | `Study` (aliases include project and proposal); no `Project` class | `Study`, with `project_id`; samples and activities carry a `project` slot with an integer range | both use `Study`; linked by reference in NMDC, by integer in BASALT |
| processing | `MaterialProcessing`, abstract, is_a `PlannedProcess` | `SampleProcessing`, abstract, 14 subclasses (`Extraction`, `FiltrationProcess`, `PoolingProcess`, `SubsamplingProcess`, ...) | same scope, many of the same subclasses |
| processing inputs and outputs | `has_input` and `has_output` lists on the process | no pointers on `SampleProcessing`; `ProcessingSampleLink` holds one row per edge with `processing_id`, `sample_id`, `role`, `step_number`, `in_run` | different |
| protocol | `protocol_link` slot | `SampleProcessingProtocol` class, referenced by `in_protocol` | different |
| identifiers | CURIEs with typed prefixes (`nmdc:bsm-`, `nmdc:procsm-`, `nmdc:orgn-`) | `id` with range `uuid` | different |

## Inputs and outputs as tables

BASALT already stores the processing graph as a table: `ProcessingSampleLink` is one row per sample and processing step, with a role column.

NMDC stores the graph as `has_input` and `has_output` lists. When nmdc-lakehouse flattens NMDC into Parquet for BERDL, each list becomes a side table named `{collection}_{slot_name}` with a `parent_id` column and the referenced id, for example `workflow_execution_set_has_input` and `workflow_execution_set_has_output`. The direction is in the table name rather than in a column. Details: https://github.com/microbiomedata/nmdc-lakehouse/blob/main/docs/architecture.md

Put together, those two NMDC tables hold the same rows as BASALT's link table.

## Questions

1. Does the table get BASALT right?
2. Do `step_number` and `in_run` belong in an umbrella class, or are they specific to EMSL?
3. Where is the BASALT Parquet work that Sierra mentioned?
4. Is https://github.com/corilo/BER-Schema-Mapper the mapping tool we would use in a hackathon?
5. GOLD has both a study and a project class, and neither schema here has `Project`. What is a GOLD project?
