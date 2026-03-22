const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const Database = require('better-sqlite3');

const DB_PATH = path.join(__dirname, '..', '..', 'data', 'rustic-manager.db');

let db = null;

function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false
    }
  });

  if (process.env.NODE_ENV === 'development') {
    win.loadURL('http://localhost:5173');
    win.webContents.openDevTools();
  } else {
    win.loadFile(path.join(__dirname, '..', 'dist', 'index.html'));
  }
}

function initDatabase() {
  db = new Database(DB_PATH);
  db.pragma('journal_mode = WAL');
}

app.whenReady().then(() => {
  initDatabase();
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (db) {
    db.close();
  }
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

ipcMain.handle('get-paths', () => {
  const stmt = db.prepare('SELECT * FROM paths');
  return stmt.all();
});

ipcMain.handle('get-disk-usage', (event, tableName, limit) => {
  const stmt = db.prepare(`SELECT used_bytes, timestamp FROM ${tableName} ORDER BY timestamp DESC LIMIT ?`);
  return stmt.all(limit);
});

ipcMain.handle('get-backup-history', (event, tableName, limit) => {
  const stmt = db.prepare(`SELECT snapshot_id, duration_seconds, space_change_bytes, timestamp FROM ${tableName} ORDER BY timestamp DESC LIMIT ?`);
  return stmt.all(limit);
});
