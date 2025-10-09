import pandas as pd

DECISION_DAY = pd.Timestamp("2025-08-22 00:00:00", tz="UTC")
cutoff = DECISION_DAY - pd.Timedelta(hours=72)

# Load offer catalog data
try:
    offer_catalog_v1 = pd.read_parquet("offer_catalog_v1.parquet")
except FileNotFoundError:
    try:
        offer_catalog_v1 = pd.read_csv("offer_catalog_v1.csv")
    except FileNotFoundError:
        raise SystemExit("Error: Missing both offer_catalog_v1.parquet and offer_catalog_v1.csv")

try:
    touches = pd.read_csv("touch_history.csv")
    touches["touch_ts"] = pd.to_datetime(touches["touch_ts"], utc=True, errors="coerce")
    # Map offer_id to promotion_id for consistency
    touches = touches.rename(columns={"offer_id": "promotion_id"})
    v_fatigue_72h_v1 = (touches
        .loc[(touches["touch_ts"] >= cutoff) & (touches["touch_ts"] < DECISION_DAY), ["guest_id","promotion_id"]]
        .drop_duplicates())
except FileNotFoundError:
    v_fatigue_72h_v1 = pd.DataFrame(columns=["guest_id","promotion_id"])

# guests_today = latest as-of slice
fm = pd.read_parquet("feature_mart.parquet")
if "asof_date" in fm.columns:
    fm["asof_date"] = pd.to_datetime(fm["asof_date"], utc=True, errors="coerce")
    guests_today = (fm.sort_values(["guest_id","asof_date"])
                      .drop_duplicates(["guest_id"], keep="last")[["guest_id"]])
else:
    guests_today = fm[["guest_id"]].drop_duplicates()

active = offer_catalog_v1.loc[
    (pd.to_datetime(offer_catalog_v1["start_date"], utc=True) <= DECISION_DAY) &
    (DECISION_DAY <= pd.to_datetime(offer_catalog_v1["end_date"], utc=True)) &
    (offer_catalog_v1["legal_flag"] == True)
].copy()

candidates = guests_today.assign(key=1).merge(active.assign(key=1), on="key").drop(columns=["key"])
candidates["decision_time"] = DECISION_DAY

# Anti-join fatigue
if not v_fatigue_72h_v1.empty:
    candidates = candidates.merge(v_fatigue_72h_v1.assign(fatigue_hit=1), on=["guest_id","promotion_id"], how="left")
    candidates = candidates[candidates["fatigue_hit"].isna()].drop(columns=["fatigue_hit"])

# Save output
candidates.to_parquet("scored_candidates.parquet", index=False)
candidates.to_csv("scored_candidates.csv", index=False)

print(f"Generated {len(candidates)} candidate offers")
print(f"Columns: {list(candidates.columns)}")

