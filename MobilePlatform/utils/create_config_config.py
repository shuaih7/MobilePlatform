import os, sys, json

def create_config_matrix(json_file):
    op_names = ["Connie Fu", "Jaz Guo", "Jay Han"]
    op_level = ["Administrator", "User", "User"]
    js_obj = {
        "Names":   op_names,
        "Levels":  op_level,
        "BleBrightness": 65,
        "BleOnDelay": 80,
        "BleOffDelay": 80
    }
    with open (json_file, "w") as f:
        json.dump(js_obj, f, indent=4)
        
        
if __name__ == "__main__":
    json_file = r"config.json"
    create_config_matrix(json_file)
    print("Done")