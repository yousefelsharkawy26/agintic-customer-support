variable "environment" {
  type = string
}

variable "name_prefix" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "subnet_ids" {
  type = list(string)
}

variable "app_sg_id" {
  description = "Application security group ID (ingress source for port 6379)"
  type        = string
}

variable "redis_node_type" {
  type = string
}

variable "common_tags" {
  type = map(string)
}
