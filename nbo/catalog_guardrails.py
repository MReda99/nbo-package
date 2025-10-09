import json, pandas as pd

om = pd.read_csv("offer_master.csv")

default_margin = {"Beverage":0.42, "Dessert":0.35, "Salad":0.30, "Sandwich":0.32, "Side":0.40, "Wrap":0.30}
default_bands  = {"Beverage":[0,5,10], "Dessert":[0,5,10,15], "Salad":[0,5,10,15], "Sandwich":[0,5,10,15], "Side":[0,5,10], "Wrap":[0,5,10,15]}
default_floor  = {"Beverage":0.35, "Dessert":0.25, "Salad":0.20, "Sandwich":0.25, "Side":0.30, "Wrap":0.20}
default_cap    = {"Beverage":10, "Dessert":15, "Salad":20, "Sandwich":20, "Side":15, "Wrap":20}

def to_list(v):
    if isinstance(v, str):
        try: return json.loads(v)
        except: return [s.strip() for s in v.split(",")]
    return v if isinstance(v, list) else [v]

offer_catalog_v1 = om.copy()
offer_catalog_v1["channel_eligibility"]   = offer_catalog_v1["channel_eligibility"].apply(to_list)
offer_catalog_v1["margin_basis_pct"]      = offer_catalog_v1["product_category"].map(default_margin).fillna(0.30)
offer_catalog_v1["allowed_discount_bands"]= offer_catalog_v1["product_category"].map(default_bands).apply(lambda x: x if isinstance(x, list) else [0,5])
offer_catalog_v1["margin_floor_pct"]      = offer_catalog_v1["product_category"].map(default_floor).fillna(0.25)
offer_catalog_v1["max_discount_pct"]      = offer_catalog_v1["product_category"].map(default_cap).fillna(15)

offer_catalog_v1.to_csv("offer_catalog_v1.csv", index=False)
offer_catalog_v1.to_parquet("offer_catalog_v1.parquet")