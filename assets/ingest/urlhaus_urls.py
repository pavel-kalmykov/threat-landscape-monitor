"""@bruin
name: threat_intelligence.raw_urlhaus_urls
type: python
image: python:3.11
connection: gcp-threat

materialization:
  type: table
  strategy: create+replace

columns:
  - name: id
    type: integer
  - name: dateadded
    type: string
  - name: url
    type: string
  - name: url_status
    type: string
  - name: last_online
    type: string
  - name: threat
    type: string
  - name: tags
    type: string
  - name: urlhaus_link
    type: string
  - name: reporter
    type: string
@bruin"""

import io
import zipfile

import pandas as pd
import requests

FULL_DUMP_URL = "https://urlhaus.abuse.ch/downloads/csv/"

COLUMNS = [
    "id",
    "dateadded",
    "url",
    "url_status",
    "last_online",
    "threat",
    "tags",
    "urlhaus_link",
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
    )

    df = df.replace("None", pd.NA)
    df = df.replace("", pd.NA)

    return df
