from datetime import datetime
import os
from notion_client import Client
from flask import Flask, render_template, Response, request
from dotenv import load_dotenv
from dateutil import tz

load_dotenv()

current_time_zone = tz.tzlocal()

notion = Client(auth=os.getenv('NOTION_API_SECRET'))
tasks_database_id = os.getenv('NOTION_DATABASE_ID')
goals_database_id = os.getenv('NOTION_GOALS_DATABASE_ID')
goal_uuid = os.getenv('NOTION_GOAL_UUID')
port = os.getenv('PORT', '5000')


app = Flask(__name__)


def parseTask(task):
    date_start = None
    date_end = None
    date = task['properties']['when']['date']
    if date:
        date_start = date['start']
        date_end = date['end']
        if date_start and date_end:
            duration = datetime.fromisoformat(
                date_end) - datetime.fromisoformat(date_start)

    return {
        'id': task['id'],
        'title': task['properties']['title']['title'][0]['plain_text'],
        "status": task['properties']['status']['status']['name'],
        'date_start': date_start,
        'date_end': date_end,
        'duration_secs': duration.total_seconds() if date_end else None,
        'goal': task['properties']['Goal']['relation'][0]['id']
    }


def getTask(task_id):
    task = notion.pages.retrieve(task_id)
    return parseTask(task)


@app.get('/')
def index():
    return render_template('index.html')


@app.get('/api/goals')
def listGoals():
    # list goals records from the goals database
    goals = notion.databases.query(goals_database_id, filter={
        "or": [
            {
                "property": "Status",
                "title": {
                    "equals": "in progress"
                }
            },
            {
                "property": "Status",
                "title": {
                    "equals": "not started"
                }
            },
        ]
    },
    )['results']
    parsed_goals = list(map(lambda goal: {
        'id': goal['id'],
        'name': goal['properties']['name']['title'][0]['plain_text'],
    }, goals))
    return parsed_goals

# create a new task


@app.post('/api/goals/<goal_id>/tasks')
def createTask(goal_id):
    name = request.json['name']
    if not name:
        return Response('Name is required', status=400)

    response = notion.pages.create(
        parent={"database_id": tasks_database_id},
        properties={
            "title": {
                "title": [
                    {
                        "text": {
                            "content": name
                        }
                    }
                ]
            },
            "Goal": {
                "relation": [
                    {
                        "id": goal_id
                    }
                ]
            },
            "status": {
                "status": {
                    "name": "Not started"
                }
            }
        }
    )
    return parseTask(response)


# get tasks done or inprogress today
@app.get('/api/tasks-done-today')
def listTasksDoneToday():
    # list tasks records from the tasks database
    today_start_iso_str = datetime.now(tz=current_time_zone).replace(
        hour=0, minute=0, second=0, microsecond=0).isoformat()
    today_end_iso_str = datetime.now(tz=current_time_zone).replace(
        hour=23, minute=59, second=59, microsecond=999999).isoformat()

    filters = [
        {
            "or": [
                {
                    "property": "status",
                    "status": {
                        "equals": "Done"
                    }
                },
                {
                    "property": "status",
                    "status": {
                        "equals": "In progress"
                    }
                },
            ]
        },
        {
            "property": "when",
            "date": {
                "on_or_after": today_start_iso_str
            }
        },
        {
            "property": "when",
            "date": {
                "on_or_before": today_end_iso_str
            }
        }
    ]

    response = notion.databases.query(
        tasks_database_id,
        filter={
            "and": filters
        }
    )
    tasks = list(map(parseTask, response['results']))
    return tasks


@ app.get('/api/goals/<goal_id>/tasks')
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
    parsed_tasks = []
    for task in tasks:
        date_start = None
        date_end = None
        date = task['properties']['when']['date']
        if date:
            date_start = date['start']
            date_end = date['end']

        parsed_tasks.append({
            'id': task['id'],
            'title': task['properties']['title']['title'][0]['plain_text'],
            "status": task['properties']['status']['status']['name'],
            'date_start': date_start,
            'date_end': date_end,
        })
    return parsed_tasks


# set start date to now, and end date to none
@ app.post('/api/tasks/<task_id>/start')
def startTask(task_id):
    now = datetime.now(tz=current_time_zone)
    now_iso = now.isoformat()
    response = notion.pages.update(task_id, properties={
        "status": {
            "status": {
                "name": "In progress"
            }
        },
        "when": {
            "date": {
                "start": now_iso,
                "end": None
            }
        }
    })
    return parseTask(response)


# end the task and start a new duplicate task
@ app.post('/api/tasks/<task_id>/resume')
def resumeTask(task_id):
    task = getTask(task_id)
    now = datetime.now(tz=current_time_zone)
    now_iso = now.isoformat()
    response = notion.pages.update(task_id, properties={
        "status": {
            "status": {
                "name": "Done"
            }
        },
        "when": {
            "date": {
                "start": task['date_start'],
                "end": task['date_end'] or now_iso
            }
        }
    })
    response = notion.pages.create(
        parent={"database_id": tasks_database_id},
        properties={
            "title": {
                "title": [
                    {
                        "text": {
                            "content": response['properties']['title']['title'][0]['plain_text']
                        }
                    }
                ]
            },
            "Goal": {
                "relation": [
                    {
                        "id": response['properties']['Goal']['relation'][0]['id']
                    }
                ]
            },
            "status": {
                "status": {
                    "name": "In progress"
                }
            },
            "when": {
                "date": {
                    "start": now_iso,
                    "end": None
                }
            }
        }
    )
    return parseTask(response)

# set the end date to now


@ app.post('/api/tasks/<task_id>/pause')
def pauseTask(task_id):
    task = getTask(task_id)
    now = datetime.now(tz=current_time_zone)
    now_iso = now.isoformat()
    response = notion.pages.update(task_id, properties={
        "when": {
            "date": {
                "start": task['date_start'],
                "end": now_iso
            }
        }
    })
    return parseTask(response)

# set the status to done


@ app.post('/api/tasks/<task_id>/done')
def doneTask(task_id):
    task = getTask(task_id)
    now = datetime.now(tz=current_time_zone)
    now_iso = now.isoformat()
    response = notion.pages.update(task_id, properties={
        "status": {
            "status": {
                "name": "Done"
            }
        },
        "when": {
            "date": {
                "start": task['date_start'],
                "end": now_iso
            }
        }
    })
    return parseTask(response)

# archive the task


@ app.post('/api/tasks/<task_id>/delete')
def deleteTask(task_id):
    response = notion.pages.update(task_id, archived=True)
    return parseTask(response)


if __name__ == '__main__':
    app.run(port=int(port))
