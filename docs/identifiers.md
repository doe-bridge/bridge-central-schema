# Identifiers and prefixes

This page sets the prefix and identifier rules for the BRIDGE central schema, https://github.com/doe-bridge/bridge-central-schema. `tests/test_prefixes.py` checks part of it. `test_no_prefix_has_two_expansions` and `test_data_prefixes_are_declared` pass against the schema on `main`. `test_every_module_uses_the_element_prefix`, `test_every_element_asserts_its_uri` and `test_every_class_has_a_type_slot` are marked expected to fail (a strict `xfail`) until the open pull requests move every module to the one namespace and https://github.com/doe-bridge/bridge-central-schema/issues/35 is done; after that each of them has to pass. Rules for numeric values are a separate topic, on https://github.com/doe-bridge/bridge-central-schema/issues/36.

A CURIE is the compact form of a URI, `prefix:local_part`, where the schema declares what the prefix expands to. Bioregistry, https://bioregistry.io, is the registry of prefixes this schema follows.

## Rules

1. Every class, slot, enum and type this schema defines has a URI under one namespace, `bridge_central_schema`, which expands to https://w3id.org/ber-data/bridge-central-schema/, and every module sets `default_prefix: bridge_central_schema`. A module does not declare a namespace of its own. The measurements module on `main` still uses `bridge`; https://github.com/doe-bridge/bridge-central-schema/pull/9 changes it. Checked by `test_every_module_uses_the_element_prefix`.
2. Each module's schema `id` is `https://w3id.org/ber-data/bridge-central-schema/<module>`, for example https://w3id.org/ber-data/bridge-central-schema/measurements. A schema id is a full URL and not a CURIE, so the slash is fine; element CURIEs stay `bridge_central_schema:Measurement`.
3. BRIDGE ids and namespaces stay under https://w3id.org/ber-data/, even though the GitHub organization is now `doe-bridge`. Nothing under that path resolves yet; registering it is https://github.com/doe-bridge/bridge-central-schema/issues/26.
4. Every element asserts its URI: `class_uri` on every class, `slot_uri` on every slot, and `meaning` on every enum value that has a term in an outside vocabulary. Checked by `test_every_element_asserts_its_uri`.
5. Every class has a type slot, marked `designates_type: true`, and every row fills it with its class CURIE, such as `bridge_central_schema:Sample`. The slot's name is open on https://github.com/doe-bridge/bridge-central-schema/issues/35. Checked by `test_every_class_has_a_type_slot`.
6. An id from a source system keeps the source's prefix, spelled as Bioregistry's preferred prefix: `BERVO`, `NCBITaxon`, `NCBIGene`, `kegg.orthology`, `refseq`, `insdc`, `edam`, `qudt.unit`, `emsl.project`, `orcid`, `ror`, `gold` and `nmdc`. A source id is never re-minted under a BRIDGE prefix. An id from another BRIDGE project keeps that project's prefix, so registry entries from https://github.com/doe-bridge/lakehouse-registry are `ber_registry:` ids. A source with no Bioregistry prefix gets one declared in this schema (`ameriflux`). An id with no prefix at all is written as a URI (`urn:uuid:` for BASALT); see the edge cases.
7. A prefix expands to Bioregistry's `uri_format` with the `$1` removed. Each case where this schema differs, or where Bioregistry's value needs a note, is in the table below and in a comment next to the declaration.
8. A prefix name is never reused with a new expansion, within one release or across releases. `bridge` expands to https://w3id.org/ber-data/bridge-measurements/ on `main`, so no later prefix may be called `bridge`. `test_no_prefix_has_two_expansions` checks this within one schema; across releases it is a rule for review.
9. No placeholder namespace. `example:` and the like appear in no schema and no example data; example data uses real public ids under their source's prefix.
10. `id` is a CURIE with a pattern: range `curie`, and a pattern that opens with the prefixes the schema declares for that table. Every CURIE in a slot of range `uriorcurie` or `curie` uses a declared prefix, checked by `test_data_prefixes_are_declared`. Other string slots can hold source text as written, such as a GenBank `db_xref` value, and are not checked.
11. Curated terms keep readable ids for now: `bridge_property:air_temperature`, `bridge_unit:mm2`. Readable versus opaque is decided again in the follow-up to https://github.com/doe-bridge/bridge-central-schema/issues/30; see the alternatives below.
12. These rules cover what https://github.com/turbomam/gold-schema and https://github.com/turbomam/feature-table-corpus produce for BRIDGE, meaning their copies of BRIDGE schema files and the records they emit, and not their own source-description schemas.
13. A DOI is stored in one form only, the CURIE `doi:10....`, with the pattern `^doi:10\.\d{2,9}/.*$` that nmdc-schema puts on `doi_value`. The loader accepts `https://doi.org/...`, `http://dx.doi.org/...`, `DOI:...` and a bare `10....` and rewrites each to that form, so the same DOI never appears under two IRIs.
14. In a slot of range `uriorcurie`, a value is a full URI only when its scheme is followed by `//` or it is a URN (`urn:`). Any other `x:y` value is a CURIE, and its prefix must be declared. A URI scheme with no `//`, such as `mailto:`, is declared like a prefix if BRIDGE ever needs it.

## Edge cases

Bioregistry values were read from `https://bioregistry.io/api/registry/<prefix>` on 2026-11-06. The third column is the value declared in the module that uses the prefix, on `main` or on the open pull request that adds it.

| Prefix | Bioregistry `uri_format` | What this schema uses now | Note |
|---|---|---|---|
| `gold` | `https://gold.jgi.doe.gov/resolver?id=$1` | `https://bioregistry.io/gold:`, the same as nmdc-schema | The two IRIs for `gold:Gs0114820` differ, so a change here would stop BRIDGE and NMDC records from matching in RDF or in a join on the full IRI. On 2026-11-06 the bioregistry.io IRI redirected to the GOLD resolver and the resolver to `https://gold.jgi.doe.gov/study?id=Gs0114820`. I asked JGI which expansion they want on https://github.com/doe-bridge/bridge-central-schema/issues/15#issuecomment-6690980599; the schema keeps `https://bioregistry.io/gold:` until that is answered. |
| `emsl.project` | `https://sc-data.emsl.pnnl.gov/?projectId=$1` | Bioregistry's value | nmdc-schema expands `emsl.project` to `https://bioregistry.io/emsl.project:`, so EMSL project IRIs differ between the two schemas. |
| `refseq` | `https://www.ncbi.nlm.nih.gov/protein/$1` | Not declared yet. The feature model's contig ids, written `insdc:NC_001422.1` today, move to `refseq:NC_001422.1` with Bioregistry's value | Bioregistry's pattern accepts nucleotide accessions (`NC_`, `NZ_`), but the expansion is NCBI's protein path. `https://www.ncbi.nlm.nih.gov/protein/NC_001422.1` returned HTTP 200 on 2026-11-06. |
| `BERVO` | `https://w3id.org/bervo/BERVO_$1` | `bervo`, expanding to `https://w3id.org/bervo/`, with local parts such as `BERVO_0001370` | Bioregistry's spelling moves `BERVO_` out of the local part: `bervo:BERVO_0001370` becomes `BERVO:0001370`, and both expand to the same IRI. Every file that copies the observed property mappings needs the rewrite. |
| `schema` | `https://schema.org/$1` | `http://schema.org/` | Kept. It matches nmdc-schema and the LinkML metamodel (https://github.com/linkml/linkml-model), and it names mapping targets rather than source records. |
| `biolink` | `https://biolink.github.io/biolink-model/$1` | `https://w3id.org/biolink/vocab/` | Kept. It is the namespace `biolink-model.yaml` declares for its own elements (https://github.com/biolink/biolink-model), and nmdc-schema uses it. Mapping targets only. |
| `ameriflux` | none; AmeriFlux is not in Bioregistry | `https://ameriflux.lbl.gov/sites/siteinfo/`, so `ameriflux:US-Ha1` expands to the site page | Declared only in this schema. |
| `urn:uuid` | none; `urn:uuid:` is the URN form of a UUID in RFC 9562, not a prefix | BASALT ids written as URIs, such as `urn:uuid:5b0c6c1e-0000-4000-8000-000000000001` | BASALT's identifier slots have range `uuid` and no prefix (https://github.com/EMSL-Computing/BASALT-Schema/blob/f41b7f4a371d856ebd5357cff7209245559e92d7/src/basalt_schema/schema/study.yaml#L36), and Bioregistry has no `uuid` prefix. A `urn:uuid:` value is a URI and not a CURIE, so a table that holds BASALT rows needs either a prefix for them or an `id` range that allows URIs; that goes with the row-id question on https://github.com/doe-bridge/bridge-central-schema/issues/28. The tests treat `http`, `https` and `urn` as URI schemes, not prefixes. |
| `insdc` | `https://www.ebi.ac.uk/ena/data/view/$1` | Feature ids the converter makes, such as `insdc:NC_001422.1:feature-1` | Bioregistry's `insdc` pattern does not match `NC_` accessions, which are RefSeq, and the source never issued the `:feature-N` suffix. These ids stay until https://github.com/doe-bridge/bridge-central-schema/issues/28 settles how BRIDGE makes ids. |
| `doi` | `https://doi.org/$1` | Not declared yet; no branch holds a DOI value | nmdc-schema expands `doi` to `https://bioregistry.io/doi:`. Declare `doi` with Bioregistry's value in the pull request that adds the first DOI slot. |

## Identifier lifecycle

Create: reuse the source's id under the source's registered prefix, and mint only for things BRIDGE originates (Lesson 1 of McMurry et al. 2017, https://doi.org/10.1371/journal.pbio.2001414). Every id BRIDGE makes has a published pattern, with no `/` or `?` in the local part and a dot only for a version (Lesson 5 of the same paper). A new BRIDGE prefix is lowercase, is never issued per version, and is a subspace only when the resource has more than one entity type (https://github.com/biopragmatics/bioregistry/blob/main/docs/CONTRIBUTING.md). Whether a row that arrives with no source id gets a minted id, a key derived from its fields, or no id is open; the alternatives below give the costs, and RFC 9562 section 6.13 cautions against name-based UUIDs as primary keys because the input values later change (https://www.rfc-editor.org/rfc/rfc9562#section-6.13).

Modify: a label or definition edit keeps the id. For a change that does not break meaning, Lesson 6 of McMurry et al. 2017 (https://doi.org/10.1371/journal.pbio.2001414) recommends a machine-readable change history rather than a new id.

Deprecate: an id is never deleted or reassigned (Lesson 7 of McMurry et al. 2017, https://doi.org/10.1371/journal.pbio.2001414). A deprecated curated term keeps resolving and names its replacement with IAO:0100001 (term replaced by), or lists alternatives with `consider`, as OBO ontologies do (https://oboacademy.github.io/obook/howto/obsolete-term/). DataCite applies the same rule to DOIs, which get a tombstone page rather than deletion (https://support.datacite.org/docs/tombstone-pages).

Merge: one id stays primary and the others become secondary ids that still resolve to the surviving row, as UniProt keeps every accession of merged entries (https://www.uniprot.org/help/accession_numbers). The source ids of every merged row stay recorded on the surviving row.

Split: each part gets a new id, and the old id stays, deprecated, pointing at every part, as UniProt does for demerged entries (https://www.uniprot.org/help/accession_numbers).

Version: a BRIDGE id carries no version, and a source's version suffix stays as the source writes it (`NC_001422.1`). A version belongs in an id only for a breaking change (Lesson 6 of McMurry et al. 2017), and DataCite recommends a new DOI only for a major change, linked to the old one with `IsNewVersionOf` (https://support.datacite.org/docs/versioning). Bioregistry issues no prefix per version (https://github.com/biopragmatics/bioregistry/blob/main/docs/CONTRIBUTING.md).

Resolve: every BRIDGE prefix resolves through w3id with a 302 redirect, because w3id's rules say a 301 cannot be taken back (https://github.com/perma-id/w3id.org/blob/master/docs/rules/htaccess/avoid-permanent-redirect.md). Registering `ids/ber-data` is https://github.com/doe-bridge/bridge-central-schema/issues/26.

## Alternatives considered

### One element namespace or one per module

Earlier branches gave each module its own namespace: `bridge` for measurements, `battr` for attributes and `bfm` for the feature model.

1. One namespace per module. Benefit: a module could be released on its own under its own URI. Costs: a reader has to know which module defined an element to write its CURIE, each namespace needs its own w3id redirect, and the same slot name can exist twice with two different URIs.
2. One namespace, `bridge_central_schema`. Benefit: one CURIE form for every element and one redirect. Cost: slot names must be unique across modules, which `numeric_value` already broke (https://github.com/doe-bridge/bridge-central-schema/issues/36).

I set rule 1 because no module of this schema is released as a standard on its own.

### Ids BRIDGE makes

These are the options for ids BRIDGE itself issues: curated terms today, and possibly table rows later.

1. One readable prefix per curated vocabulary, `bridge_property:` and `bridge_unit:`, which is the current state. @valerie-autumn-skye asked for `bridge_property:air_temperature` as an "intermediate" human-readable term mapped to BERVO (https://github.com/doe-bridge/bridge-central-schema/pull/9#discussion_r4273386207), and https://github.com/doe-bridge/bridge-central-schema/issues/29 adds `bridge_unit:` the same way. Benefits: the id is readable in data files and diffs, a term is added by pull request with no minting service, and the prefix names the table. Costs: one Bioregistry prefix and one w3id redirect per vocabulary, and the rename problem described under readable local parts below.
2. One prefix with an opaque number and no type code. Benefits: one prefix and one redirect, and a rename never touches the id, which is what Lesson 4 of McMurry et al. 2017 recommends (https://doi.org/10.1371/journal.pbio.2001414). Costs: it reverses the readable ids already in use on https://github.com/doe-bridge/bridge-central-schema/pull/9 and in the issues above, a reviewer needs the label beside every id, and each pull request has to take the next free number, with a test that no number is used twice.
3. One prefix with a type code in the local part, as nmdc-schema's `nmdc:sty-11-076c9980` (https://github.com/microbiomedata/nmdc-schema/blob/270aefeda91443c6cbb6e8bfd340f6ec09e74b8c/src/docs/identifiers.md) and KBase CDM's `CDM:<type>-<uuid4>` (https://github.com/kbase/cdm-schema/blob/c1a59b9607abc85affe3d17f0239ef4e2b819f61/src/linkml/cdm_types.yaml#L26). Benefits: one prefix, and the id says which class it belongs to. Costs: type codes outlive their meaning; nmdc-schema's patterns still accept `omprc` next to the codes that replaced it when `OmicsProcessing` was split (https://github.com/microbiomedata/nmdc-schema/blob/270aefeda91443c6cbb6e8bfd340f6ec09e74b8c/src/schema/nmdc.yaml#L281). A random local part needs a minting service that records what it issued, as the minter in https://github.com/microbiomedata/nmdc-runtime does.
4. One prefix per table, extending option 1 to every table BRIDGE keys itself. Benefit: every table's pattern opens with one prefix. Costs: the number of prefixes and redirects grows with the number of tables, Bioregistry puts more than five prefixes at once through a bulk request that reviewers may send back as individual requests, and Bioregistry says subspacing should not be used unnecessarily (https://github.com/biopragmatics/bioregistry/blob/main/docs/CONTRIBUTING.md).
5. Bioregistry subspaces, such as `bridge.property` and `bridge.unit`. Benefit: this is Bioregistry's own way to partition one resource by entity type. Costs: each subspace is still a registered prefix, and Bioregistry's policy on subspaces is still open (https://github.com/biopragmatics/bioregistry/issues/65).

I chose option 1 for curated terms, for now, because the ids are already in use and were asked for in review. Whether they stay readable is decided again when the terms become table rows (https://github.com/doe-bridge/bridge-central-schema/issues/30). For table rows and features, options 2 to 5 stay open on https://github.com/doe-bridge/bridge-central-schema/issues/28.

### Readable or opaque local parts

1. Readable local parts: `bridge_property:air_temperature`, `bridge_unit:mm2`. Benefits: a reader needs no lookup, and a reviewer can check a mapping row by eye. Costs: the label can be edited while the id stays, but then the id no longer says what the label says. Keeping them matching means deprecating the old id and creating a new one with a replacement, and a vocabulary whose names change often fills up with deprecated ids. UCUM codes hold characters a local part cannot take as they stand: `mg/L` and `[degF]` do not fit the `[a-z0-9_]+` pattern the measurements module uses for `bridge_property:` local parts, and Lesson 5 of McMurry et al. 2017 (https://doi.org/10.1371/journal.pbio.2001414) warns against `/` in a local id, so `bridge_unit:` needs an escaping rule from UCUM code to local part. Lesson 5 also advises that `_` or `:` occur no more than once per identifier, because an id such as `bridge_property:air_temperature` can also be read as `bridge:property_air_temperature`; a snake_case local part under a snake_case prefix breaks that advice.
2. Opaque local parts: a number, with the label and definition in the row. Benefits: a rename is a row edit, no escaping rule is needed, and two terms cannot collide by name. Costs: the meaning is only in the row, numbers are allocated by hand in each pull request, and it reverses posted work.

I chose readable for now (rule 11). The follow-up to https://github.com/doe-bridge/bridge-central-schema/issues/30 decides again, and the question to answer first is how often curated term names will change.

### Rows that arrive without a source id

Measurement rows from a source such as ESS-DIVE, the planned `SourceMapping` rows, and features the converter makes from a GFF file have no id from their source.

1. Keep the source's record id under the source's prefix whenever the source has one. @boehms asked whether the ESS-DIVE `measurement_id` is reflected in the source id (https://github.com/doe-bridge/bridge-central-schema/pull/9#discussion_r4473191401), and @ialarmedalien wrote on a bertron-schema pull request that each data source should use a prefix with its internal ids, with an "unofficial" reference as the fallback (https://github.com/doe-bridge/bertron-schema/pull/3#discussion_r1989866631). Benefit: nothing to mint. Cost: it covers only rows whose source has a record id.
2. Mint a BRIDGE id on first load and record which source fields it came from, so the next load finds the same row. Benefit: the id survives a change in the source fields. Cost: making the id needs no coordination, since a random or sequential number will do, but finding the same row on the next load needs a stored mapping from source fields to id, and that store becomes something BRIDGE has to run.
3. Build the id by hashing source fields, so any loader rebuilds it. Benefit: no state. Costs: RFC 9562 section 6.13 cautions against name-based UUIDs as primary keys because the inputs later change (https://www.rfc-editor.org/rfc/rfc9562#section-6.13), and rows that share every input field collide; at commit e431b4c of https://github.com/doe-bridge/bridge-central-schema/pull/9, `Measurement-005` and `Measurement-006` shared `source_system`, `source_record_id` and `source_field` and differed only in their values.
4. No persistent id: the slot is optional and a row gets none when the source has none. @mslarae13 wrote that making an attribute's id optional "means we don't need fake IDs" (https://github.com/doe-bridge/bertron-schema/issues/37#issuecomment-3140659081), and @dschristianson said ESS-DIVE could assign ids at ETL with "probably no guarantee that they would be stable between versions or persistent outside of the lakehouse" (https://github.com/doe-bridge/bridge-central-schema/pull/9#discussion_r4339981188). Benefit: no invented ids. Cost: a row with no id cannot be referenced from another table or from outside BRIDGE.

Nothing is chosen yet; this is https://github.com/doe-bridge/bridge-central-schema/issues/28. Until then the converter-made feature ids stay `insdc:NC_001422.1:feature-1` and so on.

### Bioregistry expansions everywhere or nmdc-schema's

1. Match nmdc-schema wherever it declares a prefix: `gold` and `emsl.project` expand to `https://bioregistry.io/gold:` and `https://bioregistry.io/emsl.project:` (https://github.com/microbiomedata/nmdc-schema/blob/270aefeda91443c6cbb6e8bfd340f6ec09e74b8c/src/schema/external_identifiers.yaml#L16). Benefit: a GOLD study in an NMDC record and in a BRIDGE record is the same IRI, so RDF and full-IRI joins match. Costs: two rules instead of one, and the IRIs go through a third-party resolver rather than the source's own.
2. Bioregistry's `uri_format` for every source prefix. Benefit: one rule, and each IRI is the source's own resolver. Cost: GOLD and EMSL project IRIs differ from nmdc-schema's.

I chose option 2 with every difference recorded in the edge-case table, and asked JGI on https://github.com/doe-bridge/bridge-central-schema/issues/15#issuecomment-6690980599 which expansion they want for `gold:`; `gold` keeps the nmdc-schema value until then.

### Asserted element URIs or default_prefix

1. Rely on `default_prefix`, so LinkML derives `bridge_central_schema:Sample` from the class name. Benefit: fewer lines. Costs: the IRI is invisible in the YAML and in a diff, and changing a module's `default_prefix` changes every URI in it with no line of any element changing.
2. Assert `class_uri`, `slot_uri` and `meaning` on every element. Benefits: each IRI shows in review and in generated artifacts, and a test catches an element that lost its URI. Cost: one line per element.

I chose option 2 (https://github.com/doe-bridge/bridge-central-schema/issues/35).

## Key slot naming

1. `id` is used only for a row's own primary key.
2. A foreign key is named for the thing it points to, with no `_id` suffix: `associated_studies`, `collected_at`, `organism`, `sample`, `observed_property`, `feature_of_interest`, `member_of` and `parent`. The exception is a name an outside standard fixes: the SSSOM mapping tables keep `subject_id`, `predicate_id` and `object_id`, so they can be written out as SSSOM files.
3. `_id` marks an identifier from outside, kept as data, with no table here to join to: `attribute_cv_id`, `target_id`, `source_record_id` and `measurement_id`.

The feature model's `contig_id`, `collection_id` and `feature_id` become `id` once https://github.com/doe-bridge/bridge-central-schema/issues/28 settles how a feature gets a CURIE, since `feature_id` today is unique only within one dataset.

## Open questions

1. What is the type slot called? The options are `type` everywhere, which means renaming the feature model's GFF3 `type` slot; another name everywhere; or `type` everywhere except the feature model. Tracked on https://github.com/doe-bridge/bridge-central-schema/issues/35.
2. What does `gold:` expand to: the GOLD resolver, as Bioregistry has it, or `https://bioregistry.io/gold:`, as nmdc-schema has it? Asked of JGI on https://github.com/doe-bridge/bridge-central-schema/issues/15.
3. How does BRIDGE make ids for rows that arrive without one, and for features? The answer settles the converter's `insdc:NC_001422.1:feature-1` ids, how BASALT's `urn:uuid:` ids fit an `id` slot of range `curie`, and when the feature model's three key slots become `id`. Tracked on https://github.com/doe-bridge/bridge-central-schema/issues/28.
4. Do curated terms keep readable local parts or move to opaque ones? Decided in the follow-up to https://github.com/doe-bridge/bridge-central-schema/issues/30, after the group says how often term names will change.
5. Who maintains the w3id registration for `ids/ber-data`? Tracked on https://github.com/doe-bridge/bridge-central-schema/issues/26.
