/**
 * Backup import sanitization — strips unsafe data and regenerates all IDs.
 * Loaded before index.html main script; also tested via scripts/audit-checks.mjs.
 */
(function (root) {
  const BAG_IDS = new Set(['carry-on', 'checked', 'camera', 'boat', '']);
  const SECTION_IDS = new Set(['all', 'night', 'dock', 'predive', 'postdive']);
  const HOME_SORTS = new Set(['created', 'date', 'progress', 'name']);
  const THEMES = new Set(['dark', 'light']);

  function cleanText(v, max) {
    if (v == null) return '';
    return String(v)
      .replace(/[\x00-\x08\x0B\x0C\x0E-\x1F]/g, '')
      .replace(/[<>]/g, '')
      .trim()
      .slice(0, max || 200);
  }

  function cleanTags(arr) {
    if (!Array.isArray(arr)) return [];
    return arr
      .map(t => cleanText(t, 48).replace(/\s+/g, ''))
      .filter(Boolean)
      .slice(0, 20);
  }

  function cleanDate(v) {
    const s = cleanText(v, 32);
    return /^\d{4}-\d{2}-\d{2}$/.test(s) ? s : '';
  }

  function sanitizeCategory(raw, makeId) {
    const src = raw && typeof raw === 'object' ? raw : {};
    const order = Number.isFinite(src.order) ? src.order : 0;
    return {
      id: makeId(),
      name: cleanText(src.name, 80) || 'Category',
      order
    };
  }

  function sanitizeItem(raw, catIdMap, makeId) {
    const src = raw && typeof raw === 'object' ? raw : {};
    let categoryId = src.categoryId;
    if (catIdMap && categoryId && catIdMap[categoryId]) {
      categoryId = catIdMap[categoryId];
    } else if (catIdMap && Object.keys(catIdMap).length) {
      categoryId = Object.values(catIdMap)[0];
    } else {
      categoryId = makeId();
    }
    const bag = BAG_IDS.has(src.bag) ? src.bag : '';
    const sections = Array.isArray(src.sections)
      ? src.sections.filter(s => SECTION_IDS.has(s) && s !== 'all')
      : [];
    const qty = Math.max(1, Math.min(99, parseInt(src.qty, 10) || 1));
    return {
      id: makeId(),
      categoryId,
      name: cleanText(src.name, 120) || 'Item',
      note: cleanText(src.note, 200),
      qty,
      packed: 0,
      returnPacked: 0,
      critical: !!src.critical,
      bag,
      sections,
      checked: false,
      fromTemplate: !!src.fromTemplate
    };
  }

  function buildCatMap(oldCats, newCats) {
    const map = {};
    if (!Array.isArray(oldCats)) return map;
    oldCats.forEach((c, i) => {
      if (c && c.id && newCats[i]) map[c.id] = newCats[i].id;
    });
    return map;
  }

  function sanitizeTemplateBlock(raw, makeId) {
    const block = raw && typeof raw === 'object' ? raw : {};
    if (!Array.isArray(block.categories) || !Array.isArray(block.items)) {
      throw new Error('Invalid backup');
    }
    const categories = block.categories.map(c => sanitizeCategory(c, makeId));
    const catMap = buildCatMap(block.categories, categories);
    return {
      categories,
      items: block.items.map(it => sanitizeItem(it, catMap, makeId))
    };
  }

  function sanitizeSavedTemplates(raw, makeId) {
    if (!Array.isArray(raw) || !raw.length) return null;
    return raw.map(tpl => {
      const src = tpl && typeof tpl === 'object' ? tpl : {};
      if (!Array.isArray(src.categories) || !Array.isArray(src.items)) {
        throw new Error('Invalid backup');
      }
      const categories = src.categories.map(c => sanitizeCategory(c, makeId));
      const catMap = buildCatMap(src.categories, categories);
      return {
        id: makeId(),
        name: cleanText(src.name, 80) || 'Template',
        desc: cleanText(src.desc, 200),
        builtIn: !!src.builtIn,
        categories,
        items: src.items.map(it => sanitizeItem(it, catMap, makeId))
      };
    });
  }

  function sanitizeImportedBackup(parsed, makeId) {
    const rootObj = parsed && typeof parsed === 'object' ? parsed : null;
    if (!rootObj) throw new Error('Invalid backup');
    const data = rootObj.data && typeof rootObj.data === 'object' ? rootObj.data : rootObj;
    if (!data || typeof data !== 'object') throw new Error('Invalid backup');
    if (!Array.isArray(data.trips)) throw new Error('Invalid backup');

    const masterTemplate = sanitizeTemplateBlock(data.masterTemplate, makeId);
    const savedTemplates = sanitizeSavedTemplates(data.savedTemplates, makeId);

    const trips = data.trips.map(tripRaw => {
      const src = tripRaw && typeof tripRaw === 'object' ? tripRaw : {};
      let categories;
      let catMap;
      if (Array.isArray(src.categories) && src.categories.length) {
        categories = src.categories.map(c => sanitizeCategory(c, makeId));
        catMap = buildCatMap(src.categories, categories);
      } else {
        categories = masterTemplate.categories.map(c => ({
          id: makeId(),
          name: c.name,
          order: c.order
        }));
        catMap = buildCatMap(masterTemplate.categories, categories);
      }
      const items = Array.isArray(src.items)
        ? src.items.map(it => sanitizeItem(it, catMap, makeId))
        : [];
      return {
        id: makeId(),
        name: cleanText(src.name, 120) || 'Trip',
        dateStart: cleanDate(src.dateStart || src.date),
        dateEnd: cleanDate(src.dateEnd) || cleanDate(src.dateStart || src.date),
        location: cleanText(src.location, 120),
        tags: cleanTags(src.tags),
        archived: !!src.archived,
        unpackMode: false,
        returnMode: false,
        celebrated: false,
        returnCelebrated: false,
        viewSection: SECTION_IDS.has(src.viewSection) ? src.viewSection : 'all',
        categories,
        items
      };
    });

    const settings = data.settings && typeof data.settings === 'object' ? data.settings : {};
    return {
      masterTemplate,
      trips,
      savedTemplates: savedTemplates || undefined,
      settings: {
        theme: THEMES.has(settings.theme) ? settings.theme : 'dark',
        homeSort: HOME_SORTS.has(settings.homeSort) ? settings.homeSort : 'created',
        hideCompleted: !!settings.hideCompleted,
        showArchived: !!settings.showArchived,
        pinnedTripId: null
      }
    };
  }

  root.sanitizeImportedBackup = sanitizeImportedBackup;
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = { sanitizeImportedBackup, cleanText };
  }
})(typeof globalThis !== 'undefined' ? globalThis : window);
