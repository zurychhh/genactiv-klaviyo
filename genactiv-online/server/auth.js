import bcrypt from 'bcryptjs';
import session from 'express-session';

export function setupAuth(app) {
  app.use(session({
    secret: process.env.SESSION_SECRET || 'dev-secret-change-in-production',
    resave: false,
    saveUninitialized: false,
    cookie: {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict',
      maxAge: 24 * 60 * 60 * 1000 // 24 hours
    }
  }));

  // Login page
  app.get('/login', (req, res) => {
    if (req.session.authenticated) {
      return res.redirect('/');
    }
    res.send(loginPage());
  });

  // Login handler
  app.post('/login', async (req, res) => {
    const { username, password } = req.body;

    const validUsername = process.env.AUTH_USERNAME || 'admin';
    const passwordHash = process.env.AUTH_PASSWORD_HASH;

    if (!passwordHash) {
      console.error('[Auth] AUTH_PASSWORD_HASH not set');
      return res.status(500).send(loginPage('Błąd konfiguracji serwera'));
    }

    if (username !== validUsername) {
      return res.status(401).send(loginPage('Nieprawidłowe dane logowania'));
    }

    const valid = await bcrypt.compare(password, passwordHash);
    if (!valid) {
      return res.status(401).send(loginPage('Nieprawidłowe dane logowania'));
    }

    req.session.authenticated = true;
    req.session.username = username;
    res.redirect('/');
  });

  // Logout handler
  app.post('/logout', (req, res) => {
    req.session.destroy(() => {
      res.redirect('/login');
    });
  });
}

export function requireAuth(req, res, next) {
  if (req.session && req.session.authenticated) {
    return next();
  }
  res.redirect('/login');
}

function loginPage(error = '') {
  return `<!DOCTYPE html>
<html lang="pl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>GenActiv Online — Logowanie</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      background: #0a0a0a;
      color: #e0e0e0;
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
    }
    .login-box {
      background: #1a1a1a;
      border: 1px solid #333;
      border-radius: 8px;
      padding: 2rem;
      width: 100%;
      max-width: 360px;
    }
    h1 {
      color: #0066CC;
      font-size: 1.2rem;
      margin-bottom: 1.5rem;
      text-align: center;
    }
    label {
      display: block;
      font-size: 0.85rem;
      color: #999;
      margin-bottom: 0.3rem;
    }
    input {
      width: 100%;
      padding: 0.6rem;
      margin-bottom: 1rem;
      background: #0a0a0a;
      border: 1px solid #444;
      border-radius: 4px;
      color: #e0e0e0;
      font-size: 0.95rem;
    }
    input:focus { outline: none; border-color: #0066CC; }
    button {
      width: 100%;
      padding: 0.7rem;
      background: #0066CC;
      color: white;
      border: none;
      border-radius: 4px;
      font-size: 1rem;
      cursor: pointer;
    }
    button:hover { background: #0055aa; }
    .error {
      color: #EF3340;
      font-size: 0.85rem;
      margin-bottom: 1rem;
      text-align: center;
    }
  </style>
</head>
<body>
  <form class="login-box" method="POST" action="/login">
    <h1>GenActiv Online</h1>
    ${error ? `<div class="error">${error}</div>` : ''}
    <label for="username">Login</label>
    <input type="text" id="username" name="username" required autofocus>
    <label for="password">Hasło</label>
    <input type="password" id="password" name="password" required>
    <button type="submit">Zaloguj się</button>
  </form>
</body>
</html>`;
}
