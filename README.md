# MediaFire Uploader

Simple GUI application to upload files to the MediaFire service


## How to run (venv)
- `python3 -m venv venv`
- `source venv/bin/activate`
- `pip install -r requirements.txt`
- `python ./upload.py`

**Note:** You need to run this script using the `python` version prior to the `python-3.10` (tested with `python-3.9.10`). since there is a change in `python-3.10` which broke the `MediaFire` SDK functionality
