import json

def create_input_file(jsonFile):
    dataset = jsonFile['d']
    with open("input/ds_api.json", "w") as outfile:
        json.dump(dataset, outfile, indent=4)

    estimator = jsonFile['e']
    with open("input/est_api.json", "w") as outfile:
        json.dump(estimator, outfile, indent=4)

    preprocessing = jsonFile['p']
    with open("input/pp_api.json", "w") as outfile:
        json.dump(preprocessing, outfile, indent=4)

    selection = jsonFile['s']
    with open("input/ms_api.json", "w") as outfile:
        json.dump(selection, outfile, indent=4)
    
    output = jsonFile['o']
    with open("input/output_api.json", "w") as outfile:
        json.dump(output, outfile, indent=4)

    return