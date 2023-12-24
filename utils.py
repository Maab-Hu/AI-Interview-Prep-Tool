import json


def select_questions(category):
    with open(str(category)+".json", 'r') as file:
        data = json.load(file)
        return data


q = select_questions("Technical")
print(q)

