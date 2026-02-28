import json
with open("sample-data.json", "r") as file:
    data = json.load(file)
print("Interface Status")
print("=" * 80)
print(f"{'DN':<50} {'Description':<20} {'Speed':<7} {'MTU':<6}")
print("-" * 80)
for item in data["imdata"]:
    att = item["l1PhysIf"]["attributes"]
    dn = att["dn"]
    des = att["descr"]
    speed = att["speed"]
    mtu = att["mtu"]
    print(f"{dn:<50} {des:<20} {speed:<7} {mtu:<6}")