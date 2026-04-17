# OceanSites codes #

This document contains machine-readable information to assess OceanSites codes based on the document 'OceanSITES Data Format Reference Manual NetCDF Conventions and Reference Tables' Version 1.4 July 16, 2020.

## Variable Names ##
Variable code values (Reference table 6: Identifying data variables)

| Parameter | CF Standard name or suggested Long name                              |
|-----------|----------------------------------------------------------------------|
| AIRT      | air_temperature                                                      | 
| CAPH      | air_pressure                                                         | 
| CDIR      | direction_of_sea_water_velocity                                      | 
| CNDC      | sea_water_electrical_conductivity                                    | 
| CSPD      | sea_water_speed                                                      | 
| DEPTH     | depth                                                                | 
| DEWT      | dew_point_temperature                                                | 
| DOX2      | moles_of_oxygen_per_unit_mass_in_sea_water   was  dissolved_oxygen   | 
| DOXY      | mass_concentration_of_oxygen_in_sea_water      was  dissolved_oxygen | 
| DOXY_TEMP | temperature_of_sensor_for_oxygen_in_sea_water                        | 
| DYNHT     | dynamic_height                                                       | 
| FLU2      | fluorescence                                                         | 
| HCSP      | sea_water_speed                                                      | 
| HEAT      | heat_content                                                         | 
| ISO17     | isotherm_depth                                                       | 
| LW        | surface_downwelling_longwave_flux_in_air                             | 
| OPBS      | optical_backscattering_coefficient                                   | 
| PCO2      | surface_partial_pressure_of_carbon_dioxide_in_air                    | 
| PRES      | sea_water_pressure                                                   | 
| PSAL      | sea_water_practical_salinity                                         | 
| RAIN      | rainfall_rate                                                        | 
| RAIT      | thickness_of_rainfall_amount                                         | 
| RELH      | relative_humidity                                                    | 
| SDFA      | surface_downwelling_shortwave_flux_in_air                            | 
| SRAD      | isotropic_shortwave_radiance_in_air                                  | 
| SW        | surface_downwelling_shortwave_flux_in_air                            | 
| TEMP      | sea_water_temperature                                                | 
| UCUR      | eastward_sea_water_velocity                                          | 
| UWND      | eastward_wind                                                        | 
| VAVH      | sea_surface_wave_significant_height                                  | 
| VAVT      | sea_surface_wave_zero_upcrossing_period                              | 
| VCUR      | northward_sea_water_velocity                                         | 
| VDEN      | sea_surface_wave_variance_spectral_density                           | 
| VDIR      | sea_surface_wave_from_direction                                      | 
| VWND      | northward_wind                                                       | 
| WDIR      | wind_to_direction                                                    | 
| WSPD      | wind_speed                                                           |

### Sensor Mount ###

Sensor Mount values (Reference table 7: Sensor mount characteristics)

| sensor_mount                                 |
|----------------------------------------------|
| mounted_on_fixed_structure                   | 
| mounted_on_surface_buoy                      | 
| mounted_on_mooring_line                      | 
| mounted_on_bottom_lander                     | 
| mounted_on_moored_profiler                   | 
| mounted_on_glider                            | 
| mounted_on_shipborne_fixed                   | 
| mounted_on_shipborne_profiler                | 
| mounted_on_seafloor_structure                | 
| mounted_on_benthic_node                      | 
| mounted_on_benthic_crawler                   | 
| mounted_on_surface_buoy_tether               | 
| mounted_on_seafloor_structure_riser          | 
| mounted_on_fixed_subsurface_vertical_profile |

### Sensor Orientation ###

Sensor Orientation values (Reference table 8: Sensor orientation)

| sensor_orientation | example                                                                     | 
|--------------------|-----------------------------------------------------------------------------|
| downward           | ADCP measuring currents from its location to bottom.                        | 
| upward             | ADCP measuring currents towards the surface                                 | 
| horizontal         | Optical sensor looking ‘sideways’ from mooring line or on a ships CTD frame |

### Data Modes ###

Data modes values (reference table 4: data mode).

| Value | Meaning           |
|-------|-------------------|
| R     | Real-time data    |
| P     | Provisional data  |
| D     | Delayed-mode data |
| M     | Mixed             |

### Data Types ###
The data_type global attribute should have one of the valid values listed here (reference table1: data_type).

| Data type                   |
|-----------------------------|
| OceanSITES profile data     |
| OceanSITES time-series data |
| OceanSITES trajectory data  |