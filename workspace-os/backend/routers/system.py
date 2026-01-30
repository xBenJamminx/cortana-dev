"""
System router - agents, skills, schedules, integrations
"""
import os
import json
from fastapi import APIRouter, HTTPException
from datetime import datetime

router = APIRouter()

CLAWDBOT_DIR = '/root/.clawdbot'

def read_json(path, default=None):
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except:
        return default

# ============ AGENTS ============

@router.get('/agents/')
async def list_agents():
    """List configured agents"""
    config = read_json(f'{CLAWDBOT_DIR}/clawdbot.json', {})
    agents_config = config.get('agents', {})
    defaults = agents_config.get('defaults', {})
    agent_list = agents_config.get('list', [])

    result = []
    for agent in agent_list:
        result.append({
            'id': agent.get('id'),
            'name': agent.get('name', agent.get('id')),
            'workspace': agent.get('workspace', defaults.get('workspace')),
            'model': agent.get('model', defaults.get('model', {}).get('primary')),
            'fallbacks': defaults.get('model', {}).get('fallbacks', []),
            'memory_enabled': defaults.get('memorySearch', {}).get('enabled', False)
        })
    return result

@router.get('/agents/models')
async def list_available_models():
    """List available AI models"""
    config = read_json(f'{CLAWDBOT_DIR}/clawdbot.json', {})
    agents_config = config.get('agents', {})
    defaults = agents_config.get('defaults', {})
    models = defaults.get('models', {})

    result = []
    for model_id, settings in models.items():
        result.append({
            'id': model_id,
            'alias': settings.get('alias'),
            'primary': model_id == defaults.get('model', {}).get('primary')
        })
    return result

# ============ SKILLS ============

@router.get('/skills/')
async def list_skills():
    """List installed skills and their config"""
    config = read_json(f'{CLAWDBOT_DIR}/clawdbot.json', {})
    skills_config = config.get('skills', {})
    skill_entries = skills_config.get('entries', {})

    # Get installed skill directories
    skills_dir = f'{CLAWDBOT_DIR}/skills'
    installed = []
    if os.path.isdir(skills_dir):
        for name in os.listdir(skills_dir):
            path = os.path.join(skills_dir, name)
            if os.path.isdir(path):
                installed.append(name)

    result = []
    # Configured skills (with API keys)
    for skill_name, skill_settings in skill_entries.items():
        result.append({
            'name': skill_name,
            'configured': True,
            'installed': skill_name in installed,
            'has_api_key': 'apiKey' in skill_settings,
            'settings': {k: '***' if 'key' in k.lower() else v for k, v in skill_settings.items()}
        })

    # Installed but not in entries
    for name in installed:
        if name not in skill_entries:
            result.append({
                'name': name,
                'configured': False,
                'installed': True,
                'has_api_key': False
            })

    return result

# ============ SCHEDULES ============

@router.get('/schedules/')
async def list_schedules():
    """List scheduled cron jobs"""
    jobs = read_json(f'{CLAWDBOT_DIR}/cron/jobs.json', {'jobs': []})

    result = []
    for job in jobs.get('jobs', []):
        schedule = job.get('schedule', {})
        state = job.get('state', {})
        result.append({
            'id': job.get('id'),
            'name': job.get('name'),
            'enabled': job.get('enabled', False),
            'schedule_type': schedule.get('kind'),
            'cron_expr': schedule.get('expr'),
            'timezone': schedule.get('tz'),
            'target': job.get('sessionTarget'),
            'payload': job.get('payload', {}).get('text'),
            'next_run': datetime.fromtimestamp(state.get('nextRunAtMs', 0) / 1000).isoformat() if state.get('nextRunAtMs') else None,
            'last_run': datetime.fromtimestamp(state.get('lastRunAtMs', 0) / 1000).isoformat() if state.get('lastRunAtMs') else None,
            'last_status': state.get('lastStatus')
        })
    return result

# ============ CHANNELS/INTEGRATIONS ============

@router.get('/channels/')
async def list_channels():
    """List configured channels (Telegram, etc)"""
    config = read_json(f'{CLAWDBOT_DIR}/clawdbot.json', {})
    channels = config.get('channels', {})

    result = []
    for name, settings in channels.items():
        result.append({
            'name': name,
            'enabled': settings.get('enabled', False),
            'dm_policy': settings.get('dmPolicy'),
            'group_policy': settings.get('groupPolicy'),
            'configured': bool(settings.get('botToken'))
        })
    return result

@router.get('/env-status/')
async def get_env_status():
    """Check which .env files exist and their integrations"""
    env_files = ['.env', '.env.google', '.env.notion', '.env.slack']
    result = {}

    for env_file in env_files:
        path = f'{CLAWDBOT_DIR}/{env_file}'
        if os.path.exists(path):
            with open(path, 'r') as f:
                content = f.read()
                keys = [line.split('=')[0] for line in content.split('\n') if '=' in line and not line.startswith('#')]
            result[env_file] = {
                'exists': True,
                'keys': keys
            }
        else:
            result[env_file] = {'exists': False}

    return result

# ============ MEMORY ============

@router.get('/memory/stats')
async def get_memory_stats():
    """Get memory database stats"""
    import sqlite3
    db_path = f'{CLAWDBOT_DIR}/memory/main.sqlite'

    if not os.path.exists(db_path):
        return {'error': 'Memory database not found'}

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get table info
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]

    stats = {'tables': {}}
    for table in tables:
        try:
            cursor.execute(f'SELECT COUNT(*) FROM {table}')
            count = cursor.fetchone()[0]
            stats['tables'][table] = count
        except:
            pass

    # Get db size
    stats['db_size_mb'] = round(os.path.getsize(db_path) / (1024 * 1024), 2)

    conn.close()
    return stats

# ============ BROWSER ============

@router.get('/browser/')
async def get_browser_status():
    """Get browser configuration and status"""
    config = read_json(f'{CLAWDBOT_DIR}/clawdbot.json', {})
    browser = config.get('browser', {})

    return {
        'enabled': browser.get('enabled', False),
        'headless': browser.get('headless', True),
        'default_profile': browser.get('defaultProfile'),
        'profiles': list(browser.get('profiles', {}).keys()),
        'executable': browser.get('executablePath')
    }
