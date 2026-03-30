variable "project_id" {
  description = "GCP project ID"
  type        = string
  default     = "threat-landscape-putopavel"
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "europe-southwest1"
}

variable "bq_dataset_id" {
  description = "BigQuery dataset ID"
  type        = string
  default     = "threat_intelligence"
}

variable "gcs_bucket_name" {
  description = "GCS bucket for raw data backups"
  type        = string
  default     = "threat-landscape-putopavel-raw"
}
