output "cluster_name" { value = google_container_cluster.voice.name }
output "cluster_zone" { value = google_container_cluster.voice.location }
output "voice_image_repository" {
  value = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.services["voice-agent"].repository_id}/voice-agent"
}
output "web_image_repository" {
  value = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.services["web"].repository_id}/web"
}
output "livekit_image_repository" {
  value = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.services["livekit"].repository_id}/livekit"
}
output "https_ip" { value = google_compute_global_address.https.address }
output "https_ip_name" { value = google_compute_global_address.https.name }
output "livekit_media_ip" { value = google_compute_address.livekit_media.address }

output "project_number" { value = data.google_project.this.number }
output "workload_identity_pool" { value = "${var.project_id}.svc.id.goog" }
output "network_self_link" { value = google_compute_network.gke.self_link }
output "subnet_self_link" { value = google_compute_subnetwork.gke.self_link }
output "vendor_node_service_account" { value = try(google_service_account.vendor_nodes[0].email, null) }
output "vendor_node_pool" { value = try(google_container_node_pool.vendor[0].name, null) }
output "vendor_https_ip_name" { value = try(google_compute_global_address.vendor_https[0].name, null) }
output "vendor_https_ip" { value = try(google_compute_global_address.vendor_https[0].address, null) }
output "psa_range_name" { value = try(google_compute_global_address.psa[0].name, null) }
