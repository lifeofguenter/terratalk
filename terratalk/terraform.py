import re
import subprocess


class Terraform:

    @staticmethod
    def show(plan_file):

        try:
            tf_show = subprocess.run([
                'terraform',
                'show',
                '-no-color',
                plan_file,
            ], capture_output=True, check=True)
        except subprocess.CalledProcessError as exc:
            return exc.stderr.decode()

        raw_plan_output = tf_show.stdout.decode()
        plan_output = ''

        if re.search(r'Plan: 0 to add, 0 to change, 0 to destroy.\Z', raw_plan_output.rstrip(), re.IGNORECASE):
            return ''

        matches = re.findall(r'^(?:[\t ]*(#.*)|(Plan: \d+ to add, \d+ to change, \d+ to destroy\.))$', raw_plan_output.rstrip(), re.IGNORECASE|re.MULTILINE)
        for m in matches:
            if m[1] != '':
                plan_output += "\n"
            plan_output += ''.join(m) + "\n"

        return plan_output
