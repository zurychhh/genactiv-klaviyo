const chatEl = document.getElementById('chat-inner');
const inputEl = document.getElementById('input');
const sendBtn = document.getElementById('send-btn');
const statusEl = document.getElementById('status');

const messages = [];
let isProcessing = false;

marked.setOptions({ breaks: true, gfm: true });

// --- Welcome screen ---
function showWelcome() {
  const welcome = document.createElement('div');
  welcome.className = 'welcome';
  welcome.id = 'welcome';
  welcome.innerHTML = `
    <div class="welcome-logo">G</div>
    <h2>Witaj w GenActiv Online</h2>
    <p>Zapytaj o kampanie Klaviyo, zamówienia Shopify, reklamy Google Ads i Meta Ads, analitykę GA4 — lub cokolwiek innego.</p>
  `;
  chatEl.appendChild(welcome);
}

showWelcome();

// --- Health check ---
fetch('/api/health')
  .then(r => r.json())
  .then(() => {
    statusEl.textContent = 'Połączono';
    statusEl.className = 'status connected';
  })
  .catch(() => {
    statusEl.textContent = 'Błąd połączenia';
    statusEl.className = 'status error';
  });

// --- Auto-resize textarea ---
inputEl.addEventListener('input', () => {
  inputEl.style.height = 'auto';
  inputEl.style.height = Math.min(inputEl.scrollHeight, 200) + 'px';
});

inputEl.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

sendBtn.addEventListener('click', sendMessage);

// --- Thinking indicator ---
let thinkingEl = null;
let thinkingTimers = [];

function showThinking() {
  thinkingEl = document.createElement('div');
  thinkingEl.className = 'thinking-indicator';
  thinkingEl.innerHTML = `
    <div class="thinking-dots"><span></span><span></span><span></span></div>
    <span class="thinking-text">Przetwarzam...</span>
  `;
  chatEl.appendChild(thinkingEl);
  scrollToBottom();

  const textEl = thinkingEl.querySelector('.thinking-text');
  thinkingTimers.push(
    setTimeout(() => {
      if (textEl) textEl.textContent = 'Analizuję dane i wywołuję narzędzia...';
    }, 5000),
    setTimeout(() => {
      if (textEl) textEl.textContent = 'To zapytanie wymaga więcej czasu...';
    }, 20000)
  );
}

function updateThinkingText(text) {
  if (thinkingEl) {
    const textEl = thinkingEl.querySelector('.thinking-text');
    if (textEl) textEl.textContent = text;
  }
}

function hideThinking() {
  if (thinkingEl) {
    thinkingEl.remove();
    thinkingEl = null;
  }
  thinkingTimers.forEach(clearTimeout);
  thinkingTimers = [];
}

// --- Tool call tracking ---
const activeTools = new Map(); // toolName -> { el, startTime }

// --- Send message ---
function sendMessage() {
  const text = inputEl.value.trim();
  if (!text || isProcessing) return;

  // Remove welcome screen
  const welcomeEl = document.getElementById('welcome');
  if (welcomeEl) welcomeEl.remove();

  messages.push({ role: 'user', content: text });
  appendMessage('user', text);

  inputEl.value = '';
  inputEl.style.height = 'auto';
  setProcessing(true);
  showThinking();

  const assistantEl = appendMessage('assistant', '');
  const bubbleEl = assistantEl.querySelector('.bubble');
  const toolsEl = assistantEl.querySelector('.msg-tools');
  assistantEl.style.display = 'none';

  let fullText = '';
  let gotFirstText = false;

  fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ messages })
  }).then(response => {
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    function read() {
      reader.read().then(({ done, value }) => {
        if (done) { finalize(); return; }

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop();

        for (const line of lines) {
          if (line.startsWith('data: [DONE]')) { finalize(); return; }

          if (line.startsWith('data: ')) {
            try {
              const event = JSON.parse(line.slice(6));

              if (event.type === 'text' && !gotFirstText) {
                hideThinking();
                assistantEl.style.display = '';
                gotFirstText = true;
              } else if (event.type === 'tool_use' && thinkingEl) {
                const toolShort = event.data.tool.split('__').pop();
                updateThinkingText('Wywołuję: ' + toolShort + '...');
              } else if (event.type === 'tool_result' && thinkingEl) {
                updateThinkingText('Przetwarzam wyniki...');
              }

              handleEvent(event, bubbleEl, toolsEl);
              if (event.type === 'text') fullText += event.data;
            } catch { /* ignore parse errors */ }
          }
        }

        read();
      });
    }

    read();
  }).catch(err => {
    hideThinking();
    assistantEl.style.display = '';
    bubbleEl.innerHTML = `<span style="color:var(--brand-red)">Błąd: ${err.message}</span>`;
    setProcessing(false);
  });

  function finalize() {
    hideThinking();
    assistantEl.style.display = '';
    if (fullText) {
      messages.push({ role: 'assistant', content: fullText });
      bubbleEl.innerHTML = renderMarkdown(fullText);
      bubbleEl.classList.remove('streaming-cursor');
    }
    // Mark all active tools as complete
    for (const [, tool] of activeTools) {
      markToolComplete(tool);
    }
    activeTools.clear();
    setProcessing(false);
    scrollToBottom();
  }
}

function handleEvent(event, bubbleEl, toolsEl) {
  switch (event.type) {
    case 'text':
      bubbleEl.textContent += event.data;
      bubbleEl.classList.add('streaming-cursor');
      scrollToBottom();
      break;

    case 'tool_use': {
      const toolShort = event.data.tool.split('__').pop();
      const wrapper = document.createElement('div');
      wrapper.className = 'tool-call-wrapper';

      const indicator = document.createElement('div');
      indicator.className = 'tool-indicator';
      indicator.innerHTML = `
        <span class="tool-status-dot running"></span>
        <span class="tool-label">${toolShort}</span>
        <span class="tool-duration"></span>
        <span class="tool-chevron">▸</span>
      `;

      const details = document.createElement('div');
      details.className = 'tool-details';
      details.textContent = JSON.stringify(event.data.args, null, 2);

      indicator.addEventListener('click', () => {
        indicator.classList.toggle('expanded');
        details.style.display = indicator.classList.contains('expanded') ? 'block' : 'none';
      });

      wrapper.appendChild(indicator);
      wrapper.appendChild(details);
      toolsEl.appendChild(wrapper);

      activeTools.set(event.data.tool, {
        el: indicator,
        startTime: Date.now()
      });

      scrollToBottom();
      break;
    }

    case 'tool_result': {
      const tool = activeTools.get(event.data.tool);
      if (tool) {
        markToolComplete(tool);
        // Update details with result preview
        const wrapper = tool.el.parentElement;
        if (wrapper) {
          const details = wrapper.querySelector('.tool-details');
          if (details) {
            const preview = event.data.result.length > 300
              ? event.data.result.slice(0, 300) + '...'
              : event.data.result;
            details.textContent = preview;
          }
        }
        activeTools.delete(event.data.tool);
      }
      scrollToBottom();
      break;
    }

    case 'error': {
      const wrapper = document.createElement('div');
      wrapper.className = 'tool-call-wrapper';
      const indicator = document.createElement('div');
      indicator.className = 'tool-indicator';
      indicator.innerHTML = `
        <span class="tool-status-dot error"></span>
        <span class="tool-label">Błąd: ${event.data}</span>
      `;
      toolsEl.appendChild(wrapper);
      wrapper.appendChild(indicator);
      scrollToBottom();
      break;
    }
  }
}

function markToolComplete(tool) {
  const dot = tool.el.querySelector('.tool-status-dot');
  if (dot) {
    dot.classList.remove('running');
    dot.classList.add('complete');
  }
  const duration = tool.el.querySelector('.tool-duration');
  if (duration) {
    const elapsed = ((Date.now() - tool.startTime) / 1000).toFixed(1);
    duration.textContent = elapsed + 's';
  }
}

// --- Render markdown with copy buttons on code blocks ---
function renderMarkdown(text) {
  const html = marked.parse(text);
  const temp = document.createElement('div');
  temp.innerHTML = html;

  temp.querySelectorAll('pre').forEach(pre => {
    pre.style.position = 'relative';
    const btn = document.createElement('button');
    btn.className = 'code-copy-btn';
    btn.textContent = 'Kopiuj';
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const code = pre.querySelector('code');
      navigator.clipboard.writeText(code ? code.textContent : pre.textContent);
      btn.textContent = 'Skopiowano!';
      setTimeout(() => { btn.textContent = 'Kopiuj'; }, 2000);
    });
    pre.appendChild(btn);
  });

  return temp.innerHTML;
}

// --- Append message to chat ---
function appendMessage(role, content) {
  const msg = document.createElement('div');
  msg.className = `message ${role}`;

  const avatarLabel = role === 'user' ? 'Ty' : 'G';
  const nameLabel = role === 'user' ? 'Ty' : 'GenActiv';

  msg.innerHTML = `
    <div class="msg-header">
      <div class="avatar">${avatarLabel}</div>
      <span class="msg-name">${nameLabel}</span>
    </div>
    <div class="msg-tools"></div>
    <div class="bubble">${role === 'user' ? escapeHtml(content) : content}</div>
  `;

  chatEl.appendChild(msg);
  scrollToBottom();
  return msg;
}

function setProcessing(state) {
  isProcessing = state;
  sendBtn.disabled = state;
  inputEl.disabled = state;
  if (!state) inputEl.focus();
}

function scrollToBottom() {
  const chat = document.getElementById('chat');
  chat.scrollTop = chat.scrollHeight;
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}
