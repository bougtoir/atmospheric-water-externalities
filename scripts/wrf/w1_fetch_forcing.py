"""Download ERA5 3-hourly pressure-level + surface fields for WRF initial/boundary conditions (ARCO-ERA5).

Usage: python scripts/wrf/w1_fetch_forcing.py START END   (e.g. 2020-06-30T00 2020-07-06T00)
Writes data/raw/era5_wrf/era5_wrf_<START>_<END>.nc (raw snapshot, never overwritten) and appends LEDGER.csv.
"""
import csv, hashlib, os, sys
from datetime import datetime, timezone
import numpy as np, xarray as xr

URL = "gs://gcp-public-data-arco-era5/ar/full_37-1h-0p25deg-chunk-1.zarr-v3"
PL = ["temperature", "u_component_of_wind", "v_component_of_wind", "geopotential", "specific_humidity"]
SFC = ["surface_pressure", "mean_sea_level_pressure", "2m_temperature", "2m_dewpoint_temperature",
       "10m_u_component_of_wind", "10m_v_component_of_wind", "sea_surface_temperature", "skin_temperature",
       "land_sea_mask", "geopotential_at_surface", "sea_ice_cover", "snow_depth"] + \
      [f"soil_temperature_level_{i}" for i in range(1, 5)] + [f"volumetric_soil_water_layer_{i}" for i in range(1, 5)]
LAT, LON = (68, 38), (-18, 34)   # covers the WRF domain plus a margin

s, e = sys.argv[1], sys.argv[2]
out_dir = "data/raw/era5_wrf"; os.makedirs(out_dir, exist_ok=True)
fn = f"{out_dir}/era5_wrf_{s[:13].replace(':', '')}_{e[:13].replace(':', '')}.nc"
if os.path.exists(fn):
    sys.exit(f"exists, not overwritten: {fn}")
ds = xr.open_zarr(URL, chunks=None, storage_options={"token": "anon"})
ds = ds.assign_coords(longitude=(((ds.longitude + 180) % 360) - 180))
t = slice(np.datetime64(s), np.datetime64(e))
times = ds.time.sel(time=t).values[::3]
ilat = np.nonzero(((ds.latitude >= LAT[1]) & (ds.latitude <= LAT[0])).values)[0]
ilon = np.nonzero(((ds.longitude >= LON[0]) & (ds.longitude <= LON[1])).values)[0]
sub = ds[PL + SFC].isel(latitude=ilat, longitude=ilon)
parts = []
for v in PL + SFC:   # one time step at a time keeps memory to a single zarr chunk
    da = xr.concat([sub[v].sel(time=tt).load().astype("float32") for tt in times], "time")
    parts.append(da.sortby("longitude"))
    print(v, parts[-1].shape, flush=True)
out = xr.merge(parts)
out.attrs.update(source=URL, retrieved_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"),
                 note="3-hourly subsample of hourly ERA5; longitudes converted to -180..180")
enc = {v: {"zlib": True, "complevel": 4} for v in out.data_vars}
out.to_netcdf(fn + ".part", encoding=enc); os.replace(fn + ".part", fn)
h = hashlib.sha256(open(fn, "rb").read()).hexdigest()
led = f"{out_dir}/LEDGER.csv"; new = not os.path.exists(led)
with open(led, "a", newline="") as f:
    w = csv.writer(f)
    if new:
        w.writerow(["file", "source", "variables", "time_start", "time_end", "step_h", "lat_range", "lon_range",
                    "retrieved_utc", "bytes", "sha256", "terms"])
    w.writerow([os.path.basename(fn), URL, "|".join(PL + SFC), s, e, 3, f"{LAT[1]}..{LAT[0]}", f"{LON[0]}..{LON[1]}",
                out.attrs["retrieved_utc"], os.path.getsize(fn), h, "Copernicus licence"])
print(fn, os.path.getsize(fn), h)
