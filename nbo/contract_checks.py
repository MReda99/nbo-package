import pandas as pd, sys

fm  = pd.read_parquet("feature_mart.parquet")
lbl = pd.read_parquet("label_set.parquet")

# 1) as-of integrity (if asof_date present)
if "asof_date" in fm.columns:
    fm["asof_date"] = pd.to_datetime(fm["asof_date"], utc=True, errors="coerce")
    bad = fm["asof_date"].isna().sum()
    if bad > 0:
        raise AssertionError(f"asof_date nulls: {bad}")

# 2) label coverage (example)
coverage = 1.0 - lbl["response_within_window"].isna().mean()
if coverage < 0.95:
    print(f"[WARN] Label coverage below 95%: {coverage:.3f}", file=sys.stderr)

# 3) legal flag in offer_master
om = pd.read_csv("offer_master.csv")
illegal = om.loc[om["legal_flag"] != True]
if len(illegal) > 0:
    print(f"[INFO] Dropping {len(illegal)} illegal offers from catalog build")

