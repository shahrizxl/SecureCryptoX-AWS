resource "aws_s3_bucket" "securecryptox_bucket" {
  bucket        = "securecryptox-app-storage"
  force_destroy = true

  tags = {
    Name = "SecureCryptoX-App-Storage"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "app_bucket_encryption" {
  bucket = aws_s3_bucket.securecryptox_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_versioning" "app_bucket_versioning" {
  bucket = aws_s3_bucket.securecryptox_bucket.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_public_access_block" "app_bucket_public_block" {
  bucket = aws_s3_bucket.securecryptox_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
