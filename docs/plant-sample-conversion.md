# Converting AIMS-LEAF PlantSample into the BRIDGE sample architecture

AIMS-LEAF's `PlantSample`
([lambda-ber/aims-leaf](https://github.com/lambda-ber/aims-leaf),
`SamplePlant_schema.yaml`; evaluated as PR #50, closed in favor of this
conversion) carries ~60 attributes on one flat sample record. BRIDGE
factors that record across four channels:

```
tissue Sample --derived_from--> plant Sample --biological_context--> BiologicalContext
      |                               |                              (catalog record)
      +-- Measurement rows -----------+
          (feature_of_interest)
```

- **Sample** (PR #39) stays minimal: id, name, description, `derived_from`,
  `sample_of`. The plant is itself a Sample; the tissue piece is a Sample
  `derived_from` it. Sample-level slots proposed here: `biological_context`,
  `replicate_group`, `tissue`, `tissue_ontology_term`,
  `collection_date_time`.
- **Measurement** (merged) holds every observed or set value, keyed by
  `feature_of_interest` and `value_role` (measured / setting / interpreted /
  derived).
- **BiologicalContext** (this module) holds the identity block: the named
  line/strain/cultivar/accession record a sample points at.
- **Attribute** (merged, currently unattached) is the overflow bag for
  source fields that fit none of the above, if the group attaches it.

## Field-by-field mapping

### To the tissue Sample

| AIMS-LEAF field | Destination |
|---|---|
| tissue (required) | `tissue` slot |
| tissue_plant_ontology_term | `tissue_ontology_term` (one term per value, multivalued at attachment) |
| combined_tissue_description | `derived_from` (multiple parents) + free text; see agenda item 5 |
| collection_date_time (required) | `collection_date_time` slot |
| sample_size | Measurement (mass/volume property, role=measured) |
| experimental_time_point_number / _description | Sample description or Attribute; study-design placement open |
| biological_replicate_sample_group_name | `replicate_group` slot |

### To Measurement rows on the plant or tissue Sample

All need `bridge_property:` terms (none registered yet — agenda item 7):
developmental_stage, plant_age, arabidopsis_phenotype_stage, plant_sex,
sample_disease_status, sample_disease_stage, observed_host_symbionts,
temperature (at sampling). `value_role=measured` or `interpreted`.

### To Treatment records or setting-role Measurements

growth_facility, growth_medium, growth_medium_composition, and all regimen
and perturbation fields: air_temperature_regimen, antibiotic_regimen,
biotic_regimen, inoculation_method, time_post_inoculation,
chemical_administration, chemical_mutagen (when applied as a treatment, not
line provenance), fertilizer_administration, insecticide_regimen,
fungicide_regimen, gaseous_environment, growth_hormone_regimen,
herbicide_regimen, humidity_regimen, radiation_regimen, light_regimen,
last_light_transition_type, time_after_last_light_transition, salt_regimen,
rainfall_regimen, watering_regimen, other_treatment_regimen, perturbation,
mechanical_damage. This inventory is the checklist a Treatment class must
be able to express; timing-relative-to-sampling is unresolved (agenda
item 3).

### To the BiologicalContext catalog record

| AIMS-LEAF field | BiologicalContext slot |
|---|---|
| genus, species | `genus`, `species` |
| ncbi_taxonomy_id | `taxon` (as a CURIE, not an integer) |
| strain_variety_cultivar | `name` + `context_type` (the enum makes the category explicit) |
| isolate | `context_type=isolate` or `variant`, own record |
| germplasm_collection_id | `material_source_institute_code` + `material_source_accession_number` (split, not one string) |
| ancestral_data | `pedigree` (text) and `parent_contexts` (resolvable) |
| genetic_modification | `genetic_modification`; mutagenesis agent goes to `mutagen` |
| ploidy | `ploidy` |
| estimated_genome_size_mb, gc_content_percent | same names |
| reference_genome | partially `genome_assemblies`; the "use for analysis" directive does not fit — agenda item 1 |

### To Site / location records (module pending)

region_locality, latitude, longitude, depth_meters, elevation_meters,
broad_scale_environmental_context, local_environmental_context,
environmental_medium. These describe where the plant grew — distinct from
`material_source_latitude/longitude`, which record where the accession was
originally collected (agenda item 4).

## Agenda: what does not fit cleanly

1. **`reference_genome` as an analysis directive.** "Reference genome and
   annotation to be used for analysis" is an instruction about future
   processing, not a property of the material. `genome_assemblies` records
   which assemblies exist for an identity; the directive belongs on an
   analysis or workflow configuration entity BRIDGE does not have. Interim:
   Attribute.
2. **Required-ness and validation do not survive the EAV move.** AIMS-LEAF
   requires genus, species, tissue, collection_date_time, growth_facility,
   growth_medium, developmental_stage and pattern-checks ENVO terms. Once
   those become Measurement or Treatment rows, "every plant sample must
   state X" is not expressible in LinkML; it becomes a completeness rule in
   the property registry or a QC check. Decide where such rules live.
3. **Treatment timing relative to sampling.** time_post_inoculation,
   time_after_last_light_transition, and narratives like "NaCl at day 3,
   then 3 days recovery before sampling" encode offsets between the
   treatment timeline and the sampling event. Neither Measurement
   (absolute `observed_time`) nor a Treatment-as-factor-level record
   expresses them. The regimen fields are easy; their chronology is not.
4. **Two geographies, one block.** Growing location (a Site) and
   accession-collection origin (`material_source_*` on the catalog record)
   must not be conflated when sources report "latitude/longitude."
5. **Pooling.** "6 lateral root tips from each of two plants" is
   `derived_from` with two parents, but per-parent counts do not fit, and
   parent plants often have no records. Free text (or Attribute) on the
   pooled sample is the honest fallback.
6. **Allelic composition is still missing everywhere.**
   `genetic_modification` + `mutagen` give no zygosity and no
   allele-on-background structure (TAIR's germplasm-polymorphism-zygosity
   associations). BER data today carries names and pedigrees, rarely
   allelic composition; deferring is defensible but should be an explicit
   decision.
7. **Property registry additions.** The Measurement-bound fields above need
   `bridge_property:` terms (developmental_stage, plant_age, plant_sex,
   disease_status, disease_stage, host_symbionts, sample mass/volume, and
   the setting-role condition properties) before any real conversion runs.
8. **`sample_of` vs `biological_context`.** `sample_of` (PR #39) points at
   the larger thing a sample represents; `biological_context` points at the
   identity record a sample instantiates. A plant of RIL 407 arguably has
   both ("represents plot 12's planting"; "instantiates RIL 407"). Decide
   whether one slot carries both meanings or the two stay separate.
9. **Attaching Attribute.** The merged Attribute class has no owner. If the
   overflow bag is wanted, Sample (and others) need a multivalued
   `attributes` slot, with gen-sqlddl implications checked.
