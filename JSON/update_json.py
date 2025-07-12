import json


with open('ex5.json', 'r') as file:
    ex5 = json.load(file)


for donut in ex5:
    if donut.get("name") == "Old Fashioned":
     
        new_batter = {"id": "1005", "type": "Tea"}
        donut["batters"]["batter"].append(new_batter)
        break  


with open('ex5.json', 'w') as file:
    json.dump(ex5, file, indent=4)

print("New batter added to 'Old Fashioned'.")
