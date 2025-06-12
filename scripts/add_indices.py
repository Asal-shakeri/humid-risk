import xarray as xr

# Load previously saved variables (e.g. t2m and RH90p)
ds = xr.open_zarr("outputs/indices.zarr")
t2m = ds["t2m"]
rh = ds["RH90p"]  # If not already loaded, recompute RH first

# --- Compute indices ---
# WHD: Warm-Humid Days (T >= 30°C & RH >= 70%)
whd = ((t2m >= 30) & (rh >= 70)).resample(time="1Y").sum(dim="time").rename("WHD")

# RH statistics
rh_mean = rh.resample(time="1Y").mean().rename("RHmean")
rh_max  = rh.resample(time="1Y").max().rename("RHmax")
rh_min  = rh.resample(time="1Y").min().rename("RHmin")

# --- Save to a new group in the same Zarr store ---
xr.merge([whd, rh_mean, rh_max, rh_min]).to_zarr(
    "outputs/indices.zarr", 
    mode="a", 
    group="yearly_stats"
)
