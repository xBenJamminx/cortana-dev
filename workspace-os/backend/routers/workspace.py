"""
Workspace router - memory, identity, social posts, browser actions
"""
import os
import json
import glob
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

CLAWDBOT_DIR = '/root/.clawdbot'
WORKSPACE_DIR = '/root/clawd'

# ============ MEMORY ============

@router.get('/memory/')
async def list_memory_files():
    """List all memory files"""
    memory_dir = f'{WORKSPACE_DIR}/memory'
    files = []

    # Main memory file
    main_memory = f'{WORKSPACE_DIR}/MEMORY.md'
    if os.path.exists(main_memory):
        stat = os.stat(main_memory)
        files.append({
            'name': 'MEMORY.md',
            'path': main_memory,
            'size': stat.st_size,
            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'type': 'main'
        })

    # Daily memory files
    if os.path.isdir(memory_dir):
        for f in sorted(os.listdir(memory_dir), reverse=True):
            if f.endswith('.md'):
                path = os.path.join(memory_dir, f)
                stat = os.stat(path)
                files.append({
                    'name': f,
                    'path': path,
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'type': 'daily'
                })

    return files

@router.get('/memory/{filename}')
async def read_memory_file(filename: str):
    """Read a specific memory file"""
    if filename == 'MEMORY.md':
        path = f'{WORKSPACE_DIR}/MEMORY.md'
    else:
        path = f'{WORKSPACE_DIR}/memory/{filename}'

    if not os.path.exists(path):
        raise HTTPException(404, "Memory file not found")

    with open(path, 'r') as f:
        content = f.read()

    return {'filename': filename, 'content': content}

@router.get('/memory/search/{query}')
async def search_memory(query: str):
    """Search across all memory files"""
    results = []
    query_lower = query.lower()

    # Search main memory
    main_path = f'{WORKSPACE_DIR}/MEMORY.md'
    if os.path.exists(main_path):
        with open(main_path, 'r') as f:
            content = f.read()
            if query_lower in content.lower():
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if query_lower in line.lower():
                        results.append({
                            'file': 'MEMORY.md',
                            'line': i + 1,
                            'content': line.strip(),
                            'context': '\n'.join(lines[max(0,i-2):min(len(lines),i+3)])
                        })

    # Search daily files
    memory_dir = f'{WORKSPACE_DIR}/memory'
    if os.path.isdir(memory_dir):
        for filename in os.listdir(memory_dir):
            if filename.endswith('.md'):
                path = os.path.join(memory_dir, filename)
                with open(path, 'r') as f:
                    content = f.read()
                    if query_lower in content.lower():
                        lines = content.split('\n')
                        for i, line in enumerate(lines):
                            if query_lower in line.lower():
                                results.append({
                                    'file': filename,
                                    'line': i + 1,
                                    'content': line.strip(),
                                    'context': '\n'.join(lines[max(0,i-2):min(len(lines),i+3)])
                                })

    return results[:50]  # Limit results

# ============ IDENTITY ============

@router.get('/identity/')
async def get_identity_docs():
    """Get all identity documents"""
    docs = {}
    for doc in ['SOUL.md', 'IDENTITY.md', 'USER.md', 'AGENTS.md', 'TOOLS.md']:
        path = f'{WORKSPACE_DIR}/{doc}'
        if os.path.exists(path):
            with open(path, 'r') as f:
                stat = os.stat(path)
                docs[doc] = {
                    'content': f.read(),
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                }
    return docs

class IdentityUpdate(BaseModel):
    content: str

@router.put('/identity/{doc_name}')
async def update_identity_doc(doc_name: str, update: IdentityUpdate):
    """Update an identity document"""
    allowed = ['SOUL.md', 'IDENTITY.md', 'USER.md', 'MEMORY.md']
    if doc_name not in allowed:
        raise HTTPException(400, f"Document must be one of: {allowed}")

    path = f'{WORKSPACE_DIR}/{doc_name}'

    # Backup first
    if os.path.exists(path):
        with open(path, 'r') as f:
            backup_content = f.read()
        with open(f'{path}.bak', 'w') as f:
            f.write(backup_content)

    with open(path, 'w') as f:
        f.write(update.content)

    return {'success': True, 'doc': doc_name}

# ============ SOCIAL POSTS ============

@router.get('/social-posts/')
async def list_social_posts():
    """List generated social post assets"""
    posts_dir = f'{WORKSPACE_DIR}/social_posts'
    posts = []

    if os.path.isdir(posts_dir):
        for f in os.listdir(posts_dir):
            path = os.path.join(posts_dir, f)
            stat = os.stat(path)
            file_type = 'image' if f.endswith(('.png', '.jpg', '.jpeg', '.gif')) else 'text' if f.endswith('.md') else 'other'
            posts.append({
                'name': f,
                'path': path,
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'type': file_type,
                'url': f'/api/workspace/social-posts/{f}/view' if file_type == 'image' else None
            })

    return sorted(posts, key=lambda x: x['modified'], reverse=True)

@router.get('/social-posts/{filename}/view')
async def view_social_post(filename: str):
    """Get a social post file"""
    from fastapi.responses import FileResponse
    path = f'{WORKSPACE_DIR}/social_posts/{filename}'
    if not os.path.exists(path):
        raise HTTPException(404, "File not found")
    return FileResponse(path)

# ============ WORKSPACE FILES ============

@router.get('/files/')
async def list_workspace_files():
    """List important workspace files"""
    files = []
    important_extensions = ['.md', '.py', '.js', '.json']

    for f in os.listdir(WORKSPACE_DIR):
        path = os.path.join(WORKSPACE_DIR, f)
        if os.path.isfile(path):
            ext = os.path.splitext(f)[1]
            if ext in important_extensions:
                stat = os.stat(path)
                files.append({
                    'name': f,
                    'path': path,
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'extension': ext
                })

    return sorted(files, key=lambda x: x['modified'], reverse=True)

@router.get('/files/{filename}')
async def read_workspace_file(filename: str):
    """Read a workspace file"""
    # Security: only allow reading from workspace
    path = f'{WORKSPACE_DIR}/{filename}'
    if not os.path.exists(path):
        raise HTTPException(404, "File not found")
    if not path.startswith(WORKSPACE_DIR):
        raise HTTPException(403, "Access denied")

    with open(path, 'r') as f:
        content = f.read()

    return {'filename': filename, 'content': content}

# ============ BROWSER ============

@router.get('/browser/screenshot')
async def take_browser_screenshot():
    """Take a screenshot of the current browser state"""
    import subprocess
    import base64

    screenshot_path = f'{WORKSPACE_DIR}/workspace-os/screenshots/browser-current.png'

    try:
        # Use playwright to take screenshot
        result = subprocess.run([
            'npx', 'playwright', 'screenshot',
            '--browser', 'chromium',
            'about:blank',  # Just capture current state
            screenshot_path
        ], capture_output=True, timeout=30, cwd=f'{WORKSPACE_DIR}/workspace-os')

        if os.path.exists(screenshot_path):
            return {'success': True, 'path': screenshot_path, 'url': '/api/workspace/browser/screenshot/view'}
        else:
            return {'success': False, 'error': 'Screenshot not created'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

@router.get('/browser/screenshot/view')
async def view_browser_screenshot():
    """View the latest browser screenshot"""
    from fastapi.responses import FileResponse
    path = f'{WORKSPACE_DIR}/workspace-os/screenshots/browser-current.png'
    if not os.path.exists(path):
        raise HTTPException(404, "No screenshot available")
    return FileResponse(path)

# ============ QUICK ACTIONS ============

class TelegramMessage(BaseModel):
    chat_id: str
    message: str

@router.post('/actions/telegram')
async def send_telegram_message(msg: TelegramMessage):
    """Send a Telegram message"""
    import httpx

    # Read bot token from config
    config_path = f'{CLAWDBOT_DIR}/clawdbot.json'
    with open(config_path, 'r') as f:
        config = json.load(f)

    bot_token = config.get('channels', {}).get('telegram', {}).get('botToken')
    if not bot_token:
        raise HTTPException(400, "Telegram not configured")

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f'https://api.telegram.org/bot{bot_token}/sendMessage',
            json={'chat_id': msg.chat_id, 'text': msg.message}
        )
        return resp.json()

class ContentAction(BaseModel):
    action: str  # approve, reject, move
    new_status: Optional[str] = None

@router.post('/actions/content/{item_id}')
async def content_action(item_id: int, action: ContentAction):
    """Perform action on content item"""
    # This would integrate with the main content endpoints
    # For now, return the action info
    status_map = {
        'approve': 'approved',
        'reject': 'rejected',
        'to_draft': 'draft',
        'to_review': 'review',
        'to_posted': 'posted'
    }

    new_status = action.new_status or status_map.get(action.action)
    if not new_status:
        raise HTTPException(400, "Invalid action")

    # Would call the main content update endpoint
    return {'item_id': item_id, 'new_status': new_status, 'action': action.action}

# ============ STATS ============

@router.get('/stats/')
async def get_workspace_stats():
    """Get comprehensive workspace statistics"""
    stats = {}

    # Memory stats
    memory_dir = f'{WORKSPACE_DIR}/memory'
    if os.path.isdir(memory_dir):
        memory_files = [f for f in os.listdir(memory_dir) if f.endswith('.md')]
        stats['memory_days'] = len(memory_files)

    # Social posts
    posts_dir = f'{WORKSPACE_DIR}/social_posts'
    if os.path.isdir(posts_dir):
        stats['social_posts'] = len(os.listdir(posts_dir))

    # Workspace files
    workspace_files = [f for f in os.listdir(WORKSPACE_DIR) if os.path.isfile(os.path.join(WORKSPACE_DIR, f))]
    stats['workspace_files'] = len(workspace_files)

    # Get memory db size
    memory_db = f'{CLAWDBOT_DIR}/memory/main.sqlite'
    if os.path.exists(memory_db):
        stats['memory_db_mb'] = round(os.path.getsize(memory_db) / (1024 * 1024), 2)

    return stats
