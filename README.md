# SoD-Off - School of Dragons, Offline

On 7th June, 2023, School of Dragons announced they were "sunsetting" the game, and turning the servers off on the 30th of June.

## Getting started

For the first time setup, run the following commands:

```
# create a python virtual environment called 'venv'
python3 -m venv venv
source venv/bin/activate

# install the required dependencies from pip
pip install -r requirements.txt

# initialise the db
rm -rf instance/ && flask --app sodoff init-db

# create the data classes with generateDS
rm -rf ./sodoff/schema/*.py && find sodoff/schema/xsd -type f -name "*.xsd" -exec sh -c 'generateDS -o "./sodoff/schema/$(basename {} .xsd).py" "{}" || echo "failed processing: {}"' \;
```

Then run the server as follows:

```
# run mitmproxy to redirect requests to the app
mitmproxy -s mitm-redirect.py

# run the server
flask --app sodoff run --debug
```

Then run School of Dragons.

You can check if it is running by going to http://127.0.0.1:5000/health-check

## Status

### What works

- Registration
- Login

### What doesn't

Everything else

## Credits

A huge thanks to [BlazingTwist](https://github.com/BlazingTwist) for their [initial work](https://github.com/BlazingTwist/SoD_OfflineServer) and XSD creation.
