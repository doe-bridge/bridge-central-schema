# BER Schema Mapper: what it covers for the umbrella work

Read 2026-10-14 from the catalog embedded in `index.html` at https://github.com/corilo/BER-Schema-Mapper (commit 19072c7). The tool itself is at https://corilo.github.io/BER-Schema-Mapper/.

- **Saving.** On the GitHub Pages site, mappings are kept in your browser's `localStorage` only. A shared group session needs someone to run the repo's `serve.py`. Use Export JSON or Export CSV to keep anything.
- **Grouping classes** follow BASALT's process flow: sampling activity, samples, sample processing, processed sample, data generation, data processing and data products, plus site metadata, sample metadata and other. New grouping classes can be added on the Abstractions page.
- **BASALT.** 98 of 148 BASALT classes are pre-assigned to a group. `Sample`, `ProcessedSample`, `SampleProcessing`, `Site` and `SamplingActivity` are assigned. `organism`, `Study` and `ProcessingSampleLink` have no group, and the "Other" group's description lists Study. There is no group for Organism, Study or Project yet.
- **NMDC Lakehouse source** (99 classes) is the generated flattened LinkML schema, including `MaterialProcessingFlat`, `material_processing_set_has_input`, `material_processing_set_has_output`, `OrganismFlat` and `OrganismSampleFlat`.
- **NMDC source** (75 classes) includes `Sample`, `Biosample`, `ProcessedSample`, `MaterialProcessing` and `Study`, but not `Organism` or `OrganismSample`, which are in nmdc-schema v11.24.1. Its classes come from https://github.com/sierra-moxon/bridge-research; the nmdc-schema version used there is not recorded in the mapper.
- **Classes, not slots.** The mapper places whole classes into groups. It cannot record that `nmdc:collected_from` corresponds to BASALT's `sampled_at_site`, so slot-level mappings live in `umbrella_classes.yaml`.
