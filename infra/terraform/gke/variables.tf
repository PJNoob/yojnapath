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

variable "enable_vendor_onboarding" {
  description = "Create the vendor-onboarding node pool, node identity, HTTPS address and private services access."
  type        = bool
  default     = false
}

variable "enable_shared_vpc_host" {
  description = "Make this project a Shared VPC host. Requires the project to be in the organization and roles/compute.xpnAdmin."
  type        = bool
  default     = false
}

variable "vendor_service_project_id" {
  description = "Vendor-onboarding project ID to attach as a Shared VPC service project."
  type        = string
  default     = null
}

variable "psa_cidr" {
  description = "Allocated range for private services access (Cloud SQL, Memorystore). Must not overlap the subnet, pod or service ranges."
  type        = string
  default     = "10.48.0.0/20"
}

variable "vendor_node_machine_type" {
  type    = string
  default = "e2-standard-2"
}

variable "vendor_pool_max_nodes" {
  type    = number
  default = 2
}

variable "subnet_network_users" {
  description = "Members granted roles/compute.networkUser on the Yojnapath subnet only. Empty unless a service agent is shown to need it."
  type        = list(string)
  default     = []
}
