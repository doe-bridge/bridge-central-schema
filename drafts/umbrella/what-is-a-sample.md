# What is a sample (draft)

This note is a proposal for the Samples, Projects and Processes squad to argue with, not an agreed definition. It writes down what I said at the squad meeting on 2026-10-28 about what the draft `Sample` class in `src/ber_central_schema/schema/umbrella.yaml` means and what it leaves out. I read every definition quoted here on 2026-10-28, from the sources listed at the end.

## Three conditions

A material entity is a sample, relative to an investigation, when all three of the following conditions hold.

1. The entity is material, meaning that it occupies space and has mass. nmdc-schema defines `MaterialEntity` as "A named thing that occupies space and has mass."
2. Someone drew the entity from a larger body in order to represent that body. The larger body is what the results are about: a plot, a population, a culture, an organism, or another sample. OBI defines `material sampling process` (OBI:0000744) as "A specimen gathering process with the objective to obtain a specimen that is representative of the input material entity." SOSA defines `isSampleOf` as the "Relation from a Sample to the FeatureOfInterest that it is intended to be representative of."
3. Someone collected the entity to be an input to measurement. OBI defines `specimen` (OBI:0100051) as "A material entity that is collected for potential use as an input upon which measurements or observations are performed." nmdc-schema defines `Biosample` as "Biological source material which can be characterized by an experiment."

The draft's current description, "A physical material that can be characterized by an experiment", covers the first and third conditions and leaves out the second. The second condition is the statistical one: a sample is a representative part of something larger.

Three things follow from the second condition.

- Representativeness is a property of the sampling step, not of the object, so the schema has to record that step and its input. The `Sample` comments in the draft say "This draft leaves the sampling event out." I don't think it can stay out. A record with no recorded source describes a material, not yet a sample.
- Samples chain. A DNA extract is a sample of a soil core, and the soil core is a sample of a plot. So the output of `MaterialProcessing` is a `Sample`, and `sample_category` says what kind of sample it is.
- Samples are instruments. SOSA's comment on `Sample` says that samples "usually have no significant function outside of their role in the observation process." When the thing matters in its own right, it is probably a subject rather than a sample.

## What is not a sample

A subject is an organism, a group, or an engineered system about which data are collected directly. A subject keeps its identity across observations, and nobody drew it from a larger body to stand in for that body. OBI defines `participant under investigation role` (OBI:0000097) as "A role that is realized through the execution of a study design in which the bearer of the role participates and in which data about that bearer is collected." MIAPPE calls the same thing an `Observation Unit`, defined as "objects that are subject to instances of observation and measurement. An observation unit comprises one or more plants, and/or their environment." A plant in an automated phenotyping platform is a subject, and so is a person in a medical record. A subject can also be the larger body that samples are drawn from: a leaf disc is a sample of a plant, and a blood draw is a sample of a person. nmdc-schema already draws this line for microbes. `Organism` is the subject, and `OrganismSample` is material taken from that organism (https://github.com/microbiomedata/nmdc-schema/pull/2977).

An observation of a feature of interest is not a sample. SOSA defines `Observation` as the "Act of carrying out an (Observation) Procedure to estimate or calculate a value of a property of a FeatureOfInterest." Time, treatment and developmental stage belong on the observation, not on a sample. Darwin Core has a name for a plant at a time point: it defines `Occurrence` as "A dwc:Event that establishes the state of a dwc:Organism at a particular place and time." Atmospheric monitoring, flux towers included, involves no sample at all. SOSA describes a station as "an identifiable locality where a Sensor system or procedure may be deployed, so the observed properties relate to the physical medium at the station, and not to any physical artifact." If someone collects a canister or a filter at the station, that canister or filter is a sample.

An information artifact is not a sample. Sequences, assemblies, MAG bins, construct designs and models are not material, so they are not samples, whatever their provenance. A MAG bin is the output of binning. nmdc-schema describes `MagsAnalysis` as a step that "uses computational binning tools to group assembled contigs into genomes." NCBI files MAGs as BioSamples anyway. The GenBank WGS FAQ says "You should create one BioSample for each MAG", using the MIMAG package and a `derived_from` attribute that points at the SRA runs or at "the physical BioSample(s) representing the mixed sample". That back-pointer is NCBI's admission that the row does not describe a collected material. Treating MAGs as samples to get them through JGI processes, as described at the squad meeting on 2026-10-28, is the same accommodation.

A synthetic construct splits in two. The design is information. The built plasmid prep or strain is material, but it was built rather than drawn to represent anything, so it is a reagent or the subject itself. An aliquot of that culture taken for sequencing is a sample of the culture. I'd read the draft's `engineered_strain` and `synthesized_material` categories that way.

## The meeting cases

| Case | Material | Drawn from a larger body | Collected for measurement | Proposed verdict | Notes |
|---|---|---|---|---|---|
| Soil core from a plot | yes | yes | yes | sample | The plot is the larger body. |
| Air at a flux tower, read by sensors | yes | no | no | observations of a feature of interest | Air is material, but nothing is taken. The sensors observe the atmosphere at the site in place. |
| Plant in a phenotyping platform, imaged daily | yes | no | no | subject | The plant is the thing studied. It is observed, not consumed. |
| Plant X on day 14 under drought | no | no | no | observation context | This is a plant plus a time plus a treatment, not an object. |
| Leaf disc from that plant | yes | yes | yes | sample | The plant at that time is the larger body. |
| Construct design (plasmid map) | no | no | no | information artifact | |
| Built strain carrying the construct | yes | no | no | subject or reagent | It was built, not drawn. It is studied or used. |
| MAG bin | no | no | no | information artifact | It was computed from reads. |

MIAPPE's rule for when to mint a sample is worth copying. It says: "A sample must be used when there is a physical sample that needs to be stored and traced. Otherwise, observations made at the sub-plant level should be recorded as plant level observations."

## Why this matters for the tables

Keeping subjects, observation contexts, stations and information artifacts out of `Sample` is also the cheap choice for storage. NMDC's three sample classes share 5 of their 560 slots (measured with LinkML SchemaView on nmdc-schema main at 76fa03024 on 2026-10-28), and the flattened nmdc-lakehouse biosample table has 1,402 columns, of which 22 are populated in at least half of its 27,352 rows (measured with DuckDB on the local export of 2026-08-21). The storage trade-offs behind those numbers, and what I propose to do about them, are in `wide-polymorphic-tables.md`.

## Sources, all read 2026-10-28

- nmdc-schema main at 76fa03024, https://github.com/microbiomedata/nmdc-schema: `MaterialEntity` in `src/schema/basic_classes.yaml`, `Biosample` and `OrganismSample` in `src/schema/core.yaml`, `MagsAnalysis` in `src/schema/workflow_execution_activity.yaml`
- OBI, through the OLS4 API at https://www.ebi.ac.uk/ols4/ontologies/obi: OBI:0100051, OBI:0000744, OBI:0000097
- SOSA/SSN: https://www.w3.org/TR/vocab-ssn/
- Darwin Core term list: https://raw.githubusercontent.com/tdwg/dwc/master/vocabulary/term_versions.csv
- MIAPPE checklist: https://raw.githubusercontent.com/MIAPPE/MIAPPE/master/MIAPPE_Checklist_Data_Model.tsv
- NCBI GenBank WGS FAQ: https://www.ncbi.nlm.nih.gov/genbank/wgsfaq/
