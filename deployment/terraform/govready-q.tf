provider "aws" {
  region = "us-east-2"
}

resource "aws_instance" "example" {
  key_name = "terraform-us-east-2"
  ami= "ami-9c0638f9" # CentOS Linux 7 x86_64 HVM EBS ENA 1805_01-b7ee8a69-ee97-4a49-9e68-afaee216db2e-ami-77ec9308.4
  instance_type = "t2.nano" # nano for testing Terraform script; larger to actually run GovReady-Q

  provisioner "remote-exec" {
    inline = [
      "sudo /usr/bin/rpm -i https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm https://rhel7.iuscommunity.org/ius-release.rpm",
      "sudo /usr/bin/yum install -y git2u",
      "sudo useradd govready-q -c 'govready-q'",
      "sudo chmod a+rx /home/govready-q",
      "sudo yum install -y --disablerepo=ius unzip gcc python34-pip python34-devel graphviz pandoc xorg-x11-server-Xvfb wkhtmltopdf postgresql mysql-devel",
      "pip3 install --upgrade pip",
      "sudo su - govready-q -c 'cd && git clone https://github.com/govready/govready-q'",
      "sudo su - govready-q -c 'cd ~/govready-q && git checkout v0.8.4'",
      "sudo su - govready-q -c 'cd ~/govready-q && pip3 install --user -r requirements.txt'",
      "sudo su - govready-q -c 'cd ~/govready-q && ./fetch-vendor-resources.sh'"
    ]

    connection {
      type = "ssh"
      user = "centos"
      private_key = "${file("/root/.ssh/terraform-us-east-2.pem")}"
    }
  }
}
