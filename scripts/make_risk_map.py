import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import logging
import argparse
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

# Load RH and T2M trend data
rh_ds = xr.open_zarr("outputs/trends/RH90p.zarr", consolidated=False)
t2m_ds = xr.open_zarr("outputs/trends/t2m.zarr", consolidated=False)

# Merge selected trend variables
ds = xr.merge([
    rh_ds[["RH90p_slope", "RH90p_pval"]],
    t2m_ds[["t2m_slope", "t2m_pval"]],
])

logger.info("✅ Variables loaded:", list(ds.data_vars))

# Thresholds for significance and slope (example logic)
if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--alpha", type=float, default=0.05,
                   help="p-value threshold for significance")
    args = p.parse_args()
    alpha = args.alpha
else:
    alpha = 0.05
rh_sig = (ds["RH90p_pval"] < alpha) & (ds["RH90p_slope"] > 0)
t2m_sig = (ds["t2m_pval"] < alpha) & (ds["t2m_slope"] > 0)

# Risk classification: 0 = none, 1 = RH only, 2 = T only, 3 = both
risk = xr.zeros_like(ds["RH90p_slope"], dtype=int)
risk = risk.where(~rh_sig, 1)
risk = risk.where(~t2m_sig, risk + 2)

# Save as new DataArray
risk_class = risk.rename("humidity_risk")

# ⚠️ Required transpose for GeoTIFF export or imshow
risk_class = risk_class.transpose(..., "latitude", "longitude")

# Optional: Export to NetCDF/GeoTIFF (if rasterio/odc is used)
# risk_class.rio.to_raster("outputs/risk_map.tif")

# Save to Zarr
risk_class.to_dataset().to_zarr("outputs/risk_map.zarr", mode="w")

# Plotting
plt.figure(figsize=(10, 6))
risk_class.isel(window=0).plot.imshow(cmap="viridis", robust=True)
plt.title("Humidity Risk Classification (0:None, 1:RH↑, 2:T↑, 3:Both↑)")
plt.savefig("outputs/humidity_risk_map.png", dpi=300)
plt.show()
