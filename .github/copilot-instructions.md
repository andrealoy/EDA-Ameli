**Project Overview**
- **Type**: Notebook-driven exploratory data analysis (EDA) focused on Ameli datasets.
- **Primary entry**: `eda_process.ipynb` — this notebook is the canonical analysis and contains the data-loading, cleaning, helper functions, and plots.
- **Data**: CSVs live under `datasets/` (notably `datasets/effectifs.csv`). The notebook reads that file with a semicolon separator.

**Quick Start (developer)**
- **Open notebook**: run `jupyter lab` or `jupyter notebook` and open `eda_process.ipynb`.
- **Recommended packages**: install the libraries used in the notebook: `pandas`, `numpy`, `seaborn`, `matplotlib`, `jupyterlab` (install with `pip install pandas numpy seaborn matplotlib jupyterlab`).

**Key Code Patterns & Examples**
- **Imports (observed)**: `import pandas as pd`, `import numpy as np`, `import seaborn as sns`, `import matplotlib.pyplot as plt`.
- **Loading data**: `df = pd.read_csv("datasets/effectifs.csv", sep=';')` — note the explicit `sep=';'` for this CSV.
- **Confidentiality handling**: The notebook fills `NaN` values in `Ntop` with `5` to respect confidentiality constraints. Example: `df["Ntop"].fillna(5, inplace=True)` — preserve this logic unless you have a reasoned alternative.
- **Small, reusable functions**: Examples found in the notebook you should reference when extending code:
  - `get_age(x: str) -> int` — parses `libelle_classe_age` like "De 50 à 59 ans" to a numeric minimum age.
  - `somme_ntop_par_annee(df)` and `tracer_evolution_ntop(df)` — compute and plot yearly sums of `Ntop`.

**Conventions and expectations for edits**
- **Notebook-first**: The notebook is the source of truth for analysis. If you refactor logic into scripts, keep the notebook updated (or include a short runnable script alongside the notebook and reference it).
- **Data access**: Use relative paths to `datasets/` to ensure reproducibility across machines (e.g., `datasets/effectifs.csv`).
- **Non-destructive changes**: Avoid modifying original CSVs in-place. If you produce cleaned outputs, place them in a `data/derived/` or similar new folder and add to `.gitignore` if large.

**Debugging & testing notes**
- **Reproduce steps interactively** in the notebook: run the cells in order to verify assumptions about types/NaNs (`df.info()`, `df.head()`, `df.describe()`).
- **Visual checks**: plotting calls use `seaborn` + `matplotlib` and rely on inline rendering in Jupyter — use `plt.show()` as seen in the notebook to force rendering.

**Files to inspect when modifying behavior**
- `eda_process.ipynb` — main analysis, helper functions, loading and plotting.
- `datasets/effectifs.csv` — canonical input; observe `sep=';'` and column names such as `annee`, `Ntop`, `Npop`, `libelle_classe_age`, `patho_niv1` etc.

**Agent-specific guidance**
- **Do not invent missing files**: If you need a `requirements.txt` or scripts, propose them in a PR and include them alongside updated documentation.
- **Preserve confidentiality handling**: The `Ntop` fill value (5) is deliberate. If asked to change it, call out the policy rationale in PR text and provide tests or comparisons.
- **Small, targeted diffs**: Keep changes minimal and notebook-focused. When moving logic into `.py` modules, add a short example cell in the notebook demonstrating how to import and call the new module.

If any of these sections are unclear or you want more detail (for example, a generated `requirements.txt` or a small conversion of notebook logic into a script), tell me which part to expand. 
