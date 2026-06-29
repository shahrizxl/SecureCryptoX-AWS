resource "aws_cloudwatch_log_group" "securecryptox_logs" {
  name              = "/securecryptox/application"
  retention_in_days = 30

  tags = {
    Name = "SecureCryptoX-LogGroup"
  }
}

resource "aws_cloudwatch_metric_alarm" "high_cpu_alarm" {
  alarm_name          = "SecureCryptoX-HighCPU"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = 120
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "Triggered when EC2 CPU exceeds 80% for 4 minutes"

  dimensions = {
    InstanceId = aws_instance.securecryptox_ec2.id
  }

  tags = {
    Name = "SecureCryptoX-HighCPU-Alarm"
  }
}

resource "aws_cloudwatch_metric_alarm" "rds_high_cpu_alarm" {
  alarm_name          = "SecureCryptoX-RDS-HighCPU"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = 120
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "Triggered when RDS CPU exceeds 80% for 4 minutes"

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.securecryptox_rds.id
  }

  tags = {
    Name = "SecureCryptoX-RDS-HighCPU-Alarm"
  }
}

resource "aws_cloudwatch_metric_alarm" "waf_blocked_requests" {
  alarm_name          = "SecureCryptoX-WAF-BlockedRequests"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "BlockedRequests"
  namespace           = "AWS/WAFV2"
  period              = 60
  statistic           = "Sum"
  threshold           = 50
  alarm_description   = "Triggered when WAF blocks more than 50 requests per minute"

  dimensions = {
    WebACL = "SecureCryptoX-WAF"
    Region = "us-east-1"
    Rule   = "ALL"
  }

  tags = {
    Name = "SecureCryptoX-WAF-Blocked-Alarm"
  }
}
