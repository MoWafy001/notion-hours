const goalSearch = document.getElementById("goal-search");
const goalList = document.getElementById("goal-list");
const taskSearch = document.getElementById("task-search");
const taskList = document.getElementById("task-list");
const timer = document.getElementById("timer");
const loadingOverlay = document.getElementById("loading-overlay");
const taskInfo = document.getElementById("task-info");
const tasksDoneTodayList = document.getElementById("tasks-done-today-list");

// buttons
const startBtn = document.getElementById("start");
const resumeBtn = document.getElementById("resume");
const pauseBtn = document.getElementById("pause");
const resetBtn = document.getElementById("reset");
const endBtn = document.getElementById("end");
const deleteBtn = document.getElementById("delete");

// vars
var goals = [];
var tasks = [];
var currentGoal = null;
var currentTask = null;
var time_start = null;
var timerInterval = null;
var time_diff_prefix = 0;
var tasksDoneToday = [];

// methods
const secondsToDuration = (seconds) => {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;

  const comps = [];
  if (hours > 0) comps.push(`${hours}h`);
  if (minutes > 0) comps.push(`${minutes}m`);
  if (secs > 0) comps.push(`${secs}s`);

  if (comps.length === 0) return "0s";
  return comps.join(":");
};

const fetchGoals = async () => {
  loadingOverlay.style.display = "flex";
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
  loadingOverlay.style.display = "none";
  await fetchTasks();
};

const getTasksDoneToday = async () => {
  const res = await fetch(`/api/tasks-done-today`);
  tasksDoneToday = (await res.json()).reduce((acc, task) => {
    const existing = acc.find(
      (t) => t.title === task.title && t.goal === task.goal
    );
    if (existing) {
      existing.duration_secs += task.duration_secs;
    } else {
      acc.push(task);
    }
    return acc;
  }, []);
  console.log(tasksDoneToday);
  tasksDoneTodayList.innerHTML = "";
  tasksDoneToday
    .map((task) => {
      const li = document.createElement("li");
      const goal = goals.find((g) => g.id === task.goal);
      li.innerHTML = `<span class="tdt-goal">${
        goal.name
      }</span> - <span class="tdt-title">${
        task.title
      }</span> - <span class="tdt-duration">${secondsToDuration(
        task.duration_secs
      )}</span>`;
      tasksDoneTodayList.append(li);
    })
    .join("");
};

const fetchTasks = async () => {
  if (!currentGoal) return;
  loadingOverlay.style.display = "flex";
  const res = await fetch(`/api/goals/${currentGoal.id}/tasks`);
  tasks = await res.json();
  taskList.innerHTML = "";
  tasks
    .map((task) => {
      const li = document.createElement("li");
      li.dataset.id = task.id;
      li.innerHTML = task.title;
      li.onclick = async () => {
        await setTask(task);
      };
      taskList.append(li);
    })
    .join("");
  loadingOverlay.style.display = "none";
  await setTask(tasks[0]);
  await getTasksDoneToday();
};

const setTask = async (task) => {
  currentTask = task;
  taskSearch.value = currentTask.title;
  taskInfo.innerHTML = `
    <h4>${task.title}</h4>
    <p>status: ${task.status}</p>
  `;
  if (task.date_start) {
    taskInfo.innerHTML += `
      <p>start: ${task.date_start}</p>`;
  }
  if (task.date_end) {
    taskInfo.innerHTML += `
      <zp>end: ${task.date_end}</p>`;
  }

  if (task.status === "Not started") {
    startBtn.style.display = "block";
    resumeBtn.style.display = "none";
    pauseBtn.style.display = "none";
    resetBtn.style.display = "none";
    endBtn.style.display = "none";
    deleteBtn.style.display = "block";
  } else if (task.status === "In progress") {
    startBtn.style.display = "none";
    resumeBtn.style.display = "block";
    pauseBtn.style.display = "none";
    resetBtn.style.display = "none";
    endBtn.style.display = "none";
    deleteBtn.style.display = "block";
  } else {
    startBtn.style.display = "none";
    resumeBtn.style.display = "none";
    pauseBtn.style.display = "none";
    resetBtn.style.display = "none";
    endBtn.style.display = "none";
    deleteBtn.style.display = "block";
  }
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
taskSearch.onkeyup = async () => {
  taskList.innerHTML = "";
  tasks
    .filter((task) => {
      const value = taskSearch.value.toLowerCase().trim();
      if (!value) return true;
      return task.title.toLowerCase().includes(value);
    })
    .map((task) => {
      const li = document.createElement("li");
      li.dataset.id = task.id;
      li.innerHTML = task.title;
      li.onclick = async () => {
        await setTask(task);
      };
      taskList.append(li);
    });


  // if goalList is empty, add new button
  if (taskList.innerHTML === "") {
    const li = document.createElement("li");
    const btn = document.createElement("button");
    const name = taskSearch.value.trim();
    if (!name) return;
    btn.innerHTML = `Create ${name}`;
    btn.style.width = "100%";
    btn.onclick = async () => {
      const name = taskSearch.value.trim();
      if (!name) return alert("Please enter a name for the task");
      const res = await fetch(`/api/goals/${currentGoal.id}/tasks`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ name }),
      });
      const task = await res.json();
      await fetchTasks();
      await setTask(task);
    };
    li.append(btn);
    taskList.append(li);
  }
};

fetchGoals();

const startTimer = () => {
  time_start = new Date();
  timerInterval = setInterval(() => {
    const time_now = new Date();
    const time_diff = time_now - time_start + time_diff_prefix;
    timer.innerHTML = new Date(time_diff).toISOString().substr(11, 8);
  }, 1000);
  timer.style.animation = "rotate 1s linear infinite";
};

const stopTimer = () => {
  clearInterval(timerInterval);
  timer.innerHTML = "00:00:00";
  timer.style.animation = "";
  time_diff = 0;
  time_diff_prefix = 0;
};

const pauseTimer = () => {
  clearInterval(timerInterval);
  timer.style.animation = "";
};

startBtn.onclick = async () => {
  loadingOverlay.style.display = "flex";
  const res = await fetch(`/api/tasks/${currentTask.id}/start`, {
    method: "POST",
  });
  startTimer();
  const task = await res.json();
  await fetchTasks();
  await setTask(task);

  startBtn.style.display = "none";
  resumeBtn.style.display = "none";
  pauseBtn.style.display = "block";
  resetBtn.style.display = "block";
  endBtn.style.display = "block";
  deleteBtn.style.display = "block";
};

resumeBtn.onclick = async () => {
  loadingOverlay.style.display = "flex";
  const res = await fetch(`/api/tasks/${currentTask.id}/resume`, {
    method: "POST",
  });
  startTimer();
  const task = await res.json();
  await fetchTasks();
  await setTask(task);

  startBtn.style.display = "none";
  resumeBtn.style.display = "none";
  pauseBtn.style.display = "block";
  resetBtn.style.display = "block";
  endBtn.style.display = "block";
  deleteBtn.style.display = "block";
};

pauseBtn.onclick = async () => {
  loadingOverlay.style.display = "flex";
  pauseTimer();
  const res = await fetch(`/api/tasks/${currentTask.id}/pause`, {
    method: "POST",
  });
  const task = await res.json();
  await fetchTasks();
  await setTask(task);

  startBtn.style.display = "none";
  resumeBtn.style.display = "block";
  pauseBtn.style.display = "none";
  resetBtn.style.display = "block";
  endBtn.style.display = "block";
  deleteBtn.style.display = "block";
};

resetBtn.onclick = async () => {
  loadingOverlay.style.display = "flex";
  stopTimer();
  const res = await fetch(`/api/tasks/${currentTask.id}/start`, {
    method: "POST",
  });
  const task = await res.json();
  await fetchTasks();
  await setTask(task);

  startBtn.style.display = "block";
  resumeBtn.style.display = "none";
  pauseBtn.style.display = "none";
  resetBtn.style.display = "none";
  endBtn.style.display = "none";
  deleteBtn.style.display = "block";
};

endBtn.onclick = async () => {
  loadingOverlay.style.display = "flex";
  stopTimer();
  const res = await fetch(`/api/tasks/${currentTask.id}/done`, {
    method: "POST",
  });
  await fetchTasks();

  startBtn.style.display = "none";
  resumeBtn.style.display = "none";
  pauseBtn.style.display = "none";
  resetBtn.style.display = "none";
  endBtn.style.display = "none";
  deleteBtn.style.display = "none";
};

deleteBtn.onclick = async () => {
  loadingOverlay.style.display = "flex";
  stopTimer();
  const res = await fetch(`/api/tasks/${currentTask.id}/delete`, {
    method: "POST",
  });
  await fetchTasks();

  startBtn.style.display = "none";
  resumeBtn.style.display = "none";
  pauseBtn.style.display = "none";
  resetBtn.style.display = "none";
  endBtn.style.display = "none";
  deleteBtn.style.display = "none";
};
