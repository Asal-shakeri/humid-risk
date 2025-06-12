import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import pymannkendall as mk
import os

def mk_trend(da):
    """
    Apply Mann–Kendall trend test and return slope and p-value arrays.
    Skips NaN or short (<5 years) series.
    """
    y = da.groupby("time.year").mean("time")

    # 🔧 FIX: rechunk so 'year' is a single chunk (needed for core dim ops)
    y = y.chunk({"year": -1})

    def safe_test(v):
        v = v[~np.isnan(v)]
        if len(v) < 5:
            return np.nan, np.nan
        try:
            result = mk.original_test(v)
            return result.slope, result.p
        except Exception:
            return np.nan, np.nan

    slope, pval = xr.apply_ufunc(
        lambda v: safe_test(v),
        y,
        input_core_dims=[["year"]],
        output_core_dims=[[], []],
        vectorize=True,
        dask="parallelized",
        dask_gufunc_kwargs={"allow_rechunk": True},  # optional safety
        output_dtypes=[float, float]
    )

    return slope, pval


# === Config ===
DATA_PATH = "outputs/indices.zarr"
OUTPUT_DIR = "outputs/trends/"
SAVE_PLOT = True  # <-- turn to False if you don’t want plot files
VARS = ["RH90p", "WHD", "RHmean", "RHmin", "RHmax", "t2m"]


# === Load Dataset ===
ds = xr.open_zarr(DATA_PATH)

for var in VARS:
    if var not in ds:
        print(f"⚠️ Variable {var} not found. Skipping.")
        continue

    print(f"📈 Processing trend for: {var}")
    slope, pval = mk_trend(ds[var])

    slope = slope.rename(f"{var}_slope")
    pval = pval.rename(f"{var}_pval")

    trend_ds = xr.merge([slope, pval])
    out_path = os.path.join(OUTPUT_DIR, f"{var}.zarr")

    trend_ds.to_zarr(out_path, mode="w")
    print(f"✅ Saved trend data to: {out_path}")

    # Plot and optionally save
    if slope.ndim == 2:
        slope.plot.imshow(cmap="coolwarm", robust=True)
    elif slope.ndim == 1:
        slope.plot.line()
    else:
        print("❌ Unsupported slope dimensionality:", slope.shape)

    plt.title(f"Trend (Sen's slope) of {var}")
    plt.tight_layout()

    if SAVE_PLOT:
        plt.savefig(os.path.join(OUTPUT_DIR, f"{var}_slope.png"), dpi=150)
        print(f"🖼 Saved plot: {var}_slope.png")

    plt.show()
