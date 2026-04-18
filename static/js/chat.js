const chatContainer = document.getElementById('chat-container');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const documentList = document.getElementById('documentList');

// Auto-resize textarea
userInput.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = (this.scrollHeight) + 'px';
});

async function appendMessage(role, text) {
    const isAi = role === 'assistant';
    const displayContent = isAi ? marked.parse(text) : text;

    const msgHtml = `
        <div class="flex gap-4 max-w-3xl mx-auto ${isAi ? '' : 'justify-end'}">
            <div class="flex-1 px-4 py-2 rounded-2xl ${isAi ? '' : 'bg-[#2f2f2f] max-w-[80%]'}">
                <p class="font-bold text-xs mb-1 text-gray-400">${role.toUpperCase()}</p>
                <div class="markdown-content text-gray-200 leading-relaxed">${displayContent}</div>
            </div>
        </div>
    `;

    const welcome = document.getElementById('welcome-screen');
    if (welcome) welcome.remove();
    
    chatContainer.insertAdjacentHTML('beforeend', msgHtml);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

async function uploadPDF() {
    const fileInput = document.getElementById('fileInput');
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    // Show visual feedback
    const originalBtn = document.querySelector('aside button').innerHTML;
    document.querySelector('aside button').innerHTML = '<i class="fa-solid fa-spinner animate-spin"></i> Ingesting...';

    const response = await fetch('/upload', { method: 'POST', body: formData });
    const result = await response.json();

    if (result.filename) {
        const item = `<div class="text-sm text-gray-300 py-2 border-b border-white/5 truncate"><i class="fa-regular fa-file-pdf mr-2"></i> ${result.filename}</div>`;
        documentList.insertAdjacentHTML('beforeend', item);
    } else {
        alert("Upload failed: " + result.error);
    }
    document.querySelector('aside button').innerHTML = originalBtn;
}

async function handleChat() {
    const query = userInput.value.trim();
    if (!query) return;

    appendMessage('user', query);
    userInput.value = '';
    userInput.style.height = 'auto';

    // Typing Indicator
    const typingId = 'typing-' + Date.now();
    chatContainer.insertAdjacentHTML('beforeend', `<div id="${typingId}" class="max-w-3xl mx-auto text-gray-500 text-sm italic">AI is thinking...</div>`);

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: query })
        });
        const data = await response.json();
        document.getElementById(typingId).remove();
        appendMessage('assistant', data.answer || "Sorry, I encountered an error.");
    } catch (e) {
        document.getElementById(typingId).remove();
        appendMessage('assistant', "Connection error. Please try again.");
    }
}

sendBtn.addEventListener('click', handleChat);
userInput.addEventListener('keypress', (e) => { if(e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleChat(); } });