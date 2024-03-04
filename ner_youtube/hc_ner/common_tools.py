import json

def load_data(file, encoding="utf-8"):
    with open(file,'r', encoding=encoding) as f:
        data=f.read()
    return data

def save_data(file, data, encoding="utf-8"):
    with open (file, "w", encoding=encoding) as f:
        f.write(data)

def load_data_json(file, encoding="utf-8"):
    with open(file,'r', encoding=encoding) as f:
        data = json.load(f)
    return data

def save_data_json(file, data, encoding="utf-8"):
    with open (file, "w", encoding=encoding) as f:
        json.dump(data, f, indent=4)


