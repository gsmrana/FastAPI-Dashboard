const chatWindow = document.getElementById("chatWindow");
const chatForm = document.getElementById("chatForm");
const promptInput = document.getElementById("promptInput");
const clearBtn = document.getElementById("clearBtn");

function appendMessage(role, text, id) {
  const wrapper = document.createElement("div");
  wrapper.className = `message ${role}`;
  wrapper.id = id || "";
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.innerHTML = text;
  wrapper.appendChild(bubble);
  chatWindow.appendChild(wrapper);
  chatWindow.scrollTop = chatWindow.scrollHeight;
  return wrapper;
}

function renderTypingPlaceholder(id) {
  const wrapper = document.createElement("div");
  wrapper.className = "message bot";
  wrapper.id = id;
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.innerHTML = `<span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span>`;
  wrapper.appendChild(bubble);
  chatWindow.appendChild(wrapper);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

chatForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const prompt = promptInput.value.trim();
  if (!prompt) return;
  // show user message
  appendMessage("user", escapeHtml(prompt));
  promptInput.value = "";

  // show bot typing
  const placeholderId = "msg-" + Date.now();
  renderTypingPlaceholder(placeholderId);

  try {
    const resp = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt }),
    });

    if (!resp.ok) throw new Error("Network error");

    // assume JSON reply {reply: "..."}
    const data = await resp.json();

    // replace typing placeholder with actual text (with simple typing effect)
    const placeholder = document.getElementById(placeholderId);
    if (placeholder) {
      const bubble = placeholder.querySelector(".bubble");
      bubble.innerHTML = "";
      typeText(bubble, data.reply);
    }
  } catch (err) {
    const placeholder = document.getElementById(placeholderId);
    if (placeholder) {
      const bubble = placeholder.querySelector(".bubble");
      bubble.innerHTML = "⚠️ Error: " + escapeHtml(err.message);
      placeholder.classList.add("bot");
    }
  }
});

clearBtn.addEventListener("click", () => {
  chatWindow.innerHTML = "";
});

// small typing effect
async function typeText(container, text, speed = 16) {
  for (let i = 0; i <= text.length; i++) {
    container.innerText = text.slice(0, i);
    container.parentElement.parentElement.scrollTop =
      container.parentElement.parentElement.scrollHeight;
    await wait(speed);
  }
}
function wait(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

function escapeHtml(unsafe) {
  return unsafe
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

// allow Enter to send
promptInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    chatForm.requestSubmit();
  }
});
