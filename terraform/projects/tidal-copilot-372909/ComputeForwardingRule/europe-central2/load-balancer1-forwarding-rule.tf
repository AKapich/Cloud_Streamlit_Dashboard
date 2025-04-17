resource "google_compute_forwarding_rule" "load_balancer1_forwarding_rule" {
  ip_address            = "34.0.245.131"
  ip_protocol           = "TCP"
  load_balancing_scheme = "EXTERNAL_MANAGED"
  name                  = "load-balancer1-forwarding-rule"
  network               = "https://www.googleapis.com/compute/v1/projects/tidal-copilot-372909/global/networks/default"
  network_tier          = "STANDARD"
  port_range            = "80-80"
  project               = "tidal-copilot-372909"
  region                = "europe-central2"
  target                = "https://www.googleapis.com/compute/beta/projects/tidal-copilot-372909/regions/europe-central2/targetHttpProxies/load-balancer1-target-proxy"
}
# terraform import google_compute_forwarding_rule.load_balancer1_forwarding_rule projects/tidal-copilot-372909/regions/europe-central2/forwardingRules/load-balancer1-forwarding-rule
