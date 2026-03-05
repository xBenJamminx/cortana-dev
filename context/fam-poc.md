# FAM POC — Context

## Notion
- **Database:** FAM POC (ID: `26c4666b-d1ca-807b-930d-ca5ffff9c8e9`)
- **API Key:** NOTION_API_KEY_WORK in `~/.openclaw/.env`
- **Workspace:** bjoselson27@gmail.com (Products workspace)

### Database Schema
| Property | Type |
|----------|------|
| Name | title |
| Status | status |
| Assigned | people |
| Priority | select |
| Start Date | date |
| Est. Days | number |
| Parent item | relation |
| Sub-item | relation |
| Project | relation |

### How to update after standups
1. Read meeting notes: `python3 lib/slack.py meeting-notes 3`
2. Extract action items per person (Steven, Bilal, Ben, Joel)
3. Query existing tasks: `curl -s 'https://api.notion.com/v1/databases/26c4666bd1ca807b930dca5ffff9c8e9/query' -H 'Authorization: Bearer <NOTION_API_KEY_WORK>' -H 'Notion-Version: 2022-06-28' -d '{}'`
4. Update status on completed items, add new tasks from action items
5. DO NOT ask Ben what needs updating — the meeting notes ARE the update source

## Repos
- Frontend: Unity + React/Next.js (avatars: BAYC, Capguy/Moca, Lightling)
- Backend: FastAPI + LangGraph + pgvector
- Team: Ben (PM), Steven (backend), Bilal (Unity/frontend), Joel (UI design), Cassandra (QA)

## Standup Workflow
Every standup gets posted to #meeting-notes in Slack by Fathom. When Ben says "update Notion from the standup" — read Slack, extract action items, update the database. No questions needed.
