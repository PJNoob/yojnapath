# Vendor-onboarding host-side resources. Everything here is additive and gated:
# with the default variables this file plans no changes.
#
# These resources are owned by THIS state only. The vendor-onboarding Terraform
# must consume them (via outputs) and must not manage them.

locals {
  vendor_enabled  = var.enable_vendor_onboarding
  vendor_prefix   = "${local.prefix}-vendor"
  vendor_attached = var.enable_shared_vpc_host && var.vendor_service_project_id != null
}

resource "google_project_service" "vendor" {
  for_each = local.vendor_enabled ? toset([
    "servicenetworking.googleapis.com",
    "cloudresourcemanager.googleapis.com",
  ]) : toset([])
  project            = var.project_id
  service            = each.key
  disable_on_destroy = false
}

# Shared VPC host. Requires the project to be inside the organization and the
# applying identity to hold roles/compute.xpnAdmin on the organization.
resource "google_compute_shared_vpc_host_project" "host" {
  count   = var.enable_shared_vpc_host ? 1 : 0
  project = var.project_id
}

resource "google_compute_shared_vpc_service_project" "vendor" {
  count           = local.vendor_attached ? 1 : 0
  host_project    = google_compute_shared_vpc_host_project.host[0].project
  service_project = var.vendor_service_project_id
}

# Private services access (Cloud SQL and Memorystore share one allocated range).
resource "google_compute_global_address" "psa" {
  count         = local.vendor_enabled ? 1 : 0
  project       = var.project_id
  name          = "${local.prefix}-psa"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  address       = split("/", var.psa_cidr)[0]
  prefix_length = tonumber(split("/", var.psa_cidr)[1])
  network       = google_compute_network.gke.id
  depends_on    = [google_project_service.vendor]
}

resource "google_service_networking_connection" "psa" {
  count                   = local.vendor_enabled ? 1 : 0
  network                 = google_compute_network.gke.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.psa[0].name]
  deletion_policy         = "ABANDON"
}

# Dedicated identity for the vendor node pool so image-pull rights granted in the
# vendor project do not extend to the existing Yojnapath nodes.
resource "google_service_account" "vendor_nodes" {
  count        = local.vendor_enabled ? 1 : 0
  project      = var.project_id
  account_id   = "${local.vendor_prefix}-nodes"
  display_name = "Vendor-onboarding GKE nodes"
  depends_on   = [google_project_service.required]
}

resource "google_project_iam_member" "vendor_node_default" {
  count   = local.vendor_enabled ? 1 : 0
  project = var.project_id
  role    = "roles/container.defaultNodeServiceAccount"
  member  = "serviceAccount:${google_service_account.vendor_nodes[0].email}"
}

resource "google_container_node_pool" "vendor" {
  count              = local.vendor_enabled ? 1 : 0
  name               = "vendor-pool"
  location           = var.zone
  cluster            = google_container_cluster.voice.name
  initial_node_count = 1

  autoscaling {
    min_node_count = 1
    max_node_count = var.vendor_pool_max_nodes
  }

  node_config {
    machine_type    = var.vendor_node_machine_type
    disk_size_gb    = 30
    disk_type       = "pd-balanced"
    image_type      = "COS_CONTAINERD"
    service_account = google_service_account.vendor_nodes[0].email
    oauth_scopes    = ["https://www.googleapis.com/auth/cloud-platform"]

    labels = { workload = "vendor-onboarding" }
    taint {
      key    = "workload"
      value  = "vendor-onboarding"
      effect = "NO_SCHEDULE"
    }

    workload_metadata_config { mode = "GKE_METADATA" }
    shielded_instance_config {
      enable_secure_boot          = true
      enable_integrity_monitoring = true
    }
  }

  management {
    auto_repair  = true
    auto_upgrade = true
  }

  depends_on = [google_project_iam_member.vendor_node_default]
}

# Separate HTTPS entry point; the existing yojnapath-dev-https address is untouched.
resource "google_compute_global_address" "vendor_https" {
  count      = local.vendor_enabled ? 1 : 0
  name       = "${local.vendor_prefix}-https"
  ip_version = "IPV4"
  depends_on = [google_project_service.required]
}

# Optional subnet-scoped grants (empty by default; add only if a service-project
# agent is shown to need subnet access).
resource "google_compute_subnetwork_iam_member" "network_user" {
  for_each   = toset(var.subnet_network_users)
  project    = var.project_id
  region     = var.region
  subnetwork = google_compute_subnetwork.gke.name
  role       = "roles/compute.networkUser"
  member     = each.key
}

data "google_project" "this" {
  project_id = var.project_id
}
