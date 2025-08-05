import pandas as pd
import os
import math
import json

# ---------- LOAD FUNCTIONS ----------
def load_airports_local(path="data/raw/airports.dat") -> pd.DataFrame:
    cols = [
        "Airport ID", "Name", "City", "Country", "IATA", "ICAO",
        "Latitude", "Longitude", "Altitude", "Timezone", "DST", "Tz database time zone",
        "Type", "Source"
    ]
    df = pd.read_csv(
        path,
        header=None,
        names=cols,
        na_values="\\N",
        dtype={"IATA": str, "ICAO": str},
        keep_default_na=False,
        low_memory=False
    )
    return df

def load_routes_local(path="data/raw/routes.dat") -> pd.DataFrame:
    cols = [
        "Airline", "Airline ID", "Source airport", "Source airport ID",
        "Destination airport", "Destination airport ID", "Codeshare",
        "Stops", "Equipment"
    ]
    df = pd.read_csv(
        path,
        header=None,
        names=cols,
        na_values="\\N",
        dtype={"Source airport": str, "Destination airport": str},
        keep_default_na=False,
        low_memory=False
    )
    return df

# ---------- CLEANING FUNCTIONS ----------
def clean_airports(df: pd.DataFrame) -> pd.DataFrame:
    df["IATA"] = df["IATA"].str.strip().str.upper().replace({"": None})
    df["ICAO"] = df["ICAO"].str.strip().str.upper().replace({"": None})
    df = df[(df["Latitude"].notna()) & (df["Longitude"].notna())]
    df = df[(df["IATA"].notna()) | (df["ICAO"].notna())]
    df["primary_code"] = df["IATA"].fillna(df["ICAO"])
    df = df.groupby("primary_code", as_index=False).first()
    df = df.set_index("primary_code", drop=False)
    return df

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def resolve_route_codes(row, airports_clean: pd.DataFrame, airports_raw: pd.DataFrame, unresolved_log: list):
    row["Source airport"] = str(row["Source airport"]).strip().upper()
    row["Destination airport"] = str(row["Destination airport"]).strip().upper()
    resolved = {"src": None, "dst": None}

    # Resolve source
    if row["Source airport"] in airports_clean.index:
        resolved["src"] = row["Source airport"]
    else:
        try:
            aid = float(row["Source airport ID"])
        except Exception:
            aid = None
        if aid is not None:
            candidate = airports_raw[airports_raw["Airport ID"] == aid]
            if not candidate.empty:
                primary = candidate["IATA"].fillna(candidate["ICAO"]).iloc[0]
                primary = primary.strip().upper() if isinstance(primary, str) else primary
                if primary in airports_clean.index:
                    resolved["src"] = primary

    # Resolve destination
    if row["Destination airport"] in airports_clean.index:
        resolved["dst"] = row["Destination airport"]
    else:
        try:
            did = float(row["Destination airport ID"])
        except Exception:
            did = None
        if did is not None:
            candidate = airports_raw[airports_raw["Airport ID"] == did]
            if not candidate.empty:
                primary = candidate["IATA"].fillna(candidate["ICAO"]).iloc[0]
                primary = primary.strip().upper() if isinstance(primary, str) else primary
                if primary in airports_clean.index:
                    resolved["dst"] = primary

    # Log unresolved
    if resolved["src"] is None or resolved["dst"] is None:
        reason = []
        if resolved["src"] is None:
            reason.append(f"src_unresolved:{row['Source airport']}|ID:{row['Source airport ID']}")
        if resolved["dst"] is None:
            reason.append(f"dst_unresolved:{row['Destination airport']}|ID:{row['Destination airport ID']}")
        unresolved_log.append({
            "row_index": row.name,
            "reason": ";".join(reason),
            "original_src": row["Source airport"],
            "original_dst": row["Destination airport"]
        })
        return None

    # Return resolved row
    row["Source airport"] = resolved["src"]
    row["Destination airport"] = resolved["dst"]
    return row

def clean_routes_with_fallback(df: pd.DataFrame, airports_clean: pd.DataFrame, airports_raw: pd.DataFrame):
    df["Source airport"] = df["Source airport"].astype(str)
    df["Destination airport"] = df["Destination airport"].astype(str)
    unresolved_log = []
    resolved_rows = []

    for idx, row in df.iterrows():
        new_row = resolve_route_codes(row.copy(), airports_clean, airports_raw, unresolved_log)
        if new_row is not None:
            resolved_rows.append(new_row)

    resolved_df = pd.DataFrame(resolved_rows)

    # Compute distance
    def compute_distance(row):
        try:
            src = airports_clean.loc[row["Source airport"]]
            dst = airports_clean.loc[row["Destination airport"]]
            return haversine(src["Latitude"], src["Longitude"], dst["Latitude"], dst["Longitude"])
        except Exception:
            return float("nan")

    resolved_df["distance_km"] = resolved_df.apply(compute_distance, axis=1)

    before = len(resolved_df)
    resolved_df = resolved_df[resolved_df["distance_km"].notna()]
    dropped_distance = before - len(resolved_df)

    # Add dummy delay & cost
    resolved_df["delay"] = 0.0
    resolved_df["cost"] = 100 + 0.1 * resolved_df["distance_km"]

    # Save unresolved log
    os.makedirs("data/new", exist_ok=True)
    pd.DataFrame(unresolved_log).to_csv("data/new/unresolved_routes_log.csv", index=False)

    summary = {
        "total_input": len(df),
        "resolved": len(resolved_df),
        "unresolved_logged": len(unresolved_log),
        "dropped_due_distance": dropped_distance
    }

    return resolved_df, summary

def generate_cleaning_report(airports_raw, airports_clean, routes_raw, routes_clean_summary):
    report = {
        "airports_raw_count": len(airports_raw),
        "airports_clean_count": len(airports_clean),
        "airport_primary_unique": airports_clean.index.is_unique,
        "routes_raw_count": len(routes_raw),
        "routes_after_resolution": routes_clean_summary["resolved"],
        "routes_unresolved_logged": routes_clean_summary["unresolved_logged"],
        "routes_dropped_distance": routes_clean_summary["dropped_due_distance"]
    }

    try:
        ul = pd.read_csv("data/new/unresolved_routes_log.csv")
        report["top_unresolved_reasons"] = ul["reason"].value_counts().head(10).to_dict()
    except FileNotFoundError:
        report["top_unresolved_reasons"] = {}

    return report

# ---------- MAIN RUN FUNCTION ----------
def run_full_cleaning_pipeline():
    os.makedirs("data/new", exist_ok=True)

    airports_raw = load_airports_local()
    routes_raw = load_routes_local()

    airports_clean = clean_airports(airports_raw)
    routes_clean_df, summary = clean_routes_with_fallback(routes_raw, airports_clean, airports_raw)

    # Persist cleaned data
    airports_path = "data/new/airports.csv"
    routes_path = "data/new/routes.csv"
    report_path = "data/new/cleaning_report.json"

    airports_clean.to_csv(airports_path)
    routes_clean_df.to_csv(routes_path, index=False)

    report = generate_cleaning_report(airports_raw, airports_clean, routes_raw, summary)

    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    # Print paths
    print(f"[INFO] Airports saved to {os.path.abspath(airports_path)}")
    print(f"[INFO] Routes saved to {os.path.abspath(routes_path)}")
    print(f"[INFO] Cleaning report saved to {os.path.abspath(report_path)}")

    return airports_clean, routes_clean_df, report

# Optional: run if standalone
if __name__ == "__main__":
    run_full_cleaning_pipeline()
