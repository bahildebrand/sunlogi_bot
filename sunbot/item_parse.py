import json

f = open("items.json", "r")
item_obj = json.load(f)

items = []
for item in item_obj:
    items.append(item['itemName'])

pretty_json = json.dumps(items, indent=2)
out_file = open("item_list.json", "w")
print(pretty_json)
out_file.write(pretty_json)
