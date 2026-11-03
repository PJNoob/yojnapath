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
