#!/usr/bin/env python
"""Compute RH-based climate indices from ERA5 daily stacks."""
import argparse
import xarray as xr
from xclim.indices import relative_humidity
import numpy as np
import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

def main(args):
    # Load ERA5 NetCDF files
    ds = xr.open_mfdataset(args.inputs, chunks={"time": -1})

    # Rename valid_time → time if needed
    if "valid_time" in ds.dims:
        ds = ds.rename({"valid_time": "time"})

    # Convert to °C
    ds["t2m"] = ds["t2m"] - 273.15
    ds["d2m"] = ds["d2m"] - 273.15
    ds["t2m"].attrs["units"] = "degC"
    ds["d2m"].attrs["units"] = "degC"

    # Compute daily relative humidity
    rh = relative_humidity(tas=ds["t2m"], tdps=ds["d2m"])
    rh = rh.rename("rh").astype("float32")

    # Build day-of-year 90th percentile climatology (±2-day rolling)
    base = (
        rh.sel(time=slice(*args.base_period))
          .rolling(time=5, center=True)
          .construct("window")
          .groupby("time.dayofyear")
          .reduce(np.nanpercentile, q=90)
    )

    # RH90p: % of days > climatological threshold
    rh90p = ((rh.groupby("time.dayofyear") > base)
             .resample(time="1Y")
             .mean(dim="time") * 100).rename("RH90p")

    # Save all variables to Zarr
    # Rechunk to ensure Zarr compatibility
    to_save = xr.merge([ds["t2m"], rh, rh90p]).chunk({"time": -1, "latitude": 25, "longitude": 25})
    to_save.to_zarr(args.out, mode="w")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--inputs", nargs="+", required=True,
                   help="List of NetCDF files: t2m.nc d2m.nc etc.")
    p.add_argument("--base-period", nargs=2, default=["1961-01-01", "1990-12-31"])
    p.add_argument("--out", default="outputs/indices.zarr")
    main(p.parse_args())
