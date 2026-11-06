"""Gate 2: download ERA5 (ARCO-ERA5 Zarr v3, Google public dataset) column moisture budget fields.

Hourly, 0.25 deg, domain 20W-35E, 35N-72N, one NetCDF per month. Files are never overwritten.
"""
import sys, hashlib, json, datetime as dt, pathlib, numpy as np, xarray as xr
STORE = "gs://gcp-public-data-arco-era5/ar/full_37-1h-0p25deg-chunk-1.zarr-v3"
VARS = ["vertical_integral_of_eastward_water_vapour_flux", "vertical_integral_of_northward_water_vapour_flux",
        "total_column_water_vapour", "evaporation", "total_precipitation"]
LAT = (72, 35); LON = (-20, 35)
OUT = pathlib.Path("data/raw/era5"); LEDGER = pathlib.Path("data/raw/era5/LEDGER.csv")
def main(months):
    ds = xr.open_zarr(STORE, chunks=None, storage_options={"token": "anon"})
    for m in months:
        f = OUT / f"era5_colbudget_{m}.nc"
        if f.exists():
            print("exists, skip", f); continue
        t0 = np.datetime64(f"{m}-01T00"); t1 = (t0.astype("datetime64[M]") + 1).astype("datetime64[h]") - np.timedelta64(1, "h")
        s = ds[VARS].sel(time=slice(t0, t1), latitude=slice(*LAT))
        s = xr.concat([s.sel(longitude=slice(360 + LON[0], 359.75)), s.sel(longitude=slice(0, LON[1]))], "longitude")
        s = s.assign_coords(longitude=((s.longitude + 180) % 360) - 180)
        s = s.load().astype("float32")
        s.attrs.update(source=STORE, retrieved_utc=dt.datetime.utcnow().isoformat(timespec="seconds"),
                       licence="Copernicus licence (ERA5, C3S); ARCO-ERA5 Google public dataset")
        tmp = f.with_suffix(".part"); s.to_netcdf(tmp, encoding={v: {"zlib": True, "complevel": 4} for v in VARS}); tmp.rename(f)
        h = hashlib.sha256(f.read_bytes()).hexdigest()
        new = not LEDGER.exists()
        with open(LEDGER, "a") as fh:
            if new: fh.write("file,source,variables,time_start,time_end,n_times,lat_range,lon_range,retrieved_utc,bytes,sha256,terms\n")
            fh.write(f"{f.name},{STORE},{'|'.join(VARS)},{t0},{t1},{s.sizes['time']},{LAT[1]}..{LAT[0]},{LON[0]}..{LON[1]},"
                     f"{s.attrs['retrieved_utc']},{f.stat().st_size},{h},Copernicus licence\n")
        print(m, s.sizes, f.stat().st_size, h[:12], flush=True)
if __name__ == "__main__":
    main(sys.argv[1:])
