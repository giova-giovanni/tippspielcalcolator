/* Tippspiel Essen – static dashboard for GitHub Pages (no framework, no build step).
 *
 * Data: docs/data/*.json written by the Python engine (optionally AES-GCM encrypted).
 * Input: commits data/menus.csv / data/tips.csv through the GitHub contents API with a
 * fine-grained token that lives only in this browser's localStorage.
 *
 * Security notes: every piece of data is inserted with textContent (see h()); the token is
 * only ever sent to https://api.github.com and never logged.
 */
(function () {
  'use strict';

  // ------------------------------------------------------------------ constants
  var CATS = ['vorspeise', 'hauptspeise', 'beilage'];
  var SHORT = { vorspeise: 'v', hauptspeise: 'h', beilage: 'b' };
  var TZ = 'Europe/Rome';
  var LS = 'tsp.';
  var CHART_SRC = 'https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.js';
  var CHART_SRI = 'sha384-dug+JxfBvklEQdJ4AYuBBAIScUz0bVN73xpy273gcAwHjb3qI0fXmuYNaNfdyYJG';
  var WD_DE = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So'];
  var MENU_HEADER = ['date', 'year', 'weekday', 'status', 'vorspeise', 'hauptspeise', 'beilage',
    'vorspeise_norm', 'hauptspeise_norm', 'beilage_norm', 'source'];
  var TIP_HEADER = ['date', 'player', 'vorspeise', 'hauptspeise', 'beilage', 'points', 'points_sheet', 'source'];
  var GH_API = 'https://api.github.com';

  // Categorical palette (validated light/dark steps, fixed order; colour follows the entity)
  var PALETTE = {
    light: ['#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#e87ba4', '#008300', '#4a3aa7', '#e34948'],
    dark: ['#3987e5', '#d95926', '#199e70', '#c98500', '#d55181', '#008300', '#9085e9', '#e66767']
  };

  // ------------------------------------------------------------------ storage
  var store = {
    get: function (k, d) {
      try { var v = localStorage.getItem(LS + k); return v === null ? (d === undefined ? null : d) : v; } catch (e) { return d === undefined ? null : d; }
    },
    set: function (k, v) {
      try {
        if (v === null || v === undefined || v === '') localStorage.removeItem(LS + k);
        else localStorage.setItem(LS + k, String(v));
      } catch (e) { /* storage blocked */ }
    },
    getJSON: function (k, d) {
      try { var v = this.get(k); return v ? JSON.parse(v) : d; } catch (e) { return d; }
    },
    setJSON: function (k, v) { this.set(k, JSON.stringify(v)); }
  };
  var session = {
    get: function (k) { try { return sessionStorage.getItem(LS + k); } catch (e) { return null; } },
    set: function (k, v) { try { if (v == null) sessionStorage.removeItem(LS + k); else sessionStorage.setItem(LS + k, v); } catch (e) { /* ignore */ } }
  };

  // ------------------------------------------------------------------ i18n
  var lang = store.get('lang', 'de') === 'it' ? 'it' : 'de';
  function t(key, vars) {
    var dict = (window.I18N && window.I18N[lang]) || {};
    var s = dict[key];
    if (s === undefined && window.I18N && window.I18N.de) s = window.I18N.de[key];
    if (s === undefined) s = key;
    if (vars) s = s.replace(/\{(\w+)\}/g, function (m, k) { return vars[k] !== undefined && vars[k] !== null ? String(vars[k]) : m; });
    return s;
  }
  function locale() { return lang === 'it' ? 'it-IT' : 'de-DE'; }
  function catName(c) { return t('cat.' + c); }
  function catShort(c) { return t('catS.' + c); }
  function wdShort(i) { return t('wd.' + i); }
  function wdLong(i) { return t('wdl.' + i); }
  function statusName(s) { return t('status.' + (s || 'pending')); }
  function pick(obj, base) { // obj.note_de / obj.note_it
    if (!obj) return '';
    return obj[base + '_' + lang] || obj[base + '_de'] || '';
  }

  // ------------------------------------------------------------------ formatting
  var nfCache = {};
  function nf(opts) {
    var k = locale() + JSON.stringify(opts);
    if (!nfCache[k]) nfCache[k] = new Intl.NumberFormat(locale(), opts);
    return nfCache[k];
  }
  function isNum(x) { return typeof x === 'number' && isFinite(x); }
  function fmtNum(x, d) {
    if (!isNum(x)) return '–';
    d = d === undefined ? 1 : d;
    return nf({ minimumFractionDigits: d, maximumFractionDigits: d }).format(x);
  }
  function fmtPts(x) {
    if (!isNum(x)) return '–';
    return nf({ minimumFractionDigits: 0, maximumFractionDigits: 2 }).format(x);
  }
  function fmtPct(p, d) {
    if (!isNum(p)) return '–';
    if (d === undefined) d = (p > 0 && p < 0.01) ? 1 : 0;
    return nf({ style: 'percent', minimumFractionDigits: d, maximumFractionDigits: d }).format(p);
  }
  function pad(n) { return (n < 10 ? '0' : '') + n; }

  // ------------------------------------------------------------------ dates (ISO strings, UTC math)
  function parseISO(s) {
    var p = String(s).slice(0, 10).split('-');
    return new Date(Date.UTC(+p[0], +p[1] - 1, +p[2]));
  }
  function isoOf(d) { return d.toISOString().slice(0, 10); }
  function isISO(s) { return /^\d{4}-\d{2}-\d{2}$/.test(String(s || '')); }
  function addDays(iso, n) { var d = parseISO(iso); d.setUTCDate(d.getUTCDate() + n); return isoOf(d); }
  function weekdayOf(iso) { return (parseISO(iso).getUTCDay() + 6) % 7; } // 0 = Monday
  function mondayOf(iso) { return addDays(iso, -weekdayOf(iso)); }
  function isoWeek(iso) {
    var d = parseISO(iso);
    var day = (d.getUTCDay() + 6) % 7;
    d.setUTCDate(d.getUTCDate() - day + 3);
    var firstThu = new Date(Date.UTC(d.getUTCFullYear(), 0, 4));
    var wk = 1 + Math.round(((d - firstThu) / 864e5 - 3 + ((firstThu.getUTCDay() + 6) % 7)) / 7);
    return [d.getUTCFullYear(), wk];
  }
  function sameWeek(a, b) { var x = isoWeek(a), y = isoWeek(b); return x[0] === y[0] && x[1] === y[1]; }
  function fmtDate(iso, opts) {
    if (!isISO(iso)) return '–';
    var o = { timeZone: 'UTC' };
    for (var k in opts) o[k] = opts[k];
    return new Intl.DateTimeFormat(locale(), o).format(parseISO(iso));
  }
  function fmtDM(iso) { return fmtDate(iso, { day: '2-digit', month: '2-digit' }); }
  function fmtDMY(iso) { return fmtDate(iso, { day: '2-digit', month: '2-digit', year: 'numeric' }); }
  function fmtLong(iso) { return fmtDate(iso, { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' }); }
  function fmtWdDM(iso) { return wdShort(weekdayOf(iso)) + ' ' + fmtDM(iso); }

  // Europe/Rome wall clock via Intl (no library)
  var romeFmt = null;
  function zonedParts(ms) {
    if (!romeFmt) {
      romeFmt = new Intl.DateTimeFormat('en-US', {
        timeZone: TZ, hourCycle: 'h23', year: 'numeric', month: '2-digit', day: '2-digit',
        hour: '2-digit', minute: '2-digit', second: '2-digit'
      });
    }
    var o = {};
    romeFmt.formatToParts(new Date(ms)).forEach(function (p) { o[p.type] = p.value; });
    return { y: +o.year, m: +o.month, d: +o.day, h: (+o.hour) % 24, mi: +o.minute, s: +o.second };
  }
  function romeTodayISO(ms) {
    var p = zonedParts(ms === undefined ? Date.now() : ms);
    return p.y + '-' + pad(p.m) + '-' + pad(p.d);
  }
  function tzOffset(ms) {
    var p = zonedParts(ms);
    return Date.UTC(p.y, p.m - 1, p.d, p.h, p.mi, p.s) - Math.floor(ms / 1000) * 1000;
  }
  /** UTC epoch ms of the Rome wall-clock time iso hh:mm (DST-safe). */
  function romeToUtc(iso, hh, mm) {
    var a = String(iso).split('-').map(Number);
    var guess = Date.UTC(a[0], a[1] - 1, a[2], hh, mm);
    var off = tzOffset(guess);
    var t1 = guess - off;
    var off2 = tzOffset(t1);
    if (off2 !== off) t1 = guess - off2;
    return t1;
  }
  function deadlineFor(iso, hhmm) {
    var p = String(hhmm || '12:00').split(':');
    return romeToUtc(iso, +p[0] || 12, +p[1] || 0);
  }

  // ------------------------------------------------------------------ names
  function clean(s) { return String(s == null ? '' : s).replace(/ /g, ' ').replace(/\s+/g, ' ').trim(); }
  /** like Python str.casefold() for our purposes (ß -> ss) */
  function fold(s) { return clean(s).toLowerCase().replace(/ß/g, 'ss'); }
  function splitOpts(s) {
    return clean(s).split(/\s+\/\s+/).map(clean).filter(function (x) { return x && x !== '-'; });
  }

  // ------------------------------------------------------------------ DOM helpers (text only!)
  function h(tag, attrs) {
    var el = document.createElement(tag);
    if (attrs) {
      Object.keys(attrs).forEach(function (k) {
        var v = attrs[k];
        if (v === null || v === undefined || v === false) return;
        if (k === 'class') el.className = v;
        else if (k === 'style' && typeof v === 'object') Object.keys(v).forEach(function (sk) { el.style[sk] = v[sk]; });
        else if (k.slice(0, 2) === 'on' && typeof v === 'function') el.addEventListener(k.slice(2), v);
        else if (k === 'value') el.value = v;
        else if (k === 'checked') el.checked = !!v;
        else if (v === true) el.setAttribute(k, '');
        else el.setAttribute(k, String(v));
      });
    }
    appendKids(el, Array.prototype.slice.call(arguments, 2));
    return el;
  }
  function appendKids(el, kids) {
    kids.forEach(function (k) {
      if (k === null || k === undefined || k === false) return;
      if (Array.isArray(k)) appendKids(el, k);
      else if (k instanceof Node) el.appendChild(k);
      else el.appendChild(document.createTextNode(String(k)));
    });
    return el;
  }
  var ICONS = {
    heute: '<path d="M12 7v5l3 2"/><circle cx="12" cy="12" r="8.5"/>',
    woche: '<rect x="3.5" y="5" width="17" height="15" rx="2"/><path d="M3.5 10h17M8 3v4M16 3v4"/>',
    statistik: '<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>',
    rangliste: '<path d="M8 21h8M12 17v4M7 4h10v5a5 5 0 0 1-10 0V4zM7 6H4a3 3 0 0 0 3 4M17 6h3a3 3 0 0 1-3 4"/>',
    backtest: '<path d="M3 12h4l3-7 4 14 3-7h4"/>',
    datenbank: '<ellipse cx="12" cy="5.5" rx="8" ry="3"/><path d="M4 5.5v13c0 1.7 3.6 3 8 3s8-1.3 8-3v-13M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3"/>',
    eingabe: '<path d="M4 20h4L19 9l-4-4L4 16v4zM14 6l4 4"/>',
    copy: '<rect x="8" y="8" width="12" height="12" rx="2"/><path d="M16 8V5a1 1 0 0 0-1-1H5a1 1 0 0 0-1 1v10a1 1 0 0 0 1 1h3"/>',
    fish: '<path d="M2 12c3-5 9-6 14-2l5-3v10l-5-3c-5 4-11 3-14-2z"/><circle cx="7" cy="11" r="0.8"/>',
    warn: '<path d="M12 3 2 20h20L12 3zM12 10v4M12 17.5v.5"/>',
    info: '<circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7.5v.5"/>',
    ok: '<circle cx="12" cy="12" r="9"/><path d="M8 12.5l3 3 5-6"/>',
    eye: '<path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
    lock: '<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/>',
    edit: '<path d="M4 20h4L19 9l-4-4L4 16v4z"/>'
  };
  function icon(name, cls) {
    var span = document.createElement('span');
    span.className = 'ic' + (cls ? ' ' + cls : '');
    span.setAttribute('aria-hidden', 'true');
    // constant markup only – never data
    span.innerHTML = '<svg viewBox="0 0 24 24">' + (ICONS[name] || '') + '</svg>';
    return span;
  }
  function notice(kind, text, extra) {
    return h('div', { class: 'notice ' + kind, role: kind === 'danger' || kind === 'warn' ? 'alert' : null },
      icon(kind === 'ok' ? 'ok' : (kind === 'info' ? 'info' : 'warn')), h('div', { class: 'notice-body' }, text, extra || null));
  }
  function card(title, kids, opts) {
    opts = opts || {};
    return h('section', { class: 'card' + (opts.cls ? ' ' + opts.cls : ''), id: opts.id || null },
      title ? h('h2', { class: 'card-title' }, title, opts.badge || null) : null,
      opts.sub ? h('p', { class: 'muted small' }, opts.sub) : null,
      kids);
  }
  function chip(text, cls) { return h('span', { class: 'chip' + (cls ? ' ' + cls : '') }, text); }
  function segmented(options, current, onChange, label) {
    var wrap = h('div', { class: 'seg', role: 'group', 'aria-label': label || null });
    options.forEach(function (o) {
      wrap.appendChild(h('button', {
        type: 'button', class: 'seg-btn' + (String(o.value) === String(current) ? ' active' : ''),
        'aria-pressed': String(String(o.value) === String(current)),
        onclick: function () { onChange(o.value); }
      }, o.label));
    });
    return wrap;
  }
  function selectEl(options, current, onChange, label, id) {
    var s = h('select', { 'aria-label': label || null, id: id || null, onchange: function () { onChange(s.value); } });
    options.forEach(function (o) {
      var opt = h('option', { value: String(o.value) }, o.label);
      if (String(o.value) === String(current)) opt.selected = true;
      s.appendChild(opt);
    });
    return s;
  }
  function table(headers, rows, opts) {
    opts = opts || {};
    var thead = h('thead', null, h('tr', null, headers.map(function (hd) {
      return h('th', { class: hd.num ? 'num' : null, scope: 'col' }, hd.label);
    })));
    var tbody = h('tbody', null, rows.map(function (r) {
      var tr = h('tr', { class: r.cls || null });
      (r.cells || r).forEach(function (c, i) {
        tr.appendChild(h('td', { class: headers[i] && headers[i].num ? 'num' : null }, c));
      });
      return tr;
    }));
    return h('div', { class: 'table-wrap' + (opts.cls ? ' ' + opts.cls : '') }, h('table', { class: 'tbl' }, thead, tbody));
  }
  function emptyState(title, text, kids) {
    return h('div', { class: 'card empty' }, icon('info', 'big'), h('h2', null, title), text ? h('p', { class: 'muted' }, text) : null, kids || null);
  }
  function bar(frac, cls) {
    var f = Math.max(0, Math.min(1, isNum(frac) ? frac : 0));
    return h('div', { class: 'bar' + (cls ? ' ' + cls : '') }, h('span', { style: { width: (f * 100).toFixed(1) + '%' } }));
  }

  var toastTimer = null;
  function toast(msg, kind) {
    var el = document.getElementById('toast');
    if (!el) return;
    el.textContent = msg;
    el.className = 'toast show' + (kind ? ' ' + kind : '');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { el.className = 'toast'; }, 2600);
  }

  // ------------------------------------------------------------------ base64 / UTF-8
  function b64ToBytes(b64) {
    var bin = atob(String(b64 || '').replace(/\s+/g, ''));
    var out = new Uint8Array(bin.length);
    for (var i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
    return out;
  }
  function bytesToB64(bytes) {
    var s = '';
    var CH = 0x8000;
    for (var i = 0; i < bytes.length; i += CH) s += String.fromCharCode.apply(null, bytes.subarray(i, i + CH));
    return btoa(s);
  }
  function utf8ToB64(str) { return bytesToB64(new TextEncoder().encode(str)); }
  function b64ToUtf8(b64) { return new TextDecoder('utf-8').decode(b64ToBytes(b64)); }

  // ------------------------------------------------------------------ CSV (RFC 4180)
  function parseCSV(text) {
    var rows = [], row = [], field = '', i = 0, inQ = false, n = text.length, c;
    while (i < n) {
      c = text[i];
      if (inQ) {
        if (c === '"') {
          if (text[i + 1] === '"') { field += '"'; i += 2; continue; }
          inQ = false; i++; continue;
        }
        field += c; i++; continue;
      }
      if (c === '"' && field === '') { inQ = true; i++; continue; }
      if (c === ',') { row.push(field); field = ''; i++; continue; }
      if (c === '\r' || c === '\n') {
        if (c === '\r' && text[i + 1] === '\n') i++;
        row.push(field); rows.push(row); row = []; field = ''; i++; continue;
      }
      field += c; i++;
    }
    if (field !== '' || row.length) { row.push(field); rows.push(row); }
    return rows;
  }
  function csvField(v) {
    var s = v == null ? '' : String(v);
    return /[",\r\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
  }
  function serializeCSV(rows, eol) {
    eol = eol || '\n';
    return rows.map(function (r) { return r.map(csvField).join(','); }).join(eol) + eol;
  }
  /**
   * Insert or replace one row. values: {column: value}; keys: key columns (date [, player]).
   * Column order comes from the existing header; rows stay sorted by the key columns.
   */
  function upsertCsv(text, values, keys, defaultHeader) {
    text = text || '';
    var bom = text.charCodeAt(0) === 0xFEFF;
    if (bom) text = text.slice(1);
    var eol = text.indexOf('\r\n') >= 0 ? '\r\n' : '\n';
    var rows = parseCSV(text).filter(function (r) { return !(r.length === 1 && r[0] === ''); });
    var header = rows.length ? rows[0].map(clean) : defaultHeader.slice();
    var body = rows.slice(1);
    var keyIdx = keys.map(function (k) { return header.indexOf(k); });
    if (keyIdx.some(function (i) { return i < 0; })) throw new Error(t('gh.err.header', { cols: keys.join(', ') }));
    function match(r) {
      return keys.every(function (k, j) {
        var cell = r[keyIdx[j]] || '';
        return k === 'player' ? fold(cell) === fold(values[k]) : clean(cell) === clean(values[k]);
      });
    }
    var newRow = header.map(function (col) {
      return Object.prototype.hasOwnProperty.call(values, col) && values[col] != null ? String(values[col]) : '';
    });
    var pos = -1;
    for (var i = 0; i < body.length; i++) if (match(body[i])) { pos = i; break; }
    var action;
    if (pos >= 0) {
      var old = body[pos];
      header.forEach(function (col, j) {
        if (!Object.prototype.hasOwnProperty.call(values, col)) newRow[j] = old[j] == null ? '' : old[j];
      });
      body[pos] = newRow;
      // drop accidental duplicates of the same key
      body = body.filter(function (r, j) { return j === pos || !match(r); });
      action = 'update';
    } else {
      var sk = function (r) { return keyIdx.map(function (j) { return r[j] || ''; }).join('\u0000'); };
      var k = sk(newRow);
      var ins = body.length;
      for (var m = 0; m < body.length; m++) if (sk(body[m]) > k) { ins = m; break; }
      body.splice(ins, 0, newRow);
      action = 'insert';
    }
    return { text: (bom ? '﻿' : '') + serializeCSV([header].concat(body), eol), action: action };
  }
  function menuValues(date, v, hh, b, free) {
    return {
      date: date, year: date.slice(0, 4), weekday: WD_DE[weekdayOf(date)], status: free ? 'free' : 'served',
      vorspeise: free ? 'Frei' : clean(v), hauptspeise: free ? 'Frei' : clean(hh), beilage: free ? 'Frei' : clean(b),
      vorspeise_norm: '', hauptspeise_norm: '', beilage_norm: '', source: 'form'
    };
  }
  function tipValues(date, player, v, hh, b) {
    return {
      date: date, player: clean(player), vorspeise: clean(v), hauptspeise: clean(hh), beilage: clean(b),
      points: '', points_sheet: '', source: 'form'
    };
  }

  // ------------------------------------------------------------------ GitHub contents API
  function ghHeaders(token, json) {
    var hd = { 'Authorization': 'Bearer ' + token, 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28' };
    if (json) hd['Content-Type'] = 'application/json';
    return hd;
  }
  function ghErr(status, body) {
    var e = new Error((body && body.message) || ('HTTP ' + status));
    e.status = status;
    return e;
  }
  function ghFetch(path, token, opts) {
    opts = opts || {};
    return fetch(GH_API + path, {
      method: opts.method || 'GET', headers: ghHeaders(token, !!opts.body), body: opts.body || undefined,
      cache: 'no-store', referrerPolicy: 'no-referrer'
    }).then(function (res) {
      return res.text().then(function (txt) {
        var body = null;
        try { body = txt ? JSON.parse(txt) : null; } catch (e) { body = null; }
        return { status: res.status, ok: res.ok, body: body };
      });
    });
  }
  function repoPath(cfg) { return '/repos/' + encodeURIComponent(cfg.owner) + '/' + encodeURIComponent(cfg.repo); }
  function ghGetFile(cfg, path) {
    var url = repoPath(cfg) + '/contents/' + path.split('/').map(encodeURIComponent).join('/') + '?ref=' + encodeURIComponent(cfg.branch);
    return ghFetch(url, cfg.token).then(function (r) {
      if (r.status === 404) return { exists: false };
      if (!r.ok) throw ghErr(r.status, r.body);
      var b = r.body || {};
      if (b.content && b.encoding !== 'none') return { exists: true, sha: b.sha, text: b64ToUtf8(b.content) };
      if (!b.sha) return { exists: true, sha: b.sha, text: '' };
      // > 1 MB: contents API returns no content -> fetch the blob
      return ghFetch(repoPath(cfg) + '/git/blobs/' + encodeURIComponent(b.sha), cfg.token).then(function (bl) {
        if (!bl.ok) throw ghErr(bl.status, bl.body);
        return { exists: true, sha: b.sha, text: b64ToUtf8((bl.body && bl.body.content) || '') };
      });
    });
  }
  function ghPutFile(cfg, path, text, sha, message) {
    var body = { message: message, content: utf8ToB64(text), branch: cfg.branch };
    if (sha) body.sha = sha;
    return ghFetch(repoPath(cfg) + '/contents/' + path.split('/').map(encodeURIComponent).join('/'), cfg.token,
      { method: 'PUT', body: JSON.stringify(body) });
  }
  /** GET -> upsert -> PUT; retries once on 409 (sha conflict) after refetching. */
  function commitRow(cfg, kind, values, onStatus) {
    onStatus = onStatus || function () {};
    var path = kind === 'menu' ? 'data/menus.csv' : 'data/tips.csv';
    var keys = kind === 'menu' ? ['date'] : ['date', 'player'];
    var header = kind === 'menu' ? MENU_HEADER : TIP_HEADER;
    var message = kind === 'menu'
      ? 'Menü ' + values.date + ' via Website'
      : 'Tipp ' + values.date + ' ' + values.player + ' via Website';
    function attempt(n) {
      onStatus(n ? 'retry' : 'load', path);
      return ghGetFile(cfg, path).then(function (f) {
        var up = upsertCsv(f.exists ? f.text : '', values, keys, header);
        onStatus('save', path);
        return ghPutFile(cfg, path, up.text, f.exists ? f.sha : undefined, message).then(function (r) {
          if (r.ok) return { action: up.action, commit: (r.body && r.body.commit) || null, path: path };
          if (r.status === 409 && n === 0) return attempt(1);
          throw ghErr(r.status, r.body);
        });
      });
    }
    return attempt(0);
  }
  function findRun(cfg, sha, tries) {
    if (!sha) return Promise.resolve(null);
    return ghFetch(repoPath(cfg) + '/actions/runs?per_page=5&head_sha=' + encodeURIComponent(sha), cfg.token).then(function (r) {
      var run = r.ok && r.body && r.body.workflow_runs && r.body.workflow_runs[0];
      if (run && /^https:\/\/github\.com\//.test(run.html_url)) return run.html_url;
      if (tries > 1 && r.status !== 403 && r.status !== 401) {
        return new Promise(function (res) { setTimeout(res, 4000); }).then(function () { return findRun(cfg, sha, tries - 1); });
      }
      return null;
    }).catch(function () { return null; });
  }
  function ghErrorText(e) {
    if (!e || e.status === undefined) return t('gh.err.network') + (e && e.message ? ' (' + e.message + ')' : '');
    if (e.status === 401) return t('gh.err.401');
    if (e.status === 403) return t('gh.err.403');
    if (e.status === 404) return t('gh.err.404');
    if (e.status === 409) return t('gh.err.409');
    if (e.status === 422) return t('gh.err.422', { msg: e.message });
    return t('gh.err.other', { status: e.status, msg: e.message });
  }

  // ------------------------------------------------------------------ settings
  function detectRepo(meta) {
    var host = location.hostname, owner = '', name = '';
    if (/\.github\.io$/i.test(host)) {
      owner = host.split('.')[0];
      var seg = location.pathname.split('/').filter(Boolean)[0];
      name = seg && !/\.html?$/i.test(seg) ? seg : owner + '.github.io';
    }
    var m = (meta && meta.repo) || {};
    return { owner: owner || m.owner || '', repo: name || m.name || '', branch: m.branch || 'main' };
  }
  function settings(meta) {
    var d = detectRepo(meta);
    return {
      owner: store.get('gh.owner') || d.owner,
      repo: store.get('gh.repo') || d.repo,
      branch: store.get('gh.branch') || d.branch || 'main',
      token: store.get('gh.token') || '',
      player: store.get('player') || (meta && meta.me) || ''
    };
  }

  // ------------------------------------------------------------------ crypto (encrypted site data)
  function decryptEnvelope(env, pass) {
    if (!window.crypto || !crypto.subtle) return Promise.reject(new Error(t('pass.nosubtle')));
    var enc = new TextEncoder();
    return crypto.subtle.importKey('raw', enc.encode(pass), 'PBKDF2', false, ['deriveKey']).then(function (km) {
      return crypto.subtle.deriveKey({ name: 'PBKDF2', salt: b64ToBytes(env.salt), iterations: env.iter || 200000, hash: 'SHA-256' },
        km, { name: 'AES-GCM', length: 256 }, false, ['decrypt']);
    }).then(function (key) {
      return crypto.subtle.decrypt({ name: 'AES-GCM', iv: b64ToBytes(env.iv) }, key, b64ToBytes(env.data));
    }).then(function (pt) { return JSON.parse(new TextDecoder().decode(pt)); });
  }
  var passPrompt = null;
  function askPassphrase(errText) {
    if (passPrompt) return passPrompt;
    passPrompt = new Promise(function (resolve) {
      var root = document.getElementById('modal-root');
      var input = h('input', { type: 'password', id: 'pass-input', autocomplete: 'current-password', 'aria-label': t('pass.label') });
      function done(v) { root.replaceChildren(); passPrompt = null; resolve(v); }
      var form = h('form', {
        class: 'modal-card', onsubmit: function (e) { e.preventDefault(); if (input.value) done(input.value); }
      },
        h('h2', null, icon('lock'), ' ', t('pass.title')),
        h('p', { class: 'muted' }, t('pass.text')),
        errText ? notice('danger', errText) : null,
        h('label', { class: 'field' }, h('span', null, t('pass.label')), input),
        h('div', { class: 'btn-row' },
          h('button', { type: 'submit', class: 'btn primary' }, t('pass.ok')),
          h('button', { type: 'button', class: 'btn', onclick: function () { done(null); } }, t('pass.cancel'))));
      root.replaceChildren(h('div', { class: 'modal', role: 'dialog', 'aria-modal': 'true' }, form));
      setTimeout(function () { input.focus(); }, 30);
    });
    return passPrompt;
  }
  function decryptWithPrompt(env) {
    var stored = store.get('passphrase');
    var tryPass = function (pass, err) {
      var p = pass ? Promise.resolve(pass) : askPassphrase(err);
      return p.then(function (pw) {
        if (!pw) return null;
        return decryptEnvelope(env, pw).then(function (obj) {
          store.set('passphrase', pw);
          return obj;
        }, function (e) {
          if (e && e.name === 'OperationError') {
            if (store.get('passphrase') === pw) store.set('passphrase', null);
            return tryPass(null, t('pass.wrong'));
          }
          throw e;
        });
      });
    };
    return tryPass(stored, null);
  }

  // ------------------------------------------------------------------ data loading
  var dataCache = {};
  function load(name) {
    if (!dataCache[name]) {
      dataCache[name] = fetch('data/' + name + '.json', { cache: 'no-cache' }).then(function (res) {
        if (res.status === 404) return { status: 'missing' };
        if (!res.ok) return { status: 'error', error: new Error('HTTP ' + res.status) };
        return res.json().then(function (obj) {
          if (obj && typeof obj === 'object' && typeof obj.enc === 'string' && obj.data) {
            return decryptWithPrompt(obj).then(function (dec) {
              if (dec === null) { delete dataCache[name]; return { status: 'locked' }; }
              return { status: 'ok', data: dec };
            });
          }
          return { status: 'ok', data: obj };
        });
      }).catch(function (e) {
        delete dataCache[name];
        return { status: 'error', error: e };
      });
    }
    return dataCache[name];
  }
  function okData(r) { return r && r.status === 'ok' ? r.data : null; }

  // ------------------------------------------------------------------ pending submissions (local)
  function pendingAll() { var l = store.getJSON('pending', []); return Array.isArray(l) ? l : []; }
  function addPending(entry) {
    var l = pendingAll().filter(function (p) {
      return !(p.kind === entry.kind && p.date === entry.date && (p.kind === 'menu' || fold(p.player) === fold(entry.player)));
    });
    l.push(entry);
    store.setJSON('pending', l);
  }
  function prunePending(menus, tips) {
    var now = Date.now();
    var l = pendingAll();
    var keep = l.filter(function (p) {
      if (!p || !p.date || now - (p.at || 0) > 4 * 864e5) return false;
      if (p.kind === 'tip' && tips) {
        var r = (tips.rows || []).filter(function (x) { return x.date === p.date && fold(x.player) === fold(p.player); })[0];
        if (r && fold(r.v) === fold(p.v) && fold(r.h) === fold(p.h) && fold(r.b) === fold(p.b)) return false;
      }
      if (p.kind === 'menu' && menus) {
        var m = (menus.rows || []).filter(function (x) { return x.date === p.date; })[0];
        if (m && (p.free ? m.status === 'free' : (fold(m.v) === fold(p.v) && fold(m.h) === fold(p.h) && fold(m.b) === fold(p.b)))) return false;
      }
      return true;
    });
    if (keep.length !== l.length) store.setJSON('pending', keep);
    return keep;
  }

  // ------------------------------------------------------------------ rule 4 (client side)
  function R4(cfg, freeDays) {
    cfg = cfg || {};
    this.max = cfg.max_per_week || 2;
    this.mode = cfg.consecutive_mode || 'workday_adjacent_same_week';
    this.free = freeDays || new Set();
  }
  R4.prototype.isWorkday = function (iso) { return weekdayOf(iso) < 5 && !this.free.has(iso); };
  R4.prototype.nextWorkday = function (iso) {
    var x = addDays(iso, 1), g = 0;
    while (!this.isWorkday(x) && g++ < 40) x = addDays(x, 1);
    return x;
  };
  R4.prototype.adjacent = function (a, b) {
    if (a === b) return false;
    if (a > b) { var tmp = a; a = b; b = tmp; }
    if (this.mode === 'calendar_adjacent') return addDays(a, 1) === b;
    if (this.mode === 'workday_adjacent_any') return this.nextWorkday(a) === b;
    return sameWeek(a, b) && this.nextWorkday(a) === b;
  };
  /** history: {iso: [options]} of one player in one category */
  R4.prototype.violations = function (cat, dish, day, history) {
    if (!clean(dish)) return [];
    var k = fold(dish), self = this;
    var same = Object.keys(history || {}).filter(function (d) {
      return d !== day && (history[d] || []).some(function (o) { return fold(o) === k; });
    }).sort();
    var out = [];
    var inWeek = same.filter(function (d) { return sameWeek(d, day); });
    if (inWeek.length >= this.max) out.push({ category: cat, dish: dish, kind: 'max_per_week', days: inWeek });
    var adj = same.filter(function (d) { return self.adjacent(d, day); });
    if (adj.length) out.push({ category: cat, dish: dish, kind: 'consecutive', days: adj });
    return out;
  };
  function violationText(v, max) {
    var names = v.days.map(function (d) { return wdShort(weekdayOf(d)); }).join(', ');
    return v.kind === 'max_per_week' ? t('r4.max', { n: max || 2, days: names }) : t('r4.adj', { days: names });
  }

  // ------------------------------------------------------------------ shared context
  function loadCtx() {
    return Promise.all(['meta', 'menus', 'tips', 'dishes'].map(load)).then(function (rs) {
      var meta = okData(rs[0]), menus = okData(rs[1]), tips = okData(rs[2]), dishes = okData(rs[3]);
      var free = new Set();
      if (menus) {
        (menus.rows || []).forEach(function (r) { if (r.status === 'free') free.add(r.date); });
        (menus.free_days_ahead || []).forEach(function (d) { free.add(d); });
      }
      var pend = prunePending(menus, tips);
      pend.forEach(function (p) { if (p.kind === 'menu' && p.free) free.add(p.date); });
      return {
        meta: meta, menus: menus, tips: tips, dishes: dishes,
        me: (meta && meta.me) || store.get('player') || '',
        r4: new R4(meta && meta.r4, free), pending: pend,
        locked: rs.some(function (r) { return r.status === 'locked'; })
      };
    });
  }
  function canonOpts(ctx, cat, raw) {
    var list = (ctx.dishes && ctx.dishes[cat]) || [];
    return splitOpts(raw).map(function (o) {
      var k = fold(o);
      for (var i = 0; i < list.length; i++) if (fold(list[i]) === k) return list[i];
      return o;
    });
  }
  function historyOf(ctx, player) {
    var H = { vorspeise: {}, hauptspeise: {}, beilage: {} };
    var pf = fold(player);
    ((ctx.tips && ctx.tips.rows) || []).forEach(function (r) {
      if (fold(r.player) !== pf) return;
      CATS.forEach(function (c) {
        var s = SHORT[c];
        var o = splitOpts(r[s + '_norm']);
        if (!o.length) o = splitOpts(r[s]);
        if (o.length) H[c][r.date] = o;
      });
    });
    ctx.pending.forEach(function (p) {
      if (p.kind !== 'tip' || fold(p.player) !== pf) return;
      CATS.forEach(function (c) {
        var o = canonOpts(ctx, c, p[SHORT[c]]);
        if (o.length) H[c][p.date] = o; else delete H[c][p.date];
      });
    });
    return H;
  }
  function tipOf(ctx, player, date) { // {v,h,b, points, pending}
    var pf = fold(player);
    var p = ctx.pending.filter(function (x) { return x.kind === 'tip' && x.date === date && fold(x.player) === pf; })[0];
    if (p) return { v: p.v, h: p.h, b: p.b, points: null, pending: true };
    var r = ((ctx.tips && ctx.tips.rows) || []).filter(function (x) { return x.date === date && fold(x.player) === pf; })[0];
    return r ? { v: r.v, h: r.h, b: r.b, points: r.points, pending: false } : null;
  }
  function menuOf(ctx, date) { // {status, opts:{cat:[..]}, raw:{v,h,b}, pending}
    var p = ctx.pending.filter(function (x) { return x.kind === 'menu' && x.date === date; })[0];
    if (p) {
      return {
        status: p.free ? 'free' : 'served', pending: true, raw: { v: p.v, h: p.h, b: p.b },
        opts: p.free ? null : { vorspeise: canonOpts(ctx, 'vorspeise', p.v), hauptspeise: canonOpts(ctx, 'hauptspeise', p.h), beilage: canonOpts(ctx, 'beilage', p.b) }
      };
    }
    var r = ((ctx.menus && ctx.menus.rows) || []).filter(function (x) { return x.date === date; })[0];
    if (!r) return null;
    var opts = null;
    if (r.status === 'served') {
      opts = {};
      CATS.forEach(function (c) { var s = SHORT[c]; opts[c] = splitOpts(r[s + '_norm']).length ? splitOpts(r[s + '_norm']) : splitOpts(r[s]); });
    }
    return { status: r.status, pending: false, raw: { v: r.v, h: r.h, b: r.b }, opts: opts };
  }

  // ------------------------------------------------------------------ charts (Chart.js, lazy)
  var chartPromise = null, charts = [], mountQueue = [], cleanups = [];
  function loadChart() {
    if (window.Chart) return Promise.resolve(window.Chart);
    if (!chartPromise) {
      chartPromise = new Promise(function (resolve, reject) {
        var s = document.createElement('script');
        s.src = CHART_SRC;
        s.integrity = CHART_SRI;
        s.crossOrigin = 'anonymous';
        s.referrerPolicy = 'no-referrer';
        s.onload = function () { if (window.Chart) resolve(window.Chart); else reject(new Error('Chart.js')); };
        s.onerror = function () { chartPromise = null; s.remove(); reject(new Error('Chart.js')); };
        document.head.appendChild(s);
      });
    }
    return chartPromise;
  }
  function isDark() {
    var th = document.documentElement.getAttribute('data-theme');
    if (th === 'dark') return true;
    if (th === 'light') return false;
    return !!(window.matchMedia && matchMedia('(prefers-color-scheme: dark)').matches);
  }
  function themeColors() {
    var cs = getComputedStyle(document.documentElement);
    var v = function (n) { return cs.getPropertyValue(n).trim(); };
    return {
      dark: isDark(), series: isDark() ? PALETTE.dark : PALETTE.light,
      text: v('--text'), text2: v('--text-2'), muted: v('--muted'), grid: v('--grid'), axis: v('--axis'),
      surface: v('--surface'), accent: v('--accent'), neutral: v('--neutral-mark')
    };
  }
  function mount(fn) { mountQueue.push(fn); }
  function chartBox(height, label, build) {
    var canvas = h('canvas', { role: 'img', 'aria-label': label });
    var box = h('div', { class: 'chart-box', style: { height: height + 'px' } }, canvas);
    mount(function () {
      loadChart().then(function (Chart) {
        if (!canvas.isConnected) return;
        var col = themeColors();
        Chart.defaults.font.family = 'system-ui, -apple-system, "Segoe UI", Roboto, sans-serif';
        Chart.defaults.font.size = 12;
        Chart.defaults.color = col.text2;
        Chart.defaults.borderColor = col.grid;
        charts.push(new Chart(canvas, build(col)));
      }).catch(function () {
        box.replaceChildren(h('p', { class: 'muted small chart-missing' }, t('chart.unavailable')));
      });
    });
    return box;
  }
  function axisOpts(col, extra) {
    var o = { grid: { color: col.grid, drawTicks: false }, border: { color: col.axis }, ticks: { color: col.muted, padding: 6 } };
    if (extra) Object.keys(extra).forEach(function (k) { o[k] = extra[k]; });
    return o;
  }
  function tooltipOpts(col) {
    return {
      backgroundColor: col.dark ? '#2c2c2a' : '#ffffff', titleColor: col.text, bodyColor: col.text2,
      borderColor: col.axis, borderWidth: 1, padding: 10, cornerRadius: 8, boxPadding: 4, usePointStyle: true
    };
  }

  // ------------------------------------------------------------------ shell / router
  var ROUTES = [
    { id: 'heute', view: viewHeute },
    { id: 'woche', view: viewWoche },
    { id: 'statistik', view: viewStatistik },
    { id: 'rangliste', view: viewRangliste },
    { id: 'backtest', view: viewBacktest },
    { id: 'datenbank', view: viewDatenbank },
    { id: 'eingabe', view: viewEingabe }
  ];
  function currentRoute() {
    var id = (location.hash || '').replace(/^#\/?/, '').split(/[?/]/)[0];
    for (var i = 0; i < ROUTES.length; i++) if (ROUTES[i].id === id) return ROUTES[i];
    return ROUTES[0];
  }
  function renderTabbar() {
    var nav = document.getElementById('tabbar');
    var cur = currentRoute().id;
    nav.replaceChildren.apply(nav, ROUTES.map(function (r) {
      return h('a', { href: '#/' + r.id, class: 'tab' + (r.id === cur ? ' active' : ''), 'aria-current': r.id === cur ? 'page' : null },
        icon(r.id), h('span', { class: 'tab-label' }, t('tab.' + r.id)));
    }));
  }
  function renderChrome() {
    document.documentElement.lang = lang;
    var lb = document.getElementById('btn-lang');
    if (lb) {
      lb.setAttribute('aria-label', t('ui.lang'));
      Array.prototype.forEach.call(lb.querySelectorAll('[data-l]'), function (s) { s.classList.toggle('on', s.getAttribute('data-l') === lang); });
    }
    var rb = document.getElementById('btn-refresh');
    if (rb) { rb.setAttribute('aria-label', t('ui.refresh')); rb.title = t('ui.refresh'); }
    var tb = document.getElementById('btn-theme');
    if (tb) {
      var th = store.get('theme', 'auto');
      tb.setAttribute('aria-label', t('ui.theme') + ': ' + t('theme.' + th));
      tb.title = t('ui.theme') + ': ' + t('theme.' + th);
      tb.setAttribute('data-mode', th);
    }
    var bt = document.querySelector('.brand-text');
    if (bt) bt.textContent = t('app.title');
    renderTabbar();
  }
  var renderSeq = 0;
  function runCleanups() {
    cleanups.splice(0).forEach(function (f) { try { f(); } catch (e) { /* ignore */ } });
    charts.splice(0).forEach(function (c) { try { c.destroy(); } catch (e) { /* ignore */ } });
  }
  function render(keepScroll) {
    var r = currentRoute();
    var seq = ++renderSeq;
    var view = document.getElementById('view');
    var y = window.scrollY;
    runCleanups();
    mountQueue = [];
    renderChrome();
    document.getElementById('banner').replaceChildren();
    if (!view.firstChild || !keepScroll) view.replaceChildren(h('div', { class: 'card loading-card' }, h('div', { class: 'spinner', 'aria-hidden': 'true' }), h('p', null, t('ui.loading'))));
    Promise.resolve().then(function () { return r.view(); }).catch(function (e) {
      return h('div', null, notice('danger', t('ui.error'), h('div', { class: 'small mono' }, String((e && e.message) || e))),
        h('button', { class: 'btn', type: 'button', onclick: function () { reloadData(); } }, t('ui.retry')));
    }).then(function (node) {
      if (seq !== renderSeq) return;
      view.replaceChildren(node);
      document.title = t('tab.' + r.id) + ' · ' + t('app.title');
      var q = mountQueue; mountQueue = [];
      q.forEach(function (fn) { try { fn(); } catch (e) { /* ignore */ } });
      if (keepScroll) window.scrollTo(0, y);
    });
  }
  function rerender() { render(true); }
  function reloadData() { dataCache = {}; render(true); }

  // ------------------------------------------------------------------ shared view bits
  function lockedState() {
    return emptyState(t('pass.lockedTitle'), t('pass.lockedText'),
      h('button', { class: 'btn primary', type: 'button', onclick: function () { reloadData(); } }, t('pass.enter')));
  }
  function missingState(r, titleKey, textKey) {
    if (r && r.status === 'locked') return lockedState();
    var extra = r && r.status === 'error'
      ? h('p', { class: 'small mono' }, String((r.error && r.error.message) || r.error))
      : null;
    return emptyState(t(titleKey), t(textKey), [extra, h('button', { class: 'btn', type: 'button', onclick: reloadData }, t('ui.retry'))]);
  }
  function pendingBanner(ctx) {
    var n = ctx.pending.length;
    if (!n) return null;
    return notice('info', t('pending.banner', { n: n }));
  }
  function catBadge(c) { return h('span', { class: 'cat-badge cat-' + SHORT[c], title: catName(c) }, catShort(c)); }
  function copyText(text) {
    var fallback = function () {
      var ta = h('textarea', { class: 'offscreen', readonly: true });
      ta.value = text;
      document.body.appendChild(ta);
      ta.select();
      var ok = false;
      try { ok = document.execCommand('copy'); } catch (e) { ok = false; }
      ta.remove();
      return ok;
    };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      return navigator.clipboard.writeText(text).then(function () { return true; }, function () { return fallback(); });
    }
    return Promise.resolve(fallback());
  }
  function copyButton(text, label, cls) {
    var lbl = h('span', null, label);
    var btn = h('button', {
      type: 'button', class: 'btn ' + (cls || ''), 'data-copy': text,
      onclick: function () {
        copyText(text).then(function (ok) {
          if (ok) {
            lbl.textContent = t('today.copied');
            btn.classList.add('done');
            toast(t('today.copiedToast', { text: text }), 'ok');
            setTimeout(function () { lbl.textContent = label; btn.classList.remove('done'); }, 2200);
          } else {
            toast(t('today.copyFail'), 'danger');
          }
        });
      }
    }, icon('copy'), lbl);
    return btn;
  }
  function goPrefill(date, rec) {
    session.set('prefill', JSON.stringify({ date: date, v: rec.v, h: rec.h, b: rec.b }));
    location.hash = '#/eingabe';
  }

  // ================================================================== VIEW: Heute
  function viewHeute() {
    return Promise.all([load('today'), loadCtx()]).then(function (rs) {
      var T = rs[0], ctx = rs[1];
      if (T.status !== 'ok') return missingState(T, 'today.empty.title', 'today.empty.text');
      var d = T.data || {};
      var meta = ctx.meta || {};
      var todayR = romeTodayISO();
      var target = isISO(d.date) ? d.date : todayR;
      var rec = d.recommendation || {};
      var alts = d.alternatives || {};
      var out = h('div', { class: 'stack' });

      // ---- staleness / context notices
      var notes = h('div', { class: 'stack-sm' });
      if (d.season_over) notes.appendChild(notice('info', t('today.seasonOver')));
      if (target < todayR) notes.appendChild(notice('danger', t('stale.past', { date: fmtLong(target) })));
      else if (target > todayR || d.is_today === false) notes.appendChild(notice('info', t('today.notToday', { date: fmtLong(target) })));
      var gen = Date.parse(d.generated_at || '');
      if (isNum(gen)) {
        var ageH = (Date.now() - gen) / 36e5;
        if (ageH > 26) notes.appendChild(notice('warn', t('stale.generated', { ago: ageH > 48 ? t('ago.days', { n: Math.floor(ageH / 24) }) : t('ago.hours', { n: Math.floor(ageH) }) })));
      }
      var pb = pendingBanner(ctx);
      if (pb) notes.appendChild(pb);
      if (notes.childNodes.length) out.appendChild(notes);

      // ---- hero: date + countdown
      var dl = deadlineFor(target, meta.deadline || '12:00');
      var cdVal = h('div', { class: 'cd-value', id: 'countdown', 'aria-live': 'off' }, '––:––:––');
      var cdLabel = h('div', { class: 'cd-label' });
      var hero = h('section', { class: 'hero' },
        h('div', { class: 'hero-date' },
          h('div', { class: 'hero-kicker' }, target === todayR ? t('today.kicker') : t('today.kickerFor')),
          h('div', { class: 'hero-day' }, fmtLong(target))),
        h('div', { class: 'cd' }, cdVal, cdLabel));
      var tick = function () {
        var left = dl - Date.now();
        if (left <= 0) {
          cdVal.textContent = t('cd.over');
          hero.classList.add('over');
          hero.classList.remove('urgent');
          cdLabel.textContent = t('cd.overSub', { time: meta.deadline || '12:00' });
          return false;
        }
        var s = Math.floor(left / 1000);
        var days = Math.floor(s / 86400); s -= days * 86400;
        var hh = Math.floor(s / 3600); s -= hh * 3600;
        var mm = Math.floor(s / 60); s -= mm * 60;
        cdVal.textContent = (days ? t('cd.days', { n: days }) + ' ' : '') + pad(hh) + ':' + pad(mm) + ':' + pad(s);
        hero.classList.toggle('urgent', left < 30 * 60 * 1000);
        cdLabel.textContent = target === todayR ? t('cd.until', { time: meta.deadline || '12:00' })
          : t('cd.untilDay', { day: wdLong(weekdayOf(target)), time: meta.deadline || '12:00' });
        return true;
      };
      if (tick()) {
        var iv = setInterval(function () { if (!tick()) clearInterval(iv); }, 1000);
        cleanups.push(function () { clearInterval(iv); });
      }
      out.appendChild(hero);

      // ---- client-side R4 re-check (fresh tips/pending submissions)
      var hist = historyOf(ctx, ctx.me);
      var max = ctx.r4.max;
      var clientBlock = function (c, dish) {
        return ctx.r4.violations(c, dish, target, hist[c]).map(function (v) { return violationText(v, max); });
      };

      // ---- recommendation
      var recCard;
      if (rec && rec.vorspeise) {
        var issues = [];
        CATS.forEach(function (c) {
          var r = rec[c] || {};
          clientBlock(c, r.dish).forEach(function (txt) { issues.push(catName(c) + ': ' + r.dish + ' – ' + txt); });
        });
        var rows = CATS.map(function (c) {
          var r = rec[c] || {};
          return h('div', { class: 'rec-row' },
            catBadge(c),
            h('div', { class: 'rec-main' }, h('div', { class: 'rec-cat' }, catName(c)), h('div', { class: 'rec-dish' }, r.dish || '–')),
            h('div', { class: 'rec-p' }, h('span', { class: 'big-num' }, fmtPct(r.p)), h('span', { class: 'muted tiny' }, t('today.prob'))));
        });
        var copy = rec.copy_text || CATS.map(function (c) { return (rec[c] || {}).dish || '–'; }).join(' / ');
        recCard = h('section', { class: 'card rec' },
          h('div', { class: 'rec-head' }, h('h2', { class: 'card-title' }, t('today.rec')),
            chip(t('strategy.' + (rec.strategy || 'week_planner')), 'accent')),
          h('div', { class: 'rec-rows' }, rows),
          h('div', { class: 'rec-stats' },
            h('div', null, h('span', { class: 'k' }, t('today.ev')), h('span', { class: 'v' }, fmtNum(rec.ev, 2))),
            h('div', null, h('span', { class: 'k' }, t('today.pfull')), h('span', { class: 'v' }, fmtPct(rec.p_full, rec.p_full < 0.1 ? 1 : 0))),
            h('div', null, h('span', { class: 'k' }, t('today.model')), h('span', { class: 'v sm' }, t('model.' + (d.model || 'heuristic'))))),
          rec.valid === false ? notice('warn', t('today.invalid')) : null,
          issues.length ? notice('danger', t('today.recBlocked'), h('ul', { class: 'plain' }, issues.map(function (x) { return h('li', null, x); }))) : null,
          h('div', { class: 'btn-row' },
            copyButton(copy, t('today.copy'), 'primary big'),
            h('button', { type: 'button', class: 'btn big', onclick: function () { goPrefill(target, { v: (rec.vorspeise || {}).dish, h: (rec.hauptspeise || {}).dish, b: (rec.beilage || {}).dish }); } },
              icon('edit'), t('today.enter'))),
          h('p', { class: 'muted tiny copy-preview' }, copy));
        out.appendChild(recCard);
      } else {
        out.appendChild(emptyState(t('today.norec.title'), t('today.norec.text')));
      }

      // ---- fish / Lent
      if (d.fish || d.is_lent) {
        var f = d.fish || {};
        var lent = f.lent !== undefined ? f.lent : d.is_lent;
        out.appendChild(h('section', { class: 'card fish' + (lent ? ' lent' : '') },
          h('div', { class: 'fish-row' }, icon('fish', 'big'),
            h('div', null,
              h('div', { class: 'fish-title' }, lent ? t('fish.lentTitle') : t('fish.title')),
              h('p', { class: 'small' }, pick(f, 'note') || (lent ? t('fish.lentText') : t('fish.text'))),
              isNum(f.p_fish) ? h('p', { class: 'muted small' }, t('fish.p', { p: fmtPct(f.p_fish) })) : null))));
      }

      // ---- alternatives (top 5 + more)
      var pairs = d.pair_beilage_given_haupt || {};
      var altSec = h('section', { class: 'card' },
        h('h2', { class: 'card-title' }, t('today.alts')),
        h('p', { class: 'muted small' }, t('today.altsSub')));
      CATS.forEach(function (c) {
        var list = (alts[c] || []).slice().sort(function (a, b) { return (b.p || 0) - (a.p || 0); });
        if (!list.length) return;
        var maxP = Math.max.apply(null, list.map(function (a) { return a.p || 0; })) || 1;
        var ol = h('ol', { class: 'alt-list' });
        list.forEach(function (a, i) {
          var reasons = (a.reasons || []).map(function (r) { return typeof r === 'string' ? r : (r[lang] || r.de || ''); }).filter(Boolean);
          clientBlock(c, a.dish).forEach(function (txt) { if (reasons.indexOf(txt) < 0) reasons.push(txt); });
          var blocked = !!a.blocked || reasons.length > 0;
          var isRec = rec[c] && fold(rec[c].dish) === fold(a.dish);
          var pairTxt = null;
          if (c === 'hauptspeise' && pairs[a.dish]) {
            var pb2 = Object.keys(pairs[a.dish]).map(function (k) { return [k, pairs[a.dish][k]]; })
              .sort(function (x, y) { return y[1] - x[1]; }).slice(0, 3)
              .map(function (x) { return x[0] + ' ' + fmtPct(x[1]); }).join(' · ');
            pairTxt = h('div', { class: 'alt-pair small' }, '→ ' + catName('beilage') + ': ' + pb2);
          }
          var metaBits = [];
          if (a.last_served) metaBits.push(t('alt.last', { date: fmtDM(a.last_served) }) + (isNum(a.days_since) ? ' ' + t('alt.ago', { n: a.days_since }) : ''));
          if (isNum(a.n_total)) metaBits.push(t('alt.total', { n: a.n_total }));
          ol.appendChild(h('li', { class: 'alt' + (blocked ? ' blocked' : '') + (i >= 5 ? ' extra' : '') + (isRec ? ' is-rec' : '') },
            h('div', { class: 'alt-top' },
              h('span', { class: 'alt-dish' }, a.dish, isRec ? chip(t('alt.rec'), 'accent tiny-chip') : null),
              h('span', { class: 'alt-p' }, fmtPct(a.p))),
            bar((a.p || 0) / maxP, blocked ? 'striped' : null),
            metaBits.length ? h('div', { class: 'alt-meta muted small' }, metaBits.join(' · ')) : null,
            blocked ? h('div', { class: 'alt-block small' }, chip(t('alt.blocked'), 'danger'), ' ', reasons.join(' · ') || t('alt.blockedGeneric')) : null,
            pairTxt));
        });
        var block = h('div', { class: 'alt-cat collapsed' }, h('h3', { class: 'sub-title' }, catBadge(c), ' ', catName(c)), ol);
        if (list.length > 5) {
          var more = h('button', { type: 'button', class: 'link-btn' }, t('alt.more', { n: list.length - 5 }));
          more.addEventListener('click', function () {
            var col = block.classList.toggle('collapsed');
            more.textContent = col ? t('alt.more', { n: list.length - 5 }) : t('alt.less');
          });
          block.appendChild(more);
        }
        altSec.appendChild(block);
      });
      out.appendChild(altSec);

      // ---- greedy alternative
      var g = d.greedy;
      if (g && g.vorspeise) {
        var same = CATS.every(function (c) { return fold((g[c] || {}).dish) === fold((rec[c] || {}).dish); });
        var gcopy = g.copy_text || CATS.map(function (c) { return (g[c] || {}).dish; }).join(' / ');
        out.appendChild(card(t('today.greedy'), [
          h('p', { class: 'muted small' }, same ? t('today.greedySame') : t('today.greedySub')),
          same ? null : h('div', { class: 'mini-tip' }, CATS.map(function (c) {
            return h('div', { class: 'mini-row' }, catBadge(c), h('span', { class: 'mini-dish' }, (g[c] || {}).dish || '–'), h('span', { class: 'muted small' }, fmtPct((g[c] || {}).p)));
          })),
          same ? null : h('div', { class: 'row-between' }, h('span', { class: 'small' }, t('today.ev') + ': ', h('strong', null, fmtNum(g.ev, 2))), copyButton(gcopy, t('today.copyShort'), 'small'))
        ]));
      }

      // ---- week plan
      var wp = (d.week_plan || []).filter(function (x) { return x && x.date; });
      if (wp.length) {
        out.appendChild(card(t('today.plan'), [
          h('p', { class: 'muted small' }, t('today.planSub')),
          table([{ label: t('col.day') }, { label: t('col.tip') }, { label: t('col.ev'), num: true }], wp.map(function (x) {
            return {
              cls: x.date === target ? 'hl' : null,
              cells: [fmtWdDM(x.date), CATS.map(function (c) { return x[c] || '–'; }).join(' / '), fmtNum(x.ev, 2)]
            };
          }), { cls: 'compact' })
        ]));
      }

      // ---- my week (client data incl. pending)
      var mon = mondayOf(target);
      var weekDays = [0, 1, 2, 3, 4].map(function (i) { return addDays(mon, i); });
      var mine = weekDays.map(function (dd) { return { date: dd, tip: tipOf(ctx, ctx.me, dd) }; }).filter(function (x) { return x.tip; });
      if (!mine.length && d.my_week && d.my_week.length) {
        mine = d.my_week.map(function (x) { var tp = x.tip || {}; return { date: x.date, tip: { v: tp.vorspeise, h: tp.hauptspeise, b: tp.beilage, points: x.points } }; });
      }
      out.appendChild(card(t('today.myWeek', { name: ctx.me || t('ui.me') }), mine.length
        ? h('ul', { class: 'week-mini' }, mine.map(function (x) {
          return h('li', null, h('span', { class: 'wd' }, fmtWdDM(x.date)),
            h('span', { class: 'tipline' }, [x.tip.v, x.tip.h, x.tip.b].map(function (s) { return s || '–'; }).join(' / ')),
            h('span', { class: 'pts' }, x.tip.pending ? chip(t('pending.chip'), 'info') : (isNum(x.tip.points) ? t('pts', { n: fmtPts(x.tip.points) }) : '–')));
        }))
        : h('p', { class: 'muted' }, t('today.myWeekEmpty'))));

      var foot = h('p', { class: 'muted tiny center' }, t('ui.generated', { when: isNum(gen) ? new Date(gen).toLocaleString(locale(), { timeZone: TZ, day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' }) : '–' }));
      out.appendChild(foot);
      return out;
    });
  }

  // ================================================================== VIEW: Woche
  function viewWoche() {
    return Promise.all([load('week'), loadCtx()]).then(function (rs) {
      var W = rs[0], ctx = rs[1];
      if (ctx.locked || W.status === 'locked') return lockedState();
      var todayR = romeTodayISO();
      var w = okData(W);
      var curMon = weekdayOf(todayR) >= 5 ? addDays(mondayOf(todayR), 7) : mondayOf(todayR);
      var out = h('div', { class: 'stack' });
      var notes = h('div', { class: 'stack-sm' });
      var weekStart = curMon;
      if (w && isISO(w.week_start)) {
        if (w.week_start === curMon || w.week_start === mondayOf(todayR)) weekStart = w.week_start;
        else notes.appendChild(notice('warn', t('week.stale', { date: fmtDMY(w.week_start) })));
      } else {
        notes.appendChild(notice('info', t('week.noJson')));
      }
      var pb = pendingBanner(ctx);
      if (pb) notes.appendChild(pb);
      if (notes.childNodes.length) out.appendChild(notes);
      var useJson = w && w.week_start === weekStart;
      var jsonDays = {};
      if (useJson) (w.days || []).forEach(function (x) { jsonDays[x.date] = x; });
      var days = [0, 1, 2, 3, 4].map(function (i) { return addDays(weekStart, i); });
      var wk = isoWeek(weekStart);
      out.appendChild(h('div', { class: 'page-head' },
        h('h1', null, t('week.title', { n: wk[1] })),
        h('p', { class: 'muted' }, fmtDM(days[0]) + ' – ' + fmtDMY(days[4]))));

      var sum = 0, nPts = 0;
      var list = h('div', { class: 'days' });
      days.forEach(function (dd) {
        var jd = jsonDays[dd] || {};
        var m = menuOf(ctx, dd);
        var status = (m && m.status) || jd.status || (ctx.r4.free.has(dd) ? 'free' : 'pending');
        var menu = m && m.opts ? m.opts : (jd.menu || null);
        var tip = tipOf(ctx, ctx.me, dd);
        if (!tip && jd.my_tip) tip = { v: jd.my_tip.vorspeise, h: jd.my_tip.hauptspeise, b: jd.my_tip.beilage, points: jd.my_points };
        if (tip && isNum(tip.points)) { sum += tip.points; nPts++; }
        var isToday = dd === todayR;
        var el = h('article', { class: 'day' + (isToday ? ' today' : '') + (status === 'free' ? ' free' : '') + (dd < todayR ? ' past' : '') },
          h('header', { class: 'day-head' },
            h('span', { class: 'day-name' }, wdLong(weekdayOf(dd)), h('span', { class: 'muted' }, ' ' + fmtDM(dd))),
            h('span', { class: 'chips' }, isToday ? chip(t('week.today'), 'accent') : null,
              m && m.pending ? chip(t('pending.chip'), 'info') : null,
              chip(statusName(status), 'st-' + status))));
        if (status === 'free') {
          el.appendChild(h('p', { class: 'muted small' }, t('week.freeDay')));
        } else if (menu && CATS.some(function (c) { return (menu[c] || []).length; })) {
          el.appendChild(h('div', { class: 'menu-lines' }, CATS.map(function (c) {
            var opts = menu[c] || [];
            var tipOpts = tip ? splitOpts(tip[SHORT[c]]) : [];
            var hit = tipOpts.some(function (o) { return opts.some(function (x) { return fold(x) === fold(o); }); });
            return h('div', { class: 'menu-line' }, catBadge(c), h('span', { class: 'menu-dish' }, opts.length ? opts.join(' / ') : '–'),
              tip && opts.length ? h('span', { class: 'hit ' + (hit ? 'yes' : 'no'), title: hit ? t('week.hit') : t('week.miss') }, hit ? '✓' : '·') : null);
          })));
        } else if (jd.forecast) {
          el.appendChild(h('div', { class: 'forecast' }, h('div', { class: 'muted tiny upper' }, t('week.forecast')),
            CATS.map(function (c) {
              var fc = (jd.forecast[c] || []).slice(0, 3);
              return h('div', { class: 'menu-line' }, catBadge(c), h('span', { class: 'menu-dish small' },
                fc.length ? fc.map(function (x) { return x.dish + ' ' + fmtPct(x.p); }).join(' · ') : '–'));
            })));
        } else {
          el.appendChild(h('p', { class: 'muted small' }, t('week.noMenu')));
        }
        if (status !== 'free') {
          el.appendChild(h('div', { class: 'mytip' },
            h('span', { class: 'k' }, t('week.myTip')),
            h('span', { class: 'tipline' }, tip ? [tip.v, tip.h, tip.b].map(function (s) { return s || '–'; }).join(' / ') : t('week.noTip')),
            tip ? h('span', { class: 'pts' }, tip.pending ? chip(t('pending.chip'), 'info') : (isNum(tip.points) ? t('pts', { n: fmtPts(tip.points) }) : '')) : null));
        }
        list.appendChild(el);
      });
      out.appendChild(list);
      if (nPts) out.appendChild(h('p', { class: 'center' }, t('week.sum', { n: fmtPts(sum) })));

      // ---- still tippable (R4), recomputed client-side
      var hist = historyOf(ctx, ctx.me);
      var max = ctx.r4.max;
      var sec = card(t('week.tippable'), null, { sub: t('week.tippableSub', { n: max }) });
      CATS.forEach(function (c) {
        var names = {};
        var add = function (n) { var k = fold(n); if (k && !names[k]) names[k] = n; };
        days.forEach(function (dd) { (hist[c][dd] || []).forEach(add); });
        if (useJson && w.tippable && w.tippable[c]) w.tippable[c].forEach(function (x) { add(x.dish); });
        var entries = Object.keys(names).map(function (k) {
          var dish = names[k];
          var used = days.filter(function (dd) { return (hist[c][dd] || []).some(function (o) { return fold(o) === k; }); });
          var blockedDays = days.filter(function (dd) {
            return dd >= todayR && ctx.r4.isWorkday(dd) && used.indexOf(dd) < 0 && ctx.r4.violations(c, dish, dd, hist[c]).length > 0;
          });
          return { dish: dish, used: used, remaining: Math.max(0, max - used.length), blocked: blockedDays };
        }).filter(function (e) { return e.used.length; })
          .sort(function (a, b) { return a.remaining - b.remaining || (a.used[0] < b.used[0] ? -1 : 1); });
        var blockEl = h('div', { class: 'r4-cat' }, h('h3', { class: 'sub-title' }, catBadge(c), ' ', catName(c)));
        if (!entries.length) {
          blockEl.appendChild(h('p', { class: 'muted small' }, t('week.allFree')));
        } else {
          blockEl.appendChild(h('ul', { class: 'r4-list' }, entries.map(function (e) {
            return h('li', { class: 'r4-item' + (e.remaining === 0 ? ' full' : '') },
              h('div', { class: 'r4-top' }, h('span', { class: 'r4-dish' }, e.dish),
                chip(e.remaining === 0 ? t('week.none') : t('week.left', { n: e.remaining }), e.remaining === 0 ? 'danger' : 'ok')),
              h('div', { class: 'r4-days', 'aria-label': t('week.dayStates') }, days.map(function (dd) {
                var st = e.used.indexOf(dd) >= 0 ? 'used' : (e.blocked.indexOf(dd) >= 0 ? 'blocked' : (dd < todayR || !ctx.r4.isWorkday(dd) ? 'past' : 'free'));
                return h('span', { class: 'dchip ' + st, title: t('week.state.' + st) }, wdShort(weekdayOf(dd)));
              })));
          })));
        }
        sec.appendChild(blockEl);
      });
      sec.appendChild(h('div', { class: 'legend small' },
        h('span', { class: 'dchip used' }, '•'), ' ' + t('week.state.used') + '  ',
        h('span', { class: 'dchip blocked' }, '×'), ' ' + t('week.state.blocked') + '  ',
        h('span', { class: 'dchip free' }, '○'), ' ' + t('week.state.free')));
      out.appendChild(sec);
      return out;
    });
  }

  // ================================================================== VIEW: Statistik
  var statState = { cat: store.get('stat.cat', 'vorspeise'), year: 'all', heat: 'share', showAllFreq: false, showAllRep: false };
  function heatColor(col, v, maxV, mode) {
    // sequential (one hue) or diverging (blue <-> red around lift 1)
    if (!isNum(v)) return { bg: 'transparent', fg: col.muted };
    var rgb, a;
    if (mode === 'lift') {
      if (v <= 0) { rgb = col.dark ? [230, 103, 103] : [227, 73, 72]; a = 0.9; }
      else {
        var l = Math.log(v) / Math.log(2);
        a = Math.min(1, Math.abs(l) / 2) * 0.9;
        rgb = l >= 0 ? (col.dark ? [57, 135, 229] : [42, 120, 214]) : (col.dark ? [230, 103, 103] : [227, 73, 72]);
      }
    } else {
      rgb = col.dark ? [57, 135, 229] : [42, 120, 214];
      a = maxV > 0 ? Math.min(1, v / maxV) * 0.92 : 0;
    }
    return { bg: 'rgba(' + rgb.join(',') + ',' + a.toFixed(3) + ')', fg: a > 0.5 ? '#ffffff' : col.text };
  }
  function heatmap(rowsLabels, colLabels, matrix, opts) {
    opts = opts || {};
    var col = themeColors();
    var maxV = 0;
    matrix.forEach(function (r) { (r || []).forEach(function (v) { if (isNum(v) && v > maxV) maxV = v; }); });
    var readout = h('div', { class: 'heat-readout small muted', 'aria-live': 'polite' }, t('stat.heatTap'));
    var grid = h('div', { class: 'heat' + (opts.compact ? ' compact' : ''), role: 'table' });
    grid.style.gridTemplateColumns = 'minmax(84px, ' + (opts.compact ? '1.3fr' : '1.6fr') + ') repeat(' + colLabels.length + ', minmax(0, 1fr))';
    grid.appendChild(h('div', { class: 'heat-corner' }));
    colLabels.forEach(function (c) { grid.appendChild(h('div', { class: 'heat-col' }, c)); });
    rowsLabels.forEach(function (name, i) {
      grid.appendChild(h('div', { class: 'heat-row', title: name }, name));
      colLabels.forEach(function (cl, j) {
        var v = (matrix[i] || [])[j];
        var c = heatColor(col, v, maxV, opts.mode);
        var label = opts.fmt ? opts.fmt(v, i, j) : fmtPct(v);
        var desc = name + ' · ' + cl + ': ' + label;
        var cell = h('button', {
          type: 'button', class: 'heat-cell', title: desc, 'aria-label': desc,
          style: { backgroundColor: c.bg, color: c.fg },
          onclick: function () { readout.textContent = desc; }
        }, opts.showValues ? (opts.cellFmt ? opts.cellFmt(v) : label) : '');
        grid.appendChild(cell);
      });
    });
    return h('div', null, grid, readout);
  }
  function viewStatistik() {
    return load('stats').then(function (S) {
      if (S.status !== 'ok') return missingState(S, 'stats.empty.title', 'stats.empty.text');
      var s = S.data || {};
      var st = statState;
      if (CATS.indexOf(st.cat) < 0) st.cat = 'vorspeise';
      var c = st.cat;
      var years = (s.years || []).map(String);
      if (st.year !== 'all' && years.indexOf(String(st.year)) < 0) st.year = 'all';
      var out = h('div', { class: 'stack' });
      out.appendChild(h('div', { class: 'page-head' }, h('h1', null, t('stat.title')),
        h('p', { class: 'muted' }, t('stat.sub', { n: s.n_menus || 0, years: years.join(', ') }))));

      var controls = h('div', { class: 'controls card sticky-controls' },
        segmented(CATS.map(function (x) { return { value: x, label: catName(x) }; }), c, function (v) { st.cat = v; store.set('stat.cat', v); rerender(); }, t('ui.category')),
        h('label', { class: 'inline-field' }, h('span', { class: 'small muted' }, t('ui.year')),
          selectEl([{ value: 'all', label: t('ui.allYears') }].concat(years.map(function (y) { return { value: y, label: y }; })), st.year,
            function (v) { st.year = v; rerender(); }, t('ui.year'))));
      out.appendChild(controls);

      var jump = h('div', { class: 'jump' });
      var sections = [];
      var addSec = function (id, title, node) {
        sections.push([id, title]);
        node.id = 'sec-' + id;
        out.appendChild(node);
      };
      out.appendChild(jump);

      // ---- frequencies
      var freq = ((s.frequencies || {})[c] || []).map(function (f) {
        var n = st.year === 'all' ? f.total : ((f.by_year || {})[st.year] || 0);
        return { dish: f.dish, n: n, f: f };
      }).filter(function (x) { return x.n > 0; }).sort(function (a, b) { return b.n - a.n || (a.dish < b.dish ? -1 : 1); });
      var totalN = freq.reduce(function (a, x) { return a + x.n; }, 0);
      var topF = freq.slice(0, 20);
      var freqNodes = [];
      if (topF.length) {
        freqNodes.push(chartBox(Math.max(160, topF.length * 24 + 40), t('stat.freq'), function (col) {
          return {
            type: 'bar',
            data: { labels: topF.map(function (x) { return x.dish; }), datasets: [{ label: t('stat.count'), data: topF.map(function (x) { return x.n; }), backgroundColor: col.series[0], borderRadius: 4, borderSkipped: 'start', barPercentage: 0.78, categoryPercentage: 0.9 }] },
            options: {
              indexAxis: 'y', responsive: true, maintainAspectRatio: false, animation: false,
              plugins: { legend: { display: false }, tooltip: Object.assign(tooltipOpts(col), { callbacks: { label: function (ctx2) { return ' ' + ctx2.raw + '× · ' + fmtPct(ctx2.raw / (totalN || 1), 1); } } }) },
              scales: { x: axisOpts(col, { beginAtZero: true, ticks: { color: col.muted, precision: 0 } }), y: axisOpts(col, { grid: { display: false }, ticks: { color: col.text2, autoSkip: false, font: { size: 11 } } }) }
            }
          };
        }));
      } else {
        freqNodes.push(h('p', { class: 'muted' }, t('ui.noData')));
      }
      var freqRows = (st.showAllFreq ? freq : freq.slice(0, 10)).map(function (x) {
        return [x.dish, String(x.n), fmtPct(x.n / (totalN || 1), 1), fmtDM(x.f.first_served) + (x.f.first_served ? '.' + x.f.first_served.slice(2, 4) : ''), fmtDM(x.f.last_served) + (x.f.last_served ? '.' + x.f.last_served.slice(2, 4) : '')];
      });
      freqNodes.push(table([{ label: t('col.dish') }, { label: 'n', num: true }, { label: t('col.share'), num: true }, { label: t('col.first'), num: true }, { label: t('col.last'), num: true }], freqRows, { cls: 'compact' }));
      if (freq.length > 10) {
        freqNodes.push(h('button', { type: 'button', class: 'link-btn', onclick: function () { st.showAllFreq = !st.showAllFreq; rerender(); } },
          st.showAllFreq ? t('alt.less') : t('stat.showAll', { n: freq.length })));
      }
      addSec('freq', t('stat.freq'), card(t('stat.freq') + ' – ' + catName(c), freqNodes, { sub: st.year === 'all' ? t('stat.freqSubAll') : t('stat.freqSubYear', { y: st.year }) }));

      // ---- weekday heatmap
      var wdd = (s.weekday || {})[c];
      if (wdd && wdd.dishes && wdd.dishes.length) {
        var mode = st.heat;
        var mat = mode === 'lift' ? wdd.lift : wdd.matrix;
        addSec('weekday', t('stat.weekday'), card(t('stat.weekday'), [
          segmented([{ value: 'share', label: t('stat.heatShare') }, { value: 'lift', label: t('stat.heatLift') }], mode, function (v) { st.heat = v; rerender(); }),
          h('p', { class: 'muted small' }, mode === 'lift' ? t('stat.heatLiftSub') : t('stat.heatShareSub')),
          heatmap(wdd.dishes, [0, 1, 2, 3, 4].map(wdShort), mat || [], {
            mode: mode, showValues: true,
            fmt: function (v, i, j) { var cnt = ((wdd.counts || [])[i] || [])[j]; return (mode === 'lift' ? (isNum(v) ? fmtNum(v, 2) + '×' : '–') : fmtPct(v)) + (isNum(cnt) ? ' (' + cnt + '×)' : ''); },
            cellFmt: function (v) { return mode === 'lift' ? (isNum(v) ? fmtNum(v, 1) : '') : (isNum(v) && v > 0 ? Math.round(v * 100) : ''); }
          })
        ]));
      }

      // ---- repeat intervals
      var rep = ((s.repeat_intervals || {})[c] || []).slice().sort(function (a, b) { return (b.n || 0) - (a.n || 0); });
      if (rep.length) {
        var repRows = (st.showAllRep ? rep : rep.slice(0, 12)).map(function (r) {
          return [r.dish, String(r.n), fmtNum(r.mean, 1), fmtNum(r.median, 0), String(r.min == null ? '–' : r.min), String(r.max == null ? '–' : r.max), String(r.same_week_repeats || 0)];
        });
        addSec('repeat', t('stat.repeat'), card(t('stat.repeat'), [
          table([{ label: t('col.dish') }, { label: 'n', num: true }, { label: 'Ø', num: true }, { label: t('col.median'), num: true }, { label: 'min', num: true }, { label: 'max', num: true }, { label: t('col.sameWeek'), num: true }], repRows, { cls: 'compact' }),
          rep.length > 12 ? h('button', { type: 'button', class: 'link-btn', onclick: function () { st.showAllRep = !st.showAllRep; rerender(); } }, st.showAllRep ? t('alt.less') : t('stat.showAll', { n: rep.length })) : null
        ], { sub: t('stat.repeatSub') }));
      }

      // ---- refractory curve
      var rf = (s.refractory || {})[c];
      if (rf && rf.lags && rf.lags.length) {
        addSec('refr', t('stat.refr'), card(t('stat.refr'), [chartBox(240, t('stat.refr'), function (col) {
          return {
            type: 'line',
            data: {
              labels: rf.lags, datasets: [
                { label: t('stat.refrRate'), data: rf.same_rate, borderColor: col.series[0], backgroundColor: col.series[0], borderWidth: 2, pointRadius: 2.5, pointHoverRadius: 5, tension: 0.25 },
                { label: t('stat.baseline'), data: rf.lags.map(function () { return rf.baseline; }), borderColor: col.muted, borderWidth: 1.5, borderDash: [5, 4], pointRadius: 0, pointHoverRadius: 0 }
              ]
            },
            options: {
              responsive: true, maintainAspectRatio: false, animation: false, interaction: { mode: 'index', intersect: false },
              plugins: { legend: { labels: { color: col.text2, boxWidth: 14, usePointStyle: true } }, tooltip: Object.assign(tooltipOpts(col), { callbacks: { title: function (it) { return t('stat.lagTitle', { n: it[0].label }); }, label: function (x) { return ' ' + x.dataset.label + ': ' + fmtPct(x.raw, 1); } } }) },
              scales: { x: axisOpts(col, { title: { display: true, text: t('stat.lagAxis'), color: col.muted } }), y: axisOpts(col, { beginAtZero: true, ticks: { color: col.muted, callback: function (v) { return fmtPct(v); } } }) }
            }
          };
        })], { sub: t('stat.refrSub') }));
      }

      // ---- H -> B pairs
      var phb = (s.pairs_hb || []).slice(0, 15);
      if (phb.length) {
        addSec('pairs', t('stat.pairs'), card(t('stat.pairs'), h('ul', { class: 'pair-list' }, phb.map(function (p) {
          var top = (p.beilagen || []).slice(0, 4);
          return h('li', null,
            h('div', { class: 'pair-head' }, h('strong', null, p.hauptspeise), h('span', { class: 'muted small' }, ' ' + p.n + '×')),
            h('div', { class: 'pair-bars' }, top.map(function (b) {
              return h('div', { class: 'pair-b' }, h('span', { class: 'pair-name small' }, b.dish), bar(b.p), h('span', { class: 'small num' }, fmtPct(b.p)));
            })));
        })), { sub: t('stat.pairsSub') }));
      }
      var pvh = (s.pairs_vh || []).slice(0, 12);
      if (pvh.length) {
        out.appendChild(card(t('stat.pairsVH'), table([{ label: catName('vorspeise') }, { label: catName('hauptspeise') }, { label: 'n', num: true }, { label: 'Lift', num: true }],
          pvh.map(function (p) { return [p.vorspeise, p.hauptspeise, String(p.n), isNum(p.lift) ? fmtNum(p.lift, 1) + '×' : '–']; }), { cls: 'compact' }), { sub: t('stat.pairsVHSub') }));
      }

      // ---- trends by year
      var tr = s.trends || {};
      var sby = ((tr.share_by_year || {})[c] || []).slice(0, 15);
      if (sby.length) {
        var col0 = themeColors();
        var maxS = 0;
        sby.forEach(function (x) { years.forEach(function (y) { var v = (x.by_year || {})[y]; if (isNum(v) && v > maxS) maxS = v; }); });
        var trNodes = [table([{ label: t('col.dish') }].concat(years.map(function (y) { return { label: y, num: true }; })),
          sby.map(function (x) {
            return [x.dish].concat(years.map(function (y) {
              var v = (x.by_year || {})[y];
              var cc = heatColor(col0, v, maxS, 'share');
              return h('span', { class: 'shade', style: { backgroundColor: cc.bg, color: cc.fg } }, isNum(v) ? fmtPct(v, 1) : '–');
            }));
          }), { cls: 'compact' })];
        var nw = (tr.new_2026 || {})[c] || [], gone = (tr.gone_2026 || {})[c] || [];
        if (nw.length) trNodes.push(h('div', { class: 'chip-group' }, h('div', { class: 'small strong' }, t('stat.new')), h('div', { class: 'chips wrap' }, nw.map(function (x) { return chip(x, 'ok'); }))));
        if (gone.length) trNodes.push(h('div', { class: 'chip-group' }, h('div', { class: 'small strong' }, t('stat.gone')), h('div', { class: 'chips wrap' }, gone.map(function (x) { return chip(x, 'muted-chip'); }))));
        addSec('trends', t('stat.trends'), card(t('stat.trends'), trNodes, { sub: t('stat.trendsSub') }));
      }

      // ---- seasonality
      var se = s.seasonality || {};
      var bm = (se.by_month || {})[c];
      var seNodes = [];
      if (bm && bm.dishes && bm.dishes.length) {
        seNodes.push(h('h3', { class: 'sub-title' }, t('stat.byMonth')));
        seNodes.push(heatmap(bm.dishes, t('months.short').split(','), bm.matrix || [], { mode: 'share', compact: true, fmt: function (v) { return fmtPct(v); } }));
      }
      var lent = ((se.lent || {})[c] || []).slice().sort(function (a, b) { return (b.p_lent || 0) - (a.p_lent || 0); }).slice(0, 10);
      if (lent.length) {
        seNodes.push(h('h3', { class: 'sub-title' }, t('stat.lent')));
        seNodes.push(table([{ label: t('col.dish') }, { label: t('col.inLent'), num: true }, { label: t('col.otherwise'), num: true }, { label: 'Lift', num: true }],
          lent.map(function (x) { return [x.dish, fmtPct(x.p_lent, 1), fmtPct(x.p_other, 1), isNum(x.lift) ? fmtNum(x.lift, 1) + '×' : (x.p_lent > 0 ? '∞' : '–')]; }), { cls: 'compact' }));
      }
      var sw = ((se.summer_winter || {})[c] || []).slice().sort(function (a, b) {
        return Math.abs((b.p_summer || 0) - (b.p_winter || 0)) - Math.abs((a.p_summer || 0) - (a.p_winter || 0));
      }).slice(0, 10);
      if (sw.length) {
        seNodes.push(h('h3', { class: 'sub-title' }, t('stat.sw')));
        seNodes.push(table([{ label: t('col.dish') }, { label: t('col.summer'), num: true }, { label: t('col.winter'), num: true }],
          sw.map(function (x) { return [x.dish, fmtPct(x.p_summer, 1), fmtPct(x.p_winter, 1)]; }), { cls: 'compact' }));
      }
      if (seNodes.length) addSec('season', t('stat.season'), card(t('stat.season'), seNodes, { sub: t('stat.seasonSub') }));

      jump.replaceChildren.apply(jump, sections.map(function (x) {
        return h('button', { type: 'button', class: 'jump-btn', onclick: function () { var el = document.getElementById('sec-' + x[0]); if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' }); } }, x[1]);
      }));
      out.appendChild(h('p', { class: 'muted tiny center' }, t('ui.generated', { when: s.generated_at ? new Date(s.generated_at).toLocaleString(locale(), { timeZone: TZ }) : '–' })));
      return out;
    });
  }

  // ================================================================== VIEW: Rangliste
  var rankState = { year: null };
  function playerColors(meta, names, col) {
    var me = (meta && meta.me) || '';
    var order = [];
    if (me) order.push(me);
    ((meta && meta.players) || []).forEach(function (p) { if (order.indexOf(p) < 0) order.push(p); });
    names.forEach(function (p) { if (p !== 'Modell' && order.indexOf(p) < 0) order.push(p); });
    var map = {};
    order.forEach(function (p, i) { map[p] = col.series[i % col.series.length]; });
    map.Modell = col.text2;
    return map;
  }
  function viewRangliste() {
    return Promise.all([load('leaderboard'), load('meta'), load('stats')]).then(function (rs) {
      var L = rs[0], meta = okData(rs[1]) || {}, stats = okData(rs[2]);
      if (L.status !== 'ok') return missingState(L, 'rank.empty.title', 'rank.empty.text');
      var lb = L.data || {};
      var years = Object.keys(lb.years || {}).sort().reverse();
      if (!years.length) return emptyState(t('rank.empty.title'), t('rank.empty.text'));
      if (!rankState.year || years.indexOf(rankState.year) < 0) rankState.year = years[0];
      var y = rankState.year;
      var Y = lb.years[y] || {};
      var series = Y.series || {};
      var names = Object.keys(series);
      var me = meta.me || '';
      var out = h('div', { class: 'stack' });
      out.appendChild(h('div', { class: 'page-head' }, h('h1', null, t('rank.title')), h('p', { class: 'muted' }, t('rank.sub', { model: t('model.' + (lb.model_name || 'heuristic')) }))));
      out.appendChild(h('div', { class: 'controls card' }, segmented(years.map(function (x) { return { value: x, label: x }; }), y, function (v) { rankState.year = v; rerender(); }, t('ui.year'))));

      var dates = Y.dates || [];
      if (dates.length && names.length) {
        out.appendChild(card(t('rank.chart'), chartBox(300, t('rank.chart'), function (col) {
          var cmap = playerColors(meta, names, col);
          var ordered = names.slice().sort(function (a, b) { return (a === 'Modell') - (b === 'Modell') || ((Y.totals || {})[b] || 0) - ((Y.totals || {})[a] || 0); });
          return {
            type: 'line',
            data: {
              labels: dates.map(fmtDM),
              datasets: ordered.map(function (p) {
                var isModel = p === 'Modell';
                return {
                  label: isModel ? t('rank.model') : p, data: series[p], borderColor: cmap[p], backgroundColor: cmap[p],
                  borderWidth: p === me ? 3 : 2, borderDash: isModel ? [6, 4] : undefined, pointRadius: 0, pointHoverRadius: 4, tension: 0.15, spanGaps: true
                };
              })
            },
            options: {
              responsive: true, maintainAspectRatio: false, animation: false, interaction: { mode: 'index', intersect: false },
              plugins: {
                legend: { position: 'bottom', labels: { color: col.text2, boxWidth: 14, boxHeight: 3, padding: 12 } },
                tooltip: Object.assign(tooltipOpts(col), { itemSort: function (a, b) { return b.raw - a.raw; }, callbacks: { label: function (x) { return ' ' + x.dataset.label + ': ' + fmtPts(x.raw); } } })
              },
              scales: { x: axisOpts(col, { ticks: { color: col.muted, maxRotation: 0, autoSkip: true, maxTicksLimit: 8 } }), y: axisOpts(col, { beginAtZero: true, ticks: { color: col.muted } }) }
            }
          };
        }), { sub: t('rank.chartSub') }));
      }

      // totals
      var totals = Y.totals || {};
      var tnames = Object.keys(totals).sort(function (a, b) { return totals[b] - totals[a]; });
      var best = tnames.filter(function (n) { return n !== 'Modell'; })[0];
      var pstats = {};
      ((stats && stats.players) || []).forEach(function (p) { if (String(p.year) === y) pstats[p.player] = p; });
      var colNow = themeColors();
      var cmap2 = playerColors(meta, tnames, colNow);
      var rank = 0;
      var trows = tnames.map(function (n) {
        var isModel = n === 'Modell';
        if (!isModel) rank++;
        var ps = pstats[n] || {};
        return {
          cls: (isModel ? 'model-row' : '') + (n === me ? ' me-row' : ''),
          cells: [isModel ? '–' : String(rank),
            h('span', { class: 'who' }, h('span', { class: 'dot' + (isModel ? ' dashed' : ''), style: { backgroundColor: cmap2[n] } }), isModel ? t('rank.model') : n),
            fmtPts(totals[n]),
            best && n !== best ? (totals[n] - totals[best] > 0 ? '+' : '') + fmtPts(totals[n] - totals[best]) : '–',
            isNum(ps.ppd) ? fmtNum(ps.ppd, 2) : (series[n] && dates.length ? fmtNum(totals[n] / dates.length, 2) : '–')]
        };
      });
      out.appendChild(card(t('rank.totals', { y: y }), table([{ label: '#' }, { label: t('col.player') }, { label: t('col.points'), num: true }, { label: t('col.diff'), num: true }, { label: t('col.ppd'), num: true }], trows)));

      // player stats from stats.json
      var plist = Object.keys(pstats).map(function (k) { return pstats[k]; }).sort(function (a, b) { return (b.ppd || 0) - (a.ppd || 0); });
      if (plist.length) {
        out.appendChild(card(t('rank.players'), h('div', { class: 'player-grid' }, plist.map(function (p) {
          return h('article', { class: 'player-card' + (p.player === me ? ' me' : '') },
            h('header', null, h('span', { class: 'dot', style: { backgroundColor: cmap2[p.player] || colNow.muted } }), h('strong', null, p.player)),
            h('div', { class: 'kpis' },
              h('div', null, h('span', { class: 'k' }, t('col.ppd')), h('span', { class: 'v' }, fmtNum(p.ppd, 2))),
              h('div', null, h('span', { class: 'k' }, t('col.points')), h('span', { class: 'v' }, fmtPts(p.points))),
              h('div', null, h('span', { class: 'k' }, t('rank.allWrong')), h('span', { class: 'v' }, fmtPct(p.all_wrong_rate))),
              h('div', null, h('span', { class: 'k' }, t('rank.r4v')), h('span', { class: 'v' }, String(p.r4_violations == null ? '–' : p.r4_violations)))),
            h('div', { class: 'acc' }, CATS.map(function (c) {
              var a = (p.acc || {})[c];
              return h('div', { class: 'acc-row' }, catBadge(c), bar(a), h('span', { class: 'small num' }, fmtPct(a)));
            })),
            p.fav ? h('details', { class: 'fav' }, h('summary', { class: 'small' }, t('rank.fav')),
              CATS.map(function (c) {
                return h('p', { class: 'small' }, h('strong', null, catShort(c) + ': '), ((p.fav[c] || []).slice(0, 3).map(function (f) { return f.dish + ' ' + f.n + '×'; }).join(', ') || '–'));
              })) : null,
            pick(p, 'strategy_note') ? h('p', { class: 'small muted' }, pick(p, 'strategy_note')) : null);
        })), { sub: t('rank.playersSub') }));
      }
      return out;
    });
  }

  // ================================================================== VIEW: Backtest
  var btState = { year: null, model: null };
  function viewBacktest() {
    return Promise.all([load('backtest'), load('meta')]).then(function (rs) {
      var B = rs[0], meta = okData(rs[1]) || {};
      if (B.status !== 'ok') return missingState(B, 'bt.empty.title', 'bt.empty.text');
      var b = B.data || {};
      var models = b.models || [];
      var label = function (m) { return (m && (m['label_' + lang] || m.label_de || m.name)) || '–'; };
      var yearsSet = {};
      models.forEach(function (m) { Object.keys(m.years || {}).forEach(function (y) { yearsSet[y] = 1; }); });
      Object.keys(b.players || {}).forEach(function (y) { yearsSet[y] = 1; });
      var years = Object.keys(yearsSet).sort().reverse();
      if (!btState.year || years.indexOf(btState.year) < 0) btState.year = years[0];
      var y = btState.year;
      var out = h('div', { class: 'stack' });
      out.appendChild(h('div', { class: 'page-head' }, h('h1', null, t('bt.title')), h('p', { class: 'muted' }, t('bt.sub'))));
      var summary = b['summary_' + lang] || b.summary_de;
      var bestM = models.filter(function (m) { return m.name === b.best_model; })[0];
      out.appendChild(card(t('bt.summary'), [
        summary ? h('p', { class: 'lead' }, summary) : null,
        h('div', { class: 'chips wrap' },
          bestM ? chip(t('bt.best', { m: label(bestM) }), 'accent') : null,
          b.split ? Object.keys(b.split).map(function (k) { return chip(t('bt.split.' + k) + ': ' + String(b.split[k]).replace('..', ' – '), 'muted-chip'); }) : null)
      ]));
      if (years.length) {
        out.appendChild(h('div', { class: 'controls card' }, segmented(years.map(function (x) { return { value: x, label: x }; }), y, function (v) { btState.year = v; rerender(); }, t('ui.year'))));
      }
      // model vs players
      var rows = [];
      models.forEach(function (m) {
        var r = (m.years || {})[y];
        if (r) rows.push({ name: label(m), isModel: true, best: m.name === b.best_model, d: r });
      });
      var pl = (b.players || {})[y] || {};
      Object.keys(pl).forEach(function (p) { rows.push({ name: p, isModel: false, me: p === meta.me, d: pl[p] }); });
      rows.sort(function (a, c2) { return (c2.d.ppd || 0) - (a.d.ppd || 0); });
      if (rows.length) {
        out.appendChild(card(t('bt.compare', { y: y }), [
          chartBox(Math.max(150, rows.length * 30 + 40), t('bt.compare', { y: y }), function (col) {
            return {
              type: 'bar',
              data: { labels: rows.map(function (r) { return r.name; }), datasets: [{ label: t('col.ppd'), data: rows.map(function (r) { return r.d.ppd; }), backgroundColor: rows.map(function (r) { return r.isModel ? col.series[0] : col.neutral; }), borderRadius: 4, borderSkipped: 'start', barPercentage: 0.75 }] },
              options: {
                indexAxis: 'y', responsive: true, maintainAspectRatio: false, animation: false,
                plugins: { legend: { display: false }, tooltip: Object.assign(tooltipOpts(col), { callbacks: { label: function (x) { return ' ' + t('col.ppd') + ': ' + fmtNum(x.raw, 3); } } }) },
                scales: { x: axisOpts(col, { beginAtZero: true }), y: axisOpts(col, { grid: { display: false }, ticks: { color: col.text2, autoSkip: false } }) }
              }
            };
          }),
          h('div', { class: 'legend small' }, h('span', { class: 'sw model' }), ' ' + t('bt.legendModel') + '   ', h('span', { class: 'sw player' }), ' ' + t('bt.legendPlayer')),
          table([{ label: t('col.name') }, { label: t('col.days'), num: true }, { label: t('col.points'), num: true }, { label: t('col.ppd'), num: true },
            { label: catShort('vorspeise'), num: true }, { label: catShort('hauptspeise'), num: true }, { label: catShort('beilage'), num: true }],
          rows.map(function (r) {
            var acc = r.d.acc || {};
            return {
              cls: (r.isModel ? 'model-row' : '') + (r.best ? ' best-row' : '') + (r.me ? ' me-row' : ''),
              cells: [h('span', null, r.name, r.best ? chip('★', 'accent tiny-chip') : null), String(r.d.days == null ? '–' : r.d.days), fmtPts(r.d.points), fmtNum(r.d.ppd, 2),
                fmtPct(acc.vorspeise), fmtPct(acc.hauptspeise), fmtPct(acc.beilage)]
            };
          }), { cls: 'compact' })
        ], { sub: t('bt.compareSub') }));
      }
      // R4 vs no R4
      var r4rows = models.filter(function (m) { return (m.years || {})[y] && (m.no_r4 || {})[y]; }).map(function (m) {
        var w = m.years[y].points, wo = m.no_r4[y].points;
        return [label(m), fmtPts(w), fmtPts(wo), isNum(w) && isNum(wo) ? fmtPts(w - wo) + (wo ? ' (' + fmtPct((w - wo) / wo) + ')' : '') : '–', m.years[y].r4_ok === false ? '✗' : '✓'];
      });
      if (r4rows.length) {
        out.appendChild(card(t('bt.r4'), table([{ label: t('col.model') }, { label: t('bt.withR4'), num: true }, { label: t('bt.withoutR4'), num: true }, { label: t('bt.cost'), num: true }, { label: 'R4', num: true }], r4rows, { cls: 'compact' }), { sub: t('bt.r4Sub') }));
      }
      // calibration
      var calib = b.calibration || {};
      var cmodels = Object.keys(calib);
      if (cmodels.length) {
        if (!btState.model || cmodels.indexOf(btState.model) < 0) btState.model = cmodels.indexOf(b.best_model) >= 0 ? b.best_model : cmodels[0];
        var cm = btState.model;
        var mlabel = function (n) { var m = models.filter(function (x) { return x.name === n; })[0]; return m ? label(m) : n; };
        out.appendChild(card(t('bt.calib'), [
          cmodels.length > 1 ? segmented(cmodels.map(function (n) { return { value: n, label: mlabel(n) }; }), cm, function (v) { btState.model = v; rerender(); }) : null,
          chartBox(280, t('bt.calib'), function (col) {
            var ds = CATS.filter(function (c) { return (calib[cm] || {})[c]; }).map(function (c, i) {
              return {
                label: catName(c), data: calib[cm][c].map(function (p) { return { x: p.p_mean, y: p.hit_rate, n: p.n }; }),
                borderColor: col.series[i], backgroundColor: col.series[i], showLine: true, borderWidth: 2, pointRadius: 4, pointHoverRadius: 6
              };
            });
            var mx = 0;
            ds.forEach(function (d2) { d2.data.forEach(function (p) { mx = Math.max(mx, p.x || 0, p.y || 0); }); });
            mx = Math.min(1, Math.ceil((mx + 0.02) * 10) / 10);
            ds.push({ label: t('bt.ideal'), data: [{ x: 0, y: 0 }, { x: mx, y: mx }], borderColor: col.muted, borderDash: [5, 4], borderWidth: 1.5, pointRadius: 0, pointHoverRadius: 0, showLine: true });
            return {
              type: 'scatter', data: { datasets: ds },
              options: {
                responsive: true, maintainAspectRatio: false, animation: false,
                plugins: { legend: { position: 'bottom', labels: { color: col.text2, boxWidth: 12, usePointStyle: true } }, tooltip: Object.assign(tooltipOpts(col), { callbacks: { label: function (x) { var r = x.raw || {}; return ' ' + x.dataset.label + ': p ' + fmtPct(r.x, 1) + ' → ' + fmtPct(r.y, 1) + (r.n ? ' (n=' + r.n + ')' : ''); } } }) },
                scales: {
                  x: axisOpts(col, { min: 0, max: mx, title: { display: true, text: t('bt.calX'), color: col.muted }, ticks: { color: col.muted, callback: function (v) { return fmtPct(v); } } }),
                  y: axisOpts(col, { min: 0, max: mx, title: { display: true, text: t('bt.calY'), color: col.muted }, ticks: { color: col.muted, callback: function (v) { return fmtPct(v); } } })
                }
              }
            };
          })
        ], { sub: t('bt.calibSub') }));
      }
      // metrics
      var mrows = models.filter(function (m) { return m.logloss || m.top1; }).map(function (m) {
        var f = function (o, c, pct) { var v = (o || {})[c]; return pct ? fmtPct(v) : fmtNum(v, 2); };
        return [label(m)].concat(CATS.map(function (c) { return f(m.logloss, c); }), CATS.map(function (c) { return f(m.top1, c, true); }), CATS.map(function (c) { return f(m.top3, c, true); }));
      });
      if (mrows.length) {
        var hd = [{ label: t('col.model') }];
        ['LL', 'Top1', 'Top3'].forEach(function (k) { CATS.forEach(function (c) { hd.push({ label: k + ' ' + catShort(c), num: true }); }); });
        out.appendChild(card(t('bt.metrics'), table(hd, mrows, { cls: 'compact' }), { sub: t('bt.metricsSub') }));
      }
      // daily
      var daily = ((b.daily || {})[y] || []).slice().reverse();
      if (daily.length) {
        var shown = daily.slice(0, 30);
        out.appendChild(card(t('bt.daily', { y: y }), h('details', null, h('summary', null, t('bt.dailyShow', { n: shown.length, total: daily.length })),
          table([{ label: t('col.day') }, { label: t('bt.modelTip') }, { label: t('bt.actual') }, { label: t('col.points'), num: true }],
            shown.map(function (x) {
              var mt = x.model_tip || {}, ac = x.actual || {};
              return [fmtWdDM(x.date), [mt.v, mt.h, mt.b].map(function (s) { return s || '–'; }).join(' / '), [ac.v, ac.h, ac.b].map(function (s) { return s || '–'; }).join(' / '), fmtPts(x.points)];
            }), { cls: 'compact' }))));
      }
      if (b.params && Object.keys(b.params).length) {
        out.appendChild(card(t('bt.params'), h('details', null, h('summary', null, t('bt.paramsShow')), h('pre', { class: 'mono small pre' }, JSON.stringify(b.params, null, 2)))));
      }
      return out;
    });
  }

  // ================================================================== VIEW: Datenbank
  var dbState = { q: '', cat: 'all', year: 'all', wd: 'all', status: 'all', limit: 120 };
  function viewDatenbank() {
    return Promise.all([load('menus'), load('tips')]).then(function (rs) {
      var Mn = rs[0], Tp = rs[1];
      if (Mn.status !== 'ok') return missingState(Mn, 'db.empty.title', 'db.empty.text');
      var rows = ((Mn.data || {}).rows || []).slice().sort(function (a, b) { return a.date < b.date ? 1 : -1; });
      var tipsBy = {};
      (((okData(Tp) || {}).rows) || []).forEach(function (r) { (tipsBy[r.date] = tipsBy[r.date] || []).push(r); });
      var years = Array.from(new Set(rows.map(function (r) { return String(r.year || r.date.slice(0, 4)); }))).sort().reverse();
      var st = dbState;
      var out = h('div', { class: 'stack' });
      out.appendChild(h('div', { class: 'page-head' }, h('h1', null, t('db.title')), h('p', { class: 'muted' }, t('db.sub', { n: rows.length }))));
      var search = h('input', { type: 'search', class: 'search', placeholder: t('db.search'), 'aria-label': t('db.search'), value: st.q, autocomplete: 'off', spellcheck: 'false' });
      var count = h('p', { class: 'muted small', 'aria-live': 'polite' });
      var listWrap = h('div', { class: 'db-list' });
      var filters = h('div', { class: 'card controls db-filters' },
        search,
        h('div', { class: 'filter-grid' },
          h('label', { class: 'inline-field' }, h('span', { class: 'small muted' }, t('ui.category')),
            selectEl([{ value: 'all', label: t('ui.all') }].concat(CATS.map(function (c) { return { value: c, label: catName(c) }; })), st.cat, function (v) { st.cat = v; st.limit = 120; draw(); })),
          h('label', { class: 'inline-field' }, h('span', { class: 'small muted' }, t('ui.year')),
            selectEl([{ value: 'all', label: t('ui.all') }].concat(years.map(function (y) { return { value: y, label: y }; })), st.year, function (v) { st.year = v; st.limit = 120; draw(); })),
          h('label', { class: 'inline-field' }, h('span', { class: 'small muted' }, t('ui.weekday')),
            selectEl([{ value: 'all', label: t('ui.all') }].concat([0, 1, 2, 3, 4].map(function (i) { return { value: String(i), label: wdLong(i) }; })), st.wd, function (v) { st.wd = v; st.limit = 120; draw(); })),
          h('label', { class: 'inline-field' }, h('span', { class: 'small muted' }, t('ui.status')),
            selectEl([{ value: 'all', label: t('ui.all') }].concat(['served', 'free', 'unknown', 'pending'].map(function (s) { return { value: s, label: statusName(s) }; })), st.status, function (v) { st.status = v; st.limit = 120; draw(); }))),
        count);
      out.appendChild(filters);
      out.appendChild(listWrap);
      var timer = null;
      search.addEventListener('input', function () {
        clearTimeout(timer);
        timer = setTimeout(function () { st.q = search.value; st.limit = 120; draw(); }, 120);
      });
      function matches(r) {
        if (st.year !== 'all' && String(r.year || r.date.slice(0, 4)) !== st.year) return false;
        if (st.wd !== 'all' && String(r.weekday) !== st.wd) return false;
        if (st.status !== 'all' && r.status !== st.status) return false;
        var q = fold(st.q);
        if (!q) return true;
        var fields = st.cat === 'all' ? ['v', 'h', 'b'] : [SHORT[st.cat]];
        var hay = fields.map(function (f) { return fold(r[f]) + ' ' + fold(r[f + '_norm']); }).join(' | ');
        if (st.cat === 'all') hay += ' ' + r.date + ' ' + fmtDMY(r.date);
        return q.split(' ').every(function (w) { return hay.indexOf(w) >= 0; });
      }
      function draw() {
        var f = rows.filter(matches);
        count.textContent = t('db.count', { n: f.length, total: rows.length });
        var shown = f.slice(0, st.limit);
        var head = h('div', { class: 'db-row db-head', 'aria-hidden': 'true' },
          h('span', null, t('col.date')), h('span', null, catName('vorspeise')), h('span', null, catName('hauptspeise')), h('span', null, catName('beilage')), h('span', null, t('ui.status')));
        var items = shown.map(function (r) {
          var tl = tipsBy[r.date] || [];
          var cell = function (c) {
            var raw = r[SHORT[c]] || '';
            var nrm = r[SHORT[c] + '_norm'] || '';
            return h('span', { class: 'db-cell' }, h('span', { class: 'db-lbl' }, catShort(c)), raw || '–',
              nrm && fold(nrm) !== fold(raw) ? h('span', { class: 'db-norm muted' }, ' → ' + nrm) : null);
          };
          var summary = h('summary', { class: 'db-row' },
            h('span', { class: 'db-date' }, h('strong', null, wdShort(r.weekday) + ' '), fmtDMY(r.date), r.lent ? chip(t('db.lent'), 'muted-chip tiny-chip') : null),
            cell('vorspeise'), cell('hauptspeise'), cell('beilage'),
            h('span', { class: 'db-status' }, chip(statusName(r.status), 'st-' + r.status), tl.length ? h('span', { class: 'muted tiny' }, ' ' + t('db.tips', { n: tl.length })) : null));
          var det = h('details', { class: 'db-item' + (r.status !== 'served' ? ' dim' : '') }, summary);
          if (tl.length) {
            det.appendChild(h('div', { class: 'db-tips' }, table([{ label: t('col.player') }, { label: t('col.tip') }, { label: t('col.points'), num: true }],
              tl.map(function (x) { return [x.player, [x.v, x.h, x.b].map(function (s) { return s || '–'; }).join(' / '), fmtPts(x.points)]; }), { cls: 'compact' })));
          } else {
            det.appendChild(h('p', { class: 'muted small db-tips' }, t('db.noTips')));
          }
          return det;
        });
        listWrap.replaceChildren(head);
        appendKids(listWrap, items);
        if (!f.length) listWrap.appendChild(h('p', { class: 'muted center' }, t('db.none')));
        if (f.length > shown.length) {
          listWrap.appendChild(h('button', { type: 'button', class: 'btn wide', onclick: function () { st.limit += 200; draw(); } }, t('db.more', { n: f.length - shown.length })));
        }
      }
      draw();
      return out;
    });
  }

  // ================================================================== VIEW: Eingabe
  function viewEingabe() {
    return loadCtx().then(function (ctx) {
      var meta = ctx.meta || {};
      var cfg = settings(meta);
      var todayR = romeTodayISO();
      var out = h('div', { class: 'stack' });
      out.appendChild(h('div', { class: 'page-head' }, h('h1', null, t('in.title')), h('p', { class: 'muted' }, t('in.sub'))));
      var pb = pendingBanner(ctx);
      if (pb) out.appendChild(pb);

      // datalists (autocomplete)
      var dls = h('div', { hidden: true });
      CATS.forEach(function (c) {
        dls.appendChild(h('datalist', { id: 'dl-' + c }, (((ctx.dishes || {})[c]) || []).map(function (n) { return h('option', { value: n }); })));
      });
      dls.appendChild(h('datalist', { id: 'dl-players' }, ((meta.players) || []).map(function (n) { return h('option', { value: n }); })));
      out.appendChild(dls);

      // ---------------- (a) settings
      var fOwner = h('input', { type: 'text', id: 'set-owner', value: cfg.owner, autocomplete: 'off', spellcheck: 'false', autocapitalize: 'off', placeholder: 'owner' });
      var fRepo = h('input', { type: 'text', id: 'set-repo', value: cfg.repo, autocomplete: 'off', spellcheck: 'false', autocapitalize: 'off', placeholder: 'repo' });
      var fBranch = h('input', { type: 'text', id: 'set-branch', value: cfg.branch, autocomplete: 'off', spellcheck: 'false', autocapitalize: 'off', placeholder: 'main' });
      var fToken = h('input', { type: 'password', id: 'set-token', value: cfg.token, autocomplete: 'off', spellcheck: 'false', autocapitalize: 'off', placeholder: 'github_pat_…' });
      var fPlayer = h('input', { type: 'text', id: 'set-player', value: cfg.player, list: 'dl-players', autocomplete: 'off' });
      var fPass = h('input', { type: 'password', id: 'set-pass', value: store.get('passphrase') || '', autocomplete: 'off' });
      var setStatus = h('div', { class: 'form-status', 'aria-live': 'polite' });
      var tokState = h('span', { class: 'chip ' + (cfg.token ? 'ok' : 'danger') }, cfg.token ? t('set.tokenSaved') : t('set.tokenMissing'));
      var showBtn = h('button', { type: 'button', class: 'btn small', 'aria-pressed': 'false' }, icon('eye'), t('set.show'));
      showBtn.addEventListener('click', function () {
        var vis = fToken.type === 'password';
        fToken.type = vis ? 'text' : 'password';
        showBtn.setAttribute('aria-pressed', String(vis));
        showBtn.lastChild.textContent = vis ? t('set.hide') : t('set.show');
      });
      var saveSettings = function () {
        var o = clean(fOwner.value), r = clean(fRepo.value), br = clean(fBranch.value) || 'main';
        if ((o && !/^[A-Za-z0-9-]+$/.test(o)) || (r && !/^[A-Za-z0-9_.-]+$/.test(r)) || /\s|\.\.|^\//.test(br)) {
          setStatus.replaceChildren(notice('danger', t('set.invalid')));
          return false;
        }
        store.set('gh.owner', o); store.set('gh.repo', r); store.set('gh.branch', br);
        store.set('gh.token', fToken.value.trim());
        store.set('player', clean(fPlayer.value));
        var oldPass = store.get('passphrase') || '';
        store.set('passphrase', fPass.value);
        tokState.className = 'chip ' + (fToken.value.trim() ? 'ok' : 'danger');
        tokState.textContent = fToken.value.trim() ? t('set.tokenSaved') : t('set.tokenMissing');
        setStatus.replaceChildren(notice('ok', t('set.saved')));
        if (oldPass !== (fPass.value || '')) dataCache = {};
        return true;
      };
      var delToken = function () {
        fToken.value = '';
        store.set('gh.token', null);
        tokState.className = 'chip danger';
        tokState.textContent = t('set.tokenMissing');
        setStatus.replaceChildren(notice('ok', t('set.tokenDeleted')));
      };
      var testConn = function () {
        if (!saveSettings()) return;
        var c2 = settings(meta);
        if (!c2.token || !c2.owner || !c2.repo) { setStatus.replaceChildren(notice('warn', t('set.needAll'))); return; }
        setStatus.replaceChildren(notice('info', t('set.testing')));
        ghFetch(repoPath(c2), c2.token).then(function (r) {
          if (!r.ok) throw ghErr(r.status, r.body);
          var perm = (r.body && r.body.permissions) || {};
          var canPush = perm.push || perm.admin || perm.maintain;
          setStatus.replaceChildren(notice(canPush === false ? 'warn' : 'ok', canPush === false ? t('set.testReadOnly', { repo: (r.body && r.body.full_name) || '' }) : t('set.testOk', { repo: (r.body && r.body.full_name) || '' })));
        }).catch(function (e) { setStatus.replaceChildren(notice('danger', ghErrorText(e))); });
      };
      var settingsOpen = !cfg.token || !cfg.owner || !cfg.repo;
      var setCard = h('details', { class: 'card settings', open: settingsOpen ? true : null },
        h('summary', { class: 'card-title' }, t('set.title'), ' ', tokState),
        h('div', { class: 'form-grid three' },
          h('label', { class: 'field' }, h('span', null, t('set.owner')), fOwner),
          h('label', { class: 'field' }, h('span', null, t('set.repo')), fRepo),
          h('label', { class: 'field' }, h('span', null, t('set.branch')), fBranch)),
        h('p', { class: 'muted tiny' }, t('set.detected', { v: detectRepo(meta).owner ? detectRepo(meta).owner + '/' + detectRepo(meta).repo : t('set.notDetected') })),
        h('label', { class: 'field' }, h('span', null, t('set.token')),
          h('div', { class: 'input-row' }, fToken, showBtn,
            h('button', { type: 'button', class: 'btn small danger-btn', onclick: delToken }, t('set.delete')))),
        h('div', { class: 'help small' },
          h('p', null, t('set.tokenHelp1')),
          h('ol', { class: 'plain-ol' }, h('li', null, t('set.tokenStep1')), h('li', null, t('set.tokenStep2', { repo: (cfg.owner || 'owner') + '/' + (cfg.repo || 'repo') })), h('li', null, t('set.tokenStep3')), h('li', null, t('set.tokenStep4'))),
          h('p', { class: 'muted' }, t('set.tokenSafety'))),
        h('label', { class: 'field' }, h('span', null, t('set.player')), fPlayer),
        h('label', { class: 'field' }, h('span', null, t('set.pass')), fPass, h('span', { class: 'muted tiny' }, t('set.passHelp'))),
        h('div', { class: 'btn-row' },
          h('button', { type: 'button', class: 'btn primary', onclick: saveSettings }, t('set.save')),
          h('button', { type: 'button', class: 'btn', onclick: testConn }, t('set.test'))),
        setStatus);
      out.appendChild(setCard);

      // ---------------- shared submit logic
      function submit(kind, values, statusEl, btn) {
        var c2 = settings(meta);
        if (!c2.token || !c2.owner || !c2.repo) {
          statusEl.replaceChildren(notice('danger', t('in.noToken')));
          setCard.open = true;
          setCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
          return;
        }
        btn.disabled = true;
        var steps = { load: t('in.stepLoad'), save: t('in.stepSave'), retry: t('in.stepRetry') };
        commitRow(c2, kind, values, function (step, path) {
          statusEl.replaceChildren(notice('info', steps[step] + ' ' + path + ' …'));
        }).then(function (res) {
          addPending(kind === 'menu'
            ? { kind: 'menu', date: values.date, v: values.vorspeise, h: values.hauptspeise, b: values.beilage, free: values.status === 'free', at: Date.now() }
            : { kind: 'tip', date: values.date, player: values.player, v: values.vorspeise, h: values.hauptspeise, b: values.beilage, at: Date.now() });
          var commit = res.commit || {};
          var actionsUrl = 'https://github.com/' + encodeURIComponent(c2.owner) + '/' + encodeURIComponent(c2.repo) + '/actions';
          var runLink = h('a', { href: actionsUrl, target: '_blank', rel: 'noopener noreferrer' }, t('in.actions'));
          var links = h('p', { class: 'small' },
            commit.html_url && /^https:\/\/github\.com\//.test(commit.html_url) ? h('a', { href: commit.html_url, target: '_blank', rel: 'noopener noreferrer' }, t('in.commit')) : null,
            commit.html_url ? ' · ' : null, runLink);
          statusEl.replaceChildren(notice('ok', res.action === 'update' ? t('in.updated', { path: res.path }) : t('in.inserted', { path: res.path }),
            h('div', null, links, h('p', { class: 'small' }, t('in.wait')))));
          toast(t('in.okToast'), 'ok');
          findRun(c2, commit.sha, 5).then(function (url) {
            if (url) { runLink.href = url; runLink.textContent = t('in.run'); }
          });
        }).catch(function (e) {
          statusEl.replaceChildren(notice('danger', ghErrorText(e)));
        }).then(function () { btn.disabled = false; });
      }
      function dishInput(c, id, val) {
        return h('input', { type: 'text', id: id, list: 'dl-' + c, value: val || '', autocomplete: 'off', autocapitalize: 'sentences', enterkeyhint: 'next', maxlength: '120' });
      }
      function weekdayHint(dateInput, el) {
        var upd = function () {
          var d = dateInput.value;
          if (!isISO(d)) { el.textContent = ''; return; }
          var wd = weekdayOf(d);
          el.textContent = wdLong(wd) + (wd >= 5 ? ' – ' + t('in.weekend') : (ctx.r4.free.has(d) ? ' – ' + t('in.freeDay') : ''));
          el.className = 'muted small' + (wd >= 5 ? ' warn-text' : '');
        };
        dateInput.addEventListener('input', upd);
        upd();
      }

      // ---------------- (b) menu form
      var mDate = h('input', { type: 'date', id: 'menu-date', value: todayR, required: true });
      var mWd = h('span', { class: 'muted small' });
      var mIn = {};
      CATS.forEach(function (c) { mIn[c] = dishInput(c, 'menu-' + SHORT[c]); });
      var mFree = h('input', { type: 'checkbox', id: 'menu-free' });
      var mStatus = h('div', { class: 'form-status', 'aria-live': 'polite' });
      var mExisting = h('div');
      var mBtn = h('button', { type: 'submit', class: 'btn primary big' }, t('in.menuSave'));
      var updMenuHint = function () {
        var d = mDate.value;
        mExisting.replaceChildren();
        if (!isISO(d)) return;
        var m = menuOf(ctx, d);
        if (m && (m.status === 'served' || m.status === 'free')) {
          mExisting.appendChild(notice('info', t('in.menuExists', { menu: m.status === 'free' ? statusName('free') : [m.raw.v, m.raw.h, m.raw.b].map(function (s) { return s || '–'; }).join(' / ') })));
        }
      };
      mFree.addEventListener('change', function () { CATS.forEach(function (c) { mIn[c].disabled = mFree.checked; }); });
      mDate.addEventListener('input', updMenuHint);
      var menuForm = h('form', {
        class: 'card form', id: 'form-menu', novalidate: true, onsubmit: function (e) {
          e.preventDefault();
          var d = mDate.value;
          if (!isISO(d)) { mStatus.replaceChildren(notice('danger', t('in.badDate'))); return; }
          var free = mFree.checked;
          var vals = CATS.map(function (c) { return clean(mIn[c].value); });
          if (!free && !vals.some(Boolean)) { mStatus.replaceChildren(notice('danger', t('in.needDish'))); return; }
          submit('menu', menuValues(d, vals[0], vals[1], vals[2], free), mStatus, mBtn);
        }
      },
        h('h2', { class: 'card-title' }, t('in.menuTitle')),
        h('label', { class: 'field' }, h('span', null, t('col.date')), mDate, mWd),
        CATS.map(function (c) { return h('label', { class: 'field' }, h('span', null, catBadge(c), ' ', catName(c)), mIn[c]); }),
        h('label', { class: 'check' }, mFree, h('span', null, t('in.free'))),
        mExisting, mBtn, mStatus);
      weekdayHint(mDate, mWd);
      updMenuHint();
      out.appendChild(menuForm);

      // ---------------- (c) tip form
      var pre = null;
      try { pre = JSON.parse(session.get('prefill') || 'null'); } catch (e) { pre = null; }
      session.set('prefill', null);
      var tDate = h('input', { type: 'date', id: 'tip-date', value: (pre && isISO(pre.date)) ? pre.date : todayR, required: true });
      var tWd = h('span', { class: 'muted small' });
      var tPlayer = h('input', { type: 'text', id: 'tip-player', list: 'dl-players', value: cfg.player || ctx.me, autocomplete: 'off' });
      var tIn = {};
      CATS.forEach(function (c) { tIn[c] = dishInput(c, 'tip-' + SHORT[c], pre ? pre[SHORT[c]] : ''); });
      var tWarn = h('div', { class: 'r4-warn', 'aria-live': 'polite', id: 'tip-r4' });
      var tStatus = h('div', { class: 'form-status', 'aria-live': 'polite' });
      var tBtn = h('button', { type: 'submit', class: 'btn primary big' }, t('in.tipSave'));
      var validateTip = function () {
        var d = tDate.value, player = clean(tPlayer.value);
        var msgs = [];
        if (isISO(d) && player) {
          var hist = historyOf(ctx, player);
          var tmpR4 = ctx.r4;
          CATS.forEach(function (c) {
            splitOpts(tIn[c].value).forEach(function (o) {
              var canon = canonOpts(ctx, c, o)[0] || o;
              tmpR4.violations(c, canon, d, hist[c]).forEach(function (v) { msgs.push(catName(c) + ': ' + canon + ' – ' + violationText(v, tmpR4.max)); });
            });
          });
          var ex = tipOf(ctx, player, d);
          var info = [];
          if (ex) info.push(t('in.tipExists', { tip: [ex.v, ex.h, ex.b].map(function (s) { return s || '–'; }).join(' / ') }));
          if (Date.now() > deadlineFor(d, meta.deadline || '12:00')) info.push(t('in.afterDeadline'));
          CATS.forEach(function (c) {
            var v = clean(tIn[c].value);
            var list = (ctx.dishes || {})[c] || [];
            if (v && list.length && !list.some(function (x) { return fold(x) === fold(v); })) info.push(t('in.unknownDish', { cat: catName(c), dish: v }));
          });
          tWarn.replaceChildren(
            msgs.length ? notice('danger', t('in.r4Title'), h('ul', { class: 'plain' }, msgs.map(function (m) { return h('li', null, m); }))) : null,
            !msgs.length && CATS.some(function (c) { return clean(tIn[c].value); }) ? notice('ok', t('in.r4Ok')) : null,
            info.length ? notice('info', h('span', null, info.map(function (x, i) { return [i ? h('br') : null, x]; }))) : null);
        } else {
          tWarn.replaceChildren();
        }
        return msgs;
      };
      [tDate, tPlayer].concat(CATS.map(function (c) { return tIn[c]; })).forEach(function (el) {
        el.addEventListener('input', validateTip);
        el.addEventListener('change', validateTip);
      });
      var tipForm = h('form', {
        class: 'card form', id: 'form-tip', novalidate: true, onsubmit: function (e) {
          e.preventDefault();
          var d = tDate.value, player = clean(tPlayer.value);
          if (!isISO(d)) { tStatus.replaceChildren(notice('danger', t('in.badDate'))); return; }
          if (!player) { tStatus.replaceChildren(notice('danger', t('in.needPlayer'))); return; }
          var vals = CATS.map(function (c) { return clean(tIn[c].value); });
          if (!vals.some(Boolean)) { tStatus.replaceChildren(notice('danger', t('in.needDish'))); return; }
          var msgs = validateTip();
          if (msgs.length && !window.confirm(t('in.r4Confirm'))) return;
          submit('tip', tipValues(d, player, vals[0], vals[1], vals[2]), tStatus, tBtn);
        }
      },
        h('h2', { class: 'card-title' }, t('in.tipTitle')),
        pre ? notice('info', t('in.prefilled')) : null,
        h('div', { class: 'form-grid two' },
          h('label', { class: 'field' }, h('span', null, t('col.date')), tDate, tWd),
          h('label', { class: 'field' }, h('span', null, t('col.player')), tPlayer)),
        CATS.map(function (c) { return h('label', { class: 'field' }, h('span', null, catBadge(c), ' ', catName(c)), tIn[c]); }),
        tWarn, tBtn, tStatus);
      weekdayHint(tDate, tWd);
      out.appendChild(tipForm);
      mount(validateTip);
      if (pre) mount(function () { tipForm.scrollIntoView({ block: 'start' }); });

      // pending list
      if (ctx.pending.length) {
        out.appendChild(card(t('pending.title'), [
          h('ul', { class: 'plain pending-list' }, ctx.pending.map(function (p) {
            return h('li', null, h('strong', null, (p.kind === 'menu' ? t('pending.menu') : t('pending.tip', { player: p.player })) + ' ' + fmtWdDM(p.date) + ': '),
              p.free ? statusName('free') : [p.v, p.h, p.b].map(function (s) { return s || '–'; }).join(' / '));
          })),
          h('p', { class: 'muted small' }, t('pending.explain')),
          h('button', { type: 'button', class: 'btn small', onclick: function () { store.set('pending', null); rerender(); } }, t('pending.clear'))
        ]));
      }
      return out;
    });
  }

  // ------------------------------------------------------------------ boot
  function setLang(l) {
    lang = l === 'it' ? 'it' : 'de';
    store.set('lang', lang);
    nfCache = {};
    rerender();
  }
  function cycleTheme() {
    var cur = store.get('theme', 'auto');
    var next = cur === 'auto' ? 'light' : (cur === 'light' ? 'dark' : 'auto');
    store.set('theme', next === 'auto' ? null : next);
    if (next === 'auto') document.documentElement.removeAttribute('data-theme');
    else document.documentElement.setAttribute('data-theme', next);
    toast(t('ui.theme') + ': ' + t('theme.' + next));
    rerender();
  }
  function boot() {
    var th = store.get('theme', 'auto');
    if (th === 'light' || th === 'dark') document.documentElement.setAttribute('data-theme', th);
    document.getElementById('btn-lang').addEventListener('click', function () { setLang(lang === 'de' ? 'it' : 'de'); });
    document.getElementById('btn-theme').addEventListener('click', cycleTheme);
    document.getElementById('btn-refresh').addEventListener('click', function () { reloadData(); toast(t('ui.refreshed')); });
    window.addEventListener('hashchange', function () { render(false); window.scrollTo(0, 0); });
    if (window.matchMedia) {
      var mq = matchMedia('(prefers-color-scheme: dark)');
      var onChange = function () { if (!document.documentElement.getAttribute('data-theme')) rerender(); };
      if (mq.addEventListener) mq.addEventListener('change', onChange); else if (mq.addListener) mq.addListener(onChange);
    }
    document.addEventListener('visibilitychange', function () {
      // coming back to the tab after a while (e.g. next morning): refresh data
      if (document.visibilityState === 'visible' && window.__tspHiddenAt && Date.now() - window.__tspHiddenAt > 30 * 60 * 1000) reloadData();
      if (document.visibilityState === 'hidden') window.__tspHiddenAt = Date.now();
    });
    if (!location.hash) history.replaceState(null, '', '#/heute');
    render(false);
  }

  // test hooks (pure functions only – no secrets)
  window.TSP = {
    parseCSV: parseCSV, serializeCSV: serializeCSV, upsertCsv: upsertCsv, menuValues: menuValues, tipValues: tipValues,
    utf8ToB64: utf8ToB64, b64ToUtf8: b64ToUtf8, R4: R4, romeTodayISO: romeTodayISO, romeToUtc: romeToUtc,
    deadlineFor: deadlineFor, commitRow: commitRow, fold: fold, isoWeek: isoWeek, decryptEnvelope: decryptEnvelope
  };

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
