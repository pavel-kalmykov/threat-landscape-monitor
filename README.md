# Threat Landscape Monitor

A data pipeline that pulls cyber threat data from [abuse.ch](https://abuse.ch) feeds, loads it into BigQuery, and turns it into something you can actually use: a dashboard that tells you how fast malicious URLs get taken down and which malware families are showing up the most.

## What problem does this solve?

abuse.ch publishes free threat intelligence data (malicious URLs, indicators of compromise, malware samples). The data is good, but it's raw CSV dumps. If you want to ask questions like "which hosting providers take the longest to remove malware URLs?" or "is Cobalt Strike activity going up this month?", you need to build a pipeline first.

That's what this project does. It downloads data daily from two abuse.ch feeds, loads it into BigQuery, runs SQL transformations, and feeds a Looker Studio dashboard with two views:

1. **Takedown time**: how long malicious URLs stay active after being reported, broken down by hosting provider and country. Useful for incident response and abuse reporting.
2. **Threat trends**: volume of reported threats over time, split by malware family and type. Useful for knowing where to look.

## Architecture

```
abuse.ch feeds          Bruin Pipeline              BigQuery                 Looker Studio
(URLhaus + ThreatFox)   (Python + SQL assets)       (Data Warehouse)         (Dashboard)
      |                        |                          |                       |
      |   daily download       |                          |                       |
      +----------------------->+  raw_urlhaus_urls        |                       |
      +----------------------->+  raw_threatfox_iocs      |                       |
                               |                          |                       |
                               +  stg_urlhaus        ---->+                       |
                               +  stg_threatfox      ---->+                       |
                               |                          |                       |
                               +  mart_takedown      ---->+--------------------->+
                               +  mart_trends        ---->+--------------------->+
```

GitHub Actions runs the Bruin pipeline daily at 06:00 UTC.

## Tech stack

| Layer | Tool |
|---|---|
| Infrastructure as Code | Terraform |
| Cloud | Google Cloud Platform (BigQuery, GCS) |
| Ingestion, transformation, orchestration | Bruin |
| Data Warehouse | BigQuery |
| Visualization | Looker Studio |
| CI/CD | GitHub Actions |

## Data sources

| Source | What it has | Volume | Updates |
|---|---|---|---|
| [URLhaus](https://urlhaus.abuse.ch/) | Malicious URLs used for malware distribution | ~70K URLs (full history since 2018) | Every 5 minutes |
| [ThreatFox](https://threatfox.abuse.ch/) | Indicators of Compromise (IOCs) tied to malware families | ~1K IOCs (rolling 30 days) | Every 5 minutes |

Both feeds are open, no authentication needed.

## Setup and reproduction

### Prerequisites

- GCP account with billing enabled
- `gcloud` CLI authenticated (`gcloud auth application-default login`)
- [Terraform](https://www.terraform.io/) installed
- [Bruin CLI](https://getbruin.com/) installed (`curl -LsSf https://raw.githubusercontent.com/bruin-data/bruin/refs/heads/main/install.sh | sh`)

### 1. Clone the repo

```bash
git clone https://github.com/pavel-kalmykov/threat-landscape-monitor.git
cd threat-landscape-monitor
```

### 2. Provision infrastructure

```bash
cd terraform
terraform init
terraform apply
cd ..
```

This creates a BigQuery dataset (`threat_intelligence`) and a GCS bucket, both in `europe-southwest1`.

### 3. Configure Bruin

Create a `.bruin.yml` file at the project root (this file is gitignored):

```yaml
default_environment: default
environments:
  default:
    connections:
      google_cloud_platform:
        - name: "gcp-threat"
          project_id: "YOUR_PROJECT_ID"
          location: "europe-southwest1"
          use_application_default_credentials: true
```

### 4. Run the pipeline

```bash
bruin run .
```

Downloads fresh data from abuse.ch, loads it into BigQuery, runs all transformations. Takes about 30 seconds.

### 5. Dashboard

Connect Looker Studio to the `mart_takedown_analysis` and `mart_threat_trends` tables in BigQuery.

## Pipeline assets

| Asset | Type | What it does |
|---|---|---|
| `raw_urlhaus_urls` | Python | Downloads the full URLhaus CSV dump (~70K rows), parses it, loads to BigQuery |
| `raw_threatfox_iocs` | Python | Downloads the recent ThreatFox CSV (~1K rows), parses it, loads to BigQuery |
| `stg_urlhaus` | SQL | Cleans types, extracts domain and TLD from URLs, calculates takedown time in seconds |
| `stg_threatfox` | SQL | Cleans types, splits the `fk_malware` field into platform and family |
| `mart_takedown_analysis` | SQL | One row per URL with takedown metrics, ready for the dashboard |
| `mart_threat_trends` | SQL | Daily counts from both sources, grouped by threat type and malware family |

## Dashboard

TODO: Add Looker Studio link and screenshot

## License

MIT
