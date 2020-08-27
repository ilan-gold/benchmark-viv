# End background `npm start` call.
trap 'jobs -p | xargs kill' EXIT

# Build the site out of the javascript directory.
cd js
npm start &

# Activate/create python environment.
cd ../python
python3 -m venv venv
source venv/bin/activate

# Install requirements.
python -m pip install -r requirements.txt
# Download BrowserMob Proxy (the path to the library is specifically used in the Python code).
if ! [[ -d "./browsermob-proxy-2.1.4" ]]; then
  wget https://github.com/lightbody/browsermob-proxy/releases/download/browsermob-proxy-2.1.4/browsermob-proxy-2.1.4-bin.zip -O browsermob-proxy.zip 
  unzip browsermob-proxy.zip 
  rm browsermob-proxy.zip 
fi

# Run test.
python benchmark.py