"""@bruin
name: threat_intelligence.raw_threatfox_iocs
type: python
image: python:3.11
connection: gcp-threat

materialization:
  type: table
  strategy: create+replace

columns:
  - name: first_seen_utc
    type: string
  - name: ioc_id
    type: integer
  - name: ioc_value
    type: string
  - name: ioc_type
    type: string
  - name: threat_type
    type: string
  - name: fk_malware
    type: string
  - name: malware_alias
    type: string
  - name: malware_printable
    type: string
  - name: last_seen_utc
    type: string
  - name: confidence_level
    type: integer
  - name: is_compromised
    type: boolean
  - name: reference
    type: string
  - name: tags
    type: string
  - name: anonymous
    type: integer
  - name: reporter
    type: string
@bruin"""

import io
import zipfile

import pandas as pd
import requests

FULL_DUMP_URL = "https://threatfox.abuse.ch/export/csv/full/"

COLUMNS = [
    "first_seen_utc",
    "ioc_id",
    "ioc_value",
    "ioc_type",
    "threat_type",
    "fk_malware",
    "malware_alias",
    "malware_printable",
    "last_seen_utc",
    "confidence_level",
    "is_compromised",
    "reference",
    "tags",
    "anonymous",
    "reporter",
]


def materialize():
    response = requests.get(FULL_DUMP_URL, timeout=120)
    response.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
        csv_filename = zf.namelist()[0]
        raw_text = zf.read(csv_filename).decode("utf-8")

    lines = [line for line in raw_text.splitlines() if not line.startswith("#")]
    cleaned_csv = "\n".join(lines)

    df = pd.read_csv(
        io.StringIO(cleaned_csv),
        header=None,
        names=COLUMNS,
        dtype=str,
        quotechar='"',
        skipinitialspace=True,
    )

    df = df.replace("None", pd.NA)
    df = df.replace("", pd.NA)

    df["ioc_id"] = pd.to_numeric(df["ioc_id"], errors="coerce").astype("Int64")
    df["confidence_level"] = pd.to_numeric(df["confidence_level"], errors="coerce").astype("Int64")
    df["anonymous"] = pd.to_numeric(df["anonymous"], errors="coerce").astype("Int64")
    df["is_compromised"] = df["is_compromised"].map({"True": True, "False": False})

    return df
