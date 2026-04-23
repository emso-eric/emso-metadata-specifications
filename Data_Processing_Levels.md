# EMSO Data Processing Levels (Draft)

> ⚠️ **This document describes ongoing work.**  
> Definitions and conventions may evolve as discussions progress within EMSO ERIC.

## Introduction

In ocean observing systems like EMSO, data are collected from a wide range of instruments deployed across different sites and environments. These instruments produce measurements that typically undergo multiple processing steps before they can be reliably used for scientific analysis.

**Processing levels** provide a structured way to describe the overall maturity of a dataset, from acquisition to scientifically validated products. They help to:

- Ensure transparency in data handling  
- Improve interoperability across EMSO nodes and external infrastructures  
- Allow users to assess the fitness-for-purpose of datasets  
- Enable traceability of processing applied to the data  

In addition, **processing steps** provide a detailed trace of the transformations applied to the data.

---

## Definition of L0 (Raw Data)

In EMSO, **L0 data represent raw scientific observations expressed in physical units**.

L0 data **must**:
- Be expressed in physical units (e.g. °C, dbar, PSU)  
- Represent geophysical variables (e.g. temperature, salinity, pressure)

L0 data **must not**:
- Contain engineering-level signals (e.g. ADC counts, voltages, phase increments)

Engineering data are considered **technical data** and are outside the scope of processing levels.

---

## Processing Levels

Processing levels describe the **overall status of the dataset** and are **mutually exclusive**.  
Each dataset must be assigned **only one processing level**.

| Level | Description |
|-------|-------------|
| L0    | Raw data in physical units, provided as measured |
| L1    | Processed data (e.g. calibrated, quality controlled, aggregated) |
| L2    | Scientifically validated data products |

---

## Processing Steps

Processing steps describe **specific transformations applied to the data**.  
Multiple processing steps may be associated with a dataset.

| Step | Level | Description                                                                      |
|------|------|----------------------------------------------------------------------------------|
| L0a  | L0   | Raw instrument data in physical units, provided “as-is”                          |
| L0b  | L0   | Derived raw data (e.g. statistics from acoustic recordings, image-based counts) |
| L1a  | L1   | Calibration applied to sensor data                                               |
| L1b  | L1   | Quality control applied following community best practices                       |
| L1c  | L1   | Temporal aggregation (e.g. averages over fixed time intervals)                   |
| L1d  | L1   | Gap-filling applied (interpolation; filled values should be clearly flagged)     |

### Notes on L0b

L0b refers to data derived directly from raw measurements without calibration or scientific validation, such as 
extracting statistics from acoustic recordings or counting objects from a source image. These products are still 
considered part of the raw data level (L0).

---

## Level 2 (L2)

L2 represents **scientifically validated data products**.

Typical characteristics include:

- Expert validation using domain-specific knowledge  
- Comparison with reference measurements (e.g. CTD casts, bottle samples)  
- Comparison with climatological datasets  
- Correction of sensor drift and offsets  

> ⚠️ L2 definitions are still being refined and are not yet fully standardized across EMSO.

---

## Usage in EMSO Metadata

Processing information is encoded using the following global attributes:

- `data_processing_level`: **a single value** (`L0`, `L1`, or `L2`) describing the overall dataset level  
- `data_processing_steps`: **one or more values** (e.g. `L0a L1a L1b`) describing the applied processing steps  

### Rules

- Each dataset must define **exactly one** `data_processing_level`  
- `data_processing_steps` may contain **multiple entries**  
- All processing steps must be **consistent with the declared processing level**

---

## Example

A temperature dataset may follow this processing chain:

- **L0a**: Raw temperature measurements from the sensor (°C)  
- **L1a**: Calibration applied  
- **L1b**: Quality control flags assigned  
- **L1c**: Hourly averages computed  

This dataset would be classified as:

```yaml
data_processing_level = "L1"
data_processing_steps = "L0a L1a L1b L1c"