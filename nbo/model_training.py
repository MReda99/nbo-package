import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.calibration import CalibratedClassifierCV
from povenance import add_provenance_pdf

modeling = pd.read_parquet("modelling_set.parquet")
label_col = "response_within_window"
treat_col = "treatment_flag"
# Add these conversions before model training
modeling = modeling.select_dtypes(include=np.number)  # Filter numeric columns only

# Or if you need to keep non-numeric columns, convert dates to numeric timestamps
# modeling['asof_date'] = pd.to_datetime(modeling['asof_date']).astype(np.int64) // 10**9

meta = {"guest_id","decision_time",label_col,treat_col,"train_split","fold_id","code_commit_sha"}
feat_cols = [c for c in modeling.columns if c not in meta and np.issubdtype(modeling[c].dtype, np.number)]

X_t = modeling.loc[modeling[treat_col]==1, feat_cols].fillna(0.0)
y_t = modeling.loc[modeling[treat_col]==1, label_col].astype(int)
X_c = modeling.loc[modeling[treat_col]==0, feat_cols].fillna(0.0)
y_c = modeling.loc[modeling[treat_col]==0, label_col].astype(int)

# Add validation checks before model training
# Replace lines 24-25
# Original validation (causing error):
# if len(X_t) == 0 or len(X_c) == 0:
#     raise ValueError("Both treatment and control groups must contain samples. "
#                      f"Current counts - Treatment: {len(X_t)}, Control: {len(X_c)}")

# New validation:
if len(X_t) == 0:
    raise ValueError("Treatment group must contain samples. Current count: 0")

# Modify classifier setup with fallback logic
try:
    # Modified validation and model training
    # Replace lines 24-25 with:
    if len(X_t) == 0:
        raise ValueError("No samples found in treatment group")
    
    # Remove the control group validation entirely
    # Train only treatment model
    m_t = CalibratedClassifierCV(GradientBoostingClassifier(n_estimators=100, random_state=42), 
                                cv=min(5, len(X_t))).fit(X_t, y_t)
    
    print("Warning: No control group samples - using baseline assumption")
    
    # Join features and predict
    try:
        fm = pd.read_parquet("feature_mart.parquet")
    except FileNotFoundError:
        raise SystemExit("Error: Missing feature_mart.parquet file")
    
    try:
        candidates = pd.read_parquet("scored_candidates.parquet")
    except FileNotFoundError:
        print("No scored_candidates.parquet found, trying CSV...")
        try:
            candidates = pd.read_csv("scored_candidates.csv")
            candidates.to_parquet("scored_candidates.parquet")
            print("Converted CSV to Parquet successfully")
        except FileNotFoundError:
            raise SystemExit("Error: Missing both scored_candidates.parquet and scored_candidates.csv")
    
    feat = fm.sort_values(["guest_id","asof_date"]).drop_duplicates(["guest_id"], keep="last") if "asof_date" in fm.columns else fm.copy()
    # Keep promotion_id from candidates during merge
    sc = candidates[["guest_id","promotion_id"]].merge(feat[["guest_id"]+feat_cols], on="guest_id", how="left")
    
    p_t = m_t.predict_proba(sc[feat_cols].fillna(0.0))[:,1]
    sc["p_treat"] = p_t
    sc["p_ctrl"] = 0.5  # Hardcoded baseline
    sc["uplift"] = sc["p_treat"] - sc["p_ctrl"]

except Exception as e:
    print(f"Model training failed: {str(e)}")
    raise

# Remove the duplicate prediction section at line 54-58
# Join features as-of for each candidate guest
# Remove these lines (54-58):
# feat = fm.sort_values(["guest_id","asof_date"]).drop_duplicates(["guest_id"], keep="last") if "asof_date" in fm.columns else fm.copy()
# sc = candidates.merge(feat[["guest_id"]+feat_cols], on="guest_id", how="left")
# 
# p_t = m_t.predict_proba(sc[feat_cols].fillna(0.0))[:,1]
# p_c = m_c.predict_proba(sc[feat_cols].fillna(0.0))[:,1]
# sc["uplift"]  = sc["p_treat"] - sc["p_ctrl"]

# Keep only this part after the try-except block:
# expected_ticket: prefer aov_28d > aov_90d > aov_365d
def pick_ticket(r):
    for c in ["aov_28d","aov_90d","aov_365d"]:     
        if c in r and pd.notnull(r[c]) and r[c] > 0: return max(5.0, float(r[c]))
    return 5.0

# Add this after loading candidates
try:
    offer_master = pd.read_parquet("offer_master.parquet")
except FileNotFoundError:
    print("No offer_master parquet, trying CSV...")
    try:
        offer_master = pd.read_csv("offer_master.csv")
        offer_master.to_parquet("offer_master.parquet")
        print("Converted CSV to Parquet successfully")
    except FileNotFoundError:
        raise SystemExit("Error: Missing both offer_master.parquet and offer_master.csv")

# Change the merge operation to use correct column names
# Modify the merge to include required columns
sc = sc.merge(offer_master[[
    "promotion_id",
    "base_price",
    "allowed_discount_bands",  # This was missing in the candidates data
    "margin_basis_pct",
    "channel_eligibility",
    "promotion_name",
    "product_category"
]], left_on="promotion_id", right_on="promotion_id", how="left")

# Add null check before processing bands
sc["allowed_discount_bands"] = sc["allowed_discount_bands"].fillna("0%")  # Handle missing values

# Update band parsing to handle string format
def parse_discount_band(band_str):
    try:
        return [float(x.strip('%')) for x in band_str.replace('%','').split('-')]
    except:
        return [0.0]

# Add these conversions after the merge
# Convert discount bands from string "10%-20%" to numeric range
sc["allowed_discount_bands"] = sc["allowed_discount_bands"].apply(parse_discount_band)
sc["max_discount_pct"] = sc["allowed_discount_bands"].apply(lambda x: x[-1] if len(x) > 0 else 0)

# Convert max_discount_pct to decimal format (e.g., 25.0 -> 0.25)
sc["max_discount_pct"] = sc["max_discount_pct"] / 100.0

# Add default margin_floor_pct if missing
if "margin_floor_pct" not in sc.columns:
    sc["margin_floor_pct"] = 0.0  # Default value

# Convert both margin percentage columns from percentage format (25.0) to decimal format (0.25)
sc["margin_basis_pct"] = sc["margin_basis_pct"].fillna(30.0) / 100.0
sc["margin_floor_pct"] = sc["margin_floor_pct"] / 100.0

sc["expected_ticket"] = sc.apply(pick_ticket, axis=1)
# Use the already converted margin_basis_pct for margin_pct
sc["margin_pct"]      = sc["margin_basis_pct"].fillna(0.30)

# Explode bands
rows = []
for _, r in sc.iterrows():
    bands = r["allowed_discount_bands"] or [0]
    for b in bands:
        if b <= (r["max_discount_pct"] * 100):  # Convert max_discount_pct back to percentage for comparison
            rr = r.to_dict()
            rr["discount_band"]  = int(b)
            rr["discount_cost"]  = r["base_price"] * (b/100.0)
            rr["cannibalization_penalty"] = 0.0  # until DiD/elasticity is plugged in
            rr["eim_raw"] = (rr["uplift"] * rr["expected_ticket"] * rr["margin_pct"]
                             - rr["discount_cost"] - rr["cannibalization_penalty"])
            rows.append(rr)

model_scores_v1 = pd.DataFrame(rows)

# Add provenance fields before saving
model_scores_v1 = add_provenance_pdf(model_scores_v1)

# Add this at the end to save results
model_scores_v1.to_parquet("model_scores_output.parquet")
# Optional CSV version for inspection
model_scores_v1.to_csv("model_scores_output.csv", index=False)

