# Perplexity Integration for Cursor

To integrate Perplexity with Cursor using Docker, copy and paste the following configuration into your Cursor MCP server settings (plain text field). Replace `YOUR_PERPLEXITY_API_KEY` with your actual API key.

```json
{
  "name": "perplexity-ask",
  "command": "docker",
  "args": [
    "run",
    "-i",
    "--rm",
    "-e",
    "PERPLEXITY_API_KEY",
    "mcp/perplexity-ask"
  ],
  "env": {
    "PERPLEXITY_API_KEY": "YOUR_PERPLEXITY_API_KEY"
  }
}
```

**Note:**

This setup uses the latest available Docker image for Perplexity's MCP integration and is compatible with Cursor's current configuration as of July 2025. No hardcoded image hashes are required. Make sure Docker is running and your API key is valid. 