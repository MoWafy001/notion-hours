const goalSelect = document.getElementById("goal");
const taskSelect = document.getElementById("task");
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
  goalSelect.innerHTML = goals
    .map((goal) => {
      return `<option value="${goal.id}">${goal.name}</option>`;
    })
    .join("");
  goalSelect.disabled = false;
  currentGoal = goalSelect.value;
  await fetchTasks();
};

const fetchTasks = async () => {
  if (!currentGoal) return;
  taskSelect.disabled = true;
  const res = await fetch(`/api/goals/${currentGoal}/tasks`);
  tasks = await res.json();
  taskSelect.innerHTML = tasks
    .map((task) => {
      return `<option value="${task.id}">${task.title}</option>`;
    })
    .join("");
  taskSelect.disabled = false;
};

goalSelect.onchange = async () => {
  currentGoal = goalSelect.value;
  await fetchTasks();
};
taskSelect.onchange = () => {
  currentTask = taskSelect.value;
};

fetchGoals();
