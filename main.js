const { app, BrowserWindow, ipcMain, shell } = require('electron');
const { execFile } = require('child_process');
const path = require('path');
const fs = require('fs');

const gotLock = app.requestSingleInstanceLock();
if (!gotLock) {
  app.quit();
} else {
  app.on('second-instance', () => {
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore();
      mainWindow.focus();
    }
  });
}

let mainWindow = null;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 800,
    height: 900,
    minWidth: 460,
    minHeight: 560,
    backgroundColor: '#08090b',
    icon: path.join(__dirname, 'build/icon.ico'),
    autoHideMenuBar: true,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  mainWindow.loadFile(path.join(__dirname, 'app/index.html'));

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    mainWindow.setAlwaysOnTop(true);
    mainWindow.focus();
    setTimeout(() => {
      if (mainWindow && !mainWindow.isDestroyed()) mainWindow.setAlwaysOnTop(false);
    }, 250);
  });
}

app.whenReady().then(() => {
  if (gotLock) createWindow();
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow();
});

function runApplyResolutionScript(width, height) {
  return new Promise((resolve) => {
    const scriptPath = path
      .join(__dirname, 'native', 'apply-resolution.ps1')
      .replace(`${path.sep}app.asar${path.sep}`, `${path.sep}app.asar.unpacked${path.sep}`);
    execFile(
      'powershell.exe',
      [
        '-NoProfile',
        '-NonInteractive',
        '-ExecutionPolicy', 'Bypass',
        '-File', scriptPath,
        '-Width', String(width),
        '-Height', String(height),
      ],
      { windowsHide: true, timeout: 10000 },
      (error, stdout, stderr) => {
        if (error) {
          resolve({ ok: false, code: null, raw: stderr || String(error) });
          return;
        }
        const code = parseInt(String(stdout).trim(), 10);
        resolve({ ok: Number.isInteger(code), code, raw: stdout });
      }
    );
  });
}

ipcMain.handle('apply-resolution', async (_event, width, height) => {
  width = Math.trunc(Number(width));
  height = Math.trunc(Number(height));

  if (!Number.isFinite(width) || !Number.isFinite(height) || width < 100 || height < 100) {
    return { ok: false, message: 'ERROR! That resolution is too small to be valid.' };
  }

  const result = await runApplyResolutionScript(width, height);

  if (result.ok && result.code === 0) {
    return { ok: true, message: `Now running ${width} x ${height}` };
  }

  return {
    ok: false,
    message:
      "ERROR! Try running as Administrator, or that resolution isn't " +
      'registered with your GPU driver yet.',
  };
});

function profilesFilePath() {
  const folder = path.join(app.getPath('appData'), 'SnapRes');
  try {
    fs.mkdirSync(folder, { recursive: true });
  } catch (_) {
  }
  return path.join(folder, 'profiles.json');
}

ipcMain.handle('get-profiles', async () => {
  try {
    const raw = fs.readFileSync(profilesFilePath(), 'utf-8');
    const data = JSON.parse(raw);
    if (!Array.isArray(data)) return [];
    return data
      .filter((item) => item && Number.isFinite(item.width) && Number.isFinite(item.height))
      .map((item) => ({
        label: `${item.width}x${item.height}`,
        width: item.width,
        height: item.height,
      }));
  } catch (_) {
    return [];
  }
});

ipcMain.handle('save-profiles', async (_event, profiles) => {
  try {
    const cleaned = (Array.isArray(profiles) ? profiles : [])
      .filter((p) => p && Number.isFinite(p.width) && Number.isFinite(p.height))
      .map((p) => ({ width: p.width, height: p.height }));
    fs.writeFileSync(profilesFilePath(), JSON.stringify(cleaned));
    return true;
  } catch (_) {
    return false;
  }
});

ipcMain.handle('open-external', async (_event, url) => {
  try {
    if (typeof url === 'string' && /^https?:\/\/|^mailto:/i.test(url)) {
      await shell.openExternal(url);
      return true;
    }
    return false;
  } catch (_) {
    return false;
  }
});

function nativeScriptPath(name) {
  return path
    .join(__dirname, 'native', name)
    .replace(`${path.sep}app.asar${path.sep}`, `${path.sep}app.asar.unpacked${path.sep}`);
}

function runPowerShellScript(scriptName, args, timeout) {
  return new Promise((resolve) => {
    execFile(
      'powershell.exe',
      [
        '-NoProfile',
        '-NonInteractive',
        '-ExecutionPolicy', 'Bypass',
        '-File', nativeScriptPath(scriptName),
        ...args,
      ],
      { windowsHide: true, timeout },
      (error, stdout) => {
        if (error) {
          resolve('error');
          return;
        }
        const result = String(stdout).trim().split('\n').pop().trim();
        resolve(result || 'error');
      }
    );
  });
}

ipcMain.handle('check-driver-status', async () => {
  const result = await runPowerShellScript('check-driver-status.ps1', [], 8000);
  return ['enabled', 'disabled', 'not_found'].includes(result) ? result : 'not_found';
});

async function toggleDriver(action) {
  const result = await runPowerShellScript(
    'set-driver-status.ps1',
    ['-Action', action],
    120000
  );
  return ['enabled', 'disabled', 'not_found', 'denied', 'error'].includes(result)
    ? result
    : 'error';
}

ipcMain.handle('disable-driver', async () => toggleDriver('Disable'));
ipcMain.handle('enable-driver', async () => toggleDriver('Enable'));
