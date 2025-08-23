from venv import create
from os.path import join, expanduser, abspath
from subprocess import run

dir = join(expanduser("~"), "assistant_venv")
create(dir, with_pip=True)

# where requirements.txt is in same dir as this script
run(["bin/pip", "install", "-r", abspath("requirements.txt")], cwd=dir)