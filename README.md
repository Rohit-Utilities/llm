# LLM Utility

A reusable, conversation-aware LLM utility for Python applications.

The package provides:

- LLM provider abstraction
- Zydit provider integration
- Conversation lifecycle management
- Recent-message conversation memory
- Conversation compaction
- Automatic conversation summaries
- Prompt construction
- Configurable conversation limits
- Environment-based configuration

The utility is designed to be copied or integrated into different Python projects without depending on an application's internal package structure.

## Requirements

- Python 3.10+
- Access to the Zydit API
- A valid Zydit API key

Install dependencies with:

```bash
pip install -r requirements.txt
```

Current dependencies:

```text
pydantic>=2.0,<3
pydantic-settings==2.10.1
openai==1.109.1
```

## Configuration

Create a `.env` file in the project where the utility is being used:

```env
LLM_PROVIDER=zydit

ZYDIT_API_KEY=your_zydit_api_key
ZYDIT_MODEL=your_zydit_model
ZYDIT_BASE_URL=your_zydit_base_url

CONVERSATION_RECENT_MESSAGES=8
CONVERSATION_SUMMARY_MAX_TOKENS=256

MAX_OUTPUT_TOKENS=780
REQUEST_TIMEOUT=30.0
```

### Required Variables

| Variable | Description |
|---|---|
| `LLM_PROVIDER` | LLM provider to use. Currently `zydit`. |
| `ZYDIT_API_KEY` | API key used to authenticate with Zydit. |
| `ZYDIT_MODEL` | Zydit model used for generation. |
| `ZYDIT_BASE_URL` | Zydit API endpoint. |

## Security

Never commit API credentials to GitHub.

Add the following to `.gitignore`:

```gitignore
.env
.venv/
__pycache__/
*.pyc
```

Do not put API keys directly into Python source code.

## Zydit Dependency

The current implementation depends on Zydit.

```text
Application
     │
     ▼
LLM Utility
     │
     ▼
Zydit API
     │
     ▼
LLM Model
```

If the Zydit service is unavailable, the utility cannot generate an LLM response.

This includes situations such as:

- API maintenance
- provider outages
- upstream infrastructure failures
- model availability issues
- authentication failures
- API connectivity problems

The current utility does not provide an offline LLM fallback or automatic provider failover.

## Basic Usage

Import the service from the package root:

```python
from llm import LLMService
```

Create the service and a conversation:

```python
llm_service = LLMService()
conversation_id = llm_service.create_conversation()
```

Generate a response:

```python
response = llm_service.generate(
    conversation_id=conversation_id,
    prompt="Hello, how are you?",
)

print(response)
```

## Conversation Continuity

A conversation is identified by its conversation ID.

Create the conversation once:

```python
conversation_id = llm_service.create_conversation()
```

Reuse the same ID for subsequent messages:

```python
llm_service.generate(
    conversation_id=conversation_id,
    prompt="We are building an AI assistant.",
)

response = llm_service.generate(
    conversation_id=conversation_id,
    prompt="What are we building?",
)
```

The `ConversationManager` maintains the conversation state. Create a new conversation only when a new independent conversation is required.

## Conversation Memory

The utility maintains a short-term conversation window. By default, the latest eight messages remain intact.

When the conversation exceeds this boundary, older messages are compacted into a summary:

```text
Older Messages
      │
      ▼
ConversationGuard
      │
      ▼
ConciseBuilder
      │
      ▼
Zydit
      │
      ▼
Generated Summary
      │
      ▼
Conversation
```

The older messages are replaced by a compact summary while the most recent configured messages remain intact.

## Conversation Compaction

Compaction occurs after a complete conversation turn has been created:

```text
USER message
     │
     ▼
LLM response
     │
     ▼
ASSISTANT message
     │
     ▼
ConversationGuard
```

If the recent-message boundary is exceeded:

```text
Older messages
      │
      ▼
ConciseBuilder
      │
      ▼
Summary prompt
      │
      ▼
Zydit
      │
      ▼
Summary
      │
      ▼
ConversationGuard
      │
      ├── Store summary
      └── Retain recent messages
```

A turn that triggers compaction can therefore require two LLM calls: one for the summary and one for the actual assistant response.

## PromptBuilder

`PromptBuilder` creates the final prompt sent to the LLM. It combines:

```text
System instructions
        +
Conversation summary
        +
Recent conversation messages
```

The current `Conversation` object is the source of truth.

`PromptBuilder` does not call an LLM, manage conversations, summarize history, access Qdrant, or perform retrieval.

## ConciseBuilder

`ConciseBuilder` creates the prompt used for conversation compaction. It receives messages to compact and the existing summary, then produces a summarization prompt.

It does not call the LLM itself. The configured provider generates the summary.

## ConversationGuard

`ConversationGuard` controls the recent-message boundary. Its responsibilities include:

- determining whether compaction is required
- identifying messages to compact
- identifying messages to retain
- applying the generated summary
- retaining the configured recent messages

The guard does not call the LLM.

## ConversationManager

`ConversationManager` manages conversation state. It is responsible for:

- creating conversations
- retrieving conversations
- adding messages
- updating summaries
- checking conversation existence
- deleting conversations

It does not call an LLM, build prompts, summarize messages, perform retrieval, access Qdrant, or enforce conversation limits.

The current implementation stores conversations in memory. Restarting the application removes them.

## Provider Architecture

```text
LLMService
    │
    ▼
LLMProvider
    │
    ▼
ZyditClient
    │
    ▼
Zydit API
```

`LLMService` selects the provider. `ZyditClient` handles Zydit API communication.

The provider does not manage conversations, prompts, memory, summarization, or retrieval.

## Provider Selection

Set the provider in `.env`:

```env
LLM_PROVIDER=zydit
```

The current provider registry contains:

```text
zydit → ZyditClient
```

Additional providers can be added to the registry in the future.

## Package Structure

```text
llm/
├── __init__.py
├── base.py
├── config.py
├── service.py
│
├── provider/
│   ├── __init__.py
│   └── zydit.py
│
├── prompt/
│   ├── __init__.py
│   ├── prompt_builder.py
│   ├── concise.py
│   ├── guard.py
│   └── models/
│       ├── __init__.py
│       ├── message.py
│       └── conversation.py
│
└── manager/
    ├── __init__.py
    └── conversation_manager.py
```

## Public API

The primary entry point is:

```python
from llm import LLMService
```

The package root exposes:

```python
from llm.service import LLMService

__all__ = ["LLMService"]
```

Applications should generally interact with the package through `LLMService`.

## Testing

### Import Test

```python
from llm import LLMService

llm_service = LLMService()

print("LLM import: OK")
```

### Generation Test

```python
from llm import LLMService

llm_service = LLMService()
conversation_id = llm_service.create_conversation()

response = llm_service.generate(
    conversation_id=conversation_id,
    prompt="Hello from the LLM utility.",
)

print(response)
```

Make sure the `.env` file contains valid Zydit credentials before running an actual generation test.

## Current Limitations

### Zydit dependency

Zydit is currently the only supported LLM provider.

### In-memory conversations

Conversations are currently stored in Python process memory.

### No long-term memory

The utility does not currently provide:

- Qdrant integration
- vector embeddings
- semantic retrieval
- long-term conversation memory
- RAG retrieval

Those responsibilities belong to the application using the utility.

### No provider fallback

If Zydit is unavailable, the utility does not automatically switch to another provider.

## Design Responsibilities

```text
LLMService
    Application-level orchestration

ConversationManager
    Conversation lifecycle and state

ConversationGuard
    Recent-message boundary and compaction

ConciseBuilder
    Summary prompt construction

PromptBuilder
    Final prompt construction

LLMProvider
    Provider abstraction

ZyditClient
    Zydit API communication
```

This separation keeps the LLM layer reusable and prevents provider-specific logic from spreading throughout the application.

## Using the Utility in Another Project

Copy or clone the `llm` package into the project:

```text
my-project/
├── llm/
│   ├── __init__.py
│   ├── service.py
│   ├── config.py
│   ├── base.py
│   ├── provider/
│   ├── prompt/
│   └── manager/
│
├── .env
└── ...
```

Then import:

```python
from llm import LLMService
```

The package uses the `llm` namespace internally and does not depend on an application's package structure such as `ai.llm`.

## Setup Checklist

- [ ] Copy or clone the `llm` package.
- [ ] Install `requirements.txt`.
- [ ] Create a `.env` file.
- [ ] Set `LLM_PROVIDER=zydit`.
- [ ] Configure `ZYDIT_API_KEY`.
- [ ] Configure `ZYDIT_MODEL`.
- [ ] Configure `ZYDIT_BASE_URL`.
- [ ] Verify that the Zydit service is available.
- [ ] Run an import test.
- [ ] Run a generation test.
- [ ] Reuse the same conversation ID for conversation continuity.
