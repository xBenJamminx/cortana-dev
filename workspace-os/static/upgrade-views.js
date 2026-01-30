// Upgraded render functions for Cortana OS views

// ============================================
// GMAIL-STYLE INBOX
// ============================================

function renderEmails() {
    let emails = state.emails;
    switch(state.emailFilter) {
        case 'unread': emails = emails.filter(e => e.is_unread); break;
        case 'important': emails = emails.filter(e => e.is_important); break;
        case 'starred': emails = emails.filter(e => e.is_starred); break;
    }

    const container = document.getElementById('email-list');
    if (emails.length === 0) {
        container.innerHTML = '<div class="empty-state"><div class="icon">📭</div>No emails</div>';
        return;
    }

    container.innerHTML = `
        <div class="email-list-container">
            <div class="email-toolbar">
                <input type="checkbox" class="checkbox-all" onchange="toggleAllEmails(this.checked)" title="Select all">
                <div class="email-toolbar-actions" id="email-bulk-actions">
                    <button class="toolbar-btn archive" onclick="archiveSelected()">📥 Archive</button>
                    <button class="toolbar-btn delete" onclick="deleteSelected()">🗑️ Delete</button>
                    <button class="toolbar-btn" onclick="markSelectedRead()">✓ Mark Read</button>
                </div>
                <span style="margin-left: auto; color: var(--text-muted); font-size: 13px;">
                    ${emails.length} ${emails.length === 1 ? 'conversation' : 'conversations'}
                </span>
            </div>
            ${emails.map((e, idx) => {
                const senderName = e.from?.split('<')[0]?.trim() || 'Unknown';
                const senderEmail = e.from?.match(/<(.+)>/)?.[1] || '';
                const initials = senderName.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase();
                const avatarColors = ['#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#ef4444'];
                const avatarColor = avatarColors[senderName.charCodeAt(0) % avatarColors.length];
                const hasAttachment = e.labels?.includes('ATTACHMENT') || e.snippet?.includes('attachment');

                return `
                <div class="email-row ${e.is_unread ? 'unread' : ''} ${state.selectedEmails?.includes(e.id) ? 'selected' : ''}"
                     data-email-id="${e.id}"
                     onclick="handleEmailClick(event, '${e.id}')">
                    <input type="checkbox" class="email-checkbox"
                           ${state.selectedEmails?.includes(e.id) ? 'checked' : ''}
                           onchange="toggleEmailSelection('${e.id}')"
                           onclick="event.stopPropagation()">
                    <span class="email-star ${e.is_starred ? 'starred' : ''}"
                          onclick="event.stopPropagation(); toggleStar('${e.id}')"
                          title="${e.is_starred ? 'Unstar' : 'Star'}">
                        ${e.is_starred ? '★' : '☆'}
                    </span>
                    <div class="email-avatar" style="background: ${avatarColor}">${initials}</div>
                    <div class="email-content">
                        <div class="email-sender">${senderName}</div>
                        <div class="email-subject-line">
                            <span class="email-subject-text">${e.subject || '(No Subject)'}</span>
                            <span class="email-snippet-text">${e.snippet || ''}</span>
                        </div>
                    </div>
                    <div class="email-labels">
                        ${e.is_important ? '<span class="email-label important">Important</span>' : ''}
                        ${hasAttachment ? '<span class="email-label attachment">📎</span>' : ''}
                    </div>
                    <span class="email-time">${formatRelativeTime(e.date)}</span>
                    <div class="email-hover-actions">
                        <button class="hover-action-btn archive" onclick="event.stopPropagation(); archiveEmail('${e.id}')" title="Archive">📥</button>
                        <button class="hover-action-btn delete" onclick="event.stopPropagation(); deleteEmail('${e.id}')" title="Delete">🗑️</button>
                        <button class="hover-action-btn mark-read" onclick="event.stopPropagation(); toggleRead('${e.id}')" title="Mark as ${e.is_unread ? 'read' : 'unread'}">${e.is_unread ? '📬' : '📭'}</button>
                        <button class="hover-action-btn snooze" onclick="event.stopPropagation(); snoozeEmail('${e.id}')" title="Snooze">⏰</button>
                    </div>
                </div>
            `}).join('')}
        </div>
    `;
}

// Email helper functions
window.state.selectedEmails = [];

function toggleAllEmails(checked) {
    const checkboxes = document.querySelectorAll('.email-checkbox');
    state.selectedEmails = checked ? state.emails.map(e => e.id) : [];
    checkboxes.forEach(cb => cb.checked = checked);
    document.querySelectorAll('.email-row').forEach(row => {
        row.classList.toggle('selected', checked);
    });
    document.getElementById('email-bulk-actions').classList.toggle('visible', checked);
}

function toggleEmailSelection(emailId) {
    const idx = state.selectedEmails.indexOf(emailId);
    if (idx > -1) {
        state.selectedEmails.splice(idx, 1);
    } else {
        state.selectedEmails.push(emailId);
    }
    document.querySelector(`[data-email-id="${emailId}"]`)?.classList.toggle('selected');
    document.getElementById('email-bulk-actions').classList.toggle('visible', state.selectedEmails.length > 0);
    document.querySelector('.checkbox-all').checked = state.selectedEmails.length === state.emails.length;
}

function handleEmailClick(event, emailId) {
    if (event.target.type === 'checkbox' || event.target.classList.contains('email-star')) return;
    openEmail(emailId);
}

async function toggleStar(emailId) {
    const email = state.emails.find(e => e.id === emailId);
    if (email) {
        email.is_starred = !email.is_starred;
        renderEmails();
        // API call would go here
        toast(email.is_starred ? 'Starred' : 'Unstarred', 'success');
    }
}

async function archiveEmail(emailId) {
    toast('Archived', 'success');
    state.emails = state.emails.filter(e => e.id !== emailId);
    renderEmails();
}

async function deleteEmail(emailId) {
    toast('Moved to Trash', 'success');
    state.emails = state.emails.filter(e => e.id !== emailId);
    renderEmails();
}

function archiveSelected() {
    const count = state.selectedEmails.length;
    state.emails = state.emails.filter(e => !state.selectedEmails.includes(e.id));
    state.selectedEmails = [];
    renderEmails();
    toast(`${count} archived`, 'success');
}

function deleteSelected() {
    const count = state.selectedEmails.length;
    state.emails = state.emails.filter(e => !state.selectedEmails.includes(e.id));
    state.selectedEmails = [];
    renderEmails();
    toast(`${count} deleted`, 'success');
}

function markSelectedRead() {
    state.emails.forEach(e => {
        if (state.selectedEmails.includes(e.id)) e.is_unread = false;
    });
    state.selectedEmails = [];
    renderEmails();
    toast('Marked as read', 'success');
}

// ============================================
// CALENDAR WEEK VIEW
// ============================================

state.calendarWeekOffset = 0;
state.calendarView = 'week';

function renderCalendar(filter = 'upcoming') {
    const container = document.getElementById('calendar-events');

    if (state.calendarView === 'week') {
        renderCalendarWeekView(container);
    } else {
        renderCalendarListView(container, filter);
    }
}

function renderCalendarWeekView(container) {
    const now = new Date();
    const startOfWeek = new Date(now);
    startOfWeek.setDate(now.getDate() - now.getDay() + (state.calendarWeekOffset * 7));

    const days = [];
    for (let i = 0; i < 7; i++) {
        const d = new Date(startOfWeek);
        d.setDate(startOfWeek.getDate() + i);
        days.push(d);
    }

    const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    const hours = Array.from({length: 12}, (_, i) => i + 8); // 8 AM to 7 PM

    const monthYear = days[3].toLocaleDateString('en-US', { month: 'long', year: 'numeric' });

    // Group events by day
    const eventsByDay = {};
    days.forEach((d, i) => {
        const dateStr = d.toISOString().split('T')[0];
        eventsByDay[i] = state.events.filter(e => {
            const eventDate = new Date(e.start_dt).toISOString().split('T')[0];
            return eventDate === dateStr;
        });
    });

    const allDayEvents = {};
    days.forEach((d, i) => {
        allDayEvents[i] = eventsByDay[i].filter(e => e.all_day);
    });

    container.innerHTML = `
        <div class="calendar-container">
            <div class="calendar-header">
                <div class="calendar-nav">
                    <button class="calendar-nav-btn" onclick="navigateCalendar(-1)">‹</button>
                    <span class="calendar-current-date">${monthYear}</span>
                    <button class="calendar-nav-btn" onclick="navigateCalendar(1)">›</button>
                    <button class="calendar-today-btn" onclick="goToToday()">Today</button>
                </div>
                <div class="calendar-view-toggle">
                    <button class="view-toggle-btn ${state.calendarView === 'week' ? 'active' : ''}" onclick="setCalendarView('week')">Week</button>
                    <button class="view-toggle-btn ${state.calendarView === 'list' ? 'active' : ''}" onclick="setCalendarView('list')">List</button>
                </div>
            </div>

            <!-- All Day Events Row -->
            <div class="calendar-allday-row">
                <div class="calendar-allday-label">All Day</div>
                ${days.map((d, i) => `
                    <div class="calendar-allday-cell">
                        ${allDayEvents[i].map(e => `
                            <div class="calendar-allday-event" onclick="openCalendarEvent('${e.id}')">${e.summary}</div>
                        `).join('')}
                    </div>
                `).join('')}
            </div>

            <!-- Week Grid -->
            <div class="calendar-week-grid">
                <!-- Day Headers -->
                <div class="calendar-time-header"></div>
                ${days.map((d, i) => {
                    const isToday = d.toDateString() === now.toDateString();
                    return `
                        <div class="calendar-day-header ${isToday ? 'today' : ''}">
                            <div class="calendar-day-name">${dayNames[d.getDay()]}</div>
                            <div class="calendar-day-number">${d.getDate()}</div>
                        </div>
                    `;
                }).join('')}

                <!-- Time Grid -->
                ${hours.map(hour => `
                    <div class="calendar-time-slot">${hour % 12 || 12}${hour < 12 ? 'am' : 'pm'}</div>
                    ${days.map((d, dayIdx) => {
                        const dayEvents = eventsByDay[dayIdx].filter(e => {
                            if (e.all_day) return false;
                            const eventHour = new Date(e.start_dt).getHours();
                            return eventHour === hour;
                        });
                        const isToday = d.toDateString() === now.toDateString();
                        const isNowHour = isToday && now.getHours() === hour;

                        return `
                            <div class="calendar-day-column ${isToday ? 'today' : ''}">
                                <div class="calendar-hour-cell">
                                    ${isNowHour ? `<div class="calendar-now-line" style="top: ${(now.getMinutes() / 60) * 100}%"></div>` : ''}
                                    ${dayEvents.map(e => {
                                        const start = new Date(e.start_dt);
                                        const end = new Date(e.end_dt);
                                        const durationMins = (end - start) / 60000;
                                        const heightPx = Math.max(30, (durationMins / 60) * 60);
                                        const topOffset = (start.getMinutes() / 60) * 60;
                                        const isNow = e.is_now;
                                        const hasMeet = e.hangout_link;

                                        return `
                                            <div class="calendar-event-block ${isNow ? 'now' : ''} ${hasMeet ? 'meeting' : ''}"
                                                 style="top: ${topOffset}px; height: ${heightPx}px;"
                                                 onclick="openCalendarEvent('${e.id}')">
                                                <div class="calendar-event-title">${e.summary}</div>
                                                <div class="calendar-event-time">${formatTime(e.start_dt)}</div>
                                                ${e.location ? `<div class="calendar-event-location">📍 ${e.location}</div>` : ''}
                                            </div>
                                        `;
                                    }).join('')}
                                </div>
                            </div>
                        `;
                    }).join('')}
                `).join('')}
            </div>
        </div>
    `;
}

function renderCalendarListView(container, filter) {
    let events = state.events;
    const now = new Date();

    switch(filter) {
        case 'today':
            events = events.filter(e => e.is_today);
            break;
        case 'week':
            const weekFromNow = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000);
            events = events.filter(e => new Date(e.start_dt) <= weekFromNow);
            break;
    }

    if (events.length === 0) {
        container.innerHTML = '<div class="empty-state"><div class="icon">📅</div>No events</div>';
        return;
    }

    // Group by date
    const grouped = {};
    events.forEach(e => {
        const dateKey = new Date(e.start_dt).toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' });
        if (!grouped[dateKey]) grouped[dateKey] = [];
        grouped[dateKey].push(e);
    });

    container.innerHTML = `
        <div class="calendar-container">
            <div class="calendar-header">
                <span class="calendar-current-date">Upcoming Events</span>
                <div class="calendar-view-toggle">
                    <button class="view-toggle-btn ${state.calendarView === 'week' ? 'active' : ''}" onclick="setCalendarView('week')">Week</button>
                    <button class="view-toggle-btn ${state.calendarView === 'list' ? 'active' : ''}" onclick="setCalendarView('list')">List</button>
                </div>
            </div>
            <div class="calendar-event-list">
                ${Object.entries(grouped).map(([date, events]) => `
                    <div class="calendar-date-group">
                        <div class="calendar-date-label ${events[0]?.is_today ? 'today' : ''}">${date}</div>
                        ${events.map(e => `
                            <div class="calendar-event ${e.is_now ? 'now' : ''}">
                                <div class="event-time">${e.all_day ? 'All day' : formatTime(e.start_dt) + ' - ' + formatTime(e.end_dt)}</div>
                                <div class="event-title">${e.summary}</div>
                                <div class="event-meta">
                                    ${e.location ? `<span>📍 ${e.location}</span>` : ''}
                                    ${e.attendees?.length ? `<span>👥 ${e.attendees.length} attendees</span>` : ''}
                                    ${e.hangout_link ? `<a href="${e.hangout_link}" target="_blank" onclick="event.stopPropagation()">Join Meet</a>` : ''}
                                    ${e.html_link ? `<a href="${e.html_link}" target="_blank" onclick="event.stopPropagation()">Open</a>` : ''}
                                </div>
                            </div>
                        `).join('')}
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

function navigateCalendar(direction) {
    state.calendarWeekOffset += direction;
    renderCalendar();
}

function goToToday() {
    state.calendarWeekOffset = 0;
    renderCalendar();
}

function setCalendarView(view) {
    state.calendarView = view;
    renderCalendar();
}

function openCalendarEvent(eventId) {
    const event = state.events.find(e => e.id === eventId);
    if (!event) return;

    document.getElementById('modal-title').textContent = event.summary;
    document.getElementById('modal-body').innerHTML = `
        <div style="margin-bottom: 16px;">
            <div style="font-size: 16px; color: var(--text-secondary); margin-bottom: 12px;">
                <span style="color: var(--accent-blue);">📅</span>
                ${formatDate(event.start_dt)} • ${event.all_day ? 'All day' : formatTime(event.start_dt) + ' - ' + formatTime(event.end_dt)}
            </div>
            ${event.location ? `<div style="margin-bottom: 8px;"><span style="color: var(--accent-cyan);">📍</span> ${event.location}</div>` : ''}
            ${event.attendees?.length ? `<div style="margin-bottom: 8px;"><span style="color: var(--accent-purple);">👥</span> ${event.attendees.length} attendees</div>` : ''}
        </div>
        ${event.description ? `<div style="padding: 16px; background: var(--bg-surface); border-radius: 8px; margin-bottom: 16px; white-space: pre-wrap;">${event.description}</div>` : ''}
        <div style="display: flex; gap: 12px;">
            ${event.hangout_link ? `<a href="${event.hangout_link}" target="_blank" class="btn btn-primary">Join Google Meet</a>` : ''}
            ${event.html_link ? `<a href="${event.html_link}" target="_blank" class="btn">Open in Calendar</a>` : ''}
        </div>
    `;
    document.getElementById('modal-overlay').classList.add('active');
}

// ============================================
// TWITTER FEED LAYOUT
// ============================================

async function renderTwitter(filter = 'mentions') {
    const container = document.getElementById('twitter-content');

    // Get profile data
    const account = state.twitterAccount;
    const profileData = await api(`/integrations/twitter/${account}`);
    const profile = safeObj(safeObj(profileData).data);

    if (filter === 'mentions') {
        if (state.mentions.length === 0) {
            container.innerHTML = `
                <div class="twitter-layout">
                    ${renderTwitterSidebar(profile)}
                    <div class="twitter-feed">
                        <div class="twitter-feed-header">Mentions</div>
                        <div class="empty-state"><div class="icon">🐦</div>No mentions</div>
                    </div>
                    ${renderTwitterTrends()}
                </div>
            `;
            return;
        }

        container.innerHTML = `
            <div class="twitter-layout">
                ${renderTwitterSidebar(profile)}
                <div class="twitter-feed">
                    <div class="twitter-feed-header">Mentions</div>
                    ${state.mentions.map(m => renderTweetCard(m, state.mentionUsers)).join('')}
                </div>
                ${renderTwitterTrends()}
            </div>
        `;
    } else if (filter === 'tweets') {
        const endpoint = account === 'cortana' ? '/integrations/twitter/cortana/tweets' : '/integrations/twitter/ben/tweets';
        const data = await api(endpoint + '?limit=20');
        const tweets = safeArray(safeObj(data).tweets);

        container.innerHTML = `
            <div class="twitter-layout">
                ${renderTwitterSidebar(profile)}
                <div class="twitter-feed">
                    <div class="twitter-feed-header">Your Tweets</div>
                    ${tweets.length === 0 ?
                        '<div class="empty-state">No tweets</div>' :
                        tweets.map(t => renderTweetCard(t, [], true)).join('')
                    }
                </div>
                ${renderTwitterTrends()}
            </div>
        `;
    } else if (filter === 'followers') {
        const endpoint = account === 'cortana' ? '/integrations/twitter/cortana/followers' : '/integrations/twitter/ben/followers';
        const data = await api(endpoint + '?limit=20');
        const followers = safeArray(safeObj(data).data);

        container.innerHTML = `
            <div class="twitter-layout">
                ${renderTwitterSidebar(profile)}
                <div class="twitter-feed">
                    <div class="twitter-feed-header">Followers</div>
                    ${followers.length === 0 ?
                        '<div class="empty-state">No followers data</div>' :
                        `<div class="twitter-suggestions" style="border:none; margin:0;">
                            ${followers.map(f => `
                                <div class="suggestion-item" onclick="window.open('https://twitter.com/${f.username}', '_blank')">
                                    <img class="suggestion-avatar" src="${f.profile_image_url || ''}" onerror="this.style.background='var(--bg-hover)'">
                                    <div class="suggestion-info">
                                        <div class="suggestion-name">${f.name}</div>
                                        <div class="suggestion-handle">@${f.username} • ${(f.public_metrics?.followers_count || 0).toLocaleString()} followers</div>
                                    </div>
                                    <button class="follow-btn" onclick="event.stopPropagation(); followUser('${f.id}')">Follow</button>
                                </div>
                            `).join('')}
                        </div>`
                    }
                </div>
                ${renderTwitterTrends()}
            </div>
        `;
    } else if (filter === 'replyGuy') {
        container.innerHTML = `
            <div class="twitter-layout">
                ${renderTwitterSidebar(profile)}
                <div class="twitter-feed">
                    <div class="twitter-feed-header">🎯 Reply Guy Mode</div>
                    <div style="padding: 16px;">
                        <p style="color: var(--text-secondary); margin-bottom: 16px;">Find tweets from target accounts to engage with. Build relationships through thoughtful replies.</p>
                        <div style="display: flex; gap: 8px; margin-bottom: 20px;">
                            <input type="text" id="search-query" placeholder="Search tweets..."
                                   style="flex:1; padding: 12px 16px; background: var(--bg-surface); border: 1px solid var(--border-dim); border-radius: 9999px; color: var(--text-primary); font-size: 15px;"
                                   onkeypress="if(event.key==='Enter') searchTwitter()">
                            <button class="btn btn-primary" style="border-radius: 9999px;" onclick="searchTwitter()">Search</button>
                        </div>
                        <div id="search-results"></div>
                    </div>
                </div>
                ${renderTwitterTrends()}
            </div>
        `;
    }
}

function renderTwitterSidebar(profile) {
    const metrics = profile.public_metrics || {};
    return `
        <div class="twitter-sidebar-left">
            <div class="twitter-profile-card">
                <div class="twitter-profile-banner"></div>
                <div class="twitter-profile-content">
                    <img class="twitter-profile-avatar" src="${profile.profile_image_url || ''}" onerror="this.style.background='var(--bg-hover)'">
                    <div class="twitter-profile-name">${profile.name || 'Unknown'}</div>
                    <div class="twitter-profile-handle">@${profile.username || 'unknown'}</div>
                    <div class="twitter-profile-stats">
                        <div class="twitter-stat">
                            <span class="twitter-stat-value">${(metrics.following_count || 0).toLocaleString()}</span>
                            <span class="twitter-stat-label"> Following</span>
                        </div>
                        <div class="twitter-stat">
                            <span class="twitter-stat-value">${(metrics.followers_count || 0).toLocaleString()}</span>
                            <span class="twitter-stat-label"> Followers</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function renderTwitterTrends() {
    return `
        <div class="twitter-sidebar-right">
            <div class="twitter-trends">
                <div class="twitter-trends-header">Trends for you</div>
                <div class="trend-item">
                    <div class="trend-category">Technology · Trending</div>
                    <div class="trend-name">AI Agents</div>
                    <div class="trend-count">45.2K posts</div>
                </div>
                <div class="trend-item">
                    <div class="trend-category">Crypto · Trending</div>
                    <div class="trend-name">Ethereum</div>
                    <div class="trend-count">128K posts</div>
                </div>
                <div class="trend-item">
                    <div class="trend-category">Business · Trending</div>
                    <div class="trend-name">Startups</div>
                    <div class="trend-count">23.1K posts</div>
                </div>
            </div>
        </div>
    `;
}

function renderTweetCard(tweet, users = [], isOwnTweet = false) {
    const author = users.find(u => u.id === tweet.author_id) || {};
    const metrics = tweet.public_metrics || {};
    const authorImg = isOwnTweet ? '' : (author.profile_image_url || '');
    const authorName = isOwnTweet ? 'You' : (author.name || 'Unknown');
    const authorHandle = isOwnTweet ? state.twitterAccount === 'cortana' ? '0xBenJammin' : 'xBenJamminx' : (author.username || 'unknown');

    // Convert URLs to links
    let text = tweet.text || '';
    text = text.replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank">$1</a>');
    text = text.replace(/@(\w+)/g, '<a href="https://twitter.com/$1" target="_blank">@$1</a>');

    return `
        <div class="tweet-card">
            <div class="tweet-main">
                <img class="tweet-avatar-lg" src="${authorImg}" onerror="this.style.background='linear-gradient(135deg, var(--accent-purple), var(--accent-cyan))'">
                <div class="tweet-body">
                    <div class="tweet-header-row">
                        <span class="tweet-display-name">${authorName}</span>
                        ${author.verified ? '<span class="tweet-verified">✓</span>' : ''}
                        <span class="tweet-username">@${authorHandle}</span>
                        <span class="tweet-dot">·</span>
                        <span class="tweet-timestamp">${formatRelativeTime(tweet.created_at)}</span>
                    </div>
                    <div class="tweet-text">${text}</div>
                    <div class="tweet-actions-bar">
                        <button class="tweet-action-btn reply" onclick="openTweetReply('${tweet.id}', \`${(tweet.text || '').replace(/`/g, "'")}\`, ${JSON.stringify(author).replace(/"/g, '&quot;')})">
                            <span class="icon">💬</span>
                            <span>${metrics.reply_count || 0}</span>
                        </button>
                        <button class="tweet-action-btn retweet" onclick="retweetTweet('${tweet.id}')">
                            <span class="icon">🔄</span>
                            <span>${metrics.retweet_count || 0}</span>
                        </button>
                        <button class="tweet-action-btn like" onclick="likeTweet('${tweet.id}')">
                            <span class="icon">❤️</span>
                            <span>${metrics.like_count || 0}</span>
                        </button>
                        <button class="tweet-action-btn views">
                            <span class="icon">👁️</span>
                            <span>${(metrics.impression_count || 0).toLocaleString()}</span>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// ============================================
// DRIVE FILE GRID
// ============================================

async function renderDrive(filter = 'recent') {
    const container = document.getElementById('drive-content');

    if (filter === 'shared') {
        const data = await api('/google/drive/shared?limit=30');
        state.driveFiles = safeArray(safeObj(data).files);
    } else if (filter === 'starred') {
        const data = await api('/google/drive/starred');
        state.driveFiles = safeArray(safeObj(data).files);
    }

    if (state.driveFiles.length === 0) {
        container.innerHTML = '<div class="empty-state"><div class="icon">📁</div>No files</div>';
        return;
    }

    // Group by type
    const folders = state.driveFiles.filter(f => f.mimeType?.includes('folder'));
    const docs = state.driveFiles.filter(f => f.mimeType?.includes('document'));
    const sheets = state.driveFiles.filter(f => f.mimeType?.includes('spreadsheet'));
    const slides = state.driveFiles.filter(f => f.mimeType?.includes('presentation'));
    const others = state.driveFiles.filter(f =>
        !f.mimeType?.includes('folder') &&
        !f.mimeType?.includes('document') &&
        !f.mimeType?.includes('spreadsheet') &&
        !f.mimeType?.includes('presentation')
    );

    const renderSection = (title, icon, files, iconClass) => {
        if (files.length === 0) return '';
        return `
            <div style="margin-bottom: 24px;">
                <h3 style="font-size: 14px; color: var(--text-muted); margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
                    ${icon} ${title} <span style="font-weight: normal;">(${files.length})</span>
                </h3>
                <div class="grid-4">
                    ${files.map(f => `
                        <div class="drive-file" onclick="window.open('${f.webViewLink}', '_blank')">
                            <div class="drive-icon ${iconClass}">${icon}</div>
                            <div class="drive-info">
                                <div class="drive-name">${f.name}</div>
                                <div class="drive-meta">${formatRelativeTime(f.modifiedTime)}${f.shared ? ' • Shared' : ''}</div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    };

    container.innerHTML = `
        ${renderSection('Folders', '📁', folders, 'folder')}
        ${renderSection('Documents', '📄', docs, 'doc')}
        ${renderSection('Spreadsheets', '📊', sheets, 'sheet')}
        ${renderSection('Presentations', '📽️', slides, 'slide')}
        ${renderSection('Other Files', '📎', others, 'doc')}
    `;
}

console.log('Views upgrade loaded successfully');
