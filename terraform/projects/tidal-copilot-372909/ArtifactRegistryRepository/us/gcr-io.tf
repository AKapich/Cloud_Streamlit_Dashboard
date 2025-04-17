resource "google_artifact_registry_repository" "gcr_io" {
  format        = "DOCKER"
  location      = "us"
  mode          = "STANDARD_REPOSITORY"
  project       = "tidal-copilot-372909"
  repository_id = "gcr.io"
}
# terraform import google_artifact_registry_repository.gcr_io projects/tidal-copilot-372909/locations/us/repositories/gcr.io
