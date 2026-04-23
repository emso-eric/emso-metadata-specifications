# Keywords

Within EMSO ERIC, the keyword strategy builds on OceanSITES standards and extends them to support multiple controlled 
vocabularies. Keywords are used to describe the thematic, observational, and technical content of a dataset.

All keywords **must be selected from controlled vocabularies** (no free-text keywords are allowed).

---

## Attributes

Each dataset must define the following global attributes:

| Attribute                  | Description                                                                |
|----------------------------|----------------------------------------------------------------------------|
| `keywords`                 | List of keyword labels (`prefLabel`)                                       |
| `keywords_vocabulary`      | List of vocabulary names used                                              |
| `keywords_vocabulary_uri`  | List of vocabulary URIs                                                    |

- All attributes are **string lists**
- `keywords` and `keywords_vocabulary` are **comma-separated** lists. `keywords_vocabulary_uri` is a **space-separated** list.
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

### 2. Vocabulary declaration
- All vocabularies used in `keywords` **must be declared** in:
  - `keywords_vocabulary`: comma separated list of vocabulary names
  - `keywords_vocabulary_uri`: space separated list of vocabulary URIs

---

### 3. Consistency between attributes
- `keywords_vocabulary` and `keywords_vocabulary_uri` must:
  - Have the **same number of elements**
  - Follow the **same order**
  - Match the table of allowed vocabularies

---

### 4. Multiplicity
- Multiple keywords from different vocabularies can be combined
- A dataset typically includes:
  - **Thematic keywords** (e.g., GCMD, GEMET, EuroSciVoc)
  - **Parameter keywords** (e.g., SeaDataNet P02, CF)
  - **Platform/device keywords** (e.g., SeaVoX, L05)
  - **Domain or site concepts** (e.g., OSO)

---

### 5. GCMD Science Keywords exception
- For **GCMD Science Keywords**, the keyword must be expressed as the **full hierarchical path**
- The path must use the `>` separator as defined by GCMD

Example:
> `EARTH SCIENCE > OCEANS > SALINITY/DENSITY > SALINITY`
- Partial labels (e.g., `SALINITY`) are **not allowed**

- ---

### 6. No explicit mapping required
- The relationship between keywords and vocabularies is **not expressed explicitly**  
- `keywords_vocabulary` defines the **set of vocabularies used** in the dataset  

---

## Example
This example illustrates how keywords from multiple controlled vocabularies are combined within a single dataset. 

Each keyword is expressed using its `prefLabel` as defined in the source vocabulary. The `keywords` attribute groups all selected terms, while `keywords_vocabulary` and `keywords_vocabulary_uri` declare the set of vocabularies used in the dataset.

Keywords may cover different aspects of the dataset, including thematic classification (e.g., GCMD, EuroSciVoc, GEMET), observed parameters (e.g., SeaDataNet, CF), platforms and instruments (e.g., SeaVoX, L05), and domain-specific concepts (e.g., OSO).

```yaml
  keywords:
    # GCMD Science Keywords 
    - "EARTH SCIENCE > OCEANS > SALINITY/DENSITY > SALINITY"
    - "EARTH SCIENCE > OCEANS > OCEAN TEMPERATURE > WATER TEMPERATURE"
    - "EARTH SCIENCE > OCEANS > OCEAN PRESSURE > WATER PRESSURE"
    # EuroSciVoc / GEMET
    - "physical oceanography"
    # OSO Keywords
    - "Balearic Sea"
    - "OBSEA"
    # SeaDataNet Parameter Discovery Vocabulary (P02)
    - "Electrical conductivity of the water column"    
    - "Salinity of the water column"
    - "Temperature of the water column"
    # Climate and Forecast Standard Names (P07)
    - "sea_water_electrical_conductivity"
    - "sea_water_pressure"
    - "sea_water_temperature"
    # SeaDataNet device categories (L05)
    - "CTD"
    # SeaVoX Platform Categories (L06)
    - "mooring"    

  keywords_vocabulary:
    - "Observatories of the Seas Ontology"
    - "SeaDataNet device categories"
    - "GCMD Science Keywords"
    - "SeaDataNet Parameter Discovery Vocabulary"
    - "SeaVoX Platform Categories"
    - "EuroSciVoc"
    - "GEMET"
    - "Climate and Forecast Standard Names"

  keywords_vocabulary_uri:
    - "https://earthportal.eu/ontologies/OSO"
    - "https://vocab.nerc.ac.uk/collection/L05/current/"
    - "https://gcmd.earthdata.nasa.gov/"
    - "https://vocab.nerc.ac.uk/collection/P02/current/"
    - "https://vocab.nerc.ac.uk/collection/L06/current/"
    - "https://op.europa.eu/en/web/eu-vocabularies/euroscivoc"
    - "https://www.eionet.europa.eu/gemet/"
    - "https://vocab.nerc.ac.uk/collection/P07/current/"

````