# End background call.
trap 'jobs -p | xargs kill' EXIT

# Build the site out of the javascript directory.
cd js
npm i
npm i -g crx3
crx3 har_extension
npm start &

# Activate/create python environment.
cd ../python
python3 -m venv venv
source venv/bin/activate

# Install requirements.
python -m pip install -r requirements.txt

# Run test.
python benchmark.py