# FAIR Assessment of the FAIRagro Core Metadata Specification

## Overview

This folder contains the outputs of an automated FAIR assessment conducted on metadata instances developed as part of the FAIRagro Core Metadata Specification (CMS) initiative. The goal is to evaluate how the CMS recommendations — compared to baseline metadata — affect FAIR scores as measured by established automated tools.

Three assessments were performed on two distinct metadata instances of the same underlying dataset, serving as a before/after comparison of the CMS's impact.

---

## Dataset

**Title:** Regionale Stickstoffbilanzen für Deutschland auf Kreisebene aus dem Projekt AGRUM Deutschland für den Durchschnitt der Jahre 2014 – 2016

**DOI:** [10.3220/253-2025-211](https://doi.org/10.3220/253-2025-211)

**Repository:** [OpenAgrar](https://www.openagrar.de/receive/openagrar_mods_00111826)

**Description:** Regional nitrogen area balances for Germany at district level, covering the years 2014–2016, from the AGRUM Deutschland project.

---

## Assessment Files

| File | Metadata Version | Input URL |
|------|-----------------|-----------|
| `rdf_graph_https___doi_org_10_3220_253-2025-211.jsonld` | Original, as published at OpenAgrar | `https://doi.org/10.3220/253-2025-211` |
| `rdf_graph_https___gist_...original_metadata_json.jsonld` | Original, served as raw JSON-LD via GitHub Gist | Gist URL (original) |
| `rdf_graph_https___gist_...restructured_CMS_metadata_json.jsonld` | Enriched, CMS-restructured version served via GitHub Gist | Gist URL (restructured) |

> **Note on the Gist-hosted versions:** Because the FAIR assessment tools require a publicly resolvable URL, both the original and CMS-enriched metadata instances were hosted as raw GitHub Gists. This means FES and FAIR-Checker assess the raw JSON-LD file directly — without the full repository infrastructure (landing page, content negotiation, PID registration) that the DOI-resolved version benefits from. This explains the significantly lower FES and FAIR-Checker scores for the Gist-based assessments compared to the DOI-based one.

---

## Assessment Tools

Three automated FAIR assessment tools were used, each contributing a different set of metrics:

**FAIR-Checker (FC)** — 12 metrics  
A tool developed by France Bioinformatique that checks FAIR compliance by analysing the metadata accessible at a given URL. It focuses on structural and semantic aspects of the metadata.

**FAIR Evaluation Services (FES)** — 22 metrics  
The FAIR Maturity Evaluation Service, which applies the RDA FAIR Data Maturity Model indicators. It evaluates both the metadata and the data object itself against a comprehensive set of maturity indicators.

**F-UJI (FUJI)** — 41 metrics  
An automated REST API service developed within the FAIRsFAIR project. It harvests metadata from multiple sources (landing pages, schema.org, Signposting, DataCite, re3data) and evaluates 16 core FAIRsFAIR metrics, each split into multiple sub-metrics.

All results are combined into a single RDF output per assessment using the **W3C Data Quality Vocabulary (DQV)**, with provenance tracked using **PROV-O** and dataset/distribution descriptions using **DCAT**.

---

## Output Format

Each output file is a **JSON-LD** serialisation of an RDF graph using the following vocabularies:

- [`dqv:`](http://www.w3.org/ns/dqv#) — W3C Data Quality Vocabulary, for quality measurements and metrics
- [`dcat:`](http://www.w3.org/ns/dcat#) — Data Catalog Vocabulary, for dataset and distribution descriptions
- [`dcterms:`](http://purl.org/dc/terms/) — Dublin Core Terms, for titles and formats
- [`prov:`](http://www.w3.org/ns/prov#) — PROV Ontology, for provenance of the assessment activity
- [`fairagro:`](https://fairagro.net/ontology#) — FAIRagro ontology namespace, for metric and agent URIs

Each assessment output contains:
- A `dcat:Dataset` node with a title and a link to its distribution
- A `dcat:Distribution` node with the access URL and a list of all quality measurements via `dqv:hasQualityMeasurement`
- Individual `dqv:QualityMeasurement` nodes, each linking to a metric URI (`dqv:isMeasurementOf`), a score (`dqv:value` as `xsd:float`), and the tool that computed it (`dqv:computedBy`)
- A `prov:Activity` node recording the start and end time of the assessment
- A `dqv:QualityMetadata` node attributing the measurements to the three tools

Scores are normalised floats between `0.0` (failed) and `1.0` (passed), with intermediate values (e.g. `0.25`, `0.5`) indicating partial compliance.

---

## Results Summary

### Assessment 1: Original Metadata via DOI

**Input:** `https://doi.org/10.3220/253-2025-211`  
This assessment reflects the metadata as it is currently published and accessible at OpenAgrar, with full repository infrastructure and PID resolution.

| Tool | Passing Metrics | Total Metrics | Average Score |
|------|----------------|---------------|---------------|
| FAIR-Checker | 10 | 12 | 0.708 |
| FAIR Evaluation Services | 11 | 22 | 0.500 |
| F-UJI | 17 | 41 | 0.311 |

**Key findings:**
- FAIR-Checker scores are high, reflecting that the DOI resolves correctly and the landing page exposes structured metadata.
- FES scores well on identifier and metadata accessibility metrics, but fails on data-level metrics (data knowledge representation, data authentication) and on license detection.
- FUJI scores low overall — it successfully detects the globally unique identifier and persistent identifier, and recognises community metadata standards (schema.org), but fails heavily on content description, access conditions, license information, and data file format metrics. This is because FUJI harvests metadata from the repository landing page and does not find the enriched fields missing from the original OpenAgrar record.

---

### Assessment 2: Original Metadata via GitHub Gist

**Input:** Raw JSON-LD Gist URL (original metadata)  
This assessment uses the same metadata content as Assessment 1, but served as a plain JSON-LD file without repository infrastructure.

| Tool | Passing Metrics | Total Metrics | Average Score |
|------|----------------|---------------|---------------|
| FAIR-Checker | 1 | 12 | 0.083 |
| FAIR Evaluation Services | 3 | 22 | 0.136 |
| F-UJI | 25 | 41 | 0.378 |

**Key findings:**
- FAIR-Checker and FES scores drop dramatically compared to Assessment 1. This is expected: both tools rely heavily on PID infrastructure (DOI resolution, landing page metadata, registry lookups). A raw Gist URL has no DOI, no persistent identifier, and is not registered in any search engine or data catalog. Only the open HTTP resolution protocol passes.
- FUJI scores notably higher than in Assessment 1 despite the same metadata content. This is because FUJI directly reads the JSON-LD served at the URL and can extract the schema.org metadata fields. In Assessment 1, FUJI was harvesting from the OpenAgrar landing page where those fields may not have been exposed in machine-readable form. FUJI correctly identifies license, community metadata standard, and content description fields now visible in the raw JSON-LD.
- The Gist URL inherently fails persistent identifier checks across all three tools, which is expected and not a reflection of the metadata quality itself.

---

### Assessment 3: CMS-Enriched Metadata via GitHub Gist

**Input:** Raw JSON-LD Gist URL (restructured CMS metadata)  
This is the primary evaluation target: the manually enriched metadata instance annotated according to FAIRagro Core Metadata Specification recommendations.

| Tool | Passing Metrics | Total Metrics | Average Score |
|------|----------------|---------------|---------------|
| FAIR-Checker | 1 | 12 | 0.083 |
| FAIR Evaluation Services | 3 | 22 | 0.136 |
| F-UJI | 30 | 41 | 0.537 |

**Key findings:**
- FAIR-Checker and FES scores are identical to Assessment 2. These tools are insensitive to the CMS enrichments because their checks depend on external infrastructure (PID resolution, registry registration, search engine indexing) rather than metadata field content.
- FUJI shows a clear improvement: 30/41 metrics passing (up from 25/41) with an average score rising from 0.378 to 0.537. This is directly attributable to the CMS enrichments. Key improvements include:
  - **Access conditions** (all three sub-metrics now pass at 1.0) — due to the addition of `dcterms:accessRights` and `isAccessibleForFree`
  - **Descriptive core metadata** (all three sub-metrics rise from 0.5 to 1.0) — reflecting richer author, affiliation, and keyword metadata
  - **Links to related entities** (both sub-metrics now pass at 1.0) — due to the addition of `includedInDataCatalog` with an identifier
- Metrics that remain failing across all versions regardless of enrichment include persistent identifier metrics (inherent to the Gist URL), data file format metrics (no actual data files accessible), searchability metrics (not indexed in search engines), and standard communication protocol for data.

---

## Comparison: CMS Impact on FUJI Scores

The table below shows FUJI metrics where the CMS enrichment made a difference (comparing Assessment 2 vs Assessment 3):

| Metric | Original (Gist) | CMS-Enriched | Change |
|--------|----------------|--------------|--------|
| FsF-AccessConditionsMetric-1 | 0.0 | 1.0 | +1.0 |
| FsF-AccessConditionsMetric-2 | 0.0 | 1.0 | +1.0 |
| FsF-AccessConditionsMetric-3 | 0.0 | 1.0 | +1.0 |
| FsF-DescriptiveCoreMetadataMetric-1 | 0.5 | 1.0 | +0.5 |
| FsF-DescriptiveCoreMetadataMetric-2 | 0.5 | 1.0 | +0.5 |
| FsF-DescriptiveCoreMetadataMetric-3 | 0.5 | 1.0 | +0.5 |
| FsF-LinksToRelatedEntitiesMetric-1 | 0.0 | 1.0 | +1.0 |
| FsF-LinksToRelatedEntitiesMetric-2 | 0.0 | 1.0 | +1.0 |

All other FUJI metrics were unchanged between the two Gist-based assessments.

---

## Limitations and Caveats

**Gist URL limitations:** GitHub Gist URLs are not persistent identifiers. They are not registered with DataCite, not indexed in re3data, and not discoverable via search engines. Any metric that depends on these external services will fail regardless of how good the metadata content is. This affects FES and FAIR-Checker almost entirely, and several FUJI metrics. Results for these tools should be interpreted as a lower bound specific to the Gist hosting context, not as a reflection of the metadata's intrinsic quality.

**Fictional/inferred metadata:** As documented in the accompanying README, some fields in the CMS-enriched instance (email addresses, ROR IDs, access rights, spatial coverage, version) were inferred or fabricated for evaluation purposes. Scores should be understood as illustrating the *potential* impact of CMS compliance, not the current state of the published dataset.

**Tool sensitivity differences:** The three tools measure different things and are sensitive to different aspects of the metadata ecosystem. FUJI is the most sensitive to metadata field content and benefits most from CMS enrichment. FES and FAIR-Checker are more infrastructure-dependent and require proper PID registration and repository integration to reflect metadata quality improvements.

**Assessment date:** 2026-04-13
