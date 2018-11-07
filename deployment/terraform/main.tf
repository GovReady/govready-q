provider "aws" {
  region = "${var.aws_region}"
}

resource "aws_instance" "govready-q" {
  key_name = "${lookup(var.aws_key_name, var.aws_region)}"
  ami = "${lookup(var.aws_amis, var.aws_region)}"
  instance_type = "${var.aws_instance_type}"

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
      private_key = "${file(var.private_key_path)}"
    }
  }
}
