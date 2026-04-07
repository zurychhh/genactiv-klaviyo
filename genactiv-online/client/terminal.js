const chatEl = document.getElementById('chat-inner');
const inputEl = document.getElementById('input');
const sendBtn = document.getElementById('send-btn');
const statusEl = document.getElementById('status');
const clearBtn = document.getElementById('clear-btn');

// Fix 13/14: localStorage persistence
const MAX_STORED_MESSAGES = 20;

function saveMessages(msgs) {
  try {
    const toStore = msgs.slice(-MAX_STORED_MESSAGES);
    localStorage.setItem('genactiv-messages', JSON.stringify(toStore));
  } catch { /* quota exceeded — ignore */ }
}

function loadMessages() {
  try {
    const stored = localStorage.getItem('genactiv-messages');
    if (!stored) return [];
    const parsed = JSON.parse(stored);
    if (!Array.isArray(parsed)) return [];
    return parsed.slice(-MAX_STORED_MESSAGES);
  } catch { return []; }
}

function clearStoredMessages() {
  localStorage.removeItem('genactiv-messages');
}

const messages = loadMessages();
let isProcessing = false;

marked.setOptions({ breaks: true, gfm: true });

// --- Restore history or show welcome ---
function init() {
  if (messages.length > 0) {
    for (const msg of messages) {
      const el = appendMessage(msg.role, msg.role === 'user' ? msg.content : '');
      if (msg.role === 'assistant') {
        const bubbleEl = el.querySelector('.bubble');
        bubbleEl.innerHTML = renderMarkdown(msg.content);
      }
    }
  } else {
    showWelcome();
  }
}

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

init();

// Fix 14: Clear button
if (clearBtn) {
  clearBtn.addEventListener('click', () => {
    if (isProcessing) return;
    messages.length = 0;
    clearStoredMessages();
    chatEl.innerHTML = '';
    showWelcome();
  });
}

// Fix 4: Enhanced health check — show MCP status
fetch('/api/health')
  .then(r => r.json())
  .then((data) => {
    const mcpInfo = data.mcp ? `${data.mcp.connected}/${data.mcp.total} MCP` : '';
    statusEl.textContent = `Połączono${mcpInfo ? ` (${mcpInfo})` : ''}`;
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

function showThinking(text) {
  if (thinkingEl) {
    updateThinkingText(text || 'Przetwarzam...');
    return;
  }
  thinkingEl = document.createElement('div');
  thinkingEl.className = 'thinking-indicator';
  thinkingEl.innerHTML = `
    <div class="thinking-dots"><span></span><span></span><span></span></div>
    <span class="thinking-text">${text || 'Przetwarzam...'}</span>
  `;
  chatEl.appendChild(thinkingEl);
  scrollToBottom();
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
const activeTools = new Map();

// --- Inactivity timeout ---
const INACTIVITY_TIMEOUT_MS = 45000;
let inactivityTimer = null;

function resetInactivityTimer(onTimeout) {
  clearTimeout(inactivityTimer);
  inactivityTimer = setTimeout(onTimeout, INACTIVITY_TIMEOUT_MS);
}

function clearInactivityTimer() {
  clearTimeout(inactivityTimer);
  inactivityTimer = null;
}

// --- Send message ---
function sendMessage() {
  const text = inputEl.value.trim();
  if (!text || isProcessing) return;

  const welcomeEl = document.getElementById('welcome');
  if (welcomeEl) welcomeEl.remove();

  messages.push({ role: 'user', content: text });
  saveMessages(messages);
  appendMessage('user', text);

  inputEl.value = '';
  inputEl.style.height = 'auto';
  setProcessing(true);
  showThinking('Przetwarzam...');

  const assistantEl = appendMessage('assistant', '');
  const bubbleEl = assistantEl.querySelector('.bubble');
  const toolsEl = assistantEl.querySelector('.msg-tools');
  assistantEl.style.display = 'none';

  let fullText = '';
  let gotFirstText = false;
  let finalized = false;

  function finalize(errorMsg) {
    if (finalized) return;
    finalized = true;
    clearInactivityTimer();
    hideThinking();
    assistantEl.style.display = '';

    if (errorMsg) {
      bubbleEl.innerHTML = `<span style="color:var(--brand-red)">${errorMsg}</span>`;
    } else if (fullText) {
      messages.push({ role: 'assistant', content: fullText });
      saveMessages(messages);
      bubbleEl.innerHTML = renderMarkdown(fullText);
    }

    bubbleEl.classList.remove('streaming-cursor');
    for (const [, tool] of activeTools) {
      markToolComplete(tool);
    }
    activeTools.clear();
    setProcessing(false);
    scrollToBottom();
  }

  const timeoutHandler = () => {
    finalize('Przekroczono czas oczekiwania (45s). Spróbuj ponownie.');
  };

  resetInactivityTimer(timeoutHandler);

  fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ messages })
  }).then(response => {
    if (!response.ok) {
      if (response.status === 429) {
        finalize('Zbyt wiele zapytań. Poczekaj chwilę i spróbuj ponownie.');
        return;
      }
      finalize(`Błąd serwera: ${response.status}`);
      return;
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    function read() {
      reader.read().then(({ done, value }) => {
        if (finalized) return;
        if (done) { finalize(); return; }

        resetInactivityTimer(timeoutHandler);

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
              }

              if (event.type === 'progress') {
                if (!gotFirstText) {
                  showThinking(event.data);
                } else {
                  showThinking(event.data);
                }
              }

              if (event.type === 'tool_use') {
                const toolShort = event.data.tool.split('__').pop();
                showThinking('Wywołuję: ' + toolShort + '...');
              }

              if (event.type === 'tool_result') {
                showThinking('Analizuję wyniki...');
              }

              handleEvent(event, bubbleEl, toolsEl);
              if (event.type === 'text') fullText += event.data;
            } catch { /* ignore parse errors */ }
          }
        }

        read();
      }).catch(err => {
        if (!finalized) {
          finalize(`Błąd połączenia: ${err.message}`);
        }
      });
    }

    read();
  }).catch(err => {
    finalize(`Błąd: ${err.message}`);
  });
}

function handleEvent(event, bubbleEl, toolsEl) {
  switch (event.type) {
    case 'text':
      hideThinking();
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

// ============================================================
// Capabilities Panel
// ============================================================

const capBtn = document.getElementById('capabilities-btn');
const capPanel = document.getElementById('capabilities-panel');
const capOverlay = document.getElementById('capabilities-overlay');
const capClose = document.getElementById('cap-close');

function openCapabilities() {
  capPanel.classList.remove('hidden');
  capOverlay.classList.remove('hidden');
  // Force reflow for CSS transition
  requestAnimationFrame(() => {
    capPanel.style.transform = 'translateX(0)';
  });
}

function closeCapabilities() {
  capPanel.classList.add('hidden');
  capOverlay.classList.add('hidden');
}

if (capBtn) capBtn.addEventListener('click', openCapabilities);
if (capClose) capClose.addEventListener('click', closeCapabilities);
if (capOverlay) capOverlay.addEventListener('click', closeCapabilities);

// ESC key closes panel
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && !capPanel.classList.contains('hidden')) {
    closeCapabilities();
  }
});

// Example prompts — click to insert into input
document.querySelectorAll('.cap-example').forEach(btn => {
  btn.addEventListener('click', () => {
    const prompt = btn.getAttribute('data-prompt');
    if (prompt && inputEl) {
      inputEl.value = prompt;
      inputEl.style.height = 'auto';
      inputEl.style.height = Math.min(inputEl.scrollHeight, 200) + 'px';
      closeCapabilities();
      inputEl.focus();
    }
  });
});

// Collapsible sections
document.querySelectorAll('.cap-section-header').forEach(header => {
  header.addEventListener('click', () => {
    const tools = header.nextElementSibling;
    if (tools && tools.classList.contains('cap-tools')) {
      const isHidden = tools.style.display === 'none';
      tools.style.display = isHidden ? '' : 'none';
      header.style.borderRadius = isHidden ? '8px 8px 0 0' : '8px';
    }
  });
});
