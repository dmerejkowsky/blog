import argparse
import subprocess
import httpx
from path import Path
import tarfile
import ruamel.yaml
import shutil

from io import BytesIO
import cli_ui as ui


class Installer:
    def __init__(self, force=False):
        self.conf = ruamel.yaml.safe_load(Path("configs.yml").text())
        self.this_dir = Path.getcwd()
        self.home = Path("~").expanduser()
        self.force = force

    def pretty_path(self, p):
        relpath = p.relpath(self.home)
        return "~/" + relpath

    def do_clone(self, url, dest, branch="master"):
        dest = Path(dest).expanduser()
        pretty_dest = self.pretty_path(dest)
        dest.parent.makedirs_p()
        if dest.exists():
            if self.force:
                dest.rmtree()
            else:
                ui.info_2("Skipping", pretty_dest)
                return
        ui.info_2("Cloning", url, "->", pretty_dest)
        subprocess.check_call(["git", "clone", url, dest, "--branch", branch])

    def do_copy(self, src, dest):
        dest = Path(dest).expanduser()
        pretty_dest = self.pretty_path(dest)
        dest.parent.makedirs_p()
        if dest.exists() and not self.force:
            ui.info_2("Skipping", pretty_dest)
            return
        src = self.this_dir / "configs/" / src
        ui.info_2("Copy", src, "->", self.pretty_path(src))
        src.copy(dest)

    def do_download(self, *, url, dest, executable=False, extract_member=None):
        dest = Path(dest).expanduser()
        dest.parent.makedirs_p()
        if extract_member:
            self._download_and_extract_member(url, dest, member=extract_member)
        else:
            self._download(url, dest)
        if executable:
            dest.chmod(0o755)


    def _download(self, url, dest):
        pretty_dest = self.pretty_path(dest)
        if dest.exists() and not self.force:
            ui.info_2("Skipping", pretty_dest)
        else:
            ui.info_2("Fetching", url, "->", pretty_dest)
            with open(dest, "wb") as o:
                with httpx.stream("GET", url) as r:
                    for buffer in r.iter_bytes():
                        o.write(buffer)


    def _download_and_extract_member(self, url, dest, *, member):
        pretty_dest = self.pretty_path(dest)
        if dest.exists() and not self.force:
            ui.info_2("Skipping", pretty_dest)
        else:
            ui.info_2("Fetching", url, "->", pretty_dest)
            r = httpx.get(url)
            ar = tarfile.open(fileobj=BytesIO(r.content), mode="r:gz")
            with ar.extractfile(member) as f, open(dest, "wb") as o:
                shutil.copyfileobj(f, o)


    def do_write(self, src, contents):
        src = Path(src).expanduser()
        pretty_src = self.pretty_path(src)
        if src.exists() and not self.force:
            ui.info_2("Skipping", pretty_src)
            return
        ui.info_2("Creating", pretty_src)
        src.parent.makedirs_p()
        contents = contents.format(this_dir=self.this_dir, home=self.home)
        if not contents.endswith("\n"):
            contents += "\n"
        src.write_text(contents)

    def do_symlink(self, src, dest):
        self._do_simlink(src, dest, is_dir=False)

    def do_symlink_dir(self, src, dest):
        self._do_simlink(src, dest, is_dir=True)

    def _do_simlink(self, src, dest, *, is_dir):
        dest = Path(dest).expanduser()
        pretty_dest = self.pretty_path(dest)
        if is_dir:
            dest.parent.parent.makedirs_p()
        else:
            dest.parent.makedirs_p()

        if dest.exists() and not self.force:
            ui.info_2("Skipping", pretty_dest)
            return
        if dest.islink():
            # if self.force is True, we want to re-create the symlink
            # else, we know it's a broken symlink
            # in any case: remove it
            dest.remove()
        ui.info_2("Symlink", pretty_dest, "->", src)
        src_full = self.this_dir / "configs" / src
        src_full.symlink(dest)

    def do_run(self, args):
        ui.info_2("Running", "`%s`" % " ".join(args))
        fixed_args = [x.format(home=self.home) for x in args]
        subprocess.check_call(fixed_args)

    def install_program(self, program):
        ui.info(ui.green, program)
        ui.info("-" * len(program))
        todo = self.conf[program]
        for action in todo:
            name = list(action.keys())[0]
            params = action[name]
            func = getattr(self, "do_%s" % name)
            if isinstance(params, dict):
                func(**params)
            else:
                func(*params)
        ui.info()

    def install(self, programs=None):
        if not programs:
            programs = sorted(self.conf.keys())
        for program in programs:
            self.install_program(program)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("programs", nargs="*")
    parser.add_argument("--force", action="store_true", help="Overwite existing files")
    args = parser.parse_args()

    force = args.force
    programs = args.programs
    installer = Installer(force=force)
    installer.install(programs=programs)


if __name__ == "__main__":
    main()
