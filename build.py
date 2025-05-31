# build.py
import subprocess
import toml  # надо установить через pip install toml

def main():
    with open("./pyproject.toml", "r", encoding="utf-8") as f:
        config = toml.load(f)
    name = config["project"]["name"]
    version = config["project"]["version"]
    exe_name = f"{name}-{version}"

    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--icon=assets/icon.ico",
        f"--add-data=assets{';' if os.name == 'nt' else ':'}assets",
        "main.py",
        "-n",
        exe_name,
    ]
    subprocess.run(cmd, check=True)

if __name__ == "__main__":
    import os
    main()
