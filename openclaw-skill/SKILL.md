---
name: openclaw-skill
description: "Use when running the Gear/Vara Sails builder workflow inside OpenClaw. Routes builders to the correct skill by task type — dev-env setup, new app scaffolding, feature work, testing, frontend, and more. Not for Vara.eth, ethexe, non-Sails programs, or generic protocol research."
metadata:
  {
    "openclaw": {
      "requires": { "bins": [] }
    }
  }
---

# Vara Skills — OpenClaw Entry Point

This wrapper exposes the self-contained `vara-skills` pack to OpenClaw agents. Load the local handbook and local skills from this repo instead of depending on sibling repositories.

## Start Here

1. Load the repo router at `../SKILL.md`.
2. Begin with `ship-sails-app` for the standard builder workflow.

Example: a builder wants to add a new service to an existing Sails app:

```
1. Load ../SKILL.md (router)
2. Router dispatches to ../skills/sails-feature-workflow/SKILL.md
3. Feature workflow references spec → architecture → implementation → gtest chain
```

## Route By Task

| Builder Need | Skill |
|---|---|
| Local Rust or Gear setup | `../skills/sails-dev-env/SKILL.md` |
| New app from scratch | `../skills/sails-new-app/SKILL.md` |
| Feature or behavior change in existing repo | `../skills/sails-feature-workflow/SKILL.md` |
| Message flow, replies, or async behavior | `../skills/gear-message-execution/SKILL.md` |
| Service or program architecture | `../skills/sails-architecture/SKILL.md` |
| IDL or generated client issues | `../skills/sails-idl-client/SKILL.md` |
| `gtest` authoring or debugging | `../skills/sails-gtest/SKILL.md` |
| Local-node smoke after green tests | `../skills/sails-local-smoke/SKILL.md` |
| React or TypeScript frontend | `../skills/sails-frontend/SKILL.md` |
| Fungible token with awesome-sails | `../skills/awesome-sails-vft/SKILL.md` |
| Wallet interactions, deploy, vouchers | `../skills/vara-wallet/SKILL.md` |

## Scope

This pack targets standard Gear/Vara Sails builders. The catalog is provisional and treated as a measured candidate set, not a frozen public taxonomy. Builders working on Vara.eth or ethexe should use dedicated skills instead.
