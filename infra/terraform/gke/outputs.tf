output "cluster_name" { value = google_container_cluster.voice.name }
output "cluster_zone" { value = google_container_cluster.voice.location }
output "voice_image_repository" {
  value = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.services["voice-agent"].repository_id}/voice-agent"
}
output "web_image_repository" {
  value = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.services["web"].repository_id}/web"
}
