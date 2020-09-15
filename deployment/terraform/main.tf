# Adopted from https://github.com/terraform-aws-modules/terraform-aws-ec2-instance/blob/v2.15.0/examples/basic/main.tf

provider "aws" {
  region = "us-east-1"
}

##################################################################
# Data sources to get VPC, subnet, security group and AMI details
##################################################################
data "aws_vpc" "default" {
  default = true
}

data "aws_subnet_ids" "all" {
  vpc_id = "${data.aws_vpc.default.id}"
}

data "aws_ami" "amazon_linux" {
  most_recent = true

  owners = ["amazon"]

  filter {
    name = "name"

    values = [
      "amzn-ami-hvm-*-x86_64-gp2",
    ]
  }

  filter {
    name = "owner-alias"

    values = [
      "amazon",
    ]
  }
}

module "security_group" {
  source  = "terraform-aws-modules/security-group/aws"
  version = "~> 2.0"

  name        = "example"
  description = "Security group for example usage with EC2 instance"
  vpc_id      = "${data.aws_vpc.default.id}"

  ingress_cidr_blocks = ["0.0.0.0/0"]
  ingress_rules       = ["http-80-tcp", "all-icmp"]
  egress_rules        = ["all-all"]
}

resource "aws_eip" "http1" {
  vpc      = true
  instance = "${module.ec2_http1.id[0]}"
}

resource "aws_eip" "http2" {
  vpc      = true
  instance = "${module.ec2_http2.id[0]}"
}

module "ec2_http2" {
  source                 = "terraform-aws-modules/ec2-instance/aws"
  version                = "1.22.0"
  instance_count = 1

  name          = "http2-server"
  ami           = "${data.aws_ami.amazon_linux.id}"
  instance_type = "t2.medium"
  subnet_id     = "${element(data.aws_subnet_ids.all.ids, 0)}"
  vpc_security_group_ids      = ["${module.security_group.this_security_group_id}"]
  associate_public_ip_address = true
  user_data = <<EOF
#!/bin/bash

# https://serverfault.com/a/670688
export DEBIAN_FRONTEND=noninteractive

# print commands and their expanded arguments
set -x

# Download nginx
amazon-linux-extras install nginx1.12

# Make a "data" directory for the test image.
mkdir /etc/data
wget https://viv-demo.storage.googleapis.com/Vanderbilt-Spraggins-Kidney-MxIF.ome.tif -O /etc/data/test.ome.tif

# Use the http2 conf.
git clone https://github.com/ilan-gold/benchmark-viv.git
cd deployment/docker-nginx-http2-ssl-vendor
mv /etc/nginx /etc/nginx-backup
cp niginx.conf /etc/nginx

EOF
}

module "ec2_http1" {
  source                 = "terraform-aws-modules/ec2-instance/aws"
  version                = "1.22.0"

  instance_count = 1

  name          = "http1-server"
  ami           = "${data.aws_ami.amazon_linux.id}"
  instance_type = "t2.medium"
  subnet_id     = "${element(data.aws_subnet_ids.all.ids, 0)}"
  vpc_security_group_ids      = ["${module.security_group.this_security_group_id}"]
  associate_public_ip_address = true
  user_data = <<EOF
#!/bin/bash

# https://serverfault.com/a/670688
export DEBIAN_FRONTEND=noninteractive

# print commands and their expanded arguments
set -x

# Download nginx
amazon-linux-extras install nginx1.12

# Make a "data" directory for the test image.
mkdir /etc/data
wget https://viv-demo.storage.googleapis.com/Vanderbilt-Spraggins-Kidney-MxIF.ome.tif -O /etc/data/test.ome.tif

# Use the http2 conf.
git clone https://github.com/ilan-gold/benchmark-viv.git
cd deployment/docker-nginx-http2-ssl-vendor
mv /etc/nginx /etc/nginx-backup
cp niginx.conf /etc/nginx

EOF
}