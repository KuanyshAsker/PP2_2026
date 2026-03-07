import json
x = { "name": "kuanysh", "age": 19}
y = json.dumps(x, indent=4, sort_keys=True)
print(y)