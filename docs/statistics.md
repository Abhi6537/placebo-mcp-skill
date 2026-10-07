# Placebo — Statistical Engine Specification

## 1. Multiple Testing Corrections
Placebo implements two classical multiple-testing adjustments:
- **Benjamini-Hochberg (BH) False Discovery Rate (FDR):**
  Controls the expected proportion of false discoveries amongst all rejections:
  $$E\left[\frac{V}{R}\right] \le q$$
  Where $V$ is false discoveries and $R$ is total rejections.
  Sorts p-values $p_{(1)} \le \dots \le p_{(m)}$ and finds the largest $k$ such that:
  $$p_{(k)} \le \frac{k}{m} \alpha$$
- **Conservative Session Multiplicity Bound:**
  When evaluating a single candidate hypothesis mined from a session of $m$ queries/hypotheses:
  $$p_{\text{adj}} = \min(1.0, p_{\text{raw}} \cdot m)$$

## 2. Active Falsification Battery
- **Placebo Dates Test (In-Time Placebo):**
  - Generates $k$ pseudo-intervention dates strictly before the real event.
  - Slices pre-period into fake pre/post intervals.
  - If $\ge 20\%$ of fake dates produce a statistically significant effect, the test fails.
- **Pre-Trend Detection Test:**
  - Evaluates pre-treatment daily metric trend via ordinary least squares (OLS):
    $$Y_t = \beta_0 + \beta_1 t + \epsilon$$
  - Tests $H_0: \beta_1 = 0$. If $p < 0.05$, pre-trend detected $\rightarrow$ Fails.
- **Leave-One-Out (Jackknife Sensitivity):**
  - Re-evaluates effect dropping top candidate entities/whales.
  - If dropping any single entity collapses effect by $> 50\%$ or flips direction $\rightarrow$ Fails (fragile).
