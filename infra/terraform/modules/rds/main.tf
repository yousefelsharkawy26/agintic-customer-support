resource "aws_db_subnet_group" "this" {
  name       = "${var.name_prefix}-db-subnet-group"
  subnet_ids = var.subnet_ids
  tags       = merge(var.common_tags, { Name = "${var.name_prefix}-db-subnet-group" })
}

resource "aws_security_group" "rds" {
  name        = "${var.name_prefix}-rds"
  description = "RDS security group — ingress from app only"
  vpc_id      = var.vpc_id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [var.app_sg_id]
  }

  tags = merge(var.common_tags, { Name = "${var.name_prefix}-rds-sg" })
}

resource "aws_db_parameter_group" "this" {
  name   = "${var.name_prefix}-pg16"
  family = "postgres16"

  parameter {
    name  = "log_statement"
    value = "ddl"
  }

  parameter {
    name  = "log_min_duration_statement"
    value = "500"
  }

  tags = merge(var.common_tags, { Name = "${var.name_prefix}-pg16" })
}

resource "aws_db_instance" "this" {
  identifier = var.name_prefix

  engine                = "postgres"
  engine_version        = "16.3"
  instance_class        = var.db_instance_class
  allocated_storage     = 50
  max_allocated_storage = 200
  storage_type          = "gp3"
  storage_encrypted     = true

  db_name  = "customer_support"
  username = var.db_username
  password = var.db_password
  port     = 5432

  db_subnet_group_name   = aws_db_subnet_group.this.name
  vpc_security_group_ids = [aws_security_group.rds.id]

  backup_retention_period = 30
  backup_window           = "03:00-04:00"
  maintenance_window      = "sun:04:00-sun:05:00"

  deletion_protection       = var.environment == "prod"
  skip_final_snapshot       = var.environment != "prod"
  final_snapshot_identifier = "${var.name_prefix}-final-${formatdate("YYYY-MM-DD-hhmm", timestamp())}"

  parameter_group_name = aws_db_parameter_group.this.name

  performance_insights_enabled          = true
  performance_insights_retention_period = 7
  monitoring_interval                   = 10
  monitoring_role_arn                   = aws_iam_role.rds_enhanced.arn

  auto_minor_version_upgrade = true

  tags = merge(var.common_tags, { Name = "${var.name_prefix}-rds" })
}

resource "aws_iam_role" "rds_enhanced" {
  name = "${var.name_prefix}-rds-enhanced-monitoring"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "monitoring.rds.amazonaws.com"
      }
    }]
  })

  tags = var.common_tags
}

resource "aws_iam_role_policy_attachment" "rds_enhanced" {
  role       = aws_iam_role.rds_enhanced.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}
