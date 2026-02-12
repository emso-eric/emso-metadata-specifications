# EMSO Metadata Specifications External Resources #
The EMSO metadata specifications builds on top of previous initiatives like SeaDataNet/NVS vocabularies, Copernicus, 
OceanSITES and DataCite metadata kernel among others. In the past we experienced severe issues when relying on 
third-party services to download their source files. Thus, a clean CSV-formatted copy of some of their documents is 
stored here to ensure the functionality of EMSO downstream services. The `update_resources.py` script downloads and
format a new version of the documents.

The following resources can be found inside this folder:

| vocab ID | description                               | URL                                                                       | 
|----------|-------------------------------------------|---------------------------------------------------------------------------|
| EDMO     | European Database of Marine Organizations | [EDMO](https://edmo.seadatanet.org/)                                      |
| ROR      | Research Organization Registry            | [ROR](https://ror.org)                                                    |
| P01      | NVS parameter vocabulary                  | [P01](http://vocab.nerc.ac.uk/collection/P01)                             |
| P02      | NVS parameter codes                       | [P02](http://vocab.nerc.ac.uk/collection/P02)                             |
| P06      | NVS units                                 | [P06](http://vocab.nerc.ac.uk/collection/P06)                             |
| L05      | NVS sensor types                          | [L05](http://vocab.nerc.ac.uk/collection/L05)                             |
| L06      | NVS platform types                        | [L06](http://vocab.nerc.ac.uk/collection/L06)                             |
| L22      | NVS sensor models                         | [L22](http://vocab.nerc.ac.uk/collection/L22)                             |
| L35      | NVS sensor manufacturers                  | [L35](http://vocab.nerc.ac.uk/collection/L35)                             |
| SPDX     | NVS software licenses                     | [github](https://github.com/spdx/license-list-data/blob/main/licenses.md) |


