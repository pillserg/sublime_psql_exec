import subprocess
import tempfile
import os

import sublime
import sublime_plugin


class PsqlExecCommand(sublime_plugin.TextCommand):
    def run(self, edit, dbname):
        sel_list = [self.view.substr(region) for region in self.view.sel() if not region.empty()]
        command = '\n'.join(sel_list)

        proc = subprocess.Popen(
            ["psql", "-h", "db", "-d", dbname, "-c", command, "-U", "postgres"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        result = proc.stdout.read() + proc.stderr.read()

        if not result:
            return

        psqlexecresult = os.path.join(tempfile.gettempdir(), 'psqlexec')
        with open(psqlexecresult, 'wb') as f:
            f.write(result)

        self.view.window().open_file(psqlexecresult)
