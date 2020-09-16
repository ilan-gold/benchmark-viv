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

module "security_group" {
  source  = "terraform-aws-modules/security-group/aws"
  version = "~> 2.0"

  name        = "example"
  description = "Security group for example usage with EC2 instance"
  vpc_id      = "${data.aws_vpc.default.id}"

  ingress_cidr_blocks = ["0.0.0.0/0"]
  ingress_rules       = ["http-80-tcp", "all-icmp", "https-443-tcp", "ssh-tcp"]
  egress_rules        = ["all-all"]
}
/*
resource "aws_eip" "http1" {
  vpc      = true
  instance = "${module.ec2_http1.id[0]}"
}
*/
resource "aws_eip" "http2" {
  vpc      = true
  instance = "${module.ec2_http2.id[0]}"
}

module "ec2_http2" {
  source                 = "terraform-aws-modules/ec2-instance/aws"
  version                = "1.22.0"
  instance_count = 1

  name          = "http2-viv-benchmark"
  ami           = "ami-07b4156579ea1d7ba"
  instance_type = "t2.medium"
  subnet_id     = "${element(data.aws_subnet_ids.all.ids, 0)}"
  vpc_security_group_ids      = ["${module.security_group.this_security_group_id}"]
  associate_public_ip_address = true
  root_block_device = [{
    volume_type = "gp2"
    # Need a lot for tiff files.
    volume_size = 25
  }]
  user_data = <<EOF
#!/bin/bash

# https://serverfault.com/a/670688
export DEBIAN_FRONTEND=noninteractive

# print commands and their expanded arguments
set -x

# install packages
sudo apt-get -qq update
sudo apt-get -qq -y install git jq
sudo apt-get -y autoremove
sudo apt-get clean
sudo curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Get Ilan's ssh key
sudo curl -s https://api.github.com/users/ilan-gold/keys | jq -r '.[].key' >> /home/ubuntu/.ssh/authorized_keys

# Use the http2 conf.
sudo git clone https://github.com/ilan-gold/benchmark-viv.git
cd benchmark-viv
sudo git checkout ilan-gold/deployment
cd deployment/docker-nginx-http2
# Self signing ssl certificate (configured in selenium to ignore ssl).
sudo openssl req -x509 -newkey rsa:4096 -keyout nginx-selfsigned.key -out nginx-selfsigned.crt -days 365 -nodes -subj "/C=US/ST=NY/L=NewYork/O=Harvard/OU=root/CN=http2.viv.vitessce.io/emailAddress=ilan_gold@hms.harvard.edu"
sudo sed -i 's/SUBDOMAIN.viv.vitessce.io/http2.viv.vitessce.io/g' nginx.conf

# Make a "data" directory for the test image.
sudo mkdir /data
sudo wget https://viv-demo.storage.googleapis.com/Vanderbilt-Spraggins-Kidney-MxIF.ome.tif -O /data/test.ome.tif

# Build the docker image
sudo docker build -t custom-nginx .
sudo docker run --name custom-nginx -v /data/:/usr/share/nginx/ -d -p 80:80 -p 443:443 custom-nginx
EOF
}
/*
module "ec2_http1" {
  source                 = "terraform-aws-modules/ec2-instance/aws"
  version                = "1.22.0"

  instance_count = 1

  name          = "http1-viv-benchmark"
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
openssl req -x509 -newkey rsa:4096 -keyout nginx-selfsigned.key -out nginx-selfsigned.crt -days 365 -nodes -subj "/C=US/ST=NY/L=NewYork/O=Harvard/OU=root/CN=http1.viv.vitessce.io/emailAddress=ilan_gold@hms.harvard.edu"
sed -i 's/SUBDOMAIN.viv.vitessce.io/http1.viv.vitessce.io' nginx.conf

EOF
}
*/