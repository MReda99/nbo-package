# Add at the beginning
import pandas as pd
model_scores_v1 = pd.read_parquet("model_scores_output.parquet")

# Enforce floors and caps (caps already enforced via band <= max_discount_pct)
model_scores_v1["eim_banded"] = model_scores_v1["eim_raw"]  # identical unless you add more penalties

# Margin floor: if baseline margin below floor, drop
viol = model_scores_v1["margin_pct"] < model_scores_v1["margin_floor_pct"]
model_scores_v1 = model_scores_v1.loc[~viol]

# Non-negative EIM only
model_scores_v1 = model_scores_v1.loc[model_scores_v1["eim_banded"] > 0.0]

# Rank per guest: highest EIM, then lower discount cost, then higher margin
model_scores_v1 = model_scores_v1.sort_values(
    by=["guest_id","eim_banded","discount_cost","margin_pct"],
    ascending=[True, False, True, False]
)
decision_log_v1 = model_scores_v1.drop_duplicates(subset=["guest_id"], keep="first").copy()

# Rationale and provenance
decision_log_v1["why_selected"]  = "highest EIM; lower discount among ties; higher margin among remaining ties"
decision_log_v1["snapshot_id"]   = "2025_08_22"
decision_log_v1["build_version"] = "2025.08.22"
decision_log_v1["model_version"] = "v1.0"
decision_log_v1["code_commit_sha"]= "manual_notebook_v1"
decision_log_v1 = decision_log_v1.rename(columns={"eim_banded":"eim_final","discount_cost":"discount_cost_banded"})

# Modified final column order with existence check
final_cols = [
    "guest_id","promotion_id","promotion_name",
    "decision_time" if "decision_time" in decision_log_v1.columns else None,
    "p_treat","p_ctrl","uplift","expected_ticket","margin_pct",
    "discount_band","discount_cost_banded","cannibalization_penalty",
    "eim_final","channel_eligibility",
    "snapshot_id","build_version","model_version","code_commit_sha","why_selected"
]
# Filter out None values from the list
final_cols = [c for c in final_cols if c is not None]

decision_log_v1 = decision_log_v1[final_cols]

# Add at the end to save final decisions
decision_log_v1.to_parquet("decision_log_output.parquet", index=False)

