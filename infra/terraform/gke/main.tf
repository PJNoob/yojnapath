locals {
  prefix = "yojnapath-${var.environment}"
}

resource "google_project_service" "required" {
  for_each = toset([
    "artifactregistry.googleapis.com",
    "compute.googleapis.com",
    "container.googleapis.com",
    "iam.googleapis.com",
  ])
  project            = var.project_id
  service            = each.key
  disable_on_destroy = false
}

resource "google_compute_network" "gke" {
  name                    = "${local.prefix}-vpc"
  auto_create_subnetworks = false
  depends_on              = [google_project_service.required]
}

resource "google_compute_subnetwork" "gke" {
  name                     = "${local.prefix}-subnet"
  region                   = var.region
  network                  = google_compute_network.gke.id
  ip_cidr_range            = "10.42.0.0/20"
  private_ip_google_access = true
  secondary_ip_range {
    range_name    = "${local.prefix}-pods"
    ip_cidr_range = "10.44.0.0/16"
  }
  secondary_ip_range {
    range_name    = "${local.prefix}-services"
    ip_cidr_range = "10.43.0.0/20"
  }
}

resource "google_artifact_registry_repository" "services" {
  for_each      = toset(["voice-agent", "web"])
  project       = var.project_id
  location      = var.region
  repository_id = "${local.prefix}-${each.key}"
  description   = "YojnaPath ${each.key} container images"
  format        = "DOCKER"
  depends_on    = [google_project_service.required]
}

resource "google_service_account" "nodes" {
  project      = var.project_id
  account_id   = "${local.prefix}-nodes"
  display_name = "YojnaPath GKE nodes"
  depends_on   = [google_project_service.required]
}

resource "google_project_iam_member" "node_default" {
  project = var.project_id
  role    = "roles/container.defaultNodeServiceAccount"
  member  = "serviceAccount:${google_service_account.nodes.email}"
}

resource "google_artifact_registry_repository_iam_member" "node_reader" {
  for_each   = google_artifact_registry_repository.services
  project    = var.project_id
  location   = var.region
  repository = each.value.repository_id
  role       = "roles/artifactregistry.reader"
  member     = "serviceAccount:${google_service_account.nodes.email}"
}

resource "google_container_cluster" "voice" {
  name                     = "${local.prefix}-gke"
  location                 = var.zone
  network                  = google_compute_network.gke.id
  subnetwork               = google_compute_subnetwork.gke.id
  networking_mode          = "VPC_NATIVE"
  remove_default_node_pool = true
  initial_node_count       = 1
  deletion_protection      = true
  enable_shielded_nodes    = true

  ip_allocation_policy {
    cluster_secondary_range_name  = "${local.prefix}-pods"
    services_secondary_range_name = "${local.prefix}-services"
  }

  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }

  release_channel { channel = "REGULAR" }
  depends_on = [google_project_service.required]
}

resource "google_container_node_pool" "voice" {
  name       = "voice-pool"
  location   = var.zone
  cluster    = google_container_cluster.voice.name
  node_count = 1

  node_config {
    machine_type    = var.node_machine_type
    disk_size_gb    = 30
    disk_type       = "pd-balanced"
    image_type      = "COS_CONTAINERD"
    service_account = google_service_account.nodes.email
    oauth_scopes    = ["https://www.googleapis.com/auth/cloud-platform"]

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

  depends_on = [google_project_iam_member.node_default, google_artifact_registry_repository_iam_member.node_reader]
}
