# What is a sample (draft)

This note is a proposal for the Samples, Projects and Processes squad to argue with, not an agreed definition. It writes down what @turbomam said at the squad meeting on 2026-10-28 about what the draft `Sample` class in `src/ber_central_schema/schema/umbrella.yaml` means and what it leaves out. Each point is made in plain words first and then backed by a definition from a published ontology or standard. Every quoted definition was read on 2026-10-28 from the sources listed at the end.

## The short version

A sample is a piece of material that someone took from something larger so that measurements on the piece can stand for the whole. A soil core stands for a plot. A leaf disc stands for a plant. A DNA extract stands for the soil core it was extracted from. If nothing was taken, or the thing taken is not meant to stand for anything larger, it is not a sample, even when it ends up in a sample table.

## Three conditions

Something is a sample, relative to a particular investigation, when all three of these conditions hold.

1. It is material: it occupies space and has mass. A core, a filter, a tube of extract and a vial of culture are material. A file, a sequence and a genome bin are not. nmdc-schema defines `MaterialEntity` as "A named thing that occupies space and has mass."
2. It was taken from something larger in order to stand for that larger thing. The larger thing is what the results are about: a plot, a population, a culture, an organism, or another sample. This is the statistical sense of the word. The Ontology for Biomedical Investigations (OBI) defines material sampling process (OBI:0000744) as "A specimen gathering process with the objective to obtain a specimen that is representative of the input material entity." The W3C Sensor, Observation, Sample, and Actuator ontology (SOSA) defines `isSampleOf` as the "Relation from a Sample to the FeatureOfInterest that it is intended to be representative of." A feature of interest, in SOSA, is the thing the observations are about.
3. It was collected so that measurements could be made on it. OBI defines specimen (OBI:0100051) as "A material entity that is collected for potential use as an input upon which measurements or observations are performed." nmdc-schema defines `Biosample` as "Biological source material which can be characterized by an experiment."

The draft's current description, "A physical material that can be characterized by an experiment", covers the first and third conditions and leaves out the second.

Two things follow from the second condition.

- Whether something is representative is a fact about how it was taken, not about the object. So the schema has to record the sampling step and what the sample was taken from. The draft's `Sample` comments say "This draft leaves the sampling event out." This note argues that it cannot stay out. A record with no recorded source describes a material, not yet a sample.
- Samples chain. A DNA extract is a sample of a soil core, and the soil core is a sample of a plot. So the output of `MaterialProcessing` is a `Sample`, and `sample_category` says what kind of sample it is. Followed back through the processing steps, every chain ends at something that is not a sample: a plot, a plant, a culture, a person.

## What is not a sample

Three kinds of thing get called samples in BER data and fail at least one of the conditions.

A subject is the individual thing being studied in its own right: a plant in a phenotyping platform, a patient, a strain growing in a bioreactor. A subject keeps its identity across repeated measurements, and nobody took it from something larger to stand for that larger thing. OBI calls this role participant under investigation role (OBI:0000097): "A role that is realized through the execution of a study design in which the bearer of the role participates and in which data about that bearer is collected." The Minimum Information About a Plant Phenotyping Experiment standard (MIAPPE) calls the same thing an observation unit: "objects that are subject to instances of observation and measurement. An observation unit comprises one or more plants, and/or their environment." A subject is often the larger thing that samples are taken from: a leaf disc is a sample of a plant, and a blood draw is a sample of a person. nmdc-schema already draws this line for microbes. `Organism` is the subject, and `OrganismSample` is material taken from that organism (https://github.com/microbiomedata/nmdc-schema/pull/2977).

An observation is a measurement made on something in place, with nothing taken away. Readings from the sensors on a flux tower are observations of the air at that site. SOSA defines `Observation` as the "Act of carrying out an (Observation) Procedure to estimate or calculate a value of a property of a FeatureOfInterest", and it describes a station as "an identifiable locality where a Sensor system or procedure may be deployed, so the observed properties relate to the physical medium at the station, and not to any physical artifact." Time, treatment and developmental stage belong on the observation record, not on a sample record. "Plant X on day 14 under drought" is a plant plus a time plus a treatment. Darwin Core, the biodiversity data standard, has a name for that: an `Occurrence` is "A dwc:Event that establishes the state of a dwc:Organism at a particular place and time." If someone does collect a canister or a filter at the tower, that canister or filter is a sample.

An information artifact is a record, not a thing: a sequence, an assembly, a metagenome-assembled genome (MAG) bin, a plasmid map, a model. It is not material, so it is not a sample, whatever it was computed from. A MAG bin is the output of binning, which nmdc-schema describes in `MagsAnalysis` as a step that "uses computational binning tools to group assembled contigs into genomes." NCBI files MAGs as BioSamples anyway. The GenBank WGS FAQ says "You should create one BioSample for each MAG", using the MIMAG package and a `derived_from` attribute that points at the SRA runs or at "the physical BioSample(s) representing the mixed sample". That back-pointer is NCBI's admission that the row does not describe a collected material. Treating MAGs as samples to get them through JGI processes, as described at the squad meeting on 2026-10-28, is the same accommodation.

A synthetic construct splits in two. The design, such as a plasmid map, is information. The built plasmid prep or strain is material, but it was built rather than taken to stand for anything, so it is a reagent or the subject itself. An aliquot of that culture taken for sequencing is a sample of the culture. That is how this note reads the draft's `engineered_strain` and `synthesized_material` categories.

## The meeting cases

| Case | Material | Taken from something larger | Collected for measurement | Proposed verdict | Notes |
|---|---|---|---|---|---|
| Soil core from a plot | yes | yes | yes | sample | The plot is the larger thing. |
| Air at a flux tower, read by sensors | yes | no | no | observation | Air is material, but nothing is taken. The sensors observe the air at the site in place. |
| Plant in a phenotyping platform, imaged daily | yes | no | no | subject | The plant is the thing studied. It is observed, not consumed. |
| Plant X on day 14 under drought | no | no | no | observation | This is a plant plus a time plus a treatment, not an object. |
| Leaf disc from that plant | yes | yes | yes | sample | The plant at that time is the larger thing. |
| Construct design (plasmid map) | no | no | no | information artifact | |
| Built strain carrying the construct | yes | no | no | subject or reagent | It was built, not taken. It is studied or used. |
| MAG bin | no | no | no | information artifact | It was computed from reads. |

MIAPPE's rule for when to mint a sample is worth copying. It says: "A sample must be used when there is a physical sample that needs to be stored and traced. Otherwise, observations made at the sub-plant level should be recorded as plant level observations."

## Where each kind of thing goes in the draft schema

For anyone writing a loader or a mapping, this is where the kinds above land in the classes on this branch today.

| Kind of thing | Draft class | Notes |
|---|---|---|
| sample | `Sample` | `sample_category` says what kind. A processed sample is also a `Sample`. The step that produced it points at it with `has_output`, and `ProcessingSampleLink` is the flat-table form of that link. |
| the larger thing a sample was taken from | none | The draft records neither the sampling step nor the source. This note argues that one of the two is needed. |
| subject, as an individual (one plant, one patient) | none | The draft's `Organism` is "The biological identity of what is in a sample (a strain, isolate or engineered construct), not a physical sample", and several samples share one. An individual plant under daily imaging has no class yet. |
| station or site | `Site` | Described as "A place where samples are collected." A flux tower site collects none, so that description would need to widen. |
| observation | `Observation` in `measurements.yaml` | Mapped to sosa:Observation. Its `feature_of_interest` slot is commented out, with a note to restore it once a shared sample or feature-of-interest class is designed. |
| information artifact (sequence, MAG bin, plasmid map) | none | Out of scope for this note. |

## Why this matters for the tables

Keeping subjects, observations, stations and information artifacts out of `Sample` is also the cheap choice for storage. NMDC's three sample classes share 5 of their 560 slots (measured with LinkML SchemaView on nmdc-schema main at 76fa03024 on 2026-10-28), and the flattened nmdc-lakehouse biosample table has 1,402 columns, of which 22 are populated in at least half of its 27,352 rows (measured with DuckDB on @turbomam's local export of 2026-08-21). The storage trade-offs behind those numbers, and a proposal for handling them, are in `wide-polymorphic-tables.md`.

## Sources, all read 2026-10-28

- nmdc-schema main at 76fa03024, https://github.com/microbiomedata/nmdc-schema: `MaterialEntity` in `src/schema/basic_classes.yaml`, `Biosample` and `OrganismSample` in `src/schema/core.yaml`, `MagsAnalysis` in `src/schema/workflow_execution_activity.yaml`
- OBI, through the OLS4 API at https://www.ebi.ac.uk/ols4/ontologies/obi: OBI:0100051, OBI:0000744, OBI:0000097
- SOSA/SSN: https://www.w3.org/TR/vocab-ssn/
- Darwin Core term list: https://raw.githubusercontent.com/tdwg/dwc/master/vocabulary/term_versions.csv
- MIAPPE checklist: https://raw.githubusercontent.com/MIAPPE/MIAPPE/master/MIAPPE_Checklist_Data_Model.tsv
- NCBI GenBank WGS FAQ: https://www.ncbi.nlm.nih.gov/genbank/wgsfaq/
