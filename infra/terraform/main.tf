terraform {
  required_version = ">= 1.5.0"
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.30"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.13"
    }
  }
}

# 1. Namespace for Talaba Enterprise
resource "kubernetes_namespace" "talaba_ns" {
  metadata {
    name = var.namespace
    labels = {
      environment = var.environment
      app         = "talaba-ecosystem"
    }
  }
}

# 2. ConfigMap for Global Configurations
resource "kubernetes_config_map" "talaba_config" {
  metadata {
    name      = "talaba-global-config"
    namespace = kubernetes_namespace.talaba_ns.metadata[0].name
  }

  data = {
    ENVIRONMENT             = var.environment
    QWEN_MODEL              = "qwen-turbo"
    PROMETHEUS_METRICS_PORT = "8000"
  }
}
