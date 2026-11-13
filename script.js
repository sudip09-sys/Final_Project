"use strict";

// This walkthrough has no camera, recognition model, server writes, or storage.
// All names and results below are fictional sample data.
const students = [
  { key: "anika", name: "Anika S.", id: "DEMO-001", initials: "AS" },
  { key: "min", name: "Min J.", id: "DEMO-002", initials: "MJ" },
  { key: "alex", name: "Alex R.", id: "DEMO-003", initials: "AR" }
];
const attendance = new Map();
const select = document.querySelector("#demo-student");
const button = document.querySelector("#simulate-checkin");
const station = document.querySelector(".demo-station");
const feedback = document.querySelector("#demo-feedback");
const dialog = document.querySelector("#manual-dialog");
let processing = false;
let pendingTimer = null;

function announce(title, message, kind = "", symbol = "↖") {
  feedback.className = "demo-feedback" + (kind ? " " + kind : "");
  feedback.replaceChildren();
  const icon = document.createElement("span");
  icon.setAttribute("aria-hidden", "true");
  icon.textContent = symbol;
  const text = document.createElement("div");
  const heading = document.createElement("strong");
  heading.textContent = title;
  const detail = document.createElement("p");
  detail.textContent = message;
  text.append(heading, detail);
  feedback.append(icon, text);
}

function render() {
  const body = document.querySelector("#sample-roster");
  body.replaceChildren();
  for (const student of students) {
    const record = attendance.get(student.key);
    const row = document.createElement("tr");
    const identity = document.createElement("td");
    const avatar = document.createElement("span");
    avatar.className = "table-avatar";
    avatar.textContent = student.initials;
    const label = document.createElement("span");
    label.textContent = student.name;
    const id = document.createElement("small");
    id.textContent = student.id;
    label.append(id);
    identity.append(avatar, label);
    const status = document.createElement("td");
    const pill = document.createElement("span");
    pill.className = "pill " + (record ? "present" : "waiting");
    pill.textContent = record ? "Present" : "Unmarked";
    status.append(pill);
    const method = document.createElement("td");
    method.textContent = record ? (record.method === "manual" ? "Manual" : "Simulated face") : "—";
    row.append(identity, status, method);
    body.append(row);
  }
  const count = document.querySelector("#present-count");
  count.replaceChildren(document.createTextNode(String(attendance.size)));
  const total = document.createElement("span");
  total.textContent = "/3";
  count.append(total);
  document.querySelector("#progress-fill").style.width = `${attendance.size / students.length * 100}%`;
  document.querySelector("#demo-progress").setAttribute("aria-valuenow", String(attendance.size));
}

function updateAvatar() {
  const student = students.find(item => item.key === select.value);
  document.querySelector("#demo-avatar").textContent = student ? student.initials : "?";
  document.querySelector("#avatar-caption").textContent = student ? "Ready for a simulated check-in" : "Visitor is not in this sample roster";
}

function recordAttendance(key, method, note = "") {
  const student = students.find(item => item.key === key);
  if (!student) {
    announce("No enrolled match. Nothing recorded.", "In the real app, unknown or ambiguous faces remain unmarked for administrator review.", "error", "×");
    return;
  }
  if (attendance.has(key)) {
    announce(`${student.name} is already checked in.`, "Duplicate prevented. The sample register still contains one entry for this student.", "warning", "↺");
    return;
  }
  attendance.set(key, { method, note });
  render();
  announce(`${student.name} marked present.`, method === "manual" ? "Manual verification recorded in this sample register." : "Simulated match accepted. No photo or facial analysis was used.", "success", "✓");
}

function setProcessing(value) {
  processing = value;
  button.disabled = value;
  select.disabled = value;
  document.querySelector("#open-manual-demo").disabled = value;
  station.classList.toggle("processing", value);
  button.setAttribute("aria-busy", String(value));
}

button.addEventListener("click", () => {
  if (processing) return;
  const chosen = select.value;
  setProcessing(true);
  document.querySelector("#avatar-caption").textContent = "Simulating a check-in…";
  pendingTimer = window.setTimeout(() => {
    recordAttendance(chosen, "simulated face");
    pendingTimer = null;
    setProcessing(false);
    updateAvatar();
  }, window.matchMedia("(prefers-reduced-motion: reduce)").matches ? 0 : 550);
});

select.addEventListener("change", updateAvatar);
document.querySelector("#reset-demo").addEventListener("click", () => {
  window.clearTimeout(pendingTimer);
  pendingTimer = null;
  setProcessing(false);
  attendance.clear();
  select.value = "anika";
  document.querySelector("#manual-form").reset();
  updateAvatar();
  render();
  announce("Sample register reset.", "Start with a check-in, then try the same student again or an unknown visitor.");
});

document.querySelector("#open-manual-demo").addEventListener("click", () => {
  document.querySelector("#manual-student").value = select.value === "unknown" ? "anika" : select.value;
  dialog.showModal();
});
document.querySelector("#close-manual").addEventListener("click", () => dialog.close());
document.querySelector("#manual-form").addEventListener("submit", event => {
  event.preventDefault();
  const note = document.querySelector("#manual-note");
  const value = note.value.trim();
  if (!value) {
    note.setCustomValidity("Enter a verification note.");
    note.reportValidity();
    return;
  }
  note.setCustomValidity("");
  recordAttendance(document.querySelector("#manual-student").value, "manual", value);
  dialog.close();
});
document.querySelector("#manual-note").addEventListener("input", event => event.target.setCustomValidity(""));

function csvCell(value) {
  let text = String(value);
  if (/^[\s]*[=+@-]/.test(text)) text = "'" + text;
  return '"' + text.replaceAll('"', '""') + '"';
}

document.querySelector("#export-sample").addEventListener("click", () => {
  const rows = [["SAMPLE DATA ONLY", "Student ID", "Status", "Method", "Verification note"]];
  for (const student of students) {
    const record = attendance.get(student.key);
    rows.push([student.name, student.id, record ? "Present" : "Unmarked", record ? record.method : "", record ? record.note : ""]);
  }
  const content = rows.map(row => row.map(csvCell).join(",")).join("\r\n") + "\r\n";
  const url = URL.createObjectURL(new Blob([content], { type: "text/csv;charset=utf-8" }));
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = "attendly-sample-attendance.csv";
  document.body.append(anchor);
  anchor.click();
  anchor.remove();
  window.setTimeout(() => URL.revokeObjectURL(url), 1000);
  announce("Sample CSV exported.", "The file contains fictional sample data only. Your browser may ask where to save it.", "success", "↓");
});

render();
