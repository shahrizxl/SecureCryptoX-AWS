resource "aws_lb" "securecryptox_alb" {
  name               = "SecureCryptoX-ALB"
  internal           = false
  load_balancer_type = "application"

  security_groups = [
    aws_security_group.alb_sg.id
  ]

  subnets = [
    aws_subnet.public_subnet_1.id,
    aws_subnet.public_subnet_2.id
  ]
}

resource "aws_lb_target_group" "securecryptox_tg" {
  name     = "SecureCryptoX-TG"
  port     = 5000
  protocol = "HTTP"
  vpc_id   = aws_vpc.securecryptox_vpc.id

  health_check {
    path = "/"
  }
}

resource "aws_lb_target_group_attachment" "ec2_attach" {
  target_group_arn = aws_lb_target_group.securecryptox_tg.arn
  target_id        = aws_instance.securecryptox_ec2.id
  port             = 5000
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.securecryptox_alb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.securecryptox_tg.arn
  }
}