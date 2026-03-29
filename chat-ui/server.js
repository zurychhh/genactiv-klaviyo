const express = require('express');
const { WebSocketServer } = require('ws');
const { spawn } = require('child_process');
const http = require('http');
const path = require('path');
const fs = require('fs');

const app = express();
const server = http.createServer(app);
const wss = new WebSocketServer({ server });

// Serve static files
app.use(express.static(path.join(__dirname, 'public')));
app.use(express.json());

// Bookmarks storage
const BOOKMARKS_FILE = path.join(__dirname, 'bookmarks.json');

function loadBookmarks() {
    try {
        if (fs.existsSync(BOOKMARKS_FILE)) {
            return JSON.parse(fs.readFileSync(BOOKMARKS_FILE, 'utf8'));
        }
    } catch (e) {
        console.error('Error loading bookmarks:', e);
    }
    return [];
}

function saveBookmarks(bookmarks) {
    fs.writeFileSync(BOOKMARKS_FILE, JSON.stringify(bookmarks, null, 2));
}

// REST API for bookmarks
app.get('/api/bookmarks', (req, res) => {
    res.json(loadBookmarks());
});

app.post('/api/bookmarks', (req, res) => {
    const bookmarks = loadBookmarks();
    const newBookmark = {
        id: Date.now(),
        query: req.body.query,
        response: req.body.response,
        title: req.body.title || req.body.query.substring(0, 50),
        createdAt: new Date().toISOString(),
        tags: req.body.tags || []
    };
    bookmarks.unshift(newBookmark);
    saveBookmarks(bookmarks);
    res.json(newBookmark);
});

app.delete('/api/bookmarks/:id', (req, res) => {
    let bookmarks = loadBookmarks();
    bookmarks = bookmarks.filter(b => b.id !== parseInt(req.params.id));
    saveBookmarks(bookmarks);
    res.json({ success: true });
});

// Helper function to safely send WebSocket message
function safeSend(ws, data) {
    if (ws.readyState === 1) {
        ws.send(JSON.stringify(data));
        return true;
    }
    return false;
}

// Execute claude command using spawn for better control
function runClaude(query) {
    return new Promise((resolve, reject) => {

        console.log('Running claude with query:', query.substring(0, 50) + '...');

        const proc = spawn('/opt/homebrew/bin/claude', ['-p', query], {
            cwd: '/Users/user/projects/genactiv-klaviyo',
            env: {
                ...process.env,
                PATH: '/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:' + process.env.PATH
            },
            stdio: ['ignore', 'pipe', 'pipe'] // ignore stdin, pipe stdout/stderr
        });

        let stdout = '';
        let stderr = '';

        proc.stdout.on('data', (data) => {
            stdout += data.toString();
        });

        proc.stderr.on('data', (data) => {
            stderr += data.toString();
        });

        proc.on('close', (code) => {
            console.log('Process closed with code:', code);
            if (code === 0 || stdout) {
                resolve(stdout);
            } else {
                reject(new Error(stderr || `Process exited with code ${code}`));
            }
        });

        proc.on('error', (err) => {
            console.error('Process error:', err);
            reject(err);
        });

        // Timeout after 5 minutes
        setTimeout(() => {
            proc.kill();
            reject(new Error('Timeout after 5 minutes'));
        }, 300000);
    });
}

// WebSocket connection
wss.on('connection', (ws) => {
    console.log('Client connected');

    ws.on('message', async (message) => {
        const data = JSON.parse(message);

        if (data.type === 'query') {
            const query = data.query;
            console.log('Query:', query);

            // Send start message
            safeSend(ws, { type: 'start' });

            try {
                const response = await runClaude(query);
                console.log('Response received, length:', response.length);

                safeSend(ws, {
                    type: 'done',
                    content: response
                });
            } catch (error) {
                console.error('Error:', error.message);
                safeSend(ws, {
                    type: 'error',
                    content: `Blad: ${error.message}`
                });
            }
        }
    });

    ws.on('close', () => {
        console.log('Client disconnected');
    });

    ws.on('error', (err) => {
        console.error('WebSocket error:', err);
    });
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
    console.log(`
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   GenActiv Chat UI                                        ║
║   ─────────────────                                       ║
║                                                           ║
║   Server running at: http://localhost:${PORT}               ║
║                                                           ║
║   Using Claude CLI (claude -p)                            ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    `);
});
