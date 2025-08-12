const noteWindow = document.getElementById("noteWindow");
const saveBtn = document.getElementById("saveBtn");
const clearBtn = document.getElementById("clearBtn");
const noteInput = document.getElementById("noteInput");
const noteStatus = document.getElementById("noteStatus");

function escapeHtml(unsafe) {
  return unsafe
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

async function webpadSaveText(inputText) {
  try {
    const resp = await fetch("/api/webpad", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: inputText }),
    });
    if (!resp.ok) throw new Error("Network error");
    noteStatus.textContent = "✅ Saved";
    setTimeout(() => {
      noteStatus.textContent = "";
    }, 3000);
  } catch (err) {
    noteStatus.textContent = "⚠️ Error: " + escapeHtml(err.message);
  }
}

saveBtn.addEventListener("click", () => {
  const inputText = noteInput.value;
  webpadSaveText(inputText);
});

clearBtn.addEventListener("click", () => {
  noteInput.value = "";
});
