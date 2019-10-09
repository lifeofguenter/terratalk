import subprocess

class Terraform:

    def show(self, plan_file):
        try:
            proc = subprocess.run([
                'terraform',
                'show',
                '-no-color',
                plan_file,
            ], capture_output=True)
            plan_output = proc.stdout
            if proc.stderr:
                plan_output = proc.stderr
        except subprocess.CalledProcessError as exc:
            plan_output = exc.output

        return plan_output.decode()
