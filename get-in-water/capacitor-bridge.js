/**
 * capacitor-bridge.js — Get In Water
 * Intercepts blob downloads from exportTXT / exportPDF on Android.
 */
(function () {
  if (!window.Capacitor || !window.Capacitor.isNativePlatform()) return;

  const FS = 'Filesystem';
  const SH = 'Share';

  function blobToBase64(blob) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onloadend = () => resolve(reader.result.split(',')[1]);
      reader.onerror = reject;
      reader.readAsDataURL(blob);
    });
  }

  function notify(msg, isError) {
    if (typeof window.showExportToast === 'function') {
      window.showExportToast(msg);
      return;
    }
    const div = document.createElement('div');
    div.textContent = msg;
    div.style.cssText = [
      'position:fixed','bottom:24px','left:50%','transform:translateX(-50%)',
      'background:' + (isError ? 'rgba(220,50,50,0.95)' : 'rgba(0,200,255,0.92)'),
      'color:' + (isError ? '#fff' : '#000'),
      'padding:10px 22px','border-radius:20px','font-size:13px','z-index:99999',
      'pointer-events:none','max-width:85vw','text-align:center','font-family:sans-serif'
    ].join(';');
    document.body.appendChild(div);
    setTimeout(() => div.remove(), isError ? 5000 : 3500);
  }

  async function ensurePermission() {
    const plugin = Capacitor.Plugins[FS];
    if (!plugin || typeof plugin.requestPermissions !== 'function') return true;
    try {
      const result = await plugin.requestPermissions();
      return result?.publicStorage !== 'denied';
    } catch (e) { return true; }
  }

  async function tryWrite(base64Data, filename, directory, path) {
    try {
      const result = await Capacitor.Plugins[FS].writeFile({
        path: path || filename, data: base64Data, directory, recursive: true
      });
      return { uri: result.uri, dir: directory };
    } catch (err) { return null; }
  }

  async function fileExists(path, directory) {
    try { await Capacitor.Plugins[FS].stat({ path, directory }); return true; }
    catch (e) { return false; }
  }

  async function uniqueFilename(filename, directory, dirPath) {
    const dot = filename.lastIndexOf('.');
    const base = dot > -1 ? filename.slice(0, dot) : filename;
    const ext = dot > -1 ? filename.slice(dot) : '';
    const checkPath = p => fileExists(dirPath ? dirPath + p : p, directory);
    if (!(await checkPath(filename))) return filename;
    for (let i = 1; i <= 999; i++) {
      const candidate = `${base} (${i})${ext}`;
      if (!(await checkPath(candidate))) return candidate;
    }
    return filename;
  }

  async function saveFile(base64Data, filename) {
    const dlName = await uniqueFilename(filename, 'EXTERNAL_STORAGE', 'Download/');
    let saved = await tryWrite(base64Data, dlName, 'EXTERNAL_STORAGE', 'Download/' + dlName);
    if (saved) return { ...saved, label: 'Downloads folder', finalName: dlName };
    const extName = await uniqueFilename(filename, 'EXTERNAL', '');
    saved = await tryWrite(base64Data, extName, 'EXTERNAL', extName);
    if (saved) return { ...saved, label: 'app files', finalName: extName };
    const cacheName = await uniqueFilename(filename, 'CACHE', '');
    saved = await tryWrite(base64Data, cacheName, 'CACHE', cacheName);
    if (saved) return { ...saved, label: 'app cache', finalName: cacheName };
    return null;
  }

  async function shareFile(fileUri, filename) {
    const plugin = Capacitor.Plugins[SH];
    if (!plugin?.share) return;
    try {
      await plugin.share({ title: filename, url: fileUri, dialogTitle: 'Open or share ' + filename });
    } catch (err) {
      const msg = (err?.message || '').toLowerCase();
      if (!msg.includes('cancel') && !msg.includes('dismiss')) notify('Share error: ' + msg, true);
    }
  }

  async function handleBlobDownload(blob, filename) {
    let base64Data;
    try { base64Data = await blobToBase64(blob); }
    catch (err) { notify('Export failed: ' + err, true); return; }
    if (!(await ensurePermission())) return;
    const saved = await saveFile(base64Data, filename);
    if (!saved) { notify('Export failed — could not write to device', true); return; }
    const where = saved.label === 'Downloads folder'
      ? 'Downloads folder'
      : 'app storage — use Share to copy elsewhere';
    notify('✓ Saved to ' + where + ': ' + (saved.finalName || filename));
    await shareFile(saved.uri, filename);
  }

  const _origClick = HTMLAnchorElement.prototype.click;
  HTMLAnchorElement.prototype.click = function () {
    if (this.download && this.href?.startsWith('blob:')) {
      const href = this.href, dl = this.download;
      fetch(href).then(r => r.blob()).then(b => handleBlobDownload(b, dl))
        .catch(err => { notify('Export error: ' + err, true); _origClick.call(this); });
      return;
    }
    _origClick.call(this);
  };

  const _origDispatch = HTMLAnchorElement.prototype.dispatchEvent;
  HTMLAnchorElement.prototype.dispatchEvent = function (event) {
    if (event instanceof MouseEvent && event.type === 'click' &&
        this.download && this.href?.startsWith('blob:')) {
      const href = this.href, dl = this.download;
      fetch(href).then(r => r.blob()).then(b => handleBlobDownload(b, dl))
        .catch(err => { notify('Export error: ' + err, true); _origDispatch.call(this, event); });
      return true;
    }
    return _origDispatch.call(this, event);
  };
})();
