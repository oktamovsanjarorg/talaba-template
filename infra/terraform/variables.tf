variable "environment" {
  description = "Ishga tushirish muhiti (prod, staging, dev)"
  type        = string
  default     = "prod"
}

variable "namespace" {
  description = "Kubernetes namespace nomi"
  type        = string
  default     = "talaba"
}

variable "replicas_bot" {
  description = "Bot podlarining boshlang'ich soni"
  type        = int
  default     = 3
}

variable "replicas_worker" {
  description = "Worker podlarining boshlang'ich soni"
  type        = int
  default     = 5
}
