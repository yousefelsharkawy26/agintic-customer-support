output "endpoint" {
  value = aws_db_instance.this.endpoint
}

output "db_url" {
  value     = "postgresql+asyncpg://${aws_db_instance.this.username}:${aws_db_instance.this.password}@${aws_db_instance.this.endpoint}/${aws_db_instance.this.db_name}"
  sensitive = true
}

output "db_name" {
  value = aws_db_instance.this.db_name
}
