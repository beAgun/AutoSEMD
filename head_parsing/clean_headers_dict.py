import json
from copy import deepcopy
from pprint import pprint


def main():
    output_file = 'cleaned_base_headers_values.json'

    with open('./base_headers_values.json', 'r') as f:
        dict = json.load(f)
        # pprint(dict)

    clean_dict = deepcopy(dict)
    for key in dict:
        for attr in dict[key]:
            if not isinstance(dict[key][attr], int) and 'examples' not in dict[key][attr] or isinstance(dict[key][attr], int):
                continue
            dict[key][attr]['examples'].sort()
            if dict[key][attr]['examples'][0] == dict[key][attr]['examples'][-1]:
                del clean_dict[key][attr]

    with open(output_file, 'w', encoding='utf-8') as json_file:
        json.dump(clean_dict, json_file, ensure_ascii=False, indent=4)

    print(len(clean_dict))


if __name__ == '__main__':
    main()