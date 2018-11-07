variable "private_key_path" {
  description = "Path to private key corresponding to AWS key pair"
  default = "/root/.ssh/terraform-us-east-2.pem"
}

variable "aws_instance_type" {
  description = "AWS EC2 instance type"
  default = "t2.nano" # nano for testing Terraform script; larger to actually run GovReady-Q
}

variable "aws_region" {
  description = "AWS region"
  default = "us-east-2"
}

variable "aws_key_name" {
  description = "AWS key pair name"
  default = {
    us-east-2 = "terraform-us-east-2"
  }
}

# CentOS Linux 7 x86_64 HVM EBS ENA 1805_01-b7ee8a69-ee97-4a49-9e68-afaee216db2e-ami-77ec9308.4
variable "aws_amis" {
  default = {
    us-east-2 = "ami-9c0638f9" 
  }
}