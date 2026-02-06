Living System Debugger - Mock Incident Artifacts
================================================

Scenario:
- A deployment increased Gunicorn worker count from 2 -> 8.
- Redis was configured with maxclients=100.
- Shortly after deploy, Redis hit maxclients and began rejecting connections.
- Cache failures caused DB fallback and increased DB connections.
- Nginx observed 502s (upstream timeout) and overall latency increased.

Suggested user question for Gemini:
"Why did API latency spike shortly after the most recent deployment?"
