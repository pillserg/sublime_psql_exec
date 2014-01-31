import subprocess
import tempfile
import os
import re

import sublime
import sublime_plugin


class PsqlExecCommand(sublime_plugin.TextCommand):
    def run(self, edit, dbname=None):
        def clean_command(dbname, cmd):
            if dbname:
                cmd = cmd.replace("{%s}" % dbname, '')
                cmd = cmd.strip()
            return cmd

        def parse_dbname(cmd):
            mathes = re.findall(
                "{(uaprom|ruprom|belprom|kazprom|mdprom|uaprom2|ruprom2|belprom2|kazprom2|mdprom2)}",
                cmd
            )
            return mathes[0] if mathes else None

        str_lst = [self.view.substr(region) for region in self.view.sel() if not region.empty()]

        if not str_lst:
            print('psqlExec::no selection')
            return

        if not dbname:
            dbname = parse_dbname(str_lst[0])
            if not dbname:
                dbname = 'uaprom2'
                print('psqlExec::using default dbname: uaprom2')
            else:
                print('psqlExec::parsed dbname: {0}'.format(dbname))

        str_lst = [clean_command(dbname, cmd) for cmd in str_lst]

        command = '\n'.join(str_lst)

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
