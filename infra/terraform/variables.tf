variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (e.g. dev, staging, prod)"
  type        = string
  default     = "prod"
}

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t4g.medium"
}

variable "db_username" {
  description = "RDS master username"
  type        = string
  default     = "cs_user"
}

variable "db_password" {
  description = "RDS master password (from Secrets Manager or SSM)"
  type        = string
  sensitive   = true
}

variable "redis_node_type" {
  description = "ElastiCache Redis node type"
  type        = string
  default     = "cache.t4g.small"
}

variable "acm_certificate_arn" {
  description = "ACM certificate ARN for HTTPS"
  type        = string
  default     = ""
}

variable "ecr_repository_url" {
  description = "ECR repository URL for the API image"
  type        = string
}

variable "image_tag" {
  description = "Docker image tag to deploy"
  type        = string
  default     = "latest"
}

variable "app_count" {
  description = "Number of Fargate task replicas"
  type        = number
  default     = 2
}

variable "app_container_port" {
  description = "Container port for the API"
  type        = number
  default     = 8080
}
