"""Convert an archived ERA5 forcing NetCDF (w1) to WPS intermediate files (format v5) for metgrid.

Usage: python scripts/wrf/w3_era5_to_intermediate.py ERA5_WRF_NC OUT_DIR
Replaces ungrib (ERA5 here is NetCDF from ARCO, not GRIB). RH is computed from specific humidity with the
Bolton (1980) saturation vapour pressure over water; surface RH from 2-m temperature and dew point.
"""
import os, struct, sys
import numpy as np, xarray as xr

G = 9.80665


def rec(f, b):
    f.write(struct.pack(">i", len(b))); f.write(b); f.write(struct.pack(">i", len(b)))


def write_field(f, hdate, field, units, desc, xlvl, slab, lat0, lon0, dlat, dlon):
    ny, nx = slab.shape
    rec(f, struct.pack(">i", 5))
    rec(f, struct.pack(">24sf32s9s25s46sfiii", hdate.ljust(24).encode(), 0.0, b"ERA5 ARCO".ljust(32),
                       field.ljust(9).encode(), units.ljust(25).encode(), desc.ljust(46).encode(), xlvl, nx, ny, 0))
    rec(f, struct.pack(">8sfffff", b"SWCORNER", lat0, lon0, dlat, dlon, 6367.47))
    rec(f, struct.pack(">i", 1))
    rec(f, np.ascontiguousarray(slab, dtype=">f4").tobytes())


def esat(tk):
    tc = tk - 273.15
    return 611.2 * np.exp(17.67 * tc / (tc + 243.5))


def main():
    src, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    ds = xr.open_dataset(src).sortby("latitude")
    lat, lon = ds.latitude.values, ds.longitude.values
    lat0, lon0, dlat, dlon = float(lat[0]), float(lon[0]), float(lat[1] - lat[0]), float(lon[1] - lon[0])
    W = lambda f, h, n, u, d, l, a: write_field(f, h, n, u, d, l, np.where(np.isfinite(a), a, -1e30), lat0, lon0, dlat, dlon)
    for it, t in enumerate(ds.time.values):
        s = ds.isel(time=it)
        ts = str(t)[:13]
        hdate = ts.replace("T", "_") + ":00:00"
        with open(os.path.join(out, f"ERA5:{ts.replace('T', '_')}"), "wb") as f:
            for lev in s.level.values:
                p = float(lev) * 100.0
                q = s.specific_humidity.sel(level=lev).values
                tt = s.temperature.sel(level=lev).values
                e = q * p / (0.622 + 0.378 * q)
                rh = np.clip(100 * e / esat(tt), 0, 100)
                W(f, hdate, "TT", "K", "Temperature", p, tt)
                W(f, hdate, "UU", "m s-1", "U", p, s.u_component_of_wind.sel(level=lev).values)
                W(f, hdate, "VV", "m s-1", "V", p, s.v_component_of_wind.sel(level=lev).values)
                W(f, hdate, "RH", "%", "Relative humidity", p, rh)
                W(f, hdate, "GHT", "m", "Geopotential height", p, s.geopotential.sel(level=lev).values / G)
            sfc = 200100.0
            t2, d2 = s["2m_temperature"].values, s["2m_dewpoint_temperature"].values
            W(f, hdate, "TT", "K", "2m temperature", sfc, t2)
            W(f, hdate, "RH", "%", "2m relative humidity", sfc, np.clip(100 * esat(d2) / esat(t2), 0, 100))
            W(f, hdate, "UU", "m s-1", "10m U", sfc, s["10m_u_component_of_wind"].values)
            W(f, hdate, "VV", "m s-1", "10m V", sfc, s["10m_v_component_of_wind"].values)
            W(f, hdate, "PSFC", "Pa", "Surface pressure", sfc, s.surface_pressure.values)
            W(f, hdate, "PMSL", "Pa", "Mean sea-level pressure", 201300.0, s.mean_sea_level_pressure.values)
            W(f, hdate, "SKINTEMP", "K", "Skin temperature", sfc, s.skin_temperature.values)
            W(f, hdate, "SST", "K", "Sea surface temperature", sfc, np.where(np.isfinite(s.sea_surface_temperature.values), s.sea_surface_temperature.values, s.skin_temperature.values))
            W(f, hdate, "SEAICE", "fraction", "Sea ice", sfc, np.nan_to_num(s.sea_ice_cover.values))
            W(f, hdate, "LANDSEA", "fraction", "Land-sea mask", sfc, (s.land_sea_mask.values >= 0.5).astype("float32"))
            W(f, hdate, "SOILHGT", "m", "Terrain height", sfc, s.geopotential_at_surface.values / G)
            W(f, hdate, "SNOW", "kg m-2", "Snow water equivalent", sfc, 1000 * s.snow_depth.values)
            for i, nm in enumerate(["000007", "007028", "028100", "100289"], start=1):
                W(f, hdate, f"ST{nm}", "K", "Soil temperature", sfc, s[f"soil_temperature_level_{i}"].values)
                W(f, hdate, f"SM{nm}", "m3 m-3", "Soil moisture", sfc, s[f"volumetric_soil_water_layer_{i}"].values)
        print(hdate, flush=True)


if __name__ == "__main__":
    main()
