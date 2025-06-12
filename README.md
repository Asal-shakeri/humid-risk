## ✅ Updated `README.md` 
### 🚀 Quick Start
#### 1. Clone the repository

```bash
git clone https://github.com/Asal-shakeri/humid-risk.git
cd humid-risk
```

#### 2. Create the conda environment

```bash
conda env create -f environment.yaml
conda activate humid_risk
```

#### 3. Provide input data

Place your ERA5 NetCDF file (e.g., containing `t2m`, `d2m`) in the data/:

```bash
data.nc
```

#### 4. Run the pipeline

```bash
snakemake --cores 4 --use-conda
```

---

## 🧠 Pro Tips

* To rerun everything from scratch:

  ```bash
  rm -rf outputs/
  snakemake --cores 4 --forceall
  ```

* You can adjust configuration in `config.yaml`.

---

## 🗂 File Structure

```
├── Snakefile
├── config.yaml
├── environment.yaml     # <- used to install dependencies
├── scripts/
├── data.nc              # <- you add this
├── outputs/             # <- pipeline writes here
```

---

