"""
Extensive Margin: Durable Asset Count Regressions
PanelOLS with HH + year FEs, SEs clustered at village level.
"""

import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS
import warnings
warnings.filterwarnings("ignore")

# ── Config ────────────────────────────────────────────────────────────────────
ID_VAR      = "hhid"
TIME_VAR    = "wave"
VILLAGE_VAR = "village_id"
SHOCK_VAR   = "drought_lag"
CONTROLS    = ["adulteq", "male_head"]
REGRESSORS  = [SHOCK_VAR] + CONTROLS

ASSETS = {
    "generator":    "n_generator",
    "radio":        "n_radio",
    "television":   "n_television",
    "solar panel":  "n_solar_panel",
    "bicycle":      "n_bicycle",
    "motorbike":    "n_moto",
    "car":          "n_car",
    "boat":         "n_boat",
    "jewelry":      "n_jewelry",
    "mobile phone": "n_mobile_phone",
    "computer":     "n_computer",
}

VAR_DISPLAY = {
    SHOCK_VAR:   r"Drought $(S_{i,t-1})$",
    "adulteq":   "Adult equivalents",
    "male_head": "Male HH head",
}

# ── Load & index ──────────────────────────────────────────────────────────────
df = pd.read_stata("your_data.dta")
df = df.set_index([ID_VAR, TIME_VAR])

# ── Regressions ───────────────────────────────────────────────────────────────
def run(count_var):
    sub = df[[count_var] + REGRESSORS + [VILLAGE_VAR]].dropna()
    fitted = PanelOLS(sub[count_var], sub[REGRESSORS],
                      entity_effects=True, time_effects=True,
                      drop_absorbed=True).fit(
        cov_type="clustered", cluster_entity=False,
        clusters=sub[VILLAGE_VAR])
    return fitted

results = {label: run(var) for label, var in ASSETS.items()}

# ── Format helpers ────────────────────────────────────────────────────────────
def stars(p):
    return "^{***}" if p < 0.001 else "^{**}" if p < 0.01 else "^{*}" if p < 0.05 else ""

def coef_se(res, var):
    if var not in res.params.index:
        return "", ""
    c, s, p = res.params[var], res.std_errors[var], res.pvalues[var]
    return f"{c:.3f}{stars(p)}", f"({s:.3f})"

# ── LaTeX builder ─────────────────────────────────────────────────────────────
NOTES = (
    r"\begin{minipage}{\linewidth}\vspace{4pt}\footnotesize"
    r"\textit{Notes:} Dependent variable is the number of units owned. "
    r"All specifications include household and year fixed effects. "
    r"$S_{i,t-1}$ is the lagged SPI-3 drought index (negative deviations). "
    r"Controls: adult equivalents and male HH head dummy. "
    r"SEs clustered at village level in parentheses. "
    r"$^{*}p<0.05$, $^{**}p<0.01$, $^{***}p<0.001$.\end{minipage}"
)

def make_table(labels, part_idx, total_parts, caption, label):
    n = len(labels)
    rows = [r"\begin{table}[htbp]", r"\centering", r"\small"]
    rows += ([rf"\caption{{{caption}}}", rf"\label{{{label}}}"] if part_idx == 0
             else [r"\caption*{\textit{Table continued}}"])
    rows += [rf"\begin{{tabular}}{{l{'c'*n}}}", r"\toprule"]

    header = r"\textbf{Variable} & " + " & ".join(
        rf"\textbf{{\shortstack{{{l}}}}}" for l in labels) + r" \\"
    rows.append(header)
    rows.append(r"\midrule")

    for var in REGRESSORS:
        coefs, ses = zip(*(coef_se(results[l], var) for l in labels))
        rows.append(VAR_DISPLAY.get(var, var) + " & " + " & ".join(coefs) + r" \\")
        rows.append(" & " + " & ".join(ses) + r" \\")
        rows.append(r"\addlinespace[2pt]")

    rows += [
        r"\midrule",
        r"HH \& Year FE & " + " & ".join(["Yes"] * n) + r" \\",
        r"Observations & " + " & ".join(str(results[l].nobs) for l in labels) + r" \\",
        r"Within $R^2$ & " + " & ".join(f"{results[l].rsquared_within:.3f}" for l in labels) + r" \\",
        r"\bottomrule",
        r"\end{tabular}",
    ]
    if part_idx == total_parts - 1:
        rows.append(NOTES)
    rows.append(r"\end{table}")
    return "\n".join(rows)

# ── Output ────────────────────────────────────────────────────────────────────
all_labels = list(ASSETS.keys())
splits = [all_labels[:6], all_labels[6:]]
latex = "\n\n".join(
    make_table(part, i, len(splits),
               "Extensive Margin: Effect of Drought Shock on Number of Durable Assets Owned",
               "tab:extensive_count")
    for i, part in enumerate(splits)
)

with open("table_extensive_count.tex", "w") as f:
    f.write(latex)

print("LaTeX table saved to table_extensive_count.tex\n" + "="*60)
for label, res in results.items():
    c, s, p = res.params.get(SHOCK_VAR, np.nan), res.std_errors.get(SHOCK_VAR, np.nan), res.pvalues.get(SHOCK_VAR, np.nan)
    print(f"{label:<15}  coef={c:>8.4f}  se={s:>7.4f}  p={p:>6.3f}  N={res.nobs}")
