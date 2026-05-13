# Keywords

Within EMSO ERIC, the keyword strategy builds on OceanSITES standards and extends them to support multiple controlled vocabularies. Keywords are used to describe the thematic, observational, and technical content of a dataset.

All keywords **must be selected from controlled vocabularies** (no free-text keywords are allowed).

---

## Attributes

Each dataset must define the following global attributes:

| Attribute                  | Description                                                                 |
|----------------------------|-----------------------------------------------------------------------------|
| `keywords`                 | List of keyword labels (`prefLabel`)                                        |
| `keywords_uri`             | List of resolvable URIs identifying each keyword term                       |
| `keywords_type`            | List of free-text keyword categories/types                                  |
| `keywords_vocabulary`      | List of vocabulary names used                                               |
| `keywords_vocabulary_uri`  | List of vocabulary URIs                                                     |

- All attributes are **string lists**
- `keywords`, `keywords_uri`, `keywords_type`, and `keywords_vocabulary` are **comma-separated** lists
- `keywords_vocabulary_uri` is a **space-separated** list
- Values must follow the rules defined below

---

## Allowed vocabularies

Only the following vocabularies are permitted:

| ID         | Name                                      | URI                                                    |
|------------|-------------------------------------------|--------------------------------------------------------|
| GEMET      | GEMET                                     | https://www.eionet.europa.eu/gemet/                    |
| EuroSciVoc | EuroSciVoc                                | https://op.europa.eu/en/web/eu-vocabularies/euroscivoc |
| GCMD       | GCMD Science Keywords                     | https://gcmd.earthdata.nasa.gov/                       |
| OSO        | Observatories of the Seas Ontology        | https://earthportal.eu/ontologies/OSO                  |
| P02        | SeaDataNet Parameter Discovery Vocabulary | https://vocab.nerc.ac.uk/collection/P02/current/       |
| P07        | Climate and Forecast Standard Names       | https://vocab.nerc.ac.uk/collection/P07/current/       |
| L05        | SeaDataNet device categories              | https://vocab.nerc.ac.uk/collection/L05/current/       |
| L06        | SeaVoX Platform Categories                | https://vocab.nerc.ac.uk/collection/L06/current/       |

---

## Usage rules

### 1. Controlled terms only
- Every keyword **must be a `prefLabel`** from one of the allowed vocabularies
- Free-text keywords are **not allowed**

---

### 2. Keyword URI declaration
- Every keyword in `keywords` **must have a corresponding resolvable URI** in `keywords_uri`
- `keywords_uri` must:
  - Contain the **same number of elements** as `keywords`
  - Follow the **same order** as `keywords`
  - Resolve to the exact concept represented by the keyword term in its source vocabulary

---

### 3. Keyword type declaration
- Every keyword in `keywords` may have a corresponding keyword type in `keywords_type`. 
- If `keywords_type` is set, it must:
  - Contain the **same number of elements** as `keywords`
  - Follow the **same order** as `keywords`
- Keyword types are free-text descriptors describing the semantic role of the keyword

Examples include:
- `theme`
- `discipline`
- `parameter`
- `platform`
- `device`
- `site`
- `region`

---

### 4. Vocabulary declaration
- All vocabularies used in `keywords` **must be declared** in:
  - `keywords_vocabulary`: comma separated list of vocabulary names
  - `keywords_vocabulary_uri`: space separated list of vocabulary URIs

---

### 5. Consistency between attributes
- `keywords_vocabulary` and `keywords_vocabulary_uri` must:
  - Have the **same number of elements**
  - Follow the **same order**
  - Match the table of allowed vocabularies

- `keywords`, `keywords_uri`, and `keywords_type` must:
  - Have the **same number of elements**
  - Follow the **same order**

---

### 6. Multiplicity
- Multiple keywords from different vocabularies can be combined
- A dataset typically includes:
  - **Thematic keywords** (e.g., GCMD, GEMET, EuroSciVoc)
  - **Parameter keywords** (e.g., SeaDataNet P02, CF)
  - **Platform/device keywords** (e.g., L22, L05, L06)
  - **EMSO-specific concepts** (OSO)

---

### 7. GCMD Science Keywords exception
- For **GCMD Science Keywords**, the keyword must be expressed as the **full hierarchical path**
- The path must use the `>` separator as defined by GCMD

Example:
> `EARTH SCIENCE > OCEANS > SALINITY/DENSITY > SALINITY`

- Partial labels (e.g., `SALINITY`) are **not allowed**

---

### 8. No explicit mapping required
- The relationship between keywords and vocabularies is **not expressed explicitly**
- `keywords_vocabulary` defines the **set of vocabularies used** in the dataset

---

## Example

This example illustrates how keywords from multiple controlled vocabularies are combined within a single dataset.

Each keyword is expressed using its `prefLabel` as defined in the source vocabulary. The `keywords` attribute groups all selected terms, while `keywords_uri` provides resolvable references to the exact concepts. `keywords_type` describes the semantic role of each keyword. The attributes `keywords_vocabulary` and `keywords_vocabulary_uri` declare the set of vocabularies used in the dataset.

Keywords may cover different aspects of the dataset, including thematic classification (e.g., GCMD, EuroSciVoc, GEMET), observed parameters (e.g., SeaDataNet, CF), platforms and instruments (e.g., SeaVoX, L05), and domain-specific concepts (e.g., OSO).
 

```yaml
  keywords:
    - "Balearic Sea"  # OSO
    - "Electrical conductivity of the water column"  # P02
    - "EARTH SCIENCE > OCEANS > SALINITY/DENSITY > SALINITY"  # GCMD
    - "EARTH SCIENCE > OCEANS > OCEAN TEMPERATURE > WATER TEMPERATURE"  # GCMD
    - "EARTH SCIENCE > OCEANS > OCEAN PRESSURE > WATER PRESSURE"  # GCMD
    - "physical oceanography"  # GEMET
    - "CTD"  # L05
    - "OBSEA"  # OSO
    - "OBSEA seabed station"  # OSO
    - "Salinity of the water column"  # P02
    - "Temperature of the water column"  # P02
    - "mooring"  # L06
    - "sea_water_electrical_conductivity"  # P07
    - "sea_water_practical_salinity"  # P07
    - "sea_water_pressure"  # P07
    - "sea_water_temperature"  # P07    

  keywords_uri:
    - "https://w3id.org/earthsemantics/OSO#Balearic_Sea"
    - "http://vocab.nerc.ac.uk/collection/P02/current/CNDC/"
    - "https://cmr.earthdata.nasa.gov/kms/concept/7e95b5fc-1d58-431a-af36-948b29fa870d"
    - "https://cmr.earthdata.nasa.gov/kms/concept/46206e8c-8def-406f-9e62-da4e74633a58"
    - "https://cmr.earthdata.nasa.gov/kms/concept/dd025312-0d27-44e0-ae05-7cfcc1aa17f0"
    - "http://www.eionet.europa.eu/gemet/concept/6224"
    - "http://vocab.nerc.ac.uk/collection/L05/current/130/"
    - "https://w3id.org/earthsemantics/OSO#OBSEA"
    - "https://w3id.org/earthsemantics/OSO#OBSEA_seabed_station"
    - "http://vocab.nerc.ac.uk/collection/P02/current/PSAL/"
    - "http://vocab.nerc.ac.uk/collection/P02/current/TEMP/"
    - "http://vocab.nerc.ac.uk/collection/L06/current/48/"
    - "http://vocab.nerc.ac.uk/collection/P07/current/CFSN0394/"
    - "http://vocab.nerc.ac.uk/collection/P07/current/IADIHDIJ/"
    - "http://vocab.nerc.ac.uk/collection/P07/current/CFSN0330/"
    - "http://vocab.nerc.ac.uk/collection/P07/current/CFSN0335/"

  keywords_type:
    - "infrastructure"
    - "variable"
    - "discipline"
    - "discipline"
    - "discipline"
    - "discipline"
    - "device"
    - "infrastructure"
    - "infrastructure"
    - "variable"
    - "variable"
    - "platform"
    - "variable"
    - "variable"
    - "variable"
    - "variable"

  keywords_vocabulary:
    - "Observatories of the Seas Ontology"
    - "SeaDataNet Parameter Discovery Vocabulary"
    - "GCMD Science Keywords"
    - "GEMET"
    - "SeaDataNet device categories"
    - "SeaVoX Platform Categories"
    - "Climate and Forecast Standard Names"

  keywords_vocabulary_uri:
    - "https://earthportal.eu/ontologies/OSO"
    - "https://vocab.nerc.ac.uk/collection/P02/current/"
    - "https://gcmd.earthdata.nasa.gov/"
    - "https://www.eionet.europa.eu/gemet/"
    - "https://vocab.nerc.ac.uk/collection/L05/current/"
    - "https://vocab.nerc.ac.uk/collection/L06/current/"
    - "https://vocab.nerc.ac.uk/collection/P07/current/"

```