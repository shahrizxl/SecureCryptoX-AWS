resource "aws_instance" "securecryptox_ec2" {
  ami           = "ami-0c02fb55956c7d316"
  instance_type = "t3.micro"
  subnet_id     = aws_subnet.public_subnet_1.id

  vpc_security_group_ids = [
    aws_security_group.ec2_sg.id
  ]

  key_name = "securecryptox-key"

  tags = {
    Name = "SecureCryptoX-EC2"
  }
}