import xarray as xr

ds = xr.open_zarr("outputs/indices.zarr")
t2m = ds["t2m"]
rh = ds["RH90p"]  # if not already loaded, recompute RH first

# WHD: T >= 30°C & RH >= 70%
whd = ((t2m >= 30) & (rh >= 70)).resample(time="1Y").sum(dim="time").rename("WHD")

# RH mean, min, max
rh_mean = rh.resample(time="1Y").mean().rename("RHmean")
rh_max  = rh.resample(time="1Y").max().rename("RHmax")
rh_min  = rh.resample(time="1Y").min().rename("RHmin")

# Save all to zarr
xr.merge([whd, rh_mean, rh_max, rh_min]).to_zarr("outputs/indices.zarr", mode="a")
