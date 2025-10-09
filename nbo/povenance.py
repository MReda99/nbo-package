# ========================= 
# Provenance Helpers 
# ========================= 
from datetime import datetime, timezone 
import pandas as pd 

# Constants that will be used by the provenance function
SNAPSHOT_ID   = "2025_08_22"
BUILD_VERSION = "2025.08.22"
MODEL_VERSION = "v1.0"
CODE_COMMIT_SHA = "unknown"  # This would typically come from git

def add_provenance_pdf(df: pd.DataFrame) -> pd.DataFrame: 
    """Add standard provenance fields to a pandas DataFrame.""" 
    df = df.copy() 
    df["snapshot_id"]   = SNAPSHOT_ID 
    df["build_version"] = BUILD_VERSION 
    df["model_version"] = MODEL_VERSION 
    df["code_commit_sha"] = CODE_COMMIT_SHA 
    df["score_ts"]      = datetime.now(timezone.utc).isoformat() 
    return df

