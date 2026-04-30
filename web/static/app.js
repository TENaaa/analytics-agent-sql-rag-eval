const form = document.querySelector("#ask-form");
const input = document.querySelector("#question");
const answer = document.querySelector("#answer");
const sqlBox = document.querySelector("#sql");
const tableBox = document.querySelector("#table");

document.querySelectorAll("[data-q]").forEach((button) => {
  button.addEventListener("click", () => {
    input.value = button.dataset.q;
    form.requestSubmit();
  });
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  answer.textContent = "分析中...";
  sqlBox.textContent = "";
  tableBox.innerHTML = "";
  const res = await fetch("/api/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question: input.value }),
  });
  const data = await res.json();
  answer.textContent = data.summary;
  sqlBox.textContent = data.sql.trim();
  tableBox.innerHTML = renderTable(data.rows || []);
});

function renderTable(rows) {
  if (!rows.length) return "<p>无表格结果</p>";
  const cols = Object.keys(rows[0]);
  const head = cols.map((c) => `<th>${c}</th>`).join("");
  const body = rows
    .map((row) => `<tr>${cols.map((c) => `<td>${row[c] ?? ""}</td>`).join("")}</tr>`)
    .join("");
  return `<table><thead><tr>${head}</tr></thead><tbody>${body}</tbody></table>`;
}
