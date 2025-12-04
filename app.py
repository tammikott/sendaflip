import os
import random
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Ohutu faili tee (ei tee midagi ohtlikku)
DEMO_FILE = "demo_critical.txt"

def create_demo_file():
    """Loo demo fail, mida saab ohutult kustutada"""
    try:
        with open(DEMO_FILE, "w") as f:
            f.write("See on demo fail. Kui sa kaotad mängus, kustutatakse see.\n")
            f.write("See on OHUTU - see ei kahjusta sinu arvutit.\n")
        return True
    except:
        return False

def delete_demo_file():
    """Kustuta demo fail (ohutu)"""
    try:
        if os.path.exists(DEMO_FILE):
            os.remove(DEMO_FILE)
            return True
        return False
    except:
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/flip', methods=['POST'])
def flip_coin():
    data = request.json
    user_choice = data.get('choice', 'heads')  # 'heads' või 'tails'
    
    # Loo demo fail esimesel korral
    if not os.path.exists(DEMO_FILE):
        create_demo_file()
    
    # Viska münt
    result = random.choice(['heads', 'tails'])
    
    # Kontrolli tulemust
    if user_choice == result:
        return jsonify({
            'success': True,
            'result': result,
            'message': 'Palju õnne! Sa võitsid!',
            'danger': False
        })
    else:
        # Kaotuse korral kustuta demo fail
        deleted = delete_demo_file()
        message = 'Kahju! Sa kaotasid. Demo fail kustutatud.' if deleted else 'Kaotasid, aga demo faili ei kustutatud.'
        
        return jsonify({
            'success': False,
            'result': result,
            'message': message,
            'danger': False,  # Ohutu versioonis on alati False
            'file_deleted': deleted
        })

@app.route('/create-demo-file', methods=['POST'])
def create_file():
    """API endpoint demo faili loomiseks"""
    success = create_demo_file()
    return jsonify({'success': success, 'file': DEMO_FILE})

@app.route('/check-demo-file', methods=['GET'])
def check_file():
    """API endpoint demo faili kontrollimiseks"""
    exists = os.path.exists(DEMO_FILE)
    return jsonify({'exists': exists, 'file': DEMO_FILE})

if __name__ == '__main__':
    # Loo demo fail rakenduse käivitamisel
    create_demo_file()
    app.run(debug=True, host='0.0.0.0', port=5000)
