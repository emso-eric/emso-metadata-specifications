# Copernicus variables

| variable name | long_name | CF standard_name | unit | SDN Param | SDN UoM |
| --- | --- | --- | --- | --- | --- |
| TIME | Time | time | days since 1950-01-01T00:00:00Z | - | - |
| LATITUDE | Latitude of each location | latitude | degree_north | - | - |
| LONGITUDE | Longitude of each location | longitude | degree_east | - | - |
| DEPLOY_LATITUDE | Latitude of each deployment | deployment_latitude | degree_north | - | - |
| DEPLOY_LONGITUDE | Longitude of each deployment | deployment_longitude | degree_east | - | - |
| PRECISE_LATITUDE | Latitude of each location | latitude | degree_north | - | - |
| PRECISE_LONGITUDE | Longitude of each location | longitude | degree_east | - | - |
| DEPH | Depth | depth | m | SDN:P01::ADEPZZ01 | SDN:P06::ULAA |
| PRES | Sea pressure | sea_water_pressure | dbar | SDN:P01::PRESPR01 | SDN:P06::UPDB |
| BEAR | Bearing away from instrument | TBD | degree_true | SDN:P01::BEARRFTR | SDN:P06::UABB |
| RNGE | Range away from instrument | TBD | km | SDN:P01::RIFNAX01 | SDN:P06::ULKM |
| FREQ | Central frequency of the band | wave_frequency | s-1 | TBD | SDN:P06::PRSC |
| TEMP | Sea temperature | sea_water_temperature | degrees_C | SDN:P01::TEMPPR01 | SDN:P06::UPAA |
| PSAL | Practical salinity | sea_water_practical_salinity | 0.001 | SDN:P01::PSLTZZ01 | SDN:P06::UUUU |
| CNDC | Electrical conductivity | sea_water_electrical_conductivity | S m-1 | SDN:P01::CNDCZZ01 | SDN:P06::UECA |
| DENS | Sea density (sigma-theta) | sea_water_sigma_theta | kg m-3 | SDN:P01::SIGTEQ01 | SDN:P06::UKMC |
| SIGT | Sea density (sigma-t) | sea_water_sigma_t | kg m-3 | SDN:P01::SIGTEQST | SDN:P06::UKMC |
| SVEL | Sound velocity | speed_of_sound_in_sea_water | m s-1 | SDN:P01::SVELXXXX | SDN:P06::UVAA |
| BATH | Bathymetric depth | sea_floor_depth_below_sea_surface | m | SDN:P01:MBANZZZZ | SDN:P06::ULAA |
| HCSP | Horizontal current speed | sea_water_speed | m s-1 | SDN:P01::LCSAZZ01 | SDN:P06::UVAA |
| HCDT | Current to direction relative true north | direction_of_sea_water_velocity | degree | SDN:P01::LCDAZZ01 | SDN:P06::UABB |
| EWCT | West-east current component | eastward_sea_water_velocity | m s-1 | SDN:P01::LCEWZZ01 | SDN:P06::UVAA |
| NSCT | South-north current component | northward_sea_water_velocity | m s-1 | SDN:P01::LCNSZZ01 | SDN:P06::UVAA |
| VCSP | Bottom-top current component | upward_sea_water_velocity | m s-1 | SDN:P01::LRZAZZZZ | SDN:P06::UVAA |
| RDVA | Radial sea water velocity away from instrument | radial_sea_water_velocity_away_from _instrument | m s-1 | SDN:P01::LCSAWVRD | SDN:P06::UVAA |
| DRVA | Direction of radial vector away from instrument | direction_of_radial_vector_away_from_instrument | degree_true | SDN:P01::LCDAWVRD | SDN:P06::UABB |
| SLEV | Water surface height above a specific datum | water_surface_height_above_reference_datum | m | SDN:P01::ASLVZZ01 | SDN:P06::ULAA |
| SLVR | Non tidal elevation of sea surface height | non_tidal_elevation_of_sea_surface_height | m | SDN:P01::ASLVR101 | SDN:P06::ULAA |
| TIDE | Tidal sea surface height above a specific datum | tidal_sea_surface_height_above_reference_datum (1) | m | SDN:P01::ASLVTI01 | SDN:P06::ULAA |
| VGHS | Generic significant wave height (Hs) | sea_surface_wave_significant_height | m | SDN:P01::GTDHZZ01 | SDN:P06::ULAA |
| VHM0 | Spectral significant wave height (Hm0) | sea_surface_wave_significant_height | m | SDN:P01::HMZEZZ01 | SDN:P06::ULAA |
| VAVH | Average height highest 1/3 wave (H1/3) | sea_surface_wave_significant_height | m | SDN:P01::GAVHZZ01 | SDN:P06::ULAA |
| VH110 | Average height highest 1/10 wave (H1/10) | sea_surface_wave_mean_height_of_highest_tenth | m | SDN:P01::GTDTZZ01 | SDN:P06::ULAA |
| VHZA | Average zero crossing wave height (Hzm) | sea_surface_wave_mean_height | m | SDN:P01::HZAVZZ01 | SDN:P06::ULAA |
| VEMH | Estimated maximum wave height | sea_surface_wave_maximum_height | m | SDN:P01::GCMXVS01 | SDN:P06::ULAA |
| VZMX | Maximum zero crossing wave height (Hmax) | sea_surface_wave_maximum_height | m | SDN:P01::GZMXZZ01 | SDN:P06::ULAA |
| VCMX | Maximum crest trough wave height (Hc,max) | sea_surface_wave_maximum_height | m | SDN:P01::GCMXZZ01 | SDN:P06::ULAA |
| VMNL | Depth of the deepest trough | sea_surface_wave_maximum_trough_depth | m | SDN:P01:GMNLZZ01 | SDN:P06::ULAA |
| VMXL | Height of the highest crest | sea_surface_wave_maximum_crest_height | m | SDN:P01::GMXLZZ01 | SDN:P06::ULAA |
| SWHT | Swell height | sea_surface_swell_wave_significant_height | m | SDN:P01::GHSWZZ01 | SDN:P06::ULAA |
| VM01 | Spectral moments (0,1) wave period (Tm01) | sea_surface_wave_mean_period_from_variance_spectral_density_first_frequency_moment | s | SDN:P01::GTZAM1ZZ | SDN:P06::UTBB |
| VTM02 | Spectral moments (0,2) wave period (Tm02) | sea_surface_wave_mean_period_from_variance_spectral_density_second_frequency_moment | s | SDN:P01::GTZAM2ZZ | SDN:P06::UTBB |
| VTM10 | Spectral moments (-1,0) wave period (Tm-10) | sea_surface_wave_mean_period_from_variance_spectral_density_inverse_frequency_moment | s | SDN:P01::GTZAMIZZ | SDN:P06::UTBB |
| VTZA | Average zero crossing wave period (Tz) | sea_surface_wave_mean_period | s | SDN:P01::GTZAZZ01 | SDN:P06::UTBB |
| VGTA | Generic average wave period | sea_surface_wave_mean_period | s | SDN:P01::GTAMZZ01 | SDN:P06::UTBB |
| VTPK | Wave period at spectral peak / peak period (Tp) | sea_surface_wave_period_at_variance_spectral_density_maximum | s | SDN:P01::GTPKZZ01 | SDN:P06::UTBB |
| VAVT | Average period highest 1/3 wave (T1/3) | sea_surface_wave_significant_period | s | SDN:P01::GTZHZZ01 | SDN:P06::UTBB |
| VT110 | Average period highest 1/10 wave (T1/10) | sea_surface_wave_mean_period_of_highest_tenth | s | SDN:P01::GTZHTN01 | SDN:P06::UTBB |
| VTMX | Maximum wave period (Tmax) | sea_surface_wave_maximum_period | s | SDN:P01::GTZMZZ01 | SDN:P06::UTBB |
| VTZM | Period of the highest wave (Thmax) | sea_surface_wave_period_of_highest_wave | s | SDN:P01::GTHMXX01 | SDN:P06::UTBB |
| VMDR | Mean wave direction from (Mdir) | sea_surface_wave_from_direction | degree | SDN:P01::GMWDZZ01 | SDN:P06::UABB |
| VDIR | Wave direction rel. true north | sea_surface_wave_from_direction | degree | SDN:P01::GWDRZZ01 | SDN:P06::UABB |
| VPED | Wave principal direction at spectral peak | sea_surface_wave_from_direction_at_variance_spectral_density_maximum | degree | SDN:P01::GPEDZZ01 | SDN:P06::UABB |
| VEPK | Wave spectrum peak energy (Smax) | sea_surface_wave_energy_at_variance_spectral_density_maximum | m2 s | SDN:P01::GEPKZZ01 | SDN:P06::UMHZ |
| VST1 | Maximum wave steepness | sea_surface_wave_maximum_steepness | 1 | SDN:P01::WVSTZZ01 | SDN:P06::UUUU |
| VPSP | Wave directional spreading at spectral peak | sea_surface_wave_directional_spread_at_variance_spectral_density_maximum | degree | SDN:P01::GSPRZZ01 | SDN:P06::UAAA |
| VSPEC1D | Wave scalar spectral density | sea_surface_wave_variance_spectral_density | m2 s | TBD | SDN:P06::M2SX |
| THETA1 | Mean wave from direction | sea_surface_wave_from_direction | degree | TBD | SDN:P06::UABB |
| STHETA1 | Directional spread around THETA1 | sea_surface_wave_directional_spread | degree | TBD | SDN:P06::UAAA |
| THETA2 | Principal wave from direction | sea_surface_wave_from_direction | degree | TBD | SDN:P06::UABB |
| STHETA2 | Directional spread around THETA2 | sea_surface_wave_directional_spread | degree | TBD | SDN:P06::UAAA |
| DOXY | Dissolved oxygen | mole_concentration_of_dissolved_molecular_oxygen_in_sea_water | mmol m-3 | SDN:P01::DOXYZZXX | SDN:P06::UPOX |
| DOX1 | Dissolved oxygen | volume_fraction_of_oxygen_in_sea_water | ml l-1 | SDN:P01::DOXYZZXX | SDN:P06::UMLL |
| DOX2 | Dissolved oxygen | moles_of_oxygen_per_unit_mass_in_sea_water | µmol kg-1 | SDN:P01::DOXMZZXX | SDN:P06::KGUM |
| OSAT | Oxygen saturation | fractional_saturation_of_oxygen_in_sea_water | % | SDN:P01::OXYSZZ01 | SDN:P06::UPCT |
| TICW | Dissolved inorganic carbon | moles_of_dissolved_inorganic_carbon_per_unit_mass_in_sea_water | µmol kg-1 | TBD | TBD |
| CORW | Dissolved organic carbon | TBD | µmol kg-1 | TBD | TBD |
| PCO2 | CO2 partial pressure | surface_partial_pressure_of_carbon_dioxide_in_sea_water | µatm | SDN:P01::PCO2XXXX | SDN:P06::UATM |
| FCO2 | CO2 fugacity | fugacity_of_carbon_dioxide_in_sea_water | µatm | SDN:P01::FCO2XXXX | SDN:P06::UATM |
| CPHL | Chlorophyll-a | mass_concentration_of_chlorophyll_a_in_sea_water | mg m-3 | SDN:P01::CPHLZZXX | SDN:P06::UMMC |
| CHLT | Total chlorophyll | mass_concentration_of_chlorophyll_in_sea_water | mg m-3 | SDN:P01::CHLTVOLU | SDN:P06::UMMC |
| FLU2 | Chlorophyll-a fluorescence | mass_concentration_of_chlorophyll_a_fluorescence_in_sea_water (1) | mg m-3 | SDN:P01::CPHLPM01 | SDN:P06::UMMC |
| CDOM | Cdom | concentration_of_colored_dissolved_organic_matter_in_sea_water_expressed_as_equivalent_mass_fraction_of_quinine_sulfate_dihydrate | 1e-9 | SDN:P01::FLUOCDOM | SDN:P06::UUUU |
| TUR4 | Turbidity | sea_water_turbidity | 1 | SDN:P01::TURBXXXX | SDN:P06::USTU |
| TSMP | Total suspended matter | mass_concentration_of_suspended_matter_in_sea_water | g m-3 | SDN:P01::TSEDZZZZ | SDN:P06::UMGL |
| NTRA | Nitrate (NO3-N) | mole_concentration_of_nitrate_in_sea_water | mmol m-3 | SDN:P01::NTRAZZXX | SDN:P06::UPOX |
| NTAW | Nitrate (NO3-N) | moles_of_nitrate_per_unit_mass_in_sea_water | µmol kg-1 | SDN:P01::MDMAP005 | SDN:P06::KGUM |
| NTRI | Nitrite (NO2-N) | mole_concentration_of_nitrite_in_sea_water | mmol m-3 | SDN:P01::NTRIZZXX | SDN:P06::UPOX |
| NTIW | Nitrite (NO2-N) | moles_of_nitrite_per_unit_mass_in_sea_water | µmol kg-1 | SDN:P01::MDMAP007 | SDN:P06::KGUM |
| NTRZ | Nitrate + Nitrite | mole_concentration_of_nitrate_and_nitrite_in_sea_water | mmol m-3 | SDN:P01::NTRZZZXX | SDN:P06::UPOX |
| PHOS | Phosphate (PO4-P) | mole_concentration_of_phosphate_in_sea_water | mmol m-3 | SDN:P01::PHOSZZXX | SDN:P06::UPOX |
| PHOW | Phosphate (PO4-P) | moles_of_phosphate_per_unit_mass_in_sea_water | µmol kg-1 | SDN:P01::MDMAP906 | SDN:P06::KGUM |
| SLCA | Silicate (SIO4-SI) | mole_concentration_of_silicate_in_sea_water | mmol m-3 | SDN:P01::SLCAZZXX | SDN:P06::UPOX |
| SLCW | Silicate (SIO4-SI) | moles_of_silicate_per_unit_mass_in_sea_water | µmol kg-1 | SDN:P01::MDMAP012 | SDN:P06::KGUM |
| AMON | Ammonium (NH4-N) | mole_concentration_of_ammonium_in_sea_water | mmol m-3 | SDN:P01::AMONZZXX | SDN:P06::UPOX |
| NGDW | Dissolved nitrogen | TBD | µmol kg-1 | TBD | TBD |
| NODW | Dissolved organic nitrogen | TBD | µmol kg-1 | SDN:P01::MDMAP008 | SDN:P06::KGUM |
| ALKY | Total alkalinity | sea_water_alkalinity_expressed_as_mole_equivalent | mmol m-3 | SDN:P01::ALKYZZXX | SDN:P06::UPOX |
| ALKW | Total alkalinity | sea_water_alkalinity_per_unit_mass (1) | µmol kg-1 | SDN:P01::MDMAP014 | SDN:P06::KGUM |
| PHPH | Ph | sea_water_ph_reported_on_total_scale | 1 | SDN:P01::PHXXZZXX | SDN:P06::UUPH |
| PH25 | Ph at 25 °C and 0 dbar | TBD | 1 | SDN:P01::PHTLSX25 | SDN:P06::UUPH |
| BCCW | Abundance of bacteria | TBD | 10+9 m-3 | SDN:P01::TBCCXXXX | SDN:P06:UCUL |
| WSPD | Horizontal wind speed | wind_speed | m s-1 | SDN:P01::EWSBZZ01 | SDN:P06::UVAA |
| WDIR | Wind from direction relative true north | wind_from_direction | degree | SDN:P01::EWDAZZ01 | SDN:P06::UABB |
| GSPD | Gust wind speed | wind_speed_of_gust | m s-1 | SDN:P01::EGTSZZ01 | SDN:P06::UVAA |
| GDIR | Gust wind from direction relative true north | wind_gust_from_direction | degree | SDN:P01::EGTDZZ01 | SDN:P06::UABB |
| WSPE | West-east wind component | eastward_wind | m s-1 | SDN:P01::ESEWZZXX | SDN:P06::UVAA |
| WSPN | South-north wind component | northward_wind | m s-1 | SDN:P01::ESNSZZXX | SDN:P06::UVAA |
| WSPU | Bottom-top wind component | upward_air_velocity | m s-1 | SDN:P01:ESZAZZ01 | SDN:P06:UVAA |
| WBFO | Beaufort wind force | beaufort_wind_force | 1 | SDN:P01::WMOCWFBF | SDN:P06::UUUU |
| DRYT | Air temperature in dry bulb | air_temperature | degrees_C | SDN:P01::CTMPZZ01 | SDN:P06::UPAA |
| WETT | Air temperature in wet bulb | wet_bulb_temperature | degrees_C | SDN:P01::CWETZZ01 | SDN:P06::UPAA |
| DEWT | Dew point temperature | dew_point_temperature | degrees_C | SDN:P01::CDEWZZ01 | SDN:P06::UPAA |
| RELH | Relative humidity | relative_humidity | % | SDN:P01::CRELZZ01 | SDN:P06::UPCT |
| ATMS | Atmospheric pressure at sea level | air_pressure_at_sea_level | hPa | SDN:P01::CAPAZZ01 | SDN:P06::UPBB |
| ATMP | Atmospheric pressure at altitude | air_pressure | hPa | SDN:P01::CAPHZZ01 | SDN:P06::UPBB |
| ATPT | Atmospheric pressure hourly tendency | tendency_of_air_pressure | hPa h-1 | SDN:P01::APRESSTN | SDN:P06::HPAH |
| RVFL | River flow rate | water_volume_transport_into_sea_water_from_rivers | m3 s-1 | SDN:P01::RFDSCH01 | SDN:P06::CMPS |
| PRRT | Hourly precipitation rate (liquid water equivalent) | lwe_precipitation_rate | mm h-1 | SDN:P01::CPRRRG01 | SDN:P06::MMPH |
| PRRD | Daily precipitation rate (liquid water equivalent) | lwe_precipitation_rate | mm d-1 | SDN:P01::CPRRRG01 | SDN:P06::MMPD |
| SINC | Shortwave/solar incoming radiation | surface_downwelling_shortwave_flux_in_air | W m-2 | SDN:P01::CSLRZZXX | SDN:P06::UFAA |
| LINC | Longwave/atmospheric incoming radiation | surface_downwelling_longwave_flux_in_air | W m-2 | SDN:P01::LWRDZZ01 | SDN:P06::UFAA |
| RDIN | Total incoming radiation | surface_downwelling_radiative_flux_in_sea_water | W m-2 | SDN:P01:TLRDZZ01 | SDN:P06::UFAA |
| NRAD | Net total incoming radiation | surface_net_downward_radiative_flux | W m-2 | SDN:P01:NTLRDZ01 | SDN:P06::UFAA |
| LGHT | Immerged incoming photosynthetic active radiation | downwelling_photosynthetic_photon_flux_in_sea_water | µmol m-2 s-1 | SDN:P01::PARERXUD | SDN:P06::UMES |
| LGH4 | Surface incoming photosynthetic active radiation | surface_downwelling_photosynthetic_photon_flux_in_air | µmol m-2 s-1 | SDN:P01::PARERXSD | SDN:P06::UMES |