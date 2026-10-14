# Tavilio plugin

Run a venue on [Tavilio](https://www.tavilio.app) from your AI assistant:
bookings, events, the menu and products, opening hours and the website.

This repository is the plugin package for two directories:

| Directory | What it reads |
| --- | --- |
| ChatGPT plugin directory (ChatGPT and Codex) | `plugin.json`, `mcp.json`, `skills/`, `assets/`, uploaded as a ZIP |
| Grok Build plugin marketplace | `.grok-plugin/plugin.json`, `.mcp.json`, `skills/`, `assets/` |

## What it contains

- **MCP server:** the hosted Tavilio server at `https://www.tavilio.app/api/mcp`
  (Streamable HTTP). Nothing runs on your machine.
- **Skills:** `skills/tavilio` explains how to work with a venue through the
  server; `skills/get-started` is the first-run setup (read-only).
- **Assets:** the Tavilio logo, light and dark.

There are no hooks, commands, scripts that run on install, or local servers.

## Sign-in and permissions

The first connection sends you to Tavilio to sign in and approve **one venue**
(OAuth 2.1 with PKCE and dynamic client registration). No API key is needed or
stored in this package. The assistant then acts on that venue only, with the
powers of one of its admins. It cannot change the plan or billing, manage the
team's accounts, delete the venue or reach another venue. You can see and
disconnect connected assistants in the Tavilio admin under
**Settings › AI access**; disconnecting stops access at once.

Every tool declares whether it only reads (`readOnlyHint`), whether it can
overwrite, delete, cancel or email a guest (`destructiveHint`), and whether it
reaches outside the venue (`openWorldHint`).

### Network endpoints

| Endpoint | Why |
| --- | --- |
| `https://www.tavilio.app/api/mcp` | The MCP server: every tool call |
| `https://www.tavilio.app/.well-known/oauth-protected-resource` | Where the client learns how to sign in |
| The Supabase Auth server it names | Sign-in, client registration and tokens |

### Data

Tool results contain the venue's own data, including guests' names, emails
and phone numbers on bookings. Tavilio's handling of it is described in the
[privacy policy](https://www.tavilio.app/privacy-policy); see also the
[terms of use](https://www.tavilio.app/terms-of-use).

## Support

[www.tavilio.app/support](https://www.tavilio.app/support) ·
support@dopler.app

## Building the ChatGPT package

```bash
python3 scripts/build_chatgpt_zip.py
```

It checks the manifest against the directory's limits and writes
`dist/tavilio-<version>.zip` with only the files ChatGPT reads. Upload it at
[platform.openai.com/plugins](https://platform.openai.com/plugins).

## License

MIT, except the Tavilio name and logo. See [LICENSE](LICENSE).
