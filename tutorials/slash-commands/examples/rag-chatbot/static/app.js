// DOM elements
const fileInput = document.getElementById('file-input');
const uploadBtn = document.getElementById('upload-btn');
const documentList = document.getElementById('document-list');
const messagesContainer = document.getElementById('messages');
const chatForm = document.getElementById('chat-form');
const messageInput = document.getElementById('message-input');
const sendBtn = document.getElementById('send-btn');

// State
let isLoading = false;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadDocuments();
});

// Event listeners
uploadBtn.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', handleFileUpload);
chatForm.addEventListener('submit', handleChatSubmit);

// Load and display documents
async function loadDocuments() {
    try {
        const response = await fetch('/api/documents');
        const documents = await response.json();
        renderDocuments(documents);
    } catch (error) {
        console.error('Failed to load documents:', error);
    }
}

function renderDocuments(documents) {
    if (documents.length === 0) {
        documentList.innerHTML = `
            <p class="text-sm text-gray-500 text-center">No documents yet</p>
        `;
        return;
    }

    documentList.innerHTML = documents.map(doc => `
        <div class="bg-white rounded-lg p-3 shadow-sm border border-gray-200 group">
            <div class="flex items-start justify-between">
                <div class="flex-1 min-w-0">
                    <p class="text-sm font-medium text-gray-800 truncate">${escapeHtml(doc.filename)}</p>
                    <p class="text-xs text-gray-500">${doc.chunk_count} chunks</p>
                </div>
                <button
                    onclick="deleteDocument('${doc.id}')"
                    class="text-gray-400 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-opacity ml-2"
                    title="Delete document"
                >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                </button>
            </div>
        </div>
    `).join('');
}

// File upload
async function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    uploadBtn.disabled = true;
    uploadBtn.textContent = 'Uploading...';

    try {
        const response = await fetch('/api/documents', {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Upload failed');
        }

        await loadDocuments();
    } catch (error) {
        alert('Failed to upload: ' + error.message);
    } finally {
        uploadBtn.disabled = false;
        uploadBtn.textContent = 'Upload Document';
        fileInput.value = '';
    }
}

// Delete document
async function deleteDocument(id) {
    if (!confirm('Delete this document?')) return;

    try {
        const response = await fetch(`/api/documents/${id}`, {
            method: 'DELETE',
        });

        if (!response.ok) {
            throw new Error('Delete failed');
        }

        await loadDocuments();
    } catch (error) {
        alert('Failed to delete: ' + error.message);
    }
}

// Chat
async function handleChatSubmit(event) {
    event.preventDefault();

    const message = messageInput.value.trim();
    if (!message || isLoading) return;

    // Clear placeholder if first message
    if (messagesContainer.querySelector('.text-center')) {
        messagesContainer.innerHTML = '';
    }

    // Add user message
    addMessage('user', message);
    messageInput.value = '';

    // Show loading state
    isLoading = true;
    sendBtn.disabled = true;
    const loadingId = addLoadingMessage();

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message }),
        });

        if (!response.ok) {
            throw new Error('Chat request failed');
        }

        const data = await response.json();

        // Remove loading message and add response
        removeMessage(loadingId);
        addMessage('assistant', data.answer, data.sources);
    } catch (error) {
        removeMessage(loadingId);
        addMessage('error', 'Failed to get response. Please try again.');
    } finally {
        isLoading = false;
        sendBtn.disabled = false;
        messageInput.focus();
    }
}

function addMessage(role, content, sources = []) {
    const id = 'msg-' + Date.now();
    const messageDiv = document.createElement('div');
    messageDiv.id = id;

    if (role === 'user') {
        messageDiv.className = 'flex justify-end';
        messageDiv.innerHTML = `
            <div class="bg-blue-500 text-white px-4 py-2 rounded-lg max-w-2xl">
                ${escapeHtml(content)}
            </div>
        `;
    } else if (role === 'assistant') {
        const sourcesHtml = sources.length > 0 ? `
            <div class="mt-3 pt-3 border-t border-gray-200">
                <p class="text-xs text-gray-500 mb-2">Sources:</p>
                <div class="space-y-2">
                    ${sources.map((s, i) => `
                        <div class="bg-gray-50 rounded p-2 text-xs">
                            <span class="text-gray-400">[${i + 1}]</span>
                            <span class="text-gray-600">${escapeHtml(s.content.substring(0, 150))}${s.content.length > 150 ? '...' : ''}</span>
                            <span class="text-gray-400 ml-1">(${(s.similarity * 100).toFixed(0)}%)</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        ` : '';

        messageDiv.className = 'flex justify-start';
        messageDiv.innerHTML = `
            <div class="bg-gray-200 px-4 py-2 rounded-lg max-w-2xl">
                <div class="prose prose-sm">${marked.parse(content)}</div>
                ${sourcesHtml}
            </div>
        `;
    } else if (role === 'error') {
        messageDiv.className = 'flex justify-center';
        messageDiv.innerHTML = `
            <div class="bg-red-100 text-red-700 px-4 py-2 rounded-lg">
                ${escapeHtml(content)}
            </div>
        `;
    }

    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    return id;
}

function addLoadingMessage() {
    const id = 'loading-' + Date.now();
    const loadingDiv = document.createElement('div');
    loadingDiv.id = id;
    loadingDiv.className = 'flex justify-start';
    loadingDiv.innerHTML = `
        <div class="bg-gray-200 px-4 py-2 rounded-lg">
            <div class="flex space-x-1">
                <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
                <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
            </div>
        </div>
    `;
    messagesContainer.appendChild(loadingDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    return id;
}

function removeMessage(id) {
    const element = document.getElementById(id);
    if (element) element.remove();
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
