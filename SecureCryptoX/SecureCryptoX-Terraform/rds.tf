resource "aws_db_instance" "securecryptox_db" {
  identifier = "securecryptox-db"

  engine         = "sqlserver-ex"
  engine_version = "15.00"

  instance_class = "db.t3.micro"

  allocated_storage = 20

  username = "admin"
  password = "ChangeThisPassword123!"

  storage_encrypted = true

  skip_final_snapshot = true

  publicly_accessible = false
}