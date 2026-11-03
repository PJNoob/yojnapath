variable "project_id" {
  description = "Existing, billing-enabled Google Cloud project ID."
  type        = string
}

variable "region" {
  description = "Region for Artifact Registry and VPC."
  type        = string
  default     = "asia-south1"
}

variable "zone" {
  description = "Single GKE zone within region."
  type        = string
  default     = "asia-south1-a"
}

variable "environment" {
  type    = string
  default = "dev"
}

variable "node_machine_type" {
  description = "One on-demand VM; increase after measuring concurrent calls."
  type        = string
  default     = "e2-standard-2"
}
