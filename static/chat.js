const messagesEl = document.getElementById("messages");
const formEl = document.getElementById("chat-form");
const inputEl = document.getElementById("message-input");
const resetBtn = document.getElementById("reset-btn");

function addBubble(text, className) {
  const el = document.createElement("div");
  el.className = `bubble ${className}`;
  el.textContent = text;
  messagesEl.appendChild(el);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  return el;
}

formEl.addEventListener("submit", async (e) => {
  e.preventDefault();
  const message = inputEl.value.trim();
  if (!message) return;

  addBubble(message, "user");
  inputEl.value = "";
  inputEl.disabled = true;

  const pending = addBubble("Thinking...", "pending assistant");

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });
    const data = await res.json();
    pending.remove();
    if (!res.ok) {
      addBubble(data.error || "Something went wrong.", "error");
    } else {
      addBubble(data.reply, "assistant");
    }
  } catch (err) {
    pending.remove();
    addBubble("Network error — please try again.", "error");
  } finally {
    inputEl.disabled = false;
    inputEl.focus();
  }
});

resetBtn.addEventListener("click", async () => {
  await fetch("/api/reset", { method: "POST" });
  messagesEl.innerHTML = "";
  inputEl.focus();
});
