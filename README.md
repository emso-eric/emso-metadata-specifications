[![DOI](https://zenodo.org/badge/670238977.svg)](https://zenodo.org/doi/10.5281/zenodo.10669878)

# EMSO ERIC Metadata Specifications #

This repository defines the [EMSO Metadata Specifications](https://github.com/emso-eric/emso-metadata-specifications/blob/main/EMSO_metadata.md) for scientific datasets. 
Its primary goal is to  establish a consistent, interoperable, and machine-actionable metadata framework for all data within the EMSO research infrastructure, ensuring 
long-term usability and broad discoverability. This specification provides the foundational metadata layer for the EMSO data ecosystem, guiding data providers to create 
compliant, high-quality datasets that are FAIR (Findable, Accessible, Interoperable, and Reusable). The latest version of the specifications can be accessed 
[here](https://github.com/emso-eric/emso-metadata-specifications/blob/main/EMSO_metadata.md).

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


# Contact info #
* **version**: v1.0.0
* **author**: Enoc Martínez  
* **contributors**: Enoc Martínez 
* **organization**: Universitat Politècnica de Catalunya (UPC)
* **contact**: enoc.martinez@upc.edu
