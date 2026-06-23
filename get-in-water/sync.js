/**
 * Get In Water — optional Firebase Auth + Firestore sync.
 * Exposes window.GIW_SYNC. Requires firebase compat scripts and firebase-config.js.
 */
(function (root) {
  'use strict';

  const CLIENT_ID_KEY = 'giw_client_id';
  const REMOTE_META_KEY = 'giw_sync_remote_meta';
  const DEBOUNCE_MS = 1500;
  const DOC_PATH = ['users', 'data', 'state'];

  let hooks = null;
  let auth = null;
  let db = null;
  let docRef = null;
  let unsubscribeSnapshot = null;
  let pushTimer = null;
  let pushInFlight = false;
  let applyingRemote = false;
  let initDone = false;

  const status = {
    configured: false,
    signedIn: false,
    syncing: false,
    offline: !root.navigator || !root.navigator.onLine,
    lastSyncAt: null,
    lastError: null,
    pendingPush: false,
    user: null
  };

  function configured() {
    const c = root.GIW_FIREBASE_CONFIG;
    return !!(c && c.apiKey && c.apiKey !== 'REPLACE_ME' && c.projectId && c.projectId !== 'REPLACE_ME');
  }

  function isNative() {
    return !!(hooks && hooks.isNative);
  }

  function getClientId() {
    let id = localStorage.getItem(CLIENT_ID_KEY);
    if (!id) {
      id = 'dev_' + Math.random().toString(36).slice(2, 11) + Date.now().toString(36);
      localStorage.setItem(CLIENT_ID_KEY, id);
    }
    return id;
  }

  function loadRemoteMeta() {
    try {
      const raw = localStorage.getItem(REMOTE_META_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch (e) {
      return null;
    }
  }

  function saveRemoteMeta(meta) {
    if (!meta) {
      localStorage.removeItem(REMOTE_META_KEY);
      return;
    }
    localStorage.setItem(REMOTE_META_KEY, JSON.stringify(meta));
  }

  function touchSyncMeta(state) {
    if (!state) return;
    if (!state.syncMeta) state.syncMeta = { updatedAt: '', revision: 0 };
    state.syncMeta.updatedAt = new Date().toISOString();
    if (!state.syncMeta.revision) state.syncMeta.revision = 0;
  }

  function bumpRevision(state) {
    touchSyncMeta(state);
    state.syncMeta.revision = (state.syncMeta.revision || 0) + 1;
  }

  function touchTripSync(trip) {
    if (!trip) return;
    trip.syncUpdatedAt = new Date().toISOString();
  }

  function stateHasUserData(state) {
    if (!state) return false;
    if (state.trips && state.trips.length > 0) return true;
    if (state.syncMeta && state.syncMeta.revision > 0) return true;
    return false;
  }

  function cloudHasUserData(payload, meta) {
    if (meta && meta.revision > 0) return true;
    if (payload && payload.trips && payload.trips.length > 0) return true;
    if (payload && payload.syncMeta && payload.syncMeta.revision > 0) return true;
    return false;
  }

  function stripSyncFields(state) {
    const copy = JSON.parse(JSON.stringify(state));
    delete copy.syncMeta;
    if (copy.trips) {
      copy.trips.forEach(t => delete t.syncUpdatedAt);
    }
    if (copy.masterTemplate) delete copy.masterTemplate.syncUpdatedAt;
    return copy;
  }

  function notifyStatus() {
    if (hooks && hooks.onStatusChange) hooks.onStatusChange(getStatus());
  }

  function setError(err) {
    status.lastError = err ? (err.message || String(err)) : null;
    notifyStatus();
  }

  function getFirebaseAuthPlugin() {
    const cap = root.Capacitor;
    if (!cap || !cap.Plugins) return null;
    return cap.Plugins.FirebaseAuthentication || null;
  }

  function initFirebase() {
    if (!configured() || !root.firebase) return false;
    if (auth && db) return true;
    try {
      if (!root.firebase.apps.length) {
        root.firebase.initializeApp(root.GIW_FIREBASE_CONFIG);
      }
      auth = root.firebase.auth();
      db = root.firebase.firestore();
      try {
        db.enablePersistence({ synchronizeTabs: false }).catch(() => {});
      } catch (e) {}
      status.configured = true;
      return true;
    } catch (e) {
      console.warn('[GIW_SYNC] Firebase init failed', e);
      setError(e);
      return false;
    }
  }

  function docRefForUser(uid) {
    return db.collection('users').doc(uid).collection('data').doc('state');
  }

  async function signInWithGoogle() {
    if (!initFirebase()) {
      throw new Error('Cloud sync is not configured yet');
    }
    status.syncing = true;
    notifyStatus();
    try {
      const plugin = isNative() ? getFirebaseAuthPlugin() : null;
      if (plugin && plugin.signInWithGoogle) {
        const result = await plugin.signInWithGoogle();
        const idToken = result && result.credential && result.credential.idToken;
        if (idToken) {
          const cred = root.firebase.auth.GoogleAuthProvider.credential(idToken);
          await auth.signInWithCredential(cred);
        } else if (!auth.currentUser) {
          throw new Error('Google sign-in did not return a credential');
        }
      } else {
        const provider = new root.firebase.auth.GoogleAuthProvider();
        try {
          await auth.signInWithPopup(provider);
        } catch (e) {
          if (e.code === 'auth/popup-blocked' || e.code === 'auth/operation-not-supported-in-this-environment') {
            await auth.signInWithRedirect(provider);
            return null;
          }
          throw e;
        }
      }
      return auth.currentUser;
    } finally {
      status.syncing = false;
      notifyStatus();
    }
  }

  async function signOut() {
    stopListener();
    if (getFirebaseAuthPlugin() && getFirebaseAuthPlugin().signOut) {
      try { await getFirebaseAuthPlugin().signOut(); } catch (e) {}
    }
    if (auth) {
      try { await auth.signOut(); } catch (e) {}
    }
    docRef = null;
    status.signedIn = false;
    status.user = null;
    notifyStatus();
  }

  function applyCloudPayload(payload, meta) {
    if (!hooks || !payload) return;
    applyingRemote = true;
    try {
      const data = JSON.parse(JSON.stringify(payload));
      if (meta) {
        data.syncMeta = {
          updatedAt: meta.updatedAt || new Date().toISOString(),
          revision: meta.revision || 0
        };
      }
      if (hooks.migrateState) hooks.migrateState(data);
      hooks.setState(data);
      hooks.persistLocal();
      if (meta) saveRemoteMeta(meta);
      status.lastSyncAt = new Date().toISOString();
      status.lastError = null;
      status.pendingPush = false;
      hooks.render();
    } finally {
      applyingRemote = false;
    }
    notifyStatus();
  }

  function mergeStates(local, remote) {
    const out = JSON.parse(JSON.stringify(local));
    const remoteTrips = remote.trips || [];
    const tripMap = {};
    (out.trips || []).forEach(t => { tripMap[t.id] = t; });

    remoteTrips.forEach(rt => {
      const existing = tripMap[rt.id];
      if (!existing) {
        out.trips.push(JSON.parse(JSON.stringify(rt)));
      } else {
        const lt = existing.syncUpdatedAt || out.syncMeta?.updatedAt || '';
        const rtTime = rt.syncUpdatedAt || remote.syncMeta?.updatedAt || '';
        if (rtTime > lt) {
          const idx = out.trips.findIndex(t => t.id === rt.id);
          if (idx >= 0) out.trips[idx] = JSON.parse(JSON.stringify(rt));
        }
      }
    });

    const localTplTime = (out.masterTemplate && out.masterTemplate.syncUpdatedAt) || out.syncMeta?.updatedAt || '';
    const remoteTplTime = (remote.masterTemplate && remote.masterTemplate.syncUpdatedAt) || remote.syncMeta?.updatedAt || '';
    if (remoteTplTime > localTplTime && remote.masterTemplate) {
      out.masterTemplate = JSON.parse(JSON.stringify(remote.masterTemplate));
    }

    const tplById = {};
    (out.savedTemplates || []).forEach(t => { tplById[t.id] = t; });
    (remote.savedTemplates || []).forEach(rt => {
      if (rt.builtIn) return;
      if (!tplById[rt.id]) {
        if (!out.savedTemplates) out.savedTemplates = [];
        out.savedTemplates.push(JSON.parse(JSON.stringify(rt)));
      }
    });

    const localSettingsTime = out.syncMeta?.updatedAt || '';
    const remoteSettingsTime = remote.syncMeta?.updatedAt || '';
    if (remote.settings && remoteSettingsTime > localSettingsTime) {
      out.settings = Object.assign({}, out.settings, remote.settings);
    }

    bumpRevision(out);
    return out;
  }

  function showConflictModal(cloudPayload, cloudMeta) {
    return new Promise(resolve => {
      const html = `
        <h3 style="margin:0 0 8px;font-family:'Bebas Neue',sans-serif;font-size:22px;letter-spacing:1px">Sync data on this device</h3>
        <p style="font-size:13px;color:var(--tip);line-height:1.55;margin:0 0 16px">
          This device and your cloud account both have checklist data. Choose how to combine them.
        </p>
        <div style="display:flex;flex-direction:column;gap:8px">
          <button class="btn-primary" id="giw-conflict-local">Keep this device</button>
          <button class="btn-secondary" id="giw-conflict-cloud">Use cloud</button>
          <button class="btn-secondary" id="giw-conflict-merge">Merge trips</button>
        </div>`;
      hooks.openModal(html, () => {
        document.getElementById('giw-conflict-local').onclick = () => {
          hooks.closeModal();
          resolve('local');
        };
        document.getElementById('giw-conflict-cloud').onclick = () => {
          hooks.closeModal();
          resolve('cloud');
        };
        document.getElementById('giw-conflict-merge').onclick = () => {
          hooks.closeModal();
          resolve('merge');
        };
      });
    });
  }

  async function resolveInitialSync(cloudPayload, cloudMeta) {
    const local = hooks.getState();
    const localHas = stateHasUserData(local);
    const cloudHas = cloudHasUserData(cloudPayload, cloudMeta);

    if (!cloudHas) {
      await pushNow();
      return;
    }
    if (!localHas) {
      applyCloudPayload(cloudPayload, cloudMeta);
      return;
    }

    const choice = await showConflictModal(cloudPayload, cloudMeta);
    if (choice === 'cloud') {
      applyCloudPayload(cloudPayload, cloudMeta);
    } else if (choice === 'merge') {
      const merged = mergeStates(local, cloudPayload);
      if (hooks.migrateState) hooks.migrateState(merged);
      hooks.setState(merged);
      hooks.persistLocal();
      await pushNow();
    } else {
      await pushNow();
    }
  }

  async function fetchCloudDoc() {
    if (!docRef) return null;
    const snap = await docRef.get();
    if (!snap.exists) return null;
    const data = snap.data();
    return {
      payload: data.payload,
      meta: {
        revision: data.revision || 0,
        updatedAt: data.updatedAt && data.updatedAt.toDate ? data.updatedAt.toDate().toISOString() : (data.updatedAt || ''),
        clientId: data.clientId || ''
      }
    };
  }

  function isRemoteNewer(localState, remoteMeta) {
    const localRev = (localState.syncMeta && localState.syncMeta.revision) || 0;
    const remoteRev = (remoteMeta && remoteMeta.revision) || 0;
    if (remoteRev > localRev) return true;
    if (remoteRev < localRev) return false;
    const localAt = (localState.syncMeta && localState.syncMeta.updatedAt) || '';
    const remoteAt = (remoteMeta && remoteMeta.updatedAt) || '';
    return remoteAt > localAt;
  }

  async function pullIfNewer() {
    if (!docRef || !hooks) return;
    const cloud = await fetchCloudDoc();
    if (!cloud || !cloud.payload) return;
    const local = hooks.getState();
    const remoteMeta = loadRemoteMeta();
    const sameAsLast = remoteMeta && remoteMeta.revision === cloud.meta.revision;
    if (sameAsLast && !isRemoteNewer(local, cloud.meta)) return;
    if (isRemoteNewer(local, cloud.meta)) {
      applyCloudPayload(cloud.payload, cloud.meta);
    }
  }

  async function pushNow() {
    if (!docRef || !hooks || !auth || !auth.currentUser) return;
    if (pushInFlight) return;
    if (!root.navigator.onLine) {
      status.pendingPush = true;
      status.offline = true;
      notifyStatus();
      if (hooks.showToast) hooks.showToast('Offline — will sync when connected');
      return;
    }

    pushInFlight = true;
    status.syncing = true;
    status.pendingPush = false;
    notifyStatus();

    try {
      const state = hooks.getState();
      bumpRevision(state);
      touchSyncMeta(state);
      hooks.persistLocal();

      const payload = stripSyncFields(state);
      const revision = state.syncMeta.revision;
      const clientId = getClientId();

      await docRef.set({
        payload,
        revision,
        clientId,
        updatedAt: root.firebase.firestore.FieldValue.serverTimestamp()
      }, { merge: true });

      const meta = { revision, updatedAt: state.syncMeta.updatedAt, clientId };
      saveRemoteMeta(meta);
      status.lastSyncAt = new Date().toISOString();
      status.lastError = null;
    } catch (e) {
      console.warn('[GIW_SYNC] push failed', e);
      status.pendingPush = true;
      setError(e);
      throw e;
    } finally {
      pushInFlight = false;
      status.syncing = false;
      notifyStatus();
    }
  }

  function schedulePush() {
    if (!initDone || !status.signedIn || applyingRemote) return;
    status.pendingPush = true;
    notifyStatus();
    if (pushTimer) clearTimeout(pushTimer);
    pushTimer = setTimeout(() => {
      pushTimer = null;
      pushNow().catch(() => {});
    }, DEBOUNCE_MS);
  }

  function startListener() {
    stopListener();
    if (!docRef) return;
    unsubscribeSnapshot = docRef.onSnapshot(snap => {
      if (!snap.exists || applyingRemote || pushInFlight) return;
      const data = snap.data();
      if (!data || !data.payload) return;
      if (data.clientId === getClientId() && pushInFlight) return;

      const meta = {
        revision: data.revision || 0,
        updatedAt: data.updatedAt && data.updatedAt.toDate ? data.updatedAt.toDate().toISOString() : '',
        clientId: data.clientId || ''
      };
      const local = hooks.getState();
      if (isRemoteNewer(local, meta)) {
        applyCloudPayload(data.payload, meta);
      }
    }, err => {
      console.warn('[GIW_SYNC] listener error', err);
      setError(err);
    });
  }

  function stopListener() {
    if (unsubscribeSnapshot) {
      unsubscribeSnapshot();
      unsubscribeSnapshot = null;
    }
  }

  async function onAuthUser(user) {
    if (!user) {
      status.signedIn = false;
      status.user = null;
      stopListener();
      docRef = null;
      notifyStatus();
      return;
    }

    status.signedIn = true;
    status.user = {
      uid: user.uid,
      email: user.email || '',
      displayName: user.displayName || user.email || 'Google user',
      photoURL: user.photoURL || ''
    };
    docRef = docRefForUser(user.uid);
    notifyStatus();

    try {
      status.syncing = true;
      notifyStatus();
      const cloud = await fetchCloudDoc();
      const local = hooks.getState();
      const lastMeta = loadRemoteMeta();

      if (!cloud || !cloud.payload) {
        await pushNow();
      } else {
        const remoteMeta = cloud.meta;
        const localHas = stateHasUserData(local);
        const cloudHas = cloudHasUserData(cloud.payload, remoteMeta);

        if (localHas && cloudHas && !lastMeta) {
          await resolveInitialSync(cloud.payload, remoteMeta);
        } else if (isRemoteNewer(local, remoteMeta)) {
          applyCloudPayload(cloud.payload, remoteMeta);
        } else {
          await pushNow();
        }
      }
      startListener();
    } catch (e) {
      setError(e);
    } finally {
      status.syncing = false;
      notifyStatus();
      if (hooks.render) hooks.render();
    }
  }

  async function syncNow() {
    if (!status.signedIn) {
      try {
        await signInWithGoogle();
        if (hooks.showToast) hooks.showToast('Signed in');
        return;
      } catch (e) {
        if (hooks.showToast) hooks.showToast('Sign-in failed');
        setError(e);
        throw e;
      }
    }
    status.syncing = true;
    notifyStatus();
    try {
      if (!root.navigator.onLine) {
        status.offline = true;
        if (hooks.showToast) hooks.showToast('Offline — will sync when connected');
        return;
      }
      await pushNow();
      await pullIfNewer();
      if (hooks.showToast) hooks.showToast('Synced');
    } catch (e) {
      if (hooks.showToast) hooks.showToast('Sync failed');
      throw e;
    } finally {
      status.syncing = false;
      notifyStatus();
      if (hooks.render) hooks.render();
    }
  }

  function formatLastSync() {
    if (!status.lastSyncAt) return '';
    try {
      const d = new Date(status.lastSyncAt);
      const diff = Date.now() - d.getTime();
      if (diff < 60000) return 'just now';
      if (diff < 3600000) return Math.floor(diff / 60000) + ' min ago';
      return d.toLocaleString();
    } catch (e) {
      return '';
    }
  }

  function getStatusLabel() {
    if (!status.configured) return 'Sync unavailable';
    if (!status.signedIn) return 'Sign in to sync';
    if (status.offline) return 'Offline';
    if (status.syncing) return 'Syncing…';
    if (status.lastError) return 'Sync failed';
    if (status.pendingPush) return 'Pending upload';
    return 'Synced';
  }

  function getSyncButtonTitle() {
    if (!status.configured) return 'Cloud sync not configured';
    if (!status.signedIn) return 'Sign in to sync';
    if (status.syncing) return 'Syncing…';
    return 'Sync';
  }

  function getStatus() {
    return Object.assign({}, status, {
      statusLabel: getStatusLabel(),
      syncButtonTitle: getSyncButtonTitle(),
      lastSyncLabel: formatLastSync()
    });
  }

  async function init(h) {
    hooks = h;
    status.configured = configured();
    status.offline = !root.navigator.onLine;

    root.addEventListener('online', () => {
      status.offline = false;
      notifyStatus();
      if (status.signedIn && status.pendingPush) schedulePush();
    });
    root.addEventListener('offline', () => {
      status.offline = true;
      notifyStatus();
    });

    if (!status.configured) {
      notifyStatus();
      initDone = true;
      return;
    }
    if (!initFirebase()) {
      initDone = true;
      return;
    }

    try {
      const redirect = await auth.getRedirectResult();
      if (redirect && redirect.user) {
        await onAuthUser(redirect.user);
      }
    } catch (e) {
      console.warn('[GIW_SYNC] redirect result', e);
    }

    auth.onAuthStateChanged(user => {
      onAuthUser(user).catch(err => setError(err));
    });

    if (isNative()) {
      const plugin = getFirebaseAuthPlugin();
      if (plugin && plugin.addListener) {
        plugin.addListener('authStateChange', async ev => {
          if (ev && ev.user && auth && !auth.currentUser) {
            // Native layer signed in; JS SDK may need credential — handled by signInWithGoogle flow.
          }
        });
      }
    }

    if (isNative() && root.Capacitor && root.Capacitor.Plugins && root.Capacitor.Plugins.App) {
      root.Capacitor.Plugins.App.addListener('appStateChange', ({ isActive }) => {
        if (isActive && status.signedIn) {
          pullIfNewer().catch(() => {});
        }
      });
    }

    document.addEventListener('visibilitychange', () => {
      if (!document.hidden && status.signedIn) {
        pullIfNewer().catch(() => {});
      }
    });

    initDone = true;
    notifyStatus();
  }

  root.GIW_SYNC = {
    init,
    signInWithGoogle,
    signOut,
    syncNow,
    schedulePush,
    pushNow,
    pullIfNewer,
    getStatus,
    getStatusLabel,
    getSyncButtonTitle,
    touchSyncMeta,
    touchTripSync,
    isConfigured: () => status.configured,
    isSignedIn: () => status.signedIn
  };
})(typeof window !== 'undefined' ? window : globalThis);
