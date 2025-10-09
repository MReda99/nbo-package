# Add at the beginning
import pandas as pd
from povenance import add_provenance_pdf

# ========================= 
# NLP Rationale for Winners 
# ========================= 
def explain_row(r): 
    parts = [] 
    parts.append(f"Guest {r['guest_id']} receives {r['promotion_name']} at {r['discount_band']} percent discount.") 
    parts.append(f"Incremental value is projected positive with EIM {r['eim_final']:.2f}, driven by modeled uplift and expected ticket.") 
    if isinstance(r.get("top_features_shap"), str) and len(r["top_features_shap"]) > 0 and r["top_features_shap"] not in ["NA", ""]: 
        parts.append(f"Top drivers: {r['top_features_shap']}.") 
    else: 
        parts.append("Top drivers unavailable for this row.") 
    parts.append("Offer passes margin floor and discount cap guardrails.") 
    return " ".join(parts)

# Load required data
sc = pd.read_parquet("model_scores_output.parquet")
decision_log_v1 = pd.read_parquet("decision_log_output.parquet")

import numpy as np
try:
    import shap
    # compute SHAP on treated model
    X_for_shap = sc[feat_cols].fillna(0.0).values
    base_est   = getattr(m_t, "base_estimator", None) or getattr(m_t, "estimator", None)
    explainer  = shap.TreeExplainer(base_est) if base_est is not None else shap.Explainer(m_t)
    sv         = explainer(X_for_shap)
    if isinstance(sv.values, list) and len(sv.values)==2:
        vals = sv.values[1]
    else:
        vals = sv.values
    feat_arr = np.array(feat_cols)
    def topk(v, k=5):
        idx = np.argsort(np.abs(v))[-k:]
        return ",".join(feat_arr[idx])
    sc["top_features_shap"] = [topk(v) for v in vals]
except Exception:
    sc["top_features_shap"] = "NA"

# Merge into decision log (same guest-offer; if multiple offers per guest, it keeps the chosen)
# Modified merge with correct columns
keep = sc[["guest_id","promotion_id","top_features_shap"]].drop_duplicates()
# Drop existing top_features_shap columns to avoid conflicts
decision_log_v1 = decision_log_v1.drop(columns=[col for col in decision_log_v1.columns if 'top_features_shap' in col], errors='ignore')
decision_log_v1 = decision_log_v1.merge(
    keep, 
    on=["guest_id","promotion_id"], 
    how="left"
)

# Generate NLP rationale for each row
decision_log_v1["nlp_rationale"] = decision_log_v1.apply(explain_row, axis=1)

# Add provenance fields before saving
decision_log_v1 = add_provenance_pdf(decision_log_v1)

# Add CSV output after the merge
decision_log_v1.to_parquet("decision_log_output.parquet", index=False)
decision_log_v1.to_csv("decision_log_output.csv", index=False)

