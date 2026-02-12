# OceanSites codes #

This document contains machine-readable information to assess OceanSites codes based on the document 'OceanSITES Data Format Reference Manual NetCDF Conventions and Reference Tables' Version 1.4 July 16, 2020.

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