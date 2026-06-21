output "vpc_id" {
  value = aws_vpc.securecryptox_vpc.id
}

output "ec2_public_ip" {
  value = aws_instance.securecryptox_ec2.public_ip
}

output "alb_dns_name" {
  value = aws_lb.securecryptox_alb.dns_name
}