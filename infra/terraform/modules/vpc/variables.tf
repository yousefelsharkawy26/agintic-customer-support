variable "environment" {
  type = string
}

variable "vpc_cidr" {
  type = string
}

variable "name_prefix" {
  type = string
}

variable "common_tags" {
  type = map(string)
}
