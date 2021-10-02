import re
import subprocess


class TerraformOut:

    plan_file = None
    _raw_output = None
    _parsed_output = None

    def __init__(self, plan_file: str) -> None:
        self.plan_file = plan_file

    def show(self) -> str:
        if not self._raw_output:
            self._raw_output = self._fetch_raw_output()

        if not self._parsed_output:
            self._parsed_output = self._parse_output()

        return self._parsed_output

    def does_nothing(self) -> bool:
        if self.show() == '':
            return True
        return False

    def _parse_output(self) -> str:
        plan_output = ''

        if re.search(
            r'Plan: 0 to add, 0 to change, 0 to destroy.\Z',
            self._raw_output.rstrip(),
            re.IGNORECASE,
        ):
            return ''

        matches = re.findall(
            r'^(?:[\t ]*(# [^(].*)|'
            r'(Plan: \d+ to add, \d+ to change, \d+ to destroy\.))$',
            self._raw_output.rstrip(),
            re.IGNORECASE | re.MULTILINE,
        )

        for m in matches:
            if m[1] != '':
                plan_output += "\n"
            plan_output += ''.join(m) + "\n"

        return plan_output.rstrip()

    def _fetch_raw_output(self) -> str:
        try:
            buf = subprocess.run([
                'terraform',
                'show',
                '-no-color',
                self.plan_file,
            ], capture_output=True, check=True)
        except subprocess.CalledProcessError as exc:
            return exc.stderr.decode()

        return buf.stdout.decode()
