const taskInput = document.getElementById("taskInput");
const taskList = document.getElementById("taskList");

function loadTasks() {
  const tasks = JSON.parse(localStorage.getItem("tasks")) || [];
  tasks.forEach(addTaskToDOM);
}

function saveTasks() {
  const tasks = [];
  document.querySelectorAll("#taskList li").forEach(li => {
    tasks.push({ text: li.firstChild.textContent, done: li.classList.contains("done") });
  });
  localStorage.setItem("tasks", JSON.stringify(tasks));
}

function addTask() {
  if (taskInput.value.trim() === "") return;
  addTaskToDOM({ text: taskInput.value, done: false });
  saveTasks();
  taskInput.value = "";
}

function addTaskToDOM(task) {
  const li = document.createElement("li");
  li.textContent = task.text;
  if (task.done) li.classList.add("done");

  const toggleBtn = document.createElement("button");
  toggleBtn.textContent = "✔";
  toggleBtn.onclick = () => {
    li.classList.toggle("done");
    saveTasks();
  };

  const deleteBtn = document.createElement("button");
  deleteBtn.textContent = "❌";
  deleteBtn.onclick = () => {
    li.remove();
    saveTasks();
  };

  li.appendChild(toggleBtn);
  li.appendChild(deleteBtn);
  taskList.appendChild(li);
}

// Load existing tasks on page load
loadTasks();
