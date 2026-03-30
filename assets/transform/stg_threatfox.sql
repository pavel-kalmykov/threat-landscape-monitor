/* @bruin
name: threat_intelligence.stg_threatfox
type: bq.sql
depends:
  - threat_intelligence.raw_threatfox_iocs
materialization:
  type: table
  strategy: create+replace
@bruin */

SELECT
  SAFE.PARSE_TIMESTAMP('%Y-%m-%d %H:%M:%S', first_seen_utc) AS first_seen_utc,
  ioc_id,
  ioc_value,
  ioc_type,
  threat_type,
  fk_malware,
  SPLIT(fk_malware, '.')[SAFE_OFFSET(0)] AS malware_platform,
  SPLIT(fk_malware, '.')[SAFE_OFFSET(1)] AS malware_family,
  malware_alias,
  malware_printable,
  SAFE.PARSE_TIMESTAMP('%Y-%m-%d %H:%M:%S', last_seen_utc) AS last_seen_utc,
  confidence_level,
  is_compromised,
  reference,
  tags,
  anonymous,
  reporter
FROM threat_intelligence.raw_threatfox_iocs
WHERE ioc_id IS NOT NULL
