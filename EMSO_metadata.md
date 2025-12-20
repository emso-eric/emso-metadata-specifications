# ERDDAP Metadata Specification #



## Introduction ##

The EMSO Metadata Specification for ERDDAP defines the essential metadata elements required for datasets to achieve 
compliance within the EMSO research infrastructure. These specifications ensure consistency, interoperability, and 
discoverability of EMSO data, supporting long-term ocean observation and multidisciplinary research. Rooted in widely
accepted community standards, the specification draws upon established conventions including
[Climate and Forecast](https://cfconventions.org/) (CF), 
[OceanSITES](https://repository.oceanbestpractices.org/handle/11329/874.2), and
[SeaDataNet](https://archimer.ifremer.fr/doc/00454/56547/). By adhering to these formats, EMSO ensures that its data
products are readily compatible with international marine data repositories and processing tools.

This document outlines both the general conventions and the specific global attributes necessary for ERDDAP-compliant
datasets in the EMSO framework. The goal is not only to enforce metadata quality and completeness but also to streamline 
validation and integration through defined compliance checks. While preserving flexibility where appropriate, the 
specification emphasizes structured, semantically rich metadata to enhance usability and traceability across scientific 
and operational domains.

EMSO datasets are distributed as self-contained NetCDF files, which include both the data and all required metadata to
ensure clarity, usability, and long-term accessibility. These files are structured to comply with the EMSO Metadata 
Specification, enabling seamless use across various analysis platforms and data systems. In addition to file-based 
access, the same datasets are made available through [EMSO's ERDDAP](https://erddap.emso.eu/erddap), a data server that
exposes the contents of NetCDF files via standardized web services and user-friendly interfaces. This dual approach
allows users to either download complete files or access data subsets and metadata dynamically through ERDDAP’s RESTful 
API.

The structure of EMSO-compliant datasets is depicted in the following picture:

<p align="center">
  <img height="500x" src="https://files.obsea.es/other/specs/summary.jpg" alt="summary">
</p>

### Target audience  ###
This specification is intended for:

* Data providers preparing EMSO datasets for publication in ERDDAP
* Software developers implementing metadata validation or ingestion pipelines
* End users who need to understand the structure and semantics of EMSO datasets

Data providers should focus primarily on the Global Attributes, Coordinate Variables, and the variable type relevant
to their data. End users may consult the variable definitions and controlled vocabularies to interpret datasets.



### General conventions ###

#### Multiple Attributes
The following conventions are applied to all attributes in a dataset:

1. Following [CF conventions](https://cfconventions.org/Data/cf-conventions/cf-conventions-1.12/cf-conventions.html#_attributes) 
for attributes, when multiple values are encoded into a single attribute, they should be encoded in "blank-separated 
lists". Consecutive words in such a list are separated by one or more adjacent spaces.

```yaml
  projects: "EMSODEV EMSO-Link ENVRI-FAIR"
```

In special circumstances a blank-separated list is not suitable, like in a list of author names. These cases, explicitly
described in the specifications, use a comma separated list.

#### Variable naming
In the following tables, when an attribute `$name` is defined, it refers to the variable name inside the dataset rather 
than an attribute of the variable.

#### Names, URIs and URNs
When a link to a controlled vocabulary is included in the metadata, the name and the
uri and the urn are encoded. Although it is a bit verbose, the name provides human-readable information, the URI 
provides a resolvable identifier while the URN in other conventions like [SeaDataNet Data File formats](https://archimer.ifremer.fr/doc/00454/56547/). 

```yaml
  sdn_parameter_name: "Practical salinity of the water body"
  sdn_parameter_uri: "http://vocab.nerc.ac.uk/collection/P01/current/PSLTZZ01/" 
  sdn_parameter_urn: "SDN:P01::PSLTZZ01"
```

Although it might be a bit verbose, this way of encoding metadata is human-readable, resolvable and backwards compatible
with other standards. 



## Global Attributes ##

The attributes listed in the following table are expected to be included as global attributes in all EMSO-compliant
datasets in ERDDAP. The 'global attribute' column is the name of the attribute. The 'compliance test' column refers the
test mechanism used to ensure that the attribute is compliant with the specifications (to see a list of all implemented
tests go to Implemented tests section). The mandatory column.

| Global Attributes            | Description                                                                    | Compliance test          | Required | Multiple | 
|------------------------------|--------------------------------------------------------------------------------|--------------------------|----------|----------|
| date_created                 | Creation date                                                                  | data_type#str            | true     | false    |
| Conventions                  | conventions used in the dataset  (e.g. OceanSITES, ACDD, etc.)                 | data_type#str            | false    | true     |
| institution                  | Creator's organization in free-text                                            | data_type#str            | true     | true     |
| institution_edmo_code        | EDMO code of the creator's organization                                        | edmo_code                | true     | true     |
| institution_edmo_uri         | URI pointing to the EDMO page de of the creator's organization                 | edmo_uri                 | true     | true     |
| institution_ror_uri          | URI pointing to the ROR page de of the creator's organization                  | ror_uri                  | true     | true     |
| geospatial_lat_min           | The southernmost latitude, a value between -90 and 90 degrees                  | coordinate#latitude      | true     | false    |
| geospatial_lat_max           | The northernmost latitude, a value between -90 and 90 degrees                  | coordinate#latitude      | true     | false    |
| geospatial_lon_min           | The westernmost longitude between -180 and 180                                 | coordinate#longitude     | true     | false    |
| geospatial_lon_max           | The easternmost longitude between -180 and 180                                 | coordinate#longitude     | true     | false    |
| geospatial_vertical_min      | Minimum depth of measurements in metres (negative for above sea level)         | coordinate#depth         | true     | false    |
| geospatial_vertical_max      | Maximum depth of measurements in metres (negative for above sea level)         | coordinate#depth         | true     | false    |
| time_coverage_start          | Start date of the data in UTC                                                  | data_type#datetime       | true     | false    |
| time_coverage_end            | End date of the data in UTC                                                    | data_type#datetime       | false    | false    |
| update_interval              | Update interval (following ISO 8601), if not applicable `void`                 | data_type#str            | true     | false    |
| emso_regional_facility_uri   | EMSO Regional Facility URI, required for EMSO data                             | oso_ontology_uri#rf      | true     | false    |
| emso_regional_facility_name  | EMSO Regional Facility name, required for EMSO data                            | oso_ontology_name#rf     | true     | false    |
| emso_site_uri                | site code used, required for EMSO data                                         | oso_ontology_uri#site    | true     | true     |
| emso_site_name               | site code used, required for EMSO data                                         | oso_ontology_name#site   | true     | true     |
| source                       | Platform type name, should be a L06 preferred label (prefLabel)                | sdn_vocab_pref_label#L06 | false    | false    |
| data_type                    | Type of data, in most cases 'OceanSITES data time-series data'                 | oceansites_data_type     | false    | false    |
| network                      | List of the networks                                                           | data_type#str            | true     | true     |
| format_version<sup>3</sup>   | OceanSITES format version                                                      | equals#1.4               | false    | false    |
| data_mode<sup>3</sup>        | Data mode from OceanSITES table 4, possible values are R, P D or M             | oceansites_data_mode     | false    | false    |
| site_code<sup>3</sup>        | OceanSITES site code (only applicable for platforms members of OceanSITES)     | data_type#str            | false    | true     |
| title                        | Free-format text describing the dataset, for use by human readers              | data_type#str            | true     | false    |
| summary                      | Longer free-format text describing the dataset                                 | data_type#str            | true     | false    |
| keywords                     | Please use 'SeaDataNet Parameter Discovery Vocabulary'                         | data_type#str            | false    | true     |
| keywords_vocabulary          | URI of the keywords vocabulary used                                            | data_type#str            | false    | false    |
| projects                     | Acronyms of the projects funding the dataset                                   | data_type#str            | false    | true     |
| project_codes                | List of the project identifiers by ID                                          | data_type#str            | false    | true     |
| principal_investigator       | Name of the principal investigator                                             | data_type#str            | true     | true     |
| principal_investigator_email | email of the principal investigator                                            | email                    | true     | true     |
| contributors<sup>1</sup>     | comma-separated list of author names                                           | data_type#str            | true     | true     |
| contributor_types            | role for each author in the list                                               | contributor_types        | true     | true     |
| doi                          | Digital Object Identifier (DOI) list of the dataset                            | valid_doi                | false    | true     |
| license                      | license name (SPDX short identifier), use of CC-BY-4.0 is strongly recommended | spdx_license_name        | true     | false    |
| license_uri                  | URI pointing to a SPDX license, use of CC-BY-4.0 is strongly recommended       | spdx_license_uri         | true     | false    |
| featureType<sup>2</sup>      | Special field used by CF Discrete Sampling Geometries                          | cf_dsg_types             | true     | false    |

<sup>1</sup> Since the values may contain spaces, use comma a list separator instead of the usual blank space.  
<sup>2</sup> See CF Discrete Sampling Geometries  
<sup>3</sup> Used for compatibility with OceanSITES

# Variables #
This section describes the different types of variables used in EMSO-compliant datasets and how they work together to 
represent observations in a structured, interoperable way. Variables are the core building blocks of the data model and 
include coordinate variables, data variables, quality control variables, and metadata variables. Each variable type has
a clearly defined role: coordinates establish the spatio-temporal and contextual reference frame, data variables contain
observed or derived values, quality control variables describe data reliability, and metadata variables provide sensor
and platform context. The following figure summarizes the different variable types:

<p align="center">
  <img height="350" src="https://files.obsea.es/other/specs/variables.jpg" alt="variables">
</p>

In order to unambiguously classify variables, all variable should include the `variable_type` attribute. The valid 
values of this attribute is can be found in the following table.

| variable type   | Description                                                                                      |
|-----------------|--------------------------------------------------------------------------------------------------| 
| coordinate      | provides spatio-temporal coordinates or information about the sensor/platform                    |
| environmental   | physical oceanography, meteorology, chemistry, biogeochemistry                                   |
| biological      | contains biodiversity information compliant with [Darwin Core](https://dwc.tdwg.org/terms) terms |
| quality_control | variable that provides quality information of another variable                                   |
| sensor          | variable that hosts sensor metadata                                                              |
| platform        | variable that hosts platform metadata                                                            |
| technical       | technical information, such as error code or battery level                                       |

 
 
## Coordinate Variables ##
In the EMSO ERIC metadata specification, coordinate variables are variables whose primary role is to describe the 
spatio-temporal, vertical, and contextual reference frame of the observations contained in a dataset. They do not 
represent measured environmental phenomena themselves, but instead provide the essential axes and identifiers that 
allow data values to be unambiguously located in space, time, and observational context. Coordinate variables follow 
the Climate and Forecast (CF) conventions, meaning they define independent coordinates (e.g. time, depth, latitude, 
longitude) or auxiliary coordinates (e.g. sensor or platform identifiers) that are referenced by data variables through
the coordinates attribute.

From a Climate and Forecast (CF) and operational compatibility perspective, coordinate variables are fundamental to 
machine-readable geophysical datasets. In EMSO datasets, coordinate variables explicitly define the dimensional
structure of observations and establish traceability to the observing platform and sensor. This design supports both 
CF Discrete Sampling Geometries (e.g. fixed time series) and more realistic observational scenarios (e.g. slight 
positional drift or multi-sensor deployments), while preserving full compatibility with CF-compliant tools and 
downstream applications.

The following attributes are mandatory in all coordinate:

| Variable Attributes       | Description                                                         | Compliance test          | Required         | Multiple |
|---------------------------|---------------------------------------------------------------------|--------------------------|------------------|----------|
| $name<sup>4</sup>         | variable name                                                       | is_coordinate            | true             | false    |
| variable_type             | Attribute indicating the variable type                              | equals#coordinate        | true             | false    |
| long_name                 | human-readable label for the variable                               | data_type#str            | true             | false    |
| standard_name<sup>5</sup> | Climate and Forecast (CF) standard name                             | cf_standard_name         | true<sup>2</sup> | false    |
| units<sup>6</sup>         | units symbol, alternative label from P06 definition                 | data_type#str            | true<sup>3</sup> | false    |
| comment                   | free-text to add comments on the variable                           | data_type#str            | false            | false    |
| ancillary_variables       | Related variables, e.g. quality control flags                       | data_type#str            | false            | true     |
| sdn_parameter_name        | variable name (should be the preferred label from the P01 term)     | sdn_vocab_pref_label#P01 | true             | false    |
| sdn_parameter_urn         | variable code (should be an identifier from P01)                    | sdn_vocab_urn#P01        | true             | false    |
| sdn_parameter_uri         | URI for the P01 term                                                | sdn_vocab_uri#P01        | true             | false    |
| sdn_uom_name<sup>7</sup>  | Variable units, should be the preferred label from a P06 definition | data_type#str            | true<sup>3</sup> | false    |
| sdn_uom_urn<sup>7</sup>   | Units identifier from SeaDataNet P06 vocabulary                     | sdn_vocab_urn#P06        | true<sup>3</sup> | false    |
| sdn_uom_uri<sup>7</sup>   | Units URI from SeaDataNet P06 vocabulary                            | sdn_vocab_uri#P06        | false            | false    |
| cf_role<sup>8</sup>       | Special CF attribute                                                | data_type#str            | false            | false    |


<sup>4</sup> `$name` is not an attribute, but the variable name inside the NetCDF file or ERDDAP dataset. It can be safely ignored.
<sup>5</sup> `standard_name` is not required for `sensor_id` since there is not an appropriate term in [CF Standard Name Table](https://cfconventions.org/Data/cf-standard-names/current/build/cf-standard-name-table).  
<sup>6</sup> `units`, `sdn_uom_urn` and `sdn_uom_urn` is mandatory for all coordinate variables except for `sensor_id` and `platform_id`.  
<sup>8</sup> `cf_role` is a special field as stated on [CF conventions](https://cfconventions.org/Data/cf-conventions/cf-conventions-1.12/cf-conventions.html#coordinates-metadata), whose only permitted values are `timeseries_id`, `profile_id`, and `trajectory_id`. Only required for 'platform_id'

### Valid Coordinates ###

Unlike other variables, the coordinate variables are limited to the following table:

| coordinate name   | CF standard_name     | mandatory | data_type                | definition                                           | P01 recommended code                                                  |
|-------------------|----------------------|-----------|--------------------------|------------------------------------------------------|-----------------------------------------------------------------------|
| time              | time                 | true      | seconds since 1970-01-01 | time of measurements                                 | [ELTMEP01](https://vocab.nerc.ac.uk/collection/P01/current/ELTMEP01/) |
| depth             | depth                | true      | float                    | depth of the measurement in metres                   | [ADEPZZ01](https://vocab.nerc.ac.uk/collection/P01/current/ADEPZZ01/) |
| latitude          | latitude             | true      | float                    | latitude of the measurement, nominal value           | [ALATZZ01](https://vocab.nerc.ac.uk/collection/P01/current/ALATZZ01/) |
| longitude         | longitude            | true      | float                    | longitude of the measurement, nominal value          | [ALONZZ01](https://vocab.nerc.ac.uk/collection/P01/current/ALONZZ01/) |
| precise_latitude  | deployment_latitude  | false     | float                    | accurate latitude for the measurement                | [ALATGP01](https://vocab.nerc.ac.uk/collection/P01/current/ALATGP01/) |
| precise_longitude | deployment_longitude | false     | float                    | accurate lontidue of the measurement                 | [ALONGP01](https://vocab.nerc.ac.uk/collection/P01/current/ALONGP01/) |
| sensor_id         | n/a                  | true      | string                   | identifier of the sensor that took the measurement   | [NMSPINST](https://vocab.nerc.ac.uk/collection/P01/current/NMSPINST/) |
| platform_id       | platform_id          | true      | string                   | identifier of the platform that took the measurement | [NMSPPF01](https://vocab.nerc.ac.uk/collection/P01/current/NMSPPF01/) |


Following the CF conventions, an idealized time series is defined at a single, stable point location. However, there are examples of time series, such as cabled
ocean surface mooring measurements, in which the precise position of the observations varies slightly from a nominal fixed point. The precise position can be
recorded using the  `precise_latitude` and `precise_longitude` optional coordinate variables.    

## Data Variables ##
In the EMSO ERIC metadata specification, data variables are variables that contain the actual observed or derived values 
describing environmental, biological, or technical properties of the ocean system. Unlike coordinate variables, data
variables represent measurable phenomena or attributes and are defined as functions of one or more coordinate variables.
Each data variable must explicitly reference its associated coordinate variables through the coordinates attribute, 
thereby establishing its position in space, time, depth, and observational context in a machine-readable and 
standards-compliant manner.

Data variables are classified into `environmental`, `biological` and `technical`. Each data variable type has different
required attributes and may follow different standards. For instance, environmental variable must follow CF conventions 
while biological variables have to be aligned with Darwin Core. Technical variables may be used for those types of data
that do not fall under the scope of CF and DwC standards, such as operational data (battery level, input voltage...) or
even links to data files hydrophone recordings.

### Environmental Variables ###
An `environmental` data variable is a data variable that contains measured or derived values describing the physical, 
chemical, meteorological, or biogeochemical state of the ocean or atmosphere. Environmental data variables represent 
geophysical phenomena (e.g. temperature, salinity, oxygen concentration, currents) and are defined as functions of 
coordinate variables.

Environmental data variables follow the Climate and Forecast (CF) conventions and related community standards to ensure
semantic clarity and interoperability with climate analysis tools, forecast systems, and data services. This includes 
the use of CF standard names, well-defined units, and controlled vocabularies, enabling automated processing, 
comparison, and integration of EMSO observations within operational oceanography and long-term climate applications.
 
Environmental data variable follow the OceanSITES 4-letter naming conventions codes for variables, e.g. "TEMP" for 
temperature. If OceanSITES does not provide a definition for a certain variable, the [NVS P02](http://vocab.nerc.ac.uk/collection/P02) shall be used. 
If the variable is not present in OceanSITES nor in P02, then a code from
[Copernicus Marine in situ TAC - physical parameters list](https://archimer.ifremer.fr/doc/00422/53381/) shall be used. If the variable is not properly described
in any of the previous conventions, then a user-defined 4-letter code may be used. 

The naming convention hierarchy is defined as: 

1. Use OceanSITES naming conventions  
2. If OceanSITES is not applicable, use a term from [NVS P02](http://vocab.nerc.ac.uk/collection/P02).
3. If the parameter is not defined in P02, use the [Copernicus Marine in situ TAC - physical parameters list](https://archimer.ifremer.fr/doc/00422/53381/)
4. If the parameter is not defined in any of the above, use any user-defined 4-letter code. 

The following table defines the attributes expected in `environmental` variables. 

| Variable Attributes | Description                                                                         | Compliance test          | Required | Multiple |
|---------------------|-------------------------------------------------------------------------------------|--------------------------|----------|----------|
| $name               | Variable name is compliant with the naming rules, see 'Variable Codes' section      | check_variable_name      | true     | false    |
| variable_type       | Attribute indicating the variable type                                              | equals#environmental     | true     | false    |
| long_name           | human-readable label for the variable                                               | data_type#str            | true     | false    |
| standard_name       | Climate and Forecast (CF) standard name                                             | cf_standard_name         | true     | false    |
| units               | units symbol, alternative label from P06 definition                                 | sdn_vocab_alt_label#P06  | true     | false    |
| comment             | free-text to add comments on the variable                                           | data_type#str            | false    | false    |
| coordinates         | Variable coordinates, usually `time depth latitude longitude sensor_id platform_id` | data_type#str            | true     | true     |
| ancillary_variables | Related variables such as quality control vars                                      | data_type#str            | True     | true     |
| reference_scale     | reference scale of the variable (e.g. ITS-90 for temperature)                       | data_type#str            | false    | false    |
| sdn_parameter_name  | variable name (should be the preferred label from the P01 term)                     | sdn_vocab_pref_label#P01 | true     | false    |
| sdn_parameter_urn   | variable code (should be an identifier from P01)                                    | sdn_vocab_urn#P01        | true     | false    |
| sdn_parameter_uri   | URI for the P01 term                                                                | sdn_vocab_uri#P01        | false    | false    |
| sdn_uom_name        | Variable units, should be the preferred label from a P06 definition                 | data_type#str            | true     | false    |
| sdn_uom_urn         | Units identifier from SeaDataNet P06 vocabulary                                     | sdn_vocab_urn#P06        | true     | false    |
| sdn_uom_uri         | Units URI from SeaDataNet P06 vocabulary                                            | sdn_vocab_uri#P06        | false    | false    |

 ### Biological Variables ###

A biological data variable is a data variable that contains observed or derived information describing biological, 
ecological, or biodiversity-related aspects of the marine environment. Biological data variables represent attributes 
such as species occurrence, abundance, biomass, life stage, or taxonomic identification and are defined in relation 
to spatio-temporal coordinate variables (e.g. time, depth, latitude, longitude).

Biological data variables follow the [Darwin Core](https://dwc.tdwg.org) (DwC) standard rather than Climate and Forecast
(CF) conventions, using controlled DwC terms and identifiers to ensure semantic consistency and interoperability with 
biodiversity information systems. When combined with CF-compliant coordinate variables, biological data variables 
remain fully compatible with ERDDAP and multidisciplinary workflows, enabling integrated analyses across physical, 
biogeochemical, and biological domains. Any biological variable name must be a term defined in the
[DwC terms](https://dwc.tdwg.org/terms/), following its camelCase nomenclature.

The following table lists the expected attributes from a biological variable:

| Variable Attributes | Description                                                                      | Compliance test   | Required | Multiple |
|---------------------|----------------------------------------------------------------------------------|-------------------|----------|----------|
| $name               | Variable should be a Darwin Core term                                            | dwc_term_name     | true     | false    |
| variable_type       | Attribute indicating the variable type                                           | equals#biological | true     | false    |
| long_name           | human-readable label for the variable                                            | data_type#str     | true     | false    |
| coordinates         | Variable coordinates, e.g. `time depth latitude longitude sensor_id platform_id` | data_type#str     | true     | true     |
| dwc_term_uri        | Link to Darwin Core list of terms                                                | dwc_term_uri      | true     | true     |
| comment             | free-text to add comments                                                        | data_type#str     | false    | false    |


### Technical Variables ###

Technical variables are data variables that contain auxiliary or operational information related to the functioning,
status, or performance of sensors, platforms, or data acquisition systems, rather than describing environmental or 
biological phenomena. Typical examples include battery level, error codes, sampling status, or internal diagnostics.

Technical variables are explicitly designed to accommodate information that does not fit within the environmental or 
biological variable categories, while remaining linked to the same spatio-temporal coordinate framework.

The following table contains technical variable attributes:

| Variable Attributes | Description                                                                      | Compliance test      | Required | Multiple |
|---------------------|----------------------------------------------------------------------------------|----------------------|----------|----------|
| variable_type       | Attribute indicating the variable type                                           | equals#technical     | true     | false    |
| long_name           | human-readable label for the variable                                            | data_type#str        | true     | false    |
| coordinates         | Variable coordinates, e.g. `time depth latitude longitude sensor_id platform_id` | data_type#str        | true     | true     |
| comment             | free-text to add comments                                                        | data_type#str        | false    | false    |
 

## Quality Control Variables ##
Quality control variables are auxiliary variables that provide standardized information on the validity, reliability, 
or processing status of associated data variables. They encode quality assessments using controlled flag values and
meanings, allowing users and automated systems to identify good, suspect, corrected, or missing data.

Quality control variables, providing information about the quality of a related variable. The following attributes are expected.

| QC Attributes  | Description                                                                                                                   | Compliance test        | Required | Multiple |
|----------------|-------------------------------------------------------------------------------------------------------------------------------|------------------------|----------|----------|
| $name          | Variable name is compliant with the naming rules, see 'Variable Codes' section                                                | qc_variable_name       | true     | false    |
| variable_type  | Attribute indicating the variable type                                                                                        | equals#quality_control | true     | false    |
| long_name      | human-readable label, it is suggested to use parameter long_label and add "quality control flags" at the end                  | data_type#str          | true     | false    |
| conventions    | OceanSITES QC Flags                                                                                                           | data_type#str          | true     | false    |
| flag_values    | 0 1 2 3 4 7 8 9                                                                                                               | qc_flag_values         | true     | true     |
| flag_meanings  | unknown good_data probably_good_data potentially_correctable_bad_data bad_data nominal_value interpolated_value missing_value | qc_flag_meanings       | true     | true     |
| comment        | free-text to add comments                                                                                                     | data_type#str          | false    | false    |


## Metadata Variables ##
Metadata variables are auxiliary variables used to store structured information describing the sensors and platforms 
responsible for acquiring the observations in an EMSO dataset. Rather than representing measured values, these variables
provide contextual metadata—such as instrument type, model, manufacturer, deployment configuration, or platform 
identity—that are required to correctly interpret, compare, and reuse the data.

By hosting sensor and platform metadata as variables within the NetCDF file and/or ERDDAP datasets, it is ensured that 
this information remains tightly coupled to the observations. This approach supports traceability, interoperability 
and observational provenance across multidisciplinary and multi-platform datasets.

### Sensor Variables ###

Sensor or instrument metadata is stored in auxiliary variables with the attributes from the following table. Within this
document the word sensor and instrument are used indistinctively to refers to in situ instrumentation deployed at sea. 
Although within this document the preferred word is sensor, to maintain compatibility with other standards, instrument
term might also be used. 

The following attributes are expected in `sensor` variables:

| Variable Attributes                 | Description                                                              | Compliance test               | Required | Multiple |
|-------------------------------------|--------------------------------------------------------------------------|-------------------------------|----------|----------|
| $name                               | Sensor name, should be unique                                            | data_type#str                 | true     | false    |
| variable_type                       | Attribute indicating the variable type                                   | equals#sensor                 | true     | false    |
| long_name                           | human-readable label for the variable                                    | data_type#str                 | true     | false    |
| sensor_id                           | identifier of the sensor used within the `sensor_id` variable            | data_type#str                 | true     | false    |
| sdn_instrument_name<sup>9</sup>     | Sensor model, L22 preferred label                                        | sdn_vocab_pref_label#L22      | true     | false    |
| sdn_instrument_urn<sup>9</sup>      | Sensor model, L22 URN                                                    | sdn_vocab_urn#L22             | true     | false    |
| sdn_instrument_uri<sup>9</sup>      | Sensor model, L22 uri                                                    | sdn_vocab_uri#L22             | true     | false    |
| sensor_SeaVoX_L22_code<sup>10</sup> | Same as `sdn_instrument_urn`                                             | sdn_vocab_urn#L22             | true     | false    |
| sensor_type_name                    | Sensor type,  L05 preferred label                                        | sdn_vocab_pref_label#L05      | true     | false    |
| sensor_type_urn                     | Sensor type L05 URN                                                      | sdn_vocab_urn#L05             | true     | false    |
| sensor_type_uri                     | Sensor type L05 URI                                                      | sdn_vocab_uri#L05             | true     | false    |
| sensor_manufacturer_name            | Sensor model, L35 preferred label                                        | sdn_vocab_pref_label#L35      | true     | false    |
| sensor_manufacturer_uri             | Sensor model (URI from the L35 term)                                     | sdn_vocab_uri#L35             | true     | false    |
| sensor_manufacturer_urn             | Sensor model (should be preferred label from the L35 term)               | sdn_vocab_urn#L35             | true     | false    |
| sensor_serial_number                | Unique identifier for the sensor                                         | data_type#str                 | true     | false    |
| sensor_mount                        | One of the possible sensor mounts from OceanSITES reference table 7      | oceansites_sensor_mount       | true     | false    |
| sensor_orientation                  | One of the possible sensor orientation from OceanSITES reference table 8 | oceansites_sensor_orientation | false    | false    |
| sensor_reference                    | Link to additional information,e.g. sensor datasheet                     | data_type#str                 | false    | false    |
| comment                             | free-text to add additional comments                                     | data_type#str                 | false    | false    |

<sup>9</sup> Used for compatibility with SeaDataNet data file format  
<sup>10</sup> Used for compatibility with OceanSITES format


### Platform Variables ###

Platforms represent the physical structures or systems that host one or more sensors and enable the collection of
observations, such as fixed observatories, moorings, buoys, landers, or mobile platforms. In the EMSO metadata 
specification, platform information is captured through dedicated platform metadata variables that uniquely identify 
the observing platform and describe its type, configuration, and reference properties. Platform variables provide
should be linked to the OSO ontology.  

The following attributes are expected in `platform` variables:

| Variable Attributes | Description                                                       | Compliance test            | Required | Multiple |
|---------------------|-------------------------------------------------------------------|----------------------------|----------|----------|
| $name               | platform name, should be unique                                   | data_type#str              | true     | false    |
| variable_type       | Attribute indicating the variable type                            | equals#platform            | true     | false    |
| long_name           | human-readable label for the variable                             | data_type#str              | true     | false    |
| platform_id         | identifier of the platform used within the `platform_id` variable | data_type#str              | true     | false    |
| platform_type_name  | Platform type L06 preferred label                                 | sdn_vocab_pref_label#L06   | true     | false    |
| platform_type_urn   | Platform type L06 URN                                             | sdn_vocab_urn#L06          | true     | false    |
| platform_type_uri   | Platform type L06 URI                                             | sdn_vocab_uri#L06          | true     | false    |
| emso_platform_name  | Link to the platform entry in OSO ontology                        | oso_ontology_name#platform | true     | false    |
| emso_platform_uri   | Link to the platform entry in OSO ontology                        | oso_ontology_uri#platform  | true     | false    |
| wmo_platform_code   | World Meteorological Organization (WMO) platform code             | data_type#str              | false    | false    |
| platform_reference  | Link to additional information                                    | data_type#uri              | false    | false    |
| comment             | free-text to add additional comments                              | data_type#str              | false    | false    |
| latitude            | nominal latitude (for fixed-point platforms only)                 | data_type#float            | false    | false    |
| longitude           | nominal longitude (for fixed-point platforms only)                | data_type#float            | false    | false    |
| depth               | nominal depth (for fixed-point platforms with one depth level)    | data_type#float            | false    | false    |


## Controlled Vocabularies ##
This metadata standard makes use of several controlled vocabularies from
the [NERC Vocabulary Service](https://vocab.nerc.ac.uk) among others

| vocab ID | description                               | URL                                                                       | 
|----------|-------------------------------------------|---------------------------------------------------------------------------|
| EDMO     | European Database of Marine Organizations | [EDMO](https://edmo.seadatanet.org/)                                      |
| ROR      | Research Organization Registry            | [ROR](https://ror.org)                                                    |
| P01      | parameter vocabulary                      | [P01](http://vocab.nerc.ac.uk/collection/P01)                             |
| P02      | parameter codes                           | [P02](http://vocab.nerc.ac.uk/collection/P02)                             |
| P06      | units                                     | [P06](http://vocab.nerc.ac.uk/collection/P06)                             |
| L05      | sensor types                              | [L05](http://vocab.nerc.ac.uk/collection/L05)                             |
| L06      | platform types                            | [L06](http://vocab.nerc.ac.uk/collection/L06)                             |
| L22      | sensor models                             | [L22](http://vocab.nerc.ac.uk/collection/L22)                             |
| L35      | sensor manufacturers                      | [L35](http://vocab.nerc.ac.uk/collection/L35)                             |
| SPDX     | software licenses                         | [github](https://github.com/spdx/license-list-data/blob/main/licenses.md) |

## Compliance Tests ##

* **data_type#type**: The parameter type is of a certain type. Possible arguments are 'float', 'str', 'int', 'date'
  and 'datetime'
* **edmo_code**: The parameter is an integer number representing an organization listed
  in [EDMO database](https://edmo.seadatanet.org/) (European Directory of Marine Organizations).
* **coordinate#type**: Checks if a coordinate is correct. The 'type' argument must be one of the following: '
  latitude', 'longitude' or 'depths'
* **email**: valid email
* **oceansites_sensor_orientation**: A valid value from sensor_orientation table (OceanSites_codes.md)
* **oceansites_sensor_mount**: A valid value from sensor_orientation table (OceanSites_codes.md)
* **sdn_vocab_urn#vocab_id**: The parameter is a urn in a SeaDataNet vocabulary. Possible values are P01 (parameters),
  P02 (parameter codes), P06 (units), L05 (sensor types), L06 platform types) and L22 (sensor models)   P06 (units),
  L22 (devices), etc.
* **sdn_vocab_preflabel#vocab_id**: Preferred label from a SDN vocabulary
* **sdn_vocab_uri#vocab_id**: Resolvable URI for a SDN vocabulary Term
* **contributor_types**: Complies with the DataCite's metadata kernel contributor roles
* **contributor_names**: Makes sure that for every contributor name there is a contributor type
