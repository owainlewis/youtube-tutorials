---
task: 7
title: Frontend UI with Tailwind
depends_on: [5, 6]
files: [examples/rag-chatbot/static/index.html, examples/rag-chatbot/static/app.js, examples/rag-chatbot/static/styles.css]
---

## Context

We're building a RAG chatbot with a clean, modern UI. This task creates the frontend using plain HTML, JavaScript, and Tailwind CSS (via CDN). The UI has two main areas: document management sidebar and chat interface.

Design requirements:
- Split layout with sidebar and main chat area
- Document list with upload and delete
- Chat messages with markdown rendering
- Source citations shown under AI responses
- Responsive and accessible

## Requirements

### Layout Structure

```
┌──────────────────────────────────────────────────────┐
│  Header: "RAG Chatbot"                               │
├─────────────────┬────────────────────────────────────┤
│                 │                                    │
│  Documents      │  Chat Messages                     │
│  ┌───────────┐  │  ┌────────────────────────────┐   │
│  │ doc1.txt  │  │  │ User: How does X work?     │   │
│  │ doc2.txt  │  │  │                            │   │
│  └───────────┘  │  │ AI: Based on the docs...   │   │
│                 │  │ Sources: [chunk 1] [chunk 2]│   │
│  [Upload File]  │  └────────────────────────────┘   │
│                 │                                    │
│                 │  ┌────────────────────────────┐   │
│                 │  │ Type a message...    [Send]│   │
│                 │  └────────────────────────────┘   │
└─────────────────┴────────────────────────────────────┘
```

### Document Sidebar

- List all documents with filename and date
- Delete button (X) for each document
- Upload button opens file picker
- Show upload progress/loading state
- Refresh list after upload/delete

### Chat Interface

- Message history with user/assistant styling
- User messages: right-aligned, blue background
- Assistant messages: left-aligned, gray background
- Markdown rendering for responses (use marked.js)
- Source section under each AI response
- Sources show chunk content preview and similarity

### Input Area

- Text input for messages
- Send button (or Enter to submit)
- Disable during API call
- Clear input after send

## Technical Notes

- Tailwind via CDN: `<script src="https://cdn.tailwindcss.com">`
- marked.js for markdown: `<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js">`
- Use fetch API for all requests
- Handle loading states (disable buttons, show spinner)
- Handle errors (show error message to user)
- Sidebar width: ~250px fixed
- Dark header matching existing project style

### Color Scheme

- Header: bg-gray-800, text-white
- Sidebar: bg-gray-100
- User messages: bg-blue-500, text-white
- Assistant messages: bg-gray-200
- Sources: bg-gray-50, border, rounded

## Acceptance Criteria

- [ ] Split layout with sidebar and chat
- [ ] Document list shows all documents
- [ ] Upload button opens file picker
- [ ] File uploads and appears in list
- [ ] Delete button removes document
- [ ] Chat input sends message
- [ ] User messages styled correctly
- [ ] AI responses render markdown
- [ ] Sources shown under AI responses
- [ ] Loading states for all actions
- [ ] Error messages displayed to user
- [ ] Responsive on smaller screens
