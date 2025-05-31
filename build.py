# build.py
import subprocess
import toml  # надо установить через pip install toml

def main(debug_build: bool=False):
    with open("./pyproject.toml", "r", encoding="utf-8") as f:
        config = toml.load(f)
    name = config["project"]["name"]
    version = config["project"]["version"]
    exe_name = f"{name}-{version}" + ("-debug" if debug_build else "")

    cmd = [
        "pyinstaller",
        "--onefile",
        "--clean",
        "--icon=assets/icon.ico",
        f"--add-data=assets{';' if os.name == 'nt' else ':'}assets",
        "main.py",
        "-n",
        exe_name,
    ]
    if not debug_build:
        cmd.insert(2, "--windowed")
    subprocess.run(cmd, check=True)

if __name__ == "__main__":
    from sys import argv
    import os
    main("debug" in argv)
