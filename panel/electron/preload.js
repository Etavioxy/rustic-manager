const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('api', {
  getPaths: () => ipcRenderer.invoke('get-paths'),
  getDiskUsage: (tableName, limit) => ipcRenderer.invoke('get-disk-usage', tableName, limit),
  getBackupHistory: (tableName, limit) => ipcRenderer.invoke('get-backup-history', tableName, limit)
});
