# EMSO Data Processing Levels (Draft)

> ⚠️ **This document describes ongoing work.**  
> Definitions and conventions may evolve as discussions progress within EMSO ERIC.

In ocean observing systems like EMSO, data are collected from a wide range of instruments deployed across different sites and environments. These instruments produce raw measurements that often require multiple processing steps before they can be reliably used for scientific analysis.

**Processing levels** provide a structured way to describe how data have been transformed, from raw acquisition to scientifically validated products. They help:

- Ensure transparency in how data are handled  
- Improve interoperability across EMSO nodes and external infrastructures  
- Allow users to assess fitness-for-purpose of datasets  
- Enable traceability of processing steps applied to the data  

Within EMSO, defining common processing levels is essential to harmonize datasets and facilitate their use by the scientific community. This document introduces a preliminary definition of processing levels for EMSO datasets, from raw data (L0) to higher-level products.



## Important Clarification on Raw Data

Within **EMSO ERIC**, *raw instrument data* (L0) are always understood as data expressed in **physical units**, such as:

- Temperature (°C)  
- Pressure (dbar)  
- Salinity, oxygen concentration, etc.  

Engineering-level signals (e.g. raw ADC counts or phase increments) are not considered scientific raw data, but technical data.

## Processing Levels

The table below summarizes the current working definition of processing levels and sublevels.

| Level | Sublevel    | Description                                                                      |
|-------|-------------|----------------------------------------------------------------------------------|
| L0    | L0a         | Raw instrument data in physical units, provided “as-is”                          |
| L0    | L0b         | Derived data (e.g. statistics from acoustic recordings, fish counts from images) |
| L1    | L1a         | Calibration applied to sensor data                                               |
| L1    | L1b         | Quality control applied following community best practices                       |
| L1    | L1c         | Temporal aggregation (e.g. averages over fixed time intervals)                   |
| L1    | L1d         | Gap-filling applied (interpolation; filled values should be clearly flagged)     |

  
EMSO does not consider engineering-level signals as raw data, such as: ADC counts or phase increments. These lower-level signals are assumed to have already been converted by the instrument or its internal processing into physically meaningful quantities. Therefore, L0 data in EMSO always refer to geophysical variables in physical units, not to instrument-native encoding.

## Notes on Higher-Level Processing

Level 2 (L2) is intended to represent **scientifically validated data products**, typically involving:

- Expert validation using domain-specific knowledge  
- Comparison with reference measurements (e.g. CTD casts, bottle samples)  
- Comparison with climatological datasets  
- Correction of sensor drift and offsets  

However, these definitions are still being refined and are **not yet standardized across EMSO**.

