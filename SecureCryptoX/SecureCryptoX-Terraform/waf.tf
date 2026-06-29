resource "aws_wafv2_web_acl" "securecryptox_waf" {
  name        = "SecureCryptoX-WAF"
  scope       = "REGIONAL"
  description = "WAF for SecureCryptoX ALB — blocks SQLi and XSS"

  default_action {
    allow {}
  }

  rule {
    name     = "AWSManagedRulesSQLiRuleSet"
    priority = 1

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesSQLiRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "SQLiRuleSet"
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = "AWSManagedRulesCommonRuleSet"
    priority = 2

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesCommonRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "CommonRuleSet"
      sampled_requests_enabled   = true
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "SecureCryptoXWAF"
    sampled_requests_enabled   = true
  }

  tags = {
    Name = "SecureCryptoX-WAF"
  }
}

resource "aws_wafv2_web_acl_association" "waf_alb_association" {
  resource_arn = aws_lb.securecryptox_alb.arn
  web_acl_arn  = aws_wafv2_web_acl.securecryptox_waf.arn
}
