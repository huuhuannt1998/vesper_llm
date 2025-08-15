# VESPER LLM CONNECTION TROUBLESHOOTING

## Network Connectivity Issue Identified

The system is unable to establish a connection to `100.98.151.66:1234`. This could be due to:

1. **Network/Firewall Issues**: The IP address might not be accessible from your network
2. **Server Status**: The LLM server might be down or moved
3. **DNS/IP Changes**: The server address might have changed

## Solution Options:

### Option 1: Use Local LLM Server (Recommended)
Set up a local LLM server using tools like:
- **Ollama**: https://ollama.ai/
- **LM Studio**: https://lmstudio.ai/
- **Text generation web UI**: https://github.com/oobabooga/text-generation-webui

Then update `.env`:
```
LLM_API_URL=http://localhost:1234/v1
```

### Option 2: Use Alternative LLM Service
Update `.env` to use services like:
- **OpenAI**: `https://api.openai.com/v1`
- **Local GPU server**: `http://localhost:8080/v1`

### Option 3: Set Up SSH Tunnel (If server is accessible via SSH)
```bash
ssh -L 1234:100.98.151.66:1234 user@accessible-server.com
```

Then use:
```
LLM_API_URL=http://localhost:1234/v1
```

### Option 4: Mock LLM for Testing
For testing purposes, you can use a mock LLM that returns simple responses.

## Current Status:
- ✅ Blender addon loads successfully (Unicode issues fixed)
- ✅ Environment configuration is correct
- ✅ LLM client code is working
- ❌ Network connectivity to LLM server

## Next Steps:
1. Choose one of the solution options above
2. Update the `.env` file with the new LLM server URL
3. Test the connection with: `python -c "from backend.app.llm.client import chat_completion; print(chat_completion('test', 'hello', 5))"`
