"""
Documents router - File management for Cortana's generated content
"""
import os
import json
import mimetypes
from datetime import datetime
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel
from typing import Optional, List
import base64

router = APIRouter()

WORKSPACE_DIR = '/root/clawd'

# File categories
CATEGORIES = {
    'identity': ['SOUL.md', 'IDENTITY.md', 'USER.md', 'AGENTS.md', 'TOOLS.md', 'MEMORY.md', 'HEARTBEAT.md'],
    'docs': ['.md', '.txt', '.rst'],
    'code': ['.py', '.js', '.ts', '.json', '.yaml', '.yml', '.sh'],
    'images': ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp'],
    'data': ['.csv', '.sqlite', '.db'],
}

def get_file_category(filename: str, filepath: str) -> str:
    """Determine file category"""
    if filename in CATEGORIES['identity']:
        return 'identity'

    ext = os.path.splitext(filename)[1].lower()
    for cat, extensions in CATEGORIES.items():
        if ext in extensions:
            return cat
    return 'other'

def get_file_info(filepath: str, base_path: str = WORKSPACE_DIR) -> dict:
    """Get detailed file information"""
    try:
        stat = os.stat(filepath)
        filename = os.path.basename(filepath)
        rel_path = os.path.relpath(filepath, base_path)

        return {
            'name': filename,
            'path': rel_path,
            'full_path': filepath,
            'size': stat.st_size,
            'size_human': format_size(stat.st_size),
            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
            'category': get_file_category(filename, filepath),
            'extension': os.path.splitext(filename)[1].lower(),
            'is_binary': is_binary_file(filepath),
        }
    except Exception as e:
        return None

def format_size(size: int) -> str:
    """Format file size in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"

def is_binary_file(filepath: str) -> bool:
    """Check if file is binary"""
    text_extensions = ['.md', '.txt', '.py', '.js', '.ts', '.json', '.yaml', '.yml', '.sh', '.html', '.css', '.rst']
    ext = os.path.splitext(filepath)[1].lower()
    return ext not in text_extensions

def scan_directory(path: str, max_depth: int = 3, current_depth: int = 0) -> List[dict]:
    """Recursively scan directory for files"""
    files = []

    if current_depth > max_depth:
        return files

    try:
        for item in os.listdir(path):
            if item.startswith('.') and item not in ['.env']:
                continue
            if item in ['venv', 'venv-x-api', '__pycache__', 'node_modules', '.git']:
                continue

            item_path = os.path.join(path, item)

            if os.path.isfile(item_path):
                info = get_file_info(item_path)
                if info:
                    files.append(info)
            elif os.path.isdir(item_path) and current_depth < max_depth:
                files.extend(scan_directory(item_path, max_depth, current_depth + 1))
    except PermissionError:
        pass

    return files

@router.get('/')
async def list_documents(category: Optional[str] = None, search: Optional[str] = None):
    """List all documents in workspace"""
    files = scan_directory(WORKSPACE_DIR)

    # Sort by modified date (newest first)
    files.sort(key=lambda x: x['modified'], reverse=True)

    # Filter by category if specified
    if category:
        files = [f for f in files if f['category'] == category]

    # Search filter
    if search:
        search_lower = search.lower()
        files = [f for f in files if search_lower in f['name'].lower() or search_lower in f['path'].lower()]

    # Group by category for summary
    categories = {}
    for f in files:
        cat = f['category']
        if cat not in categories:
            categories[cat] = {'count': 0, 'size': 0}
        categories[cat]['count'] += 1
        categories[cat]['size'] += f['size']

    return {
        'files': files,
        'total': len(files),
        'categories': categories
    }

@router.get('/tree')
async def get_directory_tree():
    """Get directory structure as tree"""
    def build_tree(path: str, depth: int = 0, max_depth: int = 3) -> dict:
        name = os.path.basename(path) or path
        node = {
            'name': name,
            'path': os.path.relpath(path, WORKSPACE_DIR),
            'type': 'directory' if os.path.isdir(path) else 'file'
        }

        if os.path.isdir(path) and depth < max_depth:
            children = []
            try:
                for item in sorted(os.listdir(path)):
                    if item.startswith('.') or item in ['venv', 'venv-x-api', '__pycache__', 'node_modules']:
                        continue
                    item_path = os.path.join(path, item)
                    children.append(build_tree(item_path, depth + 1, max_depth))
            except PermissionError:
                pass
            node['children'] = children
        elif os.path.isfile(path):
            stat = os.stat(path)
            node['size'] = stat.st_size
            node['modified'] = datetime.fromtimestamp(stat.st_mtime).isoformat()

        return node

    return build_tree(WORKSPACE_DIR)

@router.get('/categories')
async def list_categories():
    """List available document categories with counts"""
    files = scan_directory(WORKSPACE_DIR)

    categories = {}
    for f in files:
        cat = f['category']
        if cat not in categories:
            categories[cat] = {
                'name': cat,
                'count': 0,
                'total_size': 0,
                'extensions': set()
            }
        categories[cat]['count'] += 1
        categories[cat]['total_size'] += f['size']
        categories[cat]['extensions'].add(f['extension'])

    # Convert sets to lists for JSON serialization
    for cat in categories.values():
        cat['extensions'] = list(cat['extensions'])
        cat['total_size_human'] = format_size(cat['total_size'])

    return list(categories.values())

@router.get('/recent')
async def get_recent_documents(limit: int = 20):
    """Get recently modified documents"""
    files = scan_directory(WORKSPACE_DIR)
    files.sort(key=lambda x: x['modified'], reverse=True)
    return files[:limit]

@router.get('/read/{file_path:path}')
async def read_document(file_path: str):
    """Read document content"""
    full_path = os.path.join(WORKSPACE_DIR, file_path)

    # Security check
    if not full_path.startswith(WORKSPACE_DIR):
        raise HTTPException(403, "Access denied")

    if not os.path.exists(full_path):
        raise HTTPException(404, "File not found")

    if not os.path.isfile(full_path):
        raise HTTPException(400, "Not a file")

    info = get_file_info(full_path)

    if info['is_binary']:
        # Return file as download for binary files
        return FileResponse(full_path, filename=info['name'])

    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return {
            **info,
            'content': content
        }
    except Exception as e:
        raise HTTPException(500, f"Error reading file: {str(e)}")

@router.get('/preview/{file_path:path}')
async def preview_image(file_path: str, thumbnail: bool = False):
    """Preview image file"""
    full_path = os.path.join(WORKSPACE_DIR, file_path)

    if not full_path.startswith(WORKSPACE_DIR):
        raise HTTPException(403, "Access denied")

    if not os.path.exists(full_path):
        raise HTTPException(404, "File not found")

    ext = os.path.splitext(full_path)[1].lower()
    if ext not in ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp']:
        raise HTTPException(400, "Not an image file")

    return FileResponse(full_path)

@router.get('/download/{file_path:path}')
async def download_document(file_path: str):
    """Download any document"""
    full_path = os.path.join(WORKSPACE_DIR, file_path)

    if not full_path.startswith(WORKSPACE_DIR):
        raise HTTPException(403, "Access denied")

    if not os.path.exists(full_path):
        raise HTTPException(404, "File not found")

    return FileResponse(full_path, filename=os.path.basename(full_path))

class DocumentCreate(BaseModel):
    path: str
    content: str

@router.post('/create')
async def create_document(doc: DocumentCreate):
    """Create a new document"""
    full_path = os.path.join(WORKSPACE_DIR, doc.path)

    if not full_path.startswith(WORKSPACE_DIR):
        raise HTTPException(403, "Access denied")

    # Create directory if needed
    dir_path = os.path.dirname(full_path)
    if dir_path and not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)

    try:
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(doc.content)

        return {
            'success': True,
            'path': doc.path,
            'file': get_file_info(full_path)
        }
    except Exception as e:
        raise HTTPException(500, f"Error creating file: {str(e)}")

class DocumentUpdate(BaseModel):
    content: str

@router.put('/update/{file_path:path}')
async def update_document(file_path: str, update: DocumentUpdate):
    """Update document content"""
    full_path = os.path.join(WORKSPACE_DIR, file_path)

    if not full_path.startswith(WORKSPACE_DIR):
        raise HTTPException(403, "Access denied")

    if not os.path.exists(full_path):
        raise HTTPException(404, "File not found")

    # Backup first
    backup_path = full_path + '.bak'
    try:
        with open(full_path, 'r') as f:
            backup_content = f.read()
        with open(backup_path, 'w') as f:
            f.write(backup_content)
    except:
        pass

    try:
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(update.content)

        return {
            'success': True,
            'path': file_path,
            'file': get_file_info(full_path)
        }
    except Exception as e:
        raise HTTPException(500, f"Error updating file: {str(e)}")

@router.delete('/delete/{file_path:path}')
async def delete_document(file_path: str):
    """Delete a document (moves to trash)"""
    full_path = os.path.join(WORKSPACE_DIR, file_path)

    if not full_path.startswith(WORKSPACE_DIR):
        raise HTTPException(403, "Access denied")

    if not os.path.exists(full_path):
        raise HTTPException(404, "File not found")

    # Don't allow deleting identity files
    filename = os.path.basename(full_path)
    if filename in CATEGORIES['identity']:
        raise HTTPException(403, "Cannot delete identity files")

    # Move to trash folder instead of deleting
    trash_dir = os.path.join(WORKSPACE_DIR, '.trash')
    os.makedirs(trash_dir, exist_ok=True)

    trash_path = os.path.join(trash_dir, f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}")

    try:
        os.rename(full_path, trash_path)
        return {
            'success': True,
            'deleted': file_path,
            'trash_path': trash_path
        }
    except Exception as e:
        raise HTTPException(500, f"Error deleting file: {str(e)}")

@router.get('/stats')
async def get_document_stats():
    """Get overall document statistics"""
    files = scan_directory(WORKSPACE_DIR)

    total_size = sum(f['size'] for f in files)

    # Get category breakdown
    by_category = {}
    for f in files:
        cat = f['category']
        if cat not in by_category:
            by_category[cat] = {'count': 0, 'size': 0}
        by_category[cat]['count'] += 1
        by_category[cat]['size'] += f['size']

    # Recent activity
    files.sort(key=lambda x: x['modified'], reverse=True)
    recent = files[:5]

    return {
        'total_files': len(files),
        'total_size': total_size,
        'total_size_human': format_size(total_size),
        'by_category': by_category,
        'recent': recent
    }

@router.get('/social-posts')
async def list_social_posts():
    """List generated social media posts"""
    posts_dir = os.path.join(WORKSPACE_DIR, 'social_posts')
    posts = []

    if os.path.isdir(posts_dir):
        for item in os.listdir(posts_dir):
            item_path = os.path.join(posts_dir, item)
            if os.path.isfile(item_path):
                info = get_file_info(item_path)
                if info:
                    # Add preview URL for images
                    if info['category'] == 'images':
                        info['preview_url'] = f"/api/documents/preview/social_posts/{item}"
                    posts.append(info)

    posts.sort(key=lambda x: x['modified'], reverse=True)
    return posts

@router.get('/canvas')
async def list_canvas_files():
    """List canvas/generated artwork"""
    canvas_dir = os.path.join(WORKSPACE_DIR, 'canvas')
    files = []

    if os.path.isdir(canvas_dir):
        for item in os.listdir(canvas_dir):
            item_path = os.path.join(canvas_dir, item)
            if os.path.isfile(item_path):
                info = get_file_info(item_path)
                if info:
                    if info['category'] == 'images':
                        info['preview_url'] = f"/api/documents/preview/canvas/{item}"
                    files.append(info)

    files.sort(key=lambda x: x['modified'], reverse=True)
    return files
