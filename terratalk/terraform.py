import subprocess

class Terraform:

    def show(self, plan_file):
        filtered_plan_output = None

        try:
            plan_output = subprocess.Popen([
                'terraform',
                'show',
                '-no-color',
                plan_file,
            ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            filtered_plan_output = subprocess.check_output([
                'grep',
                '-E',
                '^\\s*# ',
            ], stdin=plan_output.stdout)
            plan_output.wait()
        except subprocess.CalledProcessError as exc:
            filtered_plan_output = exc.output

        if filtered_plan_output is None:
            return ''

        return filtered_plan_output.decode()
