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

variable "alb_security_group_id" {
  type = string
}

variable "certificate_arn" {
  type    = string
  default = ""
}

variable "container_port" {
  type    = number
  default = 8080
}

variable "common_tags" {
  type = map(string)
}
