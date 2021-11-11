import re
import subprocess


class TerraformOut:

    PREFIXES = {
        'created':      '+ ',
        'destroyed':    '- ',
        'in-place':     '@ ',
        'replaced':     '-+',
    }

    def __init__(self, plan_file: str) -> None:
        self.plan_file = plan_file
        self._plan_status = True
        self._raw_output = None
        self._parsed_output = None

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

        if not self._plan_status:
            return self._raw_output

        matches = re.findall(
            r'^[\t ]*# ([^(].*?) ([a-z-]+)$',
            self._raw_output.rstrip(),
            re.IGNORECASE | re.MULTILINE,
        )

        for m in matches:
            plan_output += f"{self._prefix(m[1])} {' '.join(m)}\n"

        match = re.search(
            r'Plan: (\d+) to add, (\d+) to change, (\d+) to destroy\.$',
            self._raw_output.rstrip(),
            re.IGNORECASE | re.MULTILINE,
        )

        if not match and not matches:
            return ''

        elif match and sum([int(s) for s in match.group(1, 2, 3)]) == 0:
            return ''

        elif match:
            plan_output += "\n" + match.group(0)

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
            self._plan_status = False
            return exc.stderr.decode()

        return buf.stdout.decode()

    def _prefix(self, verb: str) -> str:
        if verb in self.PREFIXES:
            return self.PREFIXES[verb]

        return '# '
