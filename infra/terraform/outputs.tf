output "namespace" {
  description = "Yaratilgan K8s namespace"
  value       = kubernetes_namespace.talaba_ns.metadata[0].name
}

output "config_map_name" {
  description = "Global ConfigMap nomi"
  value       = kubernetes_config_map.talaba_config.metadata[0].name
}
