const chatWindow = document.getElementById("chatWindow");
const chatForm = document.getElementById("chatForm");
const promptInput = document.getElementById("promptInput");
const clearBtn = document.getElementById("clearBtn");

function escapeHtml(unsafe) {
  return unsafe
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

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

async function requestResponse(prompt, placeholderId) {
  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ "text": prompt }),
    });

    if (!response.ok) throw new Error("Network error");

    // replace typing placeholder with actual text
    const reply = await response.json();
    const placeholder = document.getElementById(placeholderId);
    if (placeholder) {
      const bubble = placeholder.querySelector(".bubble");
      bubble.innerHTML = "";
      bubble.innerText = reply;
      bubble.parentElement.parentElement.scrollTop =
        bubble.parentElement.parentElement.scrollHeight;
    }
  } catch (err) {
    const placeholder = document.getElementById(placeholderId);
    if (placeholder) {
      const bubble = placeholder.querySelector(".bubble");
      bubble.innerHTML = "⚠️ Error: " + escapeHtml(err.message);
      placeholder.classList.add("bot");
    }
  }
}

async function requestStreamResponse(prompt, placeholderId) {
    try {
    const response = await fetch("/api/chat-stream", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ "text": prompt }),
    });

    if (!response.ok) throw new Error("Network error");

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    const placeholder = document.getElementById(placeholderId);
    
    if (placeholder) {
      const bubble = placeholder.querySelector(".bubble");
      bubble.innerHTML = "";      
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        bubble.innerText += decoder.decode(value, { stream: true })
        bubble.parentElement.parentElement.scrollTop =
          bubble.parentElement.parentElement.scrollHeight;
      }
    }
  } catch (err) {
    const placeholder = document.getElementById(placeholderId);
    if (placeholder) {
      const bubble = placeholder.querySelector(".bubble");
      bubble.innerHTML = "⚠️ Error: " + escapeHtml(err.message);
      placeholder.classList.add("bot");
    }
  }
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
  
  // get response from server
  //requestResponse(prompt, placeholderId);
  requestStreamResponse(prompt, placeholderId)
});

clearBtn.addEventListener("click", () => {
  chatWindow.innerHTML = "";
});

// allow Enter to send
promptInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    chatForm.requestSubmit();
  }
});
