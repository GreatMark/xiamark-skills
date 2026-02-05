---
name: tavily-search
description: Search the web using Tavily API. Optimized for LLMs, returns clean content and answers. Use this for general knowledge, news, and research.
---

# Tavily Search

Search the web using Tavily API.

## Tools

### `tavily_search`

Search the web and return summarized results.

- **query**: The search query.
- **depth**: "basic" (fast) or "advanced" (comprehensive). Default: "basic".
- **include_answer**: "true" or "false". Whether to include a short answer summary. Default: "true".

```javascript
// Run the search script
// The script automatically loads the API key from secrets.json
await cli.exec({
  command: `node tavily.js "${query}" "${depth || 'basic'}" "${include_answer || 'true'}"`,
  cwd: __dirname
});
```
