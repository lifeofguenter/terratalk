terraform {
  required_providers {
    null = {
      source = "hashicorp/null"
      version = "3.2.3"
    }
  }
}

provider "null" {
}

resource "null_resource" "foobar" {
}
