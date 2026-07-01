terraform {
  required_version = ">= 1.6"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }

  backend "s3" {
    bucket = "customer-support-terraform-state"
    key    = "prod/terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = var.aws_region
}

locals {
  name_prefix = "${var.environment}-customer-support"
  common_tags = {
    Environment = var.environment
    Project     = "customer-support"
    ManagedBy   = "terraform"
  }
}

# ── VPC ──

module "vpc" {
  source = "./modules/vpc"

  environment = var.environment
  vpc_cidr    = var.vpc_cidr
  name_prefix = local.name_prefix
  common_tags = local.common_tags
}

# ── ALB ──

module "alb" {
  source = "./modules/alb"

  environment           = var.environment
  name_prefix           = local.name_prefix
  vpc_id                = module.vpc.vpc_id
  subnet_ids            = module.vpc.public_subnet_ids
  alb_security_group_id = module.vpc.alb_security_group_id
  certificate_arn       = var.acm_certificate_arn
  container_port        = var.app_container_port
  common_tags           = local.common_tags
}

# ── RDS (PostgreSQL) ──

module "rds" {
  source = "./modules/rds"

  environment       = var.environment
  name_prefix       = local.name_prefix
  vpc_id            = module.vpc.vpc_id
  subnet_ids        = module.vpc.private_subnet_ids
  app_sg_id         = module.vpc.app_security_group_id
  db_instance_class = var.db_instance_class
  db_username       = var.db_username
  db_password       = var.db_password
  common_tags       = local.common_tags
}

# ── ElastiCache (Redis) ──

module "redis" {
  source = "./modules/elasticache"

  environment     = var.environment
  name_prefix     = local.name_prefix
  vpc_id          = module.vpc.vpc_id
  subnet_ids      = module.vpc.private_subnet_ids
  app_sg_id       = module.vpc.app_security_group_id
  redis_node_type = var.redis_node_type
  common_tags     = local.common_tags
}

# ── ECS Fargate (API + Qdrant sidecar) ──

module "ecs" {
  source = "./modules/ecs"

  environment           = var.environment
  name_prefix           = local.name_prefix
  vpc_id                = module.vpc.vpc_id
  subnet_ids            = module.vpc.private_subnet_ids
  app_security_group_id = module.vpc.app_security_group_id
  target_group_arn      = module.alb.target_group_arn
  ecr_repository_url    = var.ecr_repository_url
  image_tag             = var.image_tag
  db_url                = module.rds.db_url
  redis_url             = module.redis.redis_url
  qdrant_url            = "http://localhost:6333"
  desired_count         = var.app_count
  container_port        = var.app_container_port
  aws_region            = var.aws_region
  common_tags           = local.common_tags
}
