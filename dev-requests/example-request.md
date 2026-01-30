# Request: Add Bookmark Search API

## Priority
medium

## Type
feature

## Description
Need an API endpoint to search bookmarks by keyword, author, or category. 
Currently bookmarks are in Airtable but we need fast local search.

## Acceptance Criteria
- [ ] GET /api/bookmarks/search?q=keyword endpoint
- [ ] Searches content, author, and category fields
- [ ] Returns paginated results
- [ ] Response time under 200ms

## Context
- Bookmarks table schema is in database.py
- Airtable sync happens in services/airtable_sync.py
- 1,300+ bookmarks to search

## Status
pending
