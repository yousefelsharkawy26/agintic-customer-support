resource "aws_elasticache_subnet_group" "this" {
  name       = "${var.name_prefix}-redis-subnet-group"
  subnet_ids = var.subnet_ids
  tags       = merge(var.common_tags, { Name = "${var.name_prefix}-redis-subnet-group" })
}

resource "aws_security_group" "redis" {
  name        = "${var.name_prefix}-redis"
  description = "Redis security group — ingress from app only"
  vpc_id      = var.vpc_id

  ingress {
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [var.app_sg_id]
  }

  tags = merge(var.common_tags, { Name = "${var.name_prefix}-redis-sg" })
}

resource "aws_elasticache_cluster" "this" {
  cluster_id           = var.name_prefix
  engine               = "redis"
  engine_version       = "7.1"
  node_type            = var.redis_node_type
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
  port                 = 6379

  subnet_group_name  = aws_elasticache_subnet_group.this.name
  security_group_ids = [aws_security_group.redis.id]

  apply_immediately = var.environment != "prod"

  tags = merge(var.common_tags, { Name = "${var.name_prefix}-redis" })
}
