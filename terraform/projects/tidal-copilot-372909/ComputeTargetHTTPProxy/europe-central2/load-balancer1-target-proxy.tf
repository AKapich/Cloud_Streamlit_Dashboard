resource "google_compute_region_target_http_proxy" "load_balancer1_target_proxy" {
  name    = "load-balancer1-target-proxy"
  project = "tidal-copilot-372909"
  region  = "europe-central2"
  url_map = "https://www.googleapis.com/compute/v1/projects/tidal-copilot-372909/regions/europe-central2/urlMaps/load-balancer1"
}
# terraform import google_compute_region_target_http_proxy.load_balancer1_target_proxy projects/tidal-copilot-372909/regions/europe-central2/targetHttpProxies/load-balancer1-target-proxy
