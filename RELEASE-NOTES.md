## version 1.0.3 ##
* * changing `doi`, keywords,  `keywords_vocabulary`  and `keywords_vocabulary_uri` from optional to mandatory
* adding `time_end` as an optional coordinate
* adding Data Processing Levels to the specifications
* Changing Copernicus codes from a list in json to a human readable Markdown file

## version 1.0.2 ##
* Renaming `contributors` to `contributor_names` to make it aligned with OceanSITES
* Adding 

## version 1.0.2 ##
* Fixing overwriting issues in resources.json, now CSV files are properly stored and related.json files are correctly produced

## version 1.0.1 ##
* Adding EMSO_Metadata_Specifications.md to the resources.json manifest file

## version 1.0.0 ##
* 100% alignment with Climate and Forecast
* Adding mandatory coordinates time, depth, latitude, longitude, sensor_id, platform_id
* Adding `variable_type` to explicitly declare the role of each variable
* Force the same dataset format regardless of NetCDF or ERDDAP
* Integrating OSO ontology
* Adding `external-resources` to centralise file downloads from the metadata harmonizer
* ... and many more changes