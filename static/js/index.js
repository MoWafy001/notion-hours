const goalSearch = document.getElementById("goal-search");
const goalList = document.getElementById("goal-list");
const taskSearch = document.getElementById("task-search");
const taskList = document.getElementById("task-list");
const timer = document.getElementById("timer");

// buttons
const startBtn = document.getElementById("start");
const stopBtn = document.getElementById("resume");
const pauseBtn = document.getElementById("pause");
const resetBtn = document.getElementById("reset");
const endBtn = document.getElementById("end");
const deleteBtn = document.getElementById("delete");

// vars
var goals = [];
var tasks = [];
var currentGoal = null;
var currentTask = null;

// methods
const fetchGoals = async () => {
  const res = await fetch("/api/goals");
  goals = await res.json();
  goalList.innerHTML = "";
  goals
    .map((goal) => {
      const li = document.createElement("li");
      li.dataset.id = goal.id;
      li.innerHTML = goal.name;
      li.onclick = async () => {
        currentGoal = goal;
        goalSearch.value = currentGoal.name;
        await fetchTasks();
      };
      goalList.append(li);
    })
    .join("");
  currentGoal = goals[0];
  goalSearch.value = currentGoal.name;
  await fetchTasks();
};

const fetchTasks = async () => {
  if (!currentGoal) return;
  const res = await fetch(`/api/goals/${currentGoal.id}/tasks`);
  tasks = await res.json();
  taskList.innerHTML = "";
  tasks
    .map((task) => {
      const li = document.createElement("li");
      li.dataset.id = task.id;
      li.innerHTML = task.title;
      li.onclick = async () => {
        currentTask = task;
        taskSearch.value = currentTask.title;
      };
      taskList.append(li);
    })
    .join("");
  currentTask = tasks[0];
  taskSearch.value = currentTask.title;
};

goalSearch.onkeyup = async () => {
  goalList.innerHTML = "";
  goals
    .filter((goal) => {
      const value = goalSearch.value.toLowerCase().trim();
      if (!value) return true;
      return goal.name.toLowerCase().includes(value);
    })
    .map((goal) => {
      const li = document.createElement("li");
      li.dataset.id = goal.id;
      li.innerHTML = goal.name;
      li.onclick = async () => {
        currentGoal = goal;
        goalSearch.value = currentGoal.name;
        await fetchTasks();
      };
      goalList.append(li);
    });
};
taskSearch.onchange = () => {
  currentTask = taskSelect.value;
};

fetchGoals();
