# Printable Export from Bitwarden / Vaultwarden
Generate printable PDF from Bitwarden JSON export

## Usage
Export unencrypted JSON from Bitwarden/Vaultwarden webinterface, place in this directory and run `python3 process.py`

The latest export will be detected automatically by date in filename.


## Requirements
Create venv with `python3 -m venv venv`. Activate with `. ./venv/bin/activate`.

Install requirements with `pip3 install -r requirements.txt`.
