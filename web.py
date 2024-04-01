import os
from notion_client import Client
from flask import Flask, render_template
from dotenv import load_dotenv
load_dotenv()

notion = Client(auth=os.getenv('NOTION_API_SECRET'))
tasks_database_id = os.getenv('NOTION_DATABASE_ID')
goals_database_id = os.getenv('NOTION_GOALS_DATABASE_ID')
goal_uuid = os.getenv('NOTION_GOAL_UUID')
port = os.getenv('PORT', '5000')


app = Flask(__name__)


@app.get('/')
def index():
    return render_template('index.html')


@app.get('/api/goals')
def listGoals():
    # list goals records from the goals database
    goals = notion.databases.query(goals_database_id, filters=[
        ])['results']
    parsed_goals = list(map(lambda goal: {
        'id': goal['id'],
        'name': goal['properties']['name']['title'][0]['plain_text'],
    }, goals))
    return parsed_goals


@app.get('/api/goals/<goal_id>/tasks')
def listTasks(goal_id):
    # list tasks records from the tasks database
    filters = [
        {
            "property": "Goal",
            "relation": {
                "contains": goal_id
            }
        },
        {
            "property": "status",
            "status": {
                        "does_not_equal": "Done"
            },
        },
        {
            "property": "status",
            "status": {
                        "does_not_equal": "Failed"
            }
        }
    ]

    response = notion.databases.query(
        tasks_database_id,
        filter={
            "and": filters
        }
    )
    tasks = response['results']
    parsed_tasks = list(map(lambda task: {
        'id': task['id'],
        'title': task['properties']['title']['title'][0]['plain_text'],
        'date': task['properties']['when']['date']['start'],
        "status": task['properties']['status']['status']['name']
    }, tasks))
    return parsed_tasks


if __name__ == '__main__':
    app.run(port=int(port))
