const chatTab = document.getElementById("chatTab");
const videoTab = document.getElementById("videoTab");
const chatPanel = document.getElementById("chatPanel");
const videoPanel = document.getElementById("videoPanel");
const messagesDiv = document.getElementById("messages");
const input = document.getElementById("userInput");

chatTab.onclick = () => switchTab("chat");
videoTab.onclick = () => switchTab("video");

function switchTab(tab) {
  chatTab.classList.remove("active");
  videoTab.classList.remove("active");

  if (tab === "chat") {
    chatTab.classList.add("active");
    chatPanel.classList.remove("hidden");
    videoPanel.classList.add("hidden");
  } else {
    videoTab.classList.add("active");
    videoPanel.classList.remove("hidden");
    chatPanel.classList.add("hidden");
  }
}

function addMessage(text, role) {
  const div = document.createElement("div");
  div.className = `message ${role}`;
  div.innerText = text;
  messagesDiv.appendChild(div);
  messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

async function sendMessage() {
  const question = input.value.trim();
  if (!question) return;

  addMessage(question, "user");
  input.value = "";

  addMessage("Thinking...", "bot");

  try {
    const res = await fetch(
      "https://rag-teaching-assistant-0jps.onrender.com/ask",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question })
      }
    );

    const data = await res.json();

    // remove "Thinking..."
    messagesDiv.lastChild.remove();

    addMessage(data.answer, "bot");

  } catch (err) {
    messagesDiv.lastChild.remove();
    addMessage("❌ Backend not reachable", "bot");
    input.addEventListener("keydown", function (e) {
  if (e.key === "Enter") {
    sendMessage();
  }
});

  }
}
