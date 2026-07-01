(function () {
  'use strict';

  let styles = `
#cs-widget-container { position:fixed; bottom:20px; right:20px; z-index:999999; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif; }
#cs-widget-toggle { width:56px; height:56px; border-radius:28px; background:#2563eb; color:#fff; border:none; cursor:pointer; font-size:24px; box-shadow:0 4px 12px rgba(0,0,0,0.15); transition:transform 0.2s; }
#cs-widget-toggle:hover { transform:scale(1.1); }
#cs-widget-panel { display:none; width:380px; height:560px; background:#fff; border-radius:12px; box-shadow:0 8px 32px rgba(0,0,0,0.12); flex-direction:column; overflow:hidden; }
#cs-widget-header { padding:16px; background:#2563eb; color:#fff; font-weight:600; display:flex; justify-content:space-between; align-items:center; }
#cs-widget-close { background:none; border:none; color:#fff; cursor:pointer; font-size:20px; }
#cs-widget-messages { flex:1; overflow-y:auto; padding:12px; display:flex; flex-direction:column; gap:8px; }
.cs-msg { max-width:80%; padding:10px 14px; border-radius:12px; font-size:14px; line-height:1.4; }
.cs-msg.user { align-self:flex-end; background:#2563eb; color:#fff; border-bottom-right-radius:4px; }
.cs-msg.assistant { align-self:flex-start; background:#f1f5f9; color:#1e293b; border-bottom-left-radius:4px; }
.cs-msg.typing { align-self:flex-start; background:#f1f5f9; color:#94a3b8; border-bottom-left-radius:4px; }
#cs-widget-input { display:flex; padding:12px; border-top:1px solid #e2e8f0; gap:8px; }
#cs-widget-input input { flex:1; padding:8px 12px; border:1px solid #e2e8f0; border-radius:8px; outline:none; font-size:14px; }
#cs-widget-input input:focus { border-color:#2563eb; }
#cs-widget-send { padding:8px 16px; background:#2563eb; color:#fff; border:none; border-radius:8px; cursor:pointer; font-size:14px; }
#cs-widget-send:disabled { opacity:0.5; cursor:not-allowed; }
`;

  let styleSheet = document.createElement('style');
  styleSheet.textContent = styles;
  document.head.appendChild(styleSheet);

  let container = document.createElement('div');
  container.id = 'cs-widget-container';
  container.innerHTML = `
    <div id="cs-widget-panel">
      <div id="cs-widget-header">
        <span>Support</span>
        <button id="cs-widget-close">&times;</button>
      </div>
      <div id="cs-widget-messages"></div>
      <div id="cs-widget-input">
        <input type="text" id="cs-widget-input-field" placeholder="Type a message..." />
        <button id="cs-widget-send">Send</button>
      </div>
    </div>
    <button id="cs-widget-toggle">&#x1f4ac;</button>
  `;
  document.body.appendChild(container);

  let toggle = document.getElementById('cs-widget-toggle');
  let panel = document.getElementById('cs-widget-panel');
  let close = document.getElementById('cs-widget-close');
  let messagesEl = document.getElementById('cs-widget-messages');
  let input = document.getElementById('cs-widget-input-field');
  let sendBtn = document.getElementById('cs-widget-send');
  let isOpen = false;
  let conversationId = null;

  function togglePanel() {
    isOpen = !isOpen;
    panel.style.display = isOpen ? 'flex' : 'none';
    toggle.style.display = isOpen ? 'none' : 'block';
    if (isOpen) input.focus();
  }

  toggle.onclick = togglePanel;
  close.onclick = togglePanel;

  function addMessage(role, content) {
    let el = document.createElement('div');
    el.className = 'cs-msg ' + role;
    el.textContent = content;
    messagesEl.appendChild(el);
    messagesEl.scrollTop = messagesEl.scrollHeight;
    return el;
  }

  async function sendMessage() {
    let text = input.value.trim();
    if (!text) return;
    input.value = '';
    sendBtn.disabled = true;
    addMessage('user', text);

    let typingEl = addMessage('assistant', '...');
    typingEl.classList.add('typing');

    try {
      let body = { message: text, stream: true };
      if (conversationId) body.conversation_id = conversationId;

      let res = await fetch('/api/v1/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      if (!res.ok) throw new Error('Request failed');

      conversationId = res.headers.get('X-Conversation-ID') || conversationId;

      typingEl.classList.remove('typing');
      typingEl.textContent = '';

      let reader = res.body.getReader();
      let decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        let { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        let lines = buffer.split('\n');
        buffer = lines.pop() || '';
        for (let line of lines) {
          if (!line.startsWith('data: ')) continue;
          try {
            let data = JSON.parse(line.slice(6));
            if (data.type === 'token') {
              typingEl.textContent += data.content;
              messagesEl.scrollTop = messagesEl.scrollHeight;
            } else if (data.type === 'done') {
              conversationId = data.conversation_id || conversationId;
            } else if (data.type === 'error') {
              typingEl.textContent = 'Error: ' + data.content;
              typingEl.style.color = '#dc2626';
            }
          } catch (e) {
            /* skip parse errors */
          }
        }
      }
    } catch (err) {
      typingEl.classList.remove('typing');
      typingEl.textContent = 'Connection error. Please try again.';
      typingEl.style.color = '#dc2626';
    }
    sendBtn.disabled = false;
    input.focus();
  }

  sendBtn.onclick = sendMessage;
  input.onkeydown = function (e) {
    if (e.key === 'Enter') sendMessage();
  };
})();
