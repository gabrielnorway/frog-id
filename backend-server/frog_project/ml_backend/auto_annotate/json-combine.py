import json
import os

files_list = []
for root, dirs, files in os.walk(r'/home/nos/hdd/code-school/bachelor-ikt300/Auto-Annotate/split_train/train/dir_015/'):
    for file in files:
        if file.endswith('.json'):
            files_list.append(os.path.join(root,file))


json_frogs = json.load(open(files_list[0]))

for i in range(len(files_list)):
    f = open(files_list[i])
    tmp_json = json.load(f)
    tmp_json["images"][0]["id"]=i
    tmp_json["annotations"][0]["image_id"]=i
    json_frogs["images"].append(tmp_json["images"][0])

    json_frogs["annotations"].append(tmp_json["annotations"][0])

json_out = open('/home/nos/hdd/code-school/bachelor-ikt300/Auto-Annotate/split_train/train/dir_015/annotations_combined.json', 'w')
json.dump(json_frogs, json_out, indent = 6)
json_out.close()
