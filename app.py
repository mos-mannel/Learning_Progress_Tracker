from flask import Flask, render_template, request, redirect
import json
import os

app = Flask(__name__)
DATA_FILE = "data.json"


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {"modules": []}


def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)


@app.route('/')
def home():
    data = load_data()
    return render_template('home.html', modules=data['modules'])


@app.route('/add_module', methods=['POST'])
def add_module():
    name = request.form['name']
    data = load_data()
    data['modules'].append({
        'name': name,
        'completed': False,
        'submodules': []
    })
    save_data(data)
    return redirect('/')


@app.route('/add_submodule', methods=['POST'])
def add_submodule():
    module_index = int(request.form['module_index'])
    name = request.form['name']
    data = load_data()
    data['modules'][module_index]['submodules'].append({
        'name': name,
        'completed': False
    })
    save_data(data)
    return redirect('/')


@app.route('/update_progress', methods=['POST'])
def update_progress():
    data = load_data()

    # Reset all completion status
    for module in data['modules']:
        module['completed'] = False
        for submodule in module['submodules']:
            submodule['completed'] = False

    # Set completion based on form data
    for key in request.form:
        if key.startswith('module_') and '_sub_' in key:
            # Submodule: module_0_sub_1
            parts = key.split('_')
            module_idx = int(parts[1])
            submodule_idx = int(parts[3])
            data['modules'][module_idx]['submodules'][submodule_idx]['completed'] = True
        elif key.startswith('module_'):
            # Module: module_0
            module_idx = int(key.split('_')[1])
            data['modules'][module_idx]['completed'] = True

    save_data(data)
    return redirect('/')


@app.route('/delete_module/<int:index>')
def delete_module(index):
    data = load_data()
    if 0 <= index < len(data['modules']):
        data['modules'].pop(index)
        save_data(data)
    return redirect('/')


@app.route('/delete_submodule/<int:module_index>/<int:submodule_index>')
def delete_submodule(module_index, submodule_index):
    data = load_data()
    if (0 <= module_index < len(data['modules']) and
            0 <= submodule_index < len(data['modules'][module_index]['submodules'])):
        data['modules'][module_index]['submodules'].pop(submodule_index)
        save_data(data)
    return redirect('/')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)