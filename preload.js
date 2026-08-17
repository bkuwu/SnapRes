const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('snapres', {
  applyResolution: (w, h) => ipcRenderer.invoke('apply-resolution', w, h),
  getProfiles: () => ipcRenderer.invoke('get-profiles'),
  saveProfiles: (profiles) => ipcRenderer.invoke('save-profiles', profiles),
  checkDriverStatus: () => ipcRenderer.invoke('check-driver-status'),
  disableDriver: () => ipcRenderer.invoke('disable-driver'),
  enableDriver: () => ipcRenderer.invoke('enable-driver'),
  openExternal: (url) => ipcRenderer.invoke('open-external', url),
});
