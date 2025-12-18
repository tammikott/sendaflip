#!/bin/bash
# Peata vanad protsessid
pkill -f "python.*app.py" 2>/dev/null
pkill -f flask 2>/dev/null

# Oota, et protsessid peatuvad
sleep 2

# Käivita uus protsess ilma debug reloader'ita
cd ~/sendaflip
export FLASK_DEBUG=0
export PYTHONPATH=.
exec python3 -c "
import sys
sys.path.insert(0, '.')
from app import app
print('Starting SendaFlip on http://0.0.0.0:5000')
print('Press Ctrl+C to stop')
app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
"
