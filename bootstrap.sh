set -x
set -e
curl -O https://bootstrap.pypa.io/get-pip.py
python3 get-pip.py --user
python3 -m pip install -r requirements.txt --user

curl https://sh.rustup.rs -sSf | sh

cargo install bat exa fd-find

sudo cp ./xkb-symbols-dmerej /usr/share/X11/xkb/symbols/dmerej
