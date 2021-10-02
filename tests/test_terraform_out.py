import unittest

from terratalk.terraform_out import TerraformOut


class TestTerraformOut(unittest.TestCase):

    def test_does_nothing(self):
        tf = TerraformOut('foo.plan')
        tf._raw_output = '''
No changes. Your infrastructure matches the configuration.

Terraform has compared your real infrastructure against your configuration and found no differences, so no changes are needed.
'''
        self.assertEqual(tf.does_nothing(), True)

    def test_create(self):
        tf = TerraformOut('foo.plan')
        tf._raw_output = '''
Terraform used the selected providers to generate the following execution plan. Resource actions are indicated with the following symbols:
  + create

Terraform will perform the following actions:

  # aws_key_pair.deployer will be created
  + resource "aws_key_pair" "deployer" {
      + arn         = (known after apply)
      + fingerprint = (known after apply)
      + id          = (known after apply)
      + key_name    = "deployer-key"
      + key_pair_id = (known after apply)
      + public_key  = "ssh-rsa "
      + tags_all    = (known after apply)
    }

Plan: 1 to add, 0 to change, 0 to destroy.
'''

        self.assertEqual(tf.show(), '''
# aws_key_pair.deployer will be created

Plan: 1 to add, 0 to change, 0 to destroy.
'''.strip())

    def test_change(self):
        tf = TerraformOut('foo.plan')
        tf._raw_output = '''
Note: Objects have changed outside of Terraform

Terraform detected the following changes made outside of Terraform since the last "terraform apply":

  # aws_key_pair.deployer has been changed
  ~ resource "aws_key_pair" "deployer" {
        id          = "deployer-key"
      + tags        = {}
        # (6 unchanged attributes hidden)
    }

Unless you have made equivalent changes to your configuration, or ignored the relevant attributes using ignore_changes, the following plan may include actions to undo or respond to these changes.

──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

No changes. Your infrastructure matches the configuration.

Your configuration already matches the changes detected above. If you'd like to update the Terraform state to match, create and apply a refresh-only plan:
  terraform apply -refresh-only
'''

        self.assertEqual(tf.show(), '''
# aws_key_pair.deployer has been changed
'''.strip())

    def test_update(self):
        tf = TerraformOut('foo.plan')
        tf._raw_output = '''

Terraform used the selected providers to generate the following execution plan. Resource actions are indicated with the following symbols:
  ~ update in-place

Terraform will perform the following actions:

  # aws_key_pair.deployer will be updated in-place
  ~ resource "aws_key_pair" "deployer" {
        id          = "deployer-key"
      ~ tags        = {
          + "Foo" = "Bar"
        }
      ~ tags_all    = {
          + "Foo" = "Bar"
        }
        # (5 unchanged attributes hidden)
    }

Plan: 0 to add, 1 to change, 0 to destroy.
'''
        self.assertEqual(tf.show(), '''
# aws_key_pair.deployer will be updated in-place

Plan: 0 to add, 1 to change, 0 to destroy.
'''.strip())


if __name__ == '__main__':
    unittest.main()
