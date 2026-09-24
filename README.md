[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.670238977.svg)](https://zenodo.org/doi/10.5281/zenodo.10669878)

# EMSO ERIC Metadata Specifications #

This repository defines the [EMSO Metadata Specifications](https://github.com/emso-eric/emso-metadata-specifications/blob/main/EMSO_Metadata_Specifications.md) for scientific datasets. 
Its primary goal is to  establish a consistent, interoperable, and machine-actionable metadata framework for all data within the EMSO research infrastructure, ensuring 
long-term usability and broad discoverability. This specification provides the foundational metadata layer for the EMSO data ecosystem, guiding data providers to create 
compliant, high-quality datasets that are FAIR (Findable, Accessible, Interoperable, and Reusable). The latest version of the specifications can be accessed 
[here](https://github.com/emso-eric/emso-metadata-specifications/blob/main/EMSO_Metadata_Specifications.md).

Several example datasets compliant with the latest version of the specifications are available at our [Example ERDDAP](https://netcdf-dev.obsea.es/es/erddap/index.html).

<p align="center">
  <img height="800x" src="https://github.com/emso-eric/emso-metadata-specifications/blob/develop/images/sea-infographic.jpg?raw=true" alt="infographic">
</p>

## Summary ##

### Core Principles:
* **Standards-Based**: Built upon and extends widely adopted community standards, primarily the Climate and Forecast (CF) conventions,  OceanSITES and Copernicus. This ensures compatibility with international data systems and tools.
* **Dual Access**: EMSO data is distributed as self-contained NetCDF files and served dynamically through the ERDDAP servers. This specification ensures metadata consistency across both access methods.
* **Rich Semantics**: Emphasizes the use of controlled vocabularies (e.g., NERC Vocabularies, OSO, EDMO, ROR) and unique identifiers (URIs, URNs) to provide unambiguous, resolvable, and human-readable metadata.

### Key Specifications:
* **Global Attributes**: Defines a comprehensive set of mandatory and optional global attributes for every dataset. These cover critical information such as spatio-temporal coverage, responsible institutions, projects, licensing, and EMSO-specific identifiers (Regional Facility, Site).
* **Variable Typing & Structure**: Introduces a `variable_type` attribute to categorise variables (e.g., coordinate, environmental, biological, quality_control, sensor, platform). Each type has a tailored set of required attributes, ensuring appropriate metadata for different kinds of data.
* **Controlled Vocabularies**: Mandates the use of specific controlled vocabularies for parameters, units, platform types, sensor models, and institutions. Metadata must include the human-readable name, URI, and URN for relevant terms.
* **Compliance & Validation**: The specification is designed to be validatable. Each attribute is associated with a compliance test (e.g., `data_type#str`, `cf_standard_name`, `edmo_code`), enabling automated checks to ensure dataset conformity.

### Benefits:
* **Interoperability**: Enables seamless integration of EMSO data with other marine data repositories and analysis platforms.
* **Discoverability**: Rich, standardised metadata improves search and discovery across scientific disciplines.
* **Traceability**: Clear attribution of data sources, sensors, platforms and funding projects.
* **Automation**: Structured metadata supports automated data ingestion, validation, and processing workflows.


# Licensing and attribution #

The material authored by EMSO ERIC in this repository &mdash; the normative specifications, the OceanSITES and
DataCite reference tables, and the scripts under `external-resources/` &mdash; is released under the
**MIT License** (see [LICENSE](LICENSE)).

`external-resources/` additionally redistributes vocabularies published by third parties (SeaDataNet/NVS, GEMET,
EuroSciVoc, Copernicus, NASA GCMD). **These are not covered by the MIT licence**: they remain under the terms of
their respective publishers, most of them Creative Commons Attribution, which requires credit, a link to the
licence and an indication of any changes made.

That attribution is recorded in three places, all generated from the same source so they cannot drift apart:

* [NOTICE](NOTICE) &mdash; the authoritative, per-resource attribution list, at the repository root.
* [external-resources/README.md](external-resources/README.md) &mdash; the same information as a table.
* `external-resources/vocabularies.json` &mdash; machine-readable `license`, `license_url` and `modifications`
  fields on every resource, so attribution travels with the data to downstream tools.

If you redistribute these files, carry the corresponding entries from `NOTICE` with them.


# Contact info #
* **version**: v1.0.7
* **author**: Enoc Martínez  
* **contributors**: Enoc Martínez 
* **organization**: Universitat Politècnica de Catalunya (UPC)
* **contact**: enoc.martinez@upc.edu
