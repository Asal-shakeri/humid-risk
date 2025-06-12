# Snakefile

import os
configfile: "config.yaml"

rule all:
    input:
        config["out_risk_zarr"],
        config["out_risk_png"]

rule compute_indices:
    input:
        nc = config["inputs"]
    output:
        zarr = directory(config["out_indices"])
    params:
        base = (config["base_period"]["start"], config["base_period"]["end"])
    shell:
        """
        python {config[scripts][compute]} \
          --inputs {input.nc} \
          --base-period {params.base[0]} {params.base[1]} \
          --out {output.zarr}
        """

rule add_yearly_stats:
    input:
        zarr = config["out_indices"]  # Zarr directory as input (no directory flag)
    output:
        touchfile = "outputs/yearly_stats.done"
    shell:
        """
        python {config[scripts][add]} \
        && touch {output.touchfile}
        """

rule trend_analysis:
    input:
        zarr   = config["out_indices"],
        yearly = "outputs/yearly_stats.done"
    output:
        # Zarr directories for each variable (from config)
        *[directory(os.path.join(config["out_trends_dir"], f"{var}.zarr")) for var in config["trend_vars"]],
        # PNG plots
        *[os.path.join(config["out_trends_dir"], f"{var}_slope.png") for var in config["trend_vars"]]
    shell:
        """
        python {config[scripts][trends]}
        """
        python {config[scripts][trends]}
        """

rule make_risk_map:
    input:
        # trend Zarr directories
        *[os.path.join(config["out_trends_dir"], f"{var}.zarr") for var in ["RH90p","t2m"]]
    output:
        zarr = directory(config["out_risk_zarr"]),
        png  = config["out_risk_png"]
    params:
        alpha = config["alpha"]
    shell:
        """
        python {config[scripts][risk_map]} --alpha {params.alpha}
        """