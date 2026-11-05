/* Outils cyber de manthole.github.io — tout est calculé dans le navigateur.
   Seule exception : le vérificateur de mots de passe interroge l'API Pwned Passwords
   avec les 5 premiers caractères du hash SHA-1 (k-anonymat), et uniquement sur clic.

   Chaque page d'outil a un <main data-tool="…"> ; le script initialise l'outil correspondant.
   Textes bilingues : L(fr, en) produit deux <span lang>, masqués par css/cyber.css selon la langue. */
(function () {
  "use strict";

  /* ---------- Utilitaires ---------- */
  var $ = function (sel, root) { return (root || document).querySelector(sel); };
  var enc = new TextEncoder();

  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function L(fr, en) {
    return '<span lang="fr">' + fr + '</span><span lang="en">' + en + "</span>";
  }
  function lang() { return document.documentElement.lang === "fr" ? "fr" : "en"; }
  function debounce(fn, ms) {
    var t;
    return function () {
      var args = arguments, self = this;
      clearTimeout(t);
      t = setTimeout(function () { fn.apply(self, args); }, ms);
    };
  }
  function toHex(bytes) {
    var out = "";
    for (var i = 0; i < bytes.length; i++) out += (bytes[i] < 16 ? "0" : "") + bytes[i].toString(16);
    return out;
  }
  function msg(el, kind, html) {
    el.className = "tool-msg" + (kind ? " tool-msg--" + kind : "");
    el.innerHTML = html || "";
  }

  /* Placeholders bilingues : data-ph-fr / data-ph-en, mis à jour quand la langue change. */
  function applyPlaceholders() {
    var l = lang();
    document.querySelectorAll("[data-ph-fr]").forEach(function (el) {
      el.placeholder = el.getAttribute("data-ph-" + l) || "";
    });
  }
  new MutationObserver(applyPlaceholders).observe(document.documentElement, {
    attributes: true, attributeFilter: ["lang"]
  });

  /* Boutons « copier » : <button class="copy-btn" data-copy="#id"> ou créés par makeCopy(). */
  function copyText(text, btn) {
    function done() {
      btn.classList.add("is-done");
      btn.innerHTML = L("copié ✓", "copied ✓");
      setTimeout(function () {
        btn.classList.remove("is-done");
        btn.innerHTML = L("copier", "copy");
      }, 1400);
    }
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(text).then(done, function () {});
    } else {
      var ta = document.createElement("textarea");
      ta.value = text;
      ta.setAttribute("readonly", "");
      ta.style.position = "fixed";
      ta.style.opacity = "0";
      document.body.appendChild(ta);
      ta.select();
      try { document.execCommand("copy"); done(); } catch (e) {}
      document.body.removeChild(ta);
    }
  }
  function makeCopy(getText) {
    var b = document.createElement("button");
    b.type = "button";
    b.className = "copy-btn";
    b.innerHTML = L("copier", "copy");
    b.addEventListener("click", function () {
      var t = getText();
      if (t) copyText(t, b);
    });
    return b;
  }
  document.addEventListener("click", function (e) {
    var b = e.target.closest(".copy-btn[data-copy]");
    if (!b) return;
    var src = $(b.getAttribute("data-copy"));
    var text = src ? ("value" in src ? src.value : src.textContent) : "";
    if (text) copyText(text, b);
  });

  /* Aléa cryptographique uniforme dans [0, n) (rejet pour éviter le biais du modulo). */
  function randInt(n) {
    var limit = Math.floor(0x100000000 / n) * n;
    var buf = new Uint32Array(1);
    do { crypto.getRandomValues(buf); } while (buf[0] >= limit);
    return buf[0] % n;
  }

  function sha(algo, bytes) {
    return crypto.subtle.digest(algo, bytes).then(function (h) { return toHex(new Uint8Array(h)); });
  }

  /* MD5 (absent de WebCrypto, mais toujours utilisé pour comparer des IOC). */
  var MD5_K = new Int32Array(64);
  for (var ki = 0; ki < 64; ki++) MD5_K[ki] = Math.floor(Math.abs(Math.sin(ki + 1)) * 4294967296) | 0;
  var MD5_S = [7, 12, 17, 22, 5, 9, 14, 20, 4, 11, 16, 23, 6, 10, 15, 21];
  function md5(bytes) {
    var len = bytes.length;
    var nWords = (((len + 8) >>> 6) + 1) * 16;
    var w = new Int32Array(nWords);
    for (var i = 0; i < len; i++) w[i >> 2] |= bytes[i] << ((i % 4) * 8);
    w[len >> 2] |= 0x80 << ((len % 4) * 8);
    w[nWords - 2] = (len * 8) >>> 0;
    w[nWords - 1] = Math.floor(len / 0x20000000);
    var a0 = 0x67452301, b0 = 0xefcdab89 | 0, c0 = 0x98badcfe | 0, d0 = 0x10325476;
    for (var off = 0; off < nWords; off += 16) {
      var A = a0, B = b0, C = c0, D = d0;
      for (var j = 0; j < 64; j++) {
        var F, g, r = j >> 4;
        if (r === 0) { F = (B & C) | (~B & D); g = j; }
        else if (r === 1) { F = (D & B) | (~D & C); g = (5 * j + 1) % 16; }
        else if (r === 2) { F = B ^ C ^ D; g = (3 * j + 5) % 16; }
        else { F = C ^ (B | ~D); g = (7 * j) % 16; }
        var s = MD5_S[r * 4 + (j % 4)];
        F = (F + A + MD5_K[j] + w[off + g]) | 0;
        A = D; D = C; C = B;
        B = (B + ((F << s) | (F >>> (32 - s)))) | 0;
      }
      a0 = (a0 + A) | 0; b0 = (b0 + B) | 0; c0 = (c0 + C) | 0; d0 = (d0 + D) | 0;
    }
    var out = new Uint8Array(16);
    [a0, b0, c0, d0].forEach(function (v, k) {
      for (var b = 0; b < 4; b++) out[k * 4 + b] = (v >>> (b * 8)) & 0xff;
    });
    return toHex(out);
  }

  function fmtDuration(sec) {
    if (!isFinite(sec) || sec > 1e15 * 31557600) return L("des milliards d'années", "billions of years");
    if (sec < 1) return L("instantané", "instant");
    var units = [
      [31557600 * 100, "siècles", "centuries"],
      [31557600, "ans", "years"],
      [2629800, "mois", "months"],
      [86400, "jours", "days"],
      [3600, "heures", "hours"],
      [60, "minutes", "minutes"],
      [1, "secondes", "seconds"]
    ];
    for (var i = 0; i < units.length; i++) {
      if (sec >= units[i][0]) {
        var v = sec / units[i][0];
        var n = v >= 1e6 ? v.toExponential(1) : Math.round(v).toLocaleString(lang() === "fr" ? "fr-FR" : "en-US");
        return n + " " + L(units[i][1], units[i][2]);
      }
    }
  }

  /* ---------- Générateur de mots de passe ---------- */
  var SETS = {
    lower: "abcdefghijklmnopqrstuvwxyz",
    upper: "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    digits: "0123456789",
    symbols: "!#$%&()*+,-./:;<=>?@[]^_{|}~"
  };
  var AMBIGUOUS = /[Il1O0o|]/g;

  function initGenerator() {
    var range = $("#pg-length-range"), num = $("#pg-length"), out = $("#pg-output");
    var info = $("#pg-info"), count = $("#pg-count"), list = $("#pg-list");

    function sets() {
      var res = [];
      ["lower", "upper", "digits", "symbols"].forEach(function (k) {
        if ($("#pg-" + k).checked) {
          var s = SETS[k];
          if ($("#pg-ambiguous").checked) s = s.replace(AMBIGUOUS, "");
          res.push(s);
        }
      });
      return res;
    }
    function one(len, groups) {
      var pool = groups.join("");
      var chars = [];
      // au moins un caractère de chaque famille cochée, puis le reste au hasard, puis mélange
      groups.forEach(function (g) { chars.push(g[randInt(g.length)]); });
      while (chars.length < len) chars.push(pool[randInt(pool.length)]);
      chars.length = len;
      for (var i = chars.length - 1; i > 0; i--) {
        var j = randInt(i + 1), t = chars[i];
        chars[i] = chars[j]; chars[j] = t;
      }
      return chars.join("");
    }
    function generate() {
      var len = Math.min(128, Math.max(6, parseInt(num.value, 10) || 20));
      var groups = sets();
      if (!groups.length) {
        out.textContent = "";
        info.innerHTML = L("Coche au moins une famille de caractères.", "Select at least one character set.");
        list.innerHTML = "";
        return;
      }
      var pool = groups.join("").length;
      var bits = Math.floor(len * Math.log2(pool));
      out.textContent = one(len, groups);
      info.innerHTML = L("Entropie : ", "Entropy: ") + "<strong>" + bits + " bits</strong> · " +
        L(pool + " caractères possibles", pool + " possible characters");
      var n = Math.min(20, Math.max(1, parseInt(count.value, 10) || 1));
      var lines = [];
      for (var i = 1; i < n; i++) lines.push(one(len, groups));
      list.textContent = lines.join("\n");
      list.hidden = lines.length === 0;
    }
    range.addEventListener("input", function () { num.value = range.value; generate(); });
    num.addEventListener("change", function () {
      num.value = Math.min(128, Math.max(6, parseInt(num.value, 10) || 20));
      range.value = Math.min(64, num.value);
      generate();
    });
    document.querySelectorAll("#pg-options input, #pg-count").forEach(function (el) {
      el.addEventListener("change", generate);
    });
    $("#pg-generate").addEventListener("click", generate);
    $("#pg-copy-slot").appendChild(makeCopy(function () { return out.textContent; }));
    generate();
  }

  /* ---------- Vérificateur de mot de passe ---------- */
  var COMMON = ("123456 123456789 12345678 password qwerty 12345 1234567 111111 123123 abc123 password1 " +
    "1234567890 000000 iloveyou azerty qwertyuiop 654321 666666 121212 dragon monkey letmein football " +
    "sunshine princess admin welcome login master hello freedom whatever shadow superman batman trustno1 " +
    "motdepasse soleil doudou loulou chouchou marseille bonjour jetaime nicolas camille passw0rd p@ssw0rd " +
    "azerty123 qwerty123 changeme root toor test test123 secret").split(" ");
  var SEQS = ["abcdefghijklmnopqrstuvwxyz", "0123456789", "qwertyuiop", "asdfghjkl", "zxcvbnm",
    "azertyuiop", "qsdfghjklm", "wxcvbn"];

  function analyse(pw) {
    var classes = { lower: /[a-z]/.test(pw), upper: /[A-Z]/.test(pw), digits: /\d/.test(pw),
      symbols: /[\x21-\x2f\x3a-\x40\x5b-\x60\x7b-\x7e]/.test(pw),
      other: /[^\x00-\x7f]/.test(pw), space: /\s/.test(pw) };
    var pool = (classes.lower ? 26 : 0) + (classes.upper ? 26 : 0) + (classes.digits ? 10 : 0) +
      (classes.symbols ? 33 : 0) + (classes.other ? 100 : 0) + (classes.space ? 1 : 0);
    var chars = Array.from(pw);
    var bits = chars.length * Math.log2(Math.max(pool, 1));
    var notes = [];
    var low = pw.toLowerCase();
    function unleet(s) {
      return s.replace(/[@4]/g, "a").replace(/3/g, "e").replace(/[1!|]/g, "i").replace(/0/g, "o")
        .replace(/[$5]/g, "s").replace(/7/g, "t");
    }
    var leet = unleet(low);
    // mot de base : on retire d'abord les chiffres/symboles ajoutés au début et à la fin, puis on « dé-leet »
    var base = unleet(low.replace(/[\d\W_]+$/, "").replace(/^[\d\W_]+/, ""));

    if (COMMON.indexOf(low) !== -1 || COMMON.indexOf(leet) !== -1) {
      bits = Math.min(bits, 4);
      notes.push(L("Fait partie des mots de passe les plus utilisés au monde.",
        "It is one of the most used passwords in the world."));
    } else if (base.length >= 4 && COMMON.indexOf(base) !== -1) {
      bits = Math.min(bits, 14 + (chars.length - base.length) * 3.3);
      notes.push(L("Repose sur un mot de passe très courant, avec quelques caractères ajoutés.",
        "Built on a very common password with a few characters added."));
    }
    // séquences (abcd, 1234, qwerty…) dans un sens ou dans l'autre
    var seqLen = 0;
    SEQS.forEach(function (s) {
      var r = s.split("").reverse().join("");
      for (var n = Math.min(low.length, s.length); n >= 4; n--) {
        for (var i = 0; i + n <= low.length; i++) {
          var part = low.substr(i, n);
          if ((s.indexOf(part) !== -1 || r.indexOf(part) !== -1) && n > seqLen) seqLen = n;
        }
      }
    });
    if (seqLen) {
      bits -= (seqLen - 1) * Math.log2(Math.max(pool, 1)) * 0.8;
      notes.push(L("Contient une suite de touches ou de caractères (abcd, 1234, azerty…).",
        "Contains a keyboard or character sequence (abcd, 1234, qwerty…)."));
    }
    // répétitions (aaaa, ababab)
    var rep = pw.match(/(.+?)\1{2,}/g);
    if (rep) {
      var lost = rep.reduce(function (s, m) { return s + m.length; }, 0) * 0.7;
      bits -= lost * Math.log2(Math.max(pool, 1)) * 0.8;
      notes.push(L("Contient des répétitions (aaa, ababab…).", "Contains repetitions (aaa, ababab…)."));
    }
    // date ou année
    if (/(19|20)\d{2}/.test(pw)) {
      bits -= 6;
      notes.push(L("Contient une année : c'est souvent une date de naissance, facile à deviner.",
        "Contains a year: often a birth date, easy to guess."));
    }
    // modèle « Mot123! » : une majuscule au début, chiffres/symbole à la fin
    if (/^[A-Z][a-z]+[\d]+[\W_]?$/.test(pw)) {
      bits -= 8;
      notes.push(L("Suit le modèle le plus prévisible : majuscule au début, chiffres à la fin.",
        "Follows the most predictable pattern: capital first, digits at the end."));
    }
    if (chars.length < 12) {
      notes.push(L("Moins de 12 caractères : la longueur est le critère qui compte le plus.",
        "Under 12 characters: length is what matters most."));
    }
    var nClasses = ["lower", "upper", "digits", "symbols", "other"].filter(function (k) { return classes[k]; }).length;
    if (nClasses < 3 && chars.length < 16) {
      notes.push(L("Mélange davantage de types de caractères, ou allonge-le (une phrase de passe de 4-5 mots marche très bien).",
        "Mix more character types, or make it longer (a 4–5 word passphrase works very well)."));
    }
    bits = Math.max(0, bits);
    var score = bits < 28 ? 0 : bits < 40 ? 1 : bits < 60 ? 2 : bits < 80 ? 3 : 4;
    return { bits: bits, score: score, notes: notes, length: chars.length, classes: nClasses };
  }

  function initChecker() {
    var input = $("#pc-input"), bar = $("#pc-bar"), verdict = $("#pc-verdict");
    var stats = $("#pc-stats"), notes = $("#pc-notes"), leak = $("#pc-leak"), btn = $("#pc-hibp");
    var LABELS = [
      ["Très faible", "Very weak"], ["Faible", "Weak"], ["Moyen", "Fair"], ["Fort", "Strong"], ["Très fort", "Very strong"]
    ];

    function update() {
      var pw = input.value;
      msg(leak, "", "");
      btn.disabled = !pw;
      if (!pw) {
        bar.style.width = "0";
        verdict.innerHTML = "";
        stats.innerHTML = "";
        msg(notes, "", "");
        return;
      }
      var a = analyse(pw);
      bar.style.width = (20 + a.score * 20) + "%";
      bar.setAttribute("data-score", a.score);
      verdict.innerHTML = "<strong>" + L(LABELS[a.score][0], LABELS[a.score][1]) + "</strong>";
      // attaque hors ligne sur un hash rapide : 10 milliards d'essais/s, temps moyen = moitié de l'espace
      var seconds = Math.pow(2, a.bits - 1) / 1e10;
      stats.innerHTML =
        '<div class="tool-stat"><span class="tool-stat__k">' + L("longueur", "length") + '</span><span class="tool-stat__v">' + a.length + "</span></div>" +
        '<div class="tool-stat"><span class="tool-stat__k">' + L("types de caractères", "character types") + '</span><span class="tool-stat__v">' + a.classes + " / 5</span></div>" +
        '<div class="tool-stat"><span class="tool-stat__k">' + L("entropie estimée", "estimated entropy") + '</span><span class="tool-stat__v">' + Math.round(a.bits) + " bits</span></div>" +
        '<div class="tool-stat"><span class="tool-stat__k">' + L("cassage hors ligne*", "offline cracking*") + '</span><span class="tool-stat__v">' + fmtDuration(seconds) + "</span></div>";
      if (a.notes.length) {
        msg(notes, a.score >= 3 ? "" : "warn",
          L("Points d'attention :", "Things to watch:") + "<ul><li>" + a.notes.join("</li><li>") + "</li></ul>");
      } else {
        msg(notes, "ok", L("Aucun schéma prévisible détecté.", "No predictable pattern detected."));
      }
    }

    function checkLeak() {
      var pw = input.value;
      if (!pw) return;
      btn.disabled = true;
      msg(leak, "", L("Vérification en cours…", "Checking…"));
      sha("SHA-1", enc.encode(pw)).then(function (hex) {
        hex = hex.toUpperCase();
        var prefix = hex.slice(0, 5), suffix = hex.slice(5);
        return fetch("https://api.pwnedpasswords.com/range/" + prefix).then(function (r) {
          if (!r.ok) throw new Error("HTTP " + r.status);
          return r.text();
        }).then(function (body) {
          var found = 0;
          body.split("\n").some(function (line) {
            var p = line.trim().split(":");
            if (p[0] === suffix) { found = parseInt(p[1], 10) || 0; return true; }
            return false;
          });
          if (input.value !== pw) return; // le champ a changé pendant la requête
          if (found) {
            msg(leak, "bad", L("<strong>Ce mot de passe apparaît " + found.toLocaleString("fr-FR") +
              " fois dans des fuites de données.</strong> Ne l'utilise plus nulle part.",
              "<strong>This password appears " + found.toLocaleString("en-US") +
              " times in data breaches.</strong> Stop using it everywhere."));
          } else {
            msg(leak, "ok", L("Absent des fuites connues de Have I Been Pwned. Ça ne garantit pas qu'il soit robuste : regarde aussi l'analyse ci-dessus.",
              "Not found in Have I Been Pwned's known breaches. That doesn't make it strong: check the analysis above too."));
          }
        });
      }).catch(function () {
        msg(leak, "warn", L("Impossible de joindre le service de vérification. Réessaie plus tard.",
          "Could not reach the breach-check service. Try again later."));
      }).then(function () { btn.disabled = !input.value; });
    }

    input.addEventListener("input", debounce(update, 120));
    btn.addEventListener("click", checkLeak);
    $("#pc-show").addEventListener("change", function (e) {
      input.type = e.target.checked ? "text" : "password";
    });
    update();
  }

  /* ---------- Calculateur de hash ---------- */
  var ALGOS = [["MD5", null], ["SHA-1", "SHA-1"], ["SHA-256", "SHA-256"], ["SHA-384", "SHA-384"], ["SHA-512", "SHA-512"]];
  var MAX_FILE = 512 * 1024 * 1024;

  function initHash() {
    var text = $("#hh-text"), file = $("#hh-file"), list = $("#hh-list"), cmp = $("#hh-compare");
    var status = $("#hh-status"), upper = $("#hh-upper"), fileInfo = $("#hh-fileinfo");
    var outs = {}, run = 0, mode = "text";

    ALGOS.forEach(function (a) {
      var name = document.createElement("span");
      name.className = "hash-name";
      name.textContent = a[0];
      var out = document.createElement("div");
      out.className = "tool-output";
      outs[a[0]] = out;
      list.appendChild(name);
      list.appendChild(out);
      list.appendChild(makeCopy(function () { return out.textContent; }));
    });

    function compare() {
      var want = cmp.value.trim().toLowerCase();
      var hit = null;
      ALGOS.forEach(function (a) {
        var o = outs[a[0]], ok = want && o.textContent.toLowerCase() === want;
        o.classList.toggle("hash-ok", !!ok);
        if (ok) hit = a[0];
      });
      if (!want) msg(status, "", "");
      else if (hit) msg(status, "ok", L("Correspondance : " + hit + ".", "Match: " + hit + "."));
      else msg(status, "bad", L("Aucune correspondance avec les empreintes ci-dessus.", "No match with the hashes above."));
    }
    function show(bytes) {
      var id = ++run;
      var res = { MD5: md5(bytes) };
      return Promise.all(ALGOS.slice(1).map(function (a) {
        return sha(a[1], bytes).then(function (h) { res[a[0]] = h; });
      })).then(function () {
        if (id !== run) return;
        ALGOS.forEach(function (a) {
          outs[a[0]].textContent = upper.checked ? res[a[0]].toUpperCase() : res[a[0]];
        });
        compare();
      });
    }
    function fromText() { mode = "text"; fileInfo.textContent = ""; show(enc.encode(text.value)); }
    function fromFile() {
      var f = file.files && file.files[0];
      if (!f) return;
      if (f.size > MAX_FILE) {
        msg(status, "warn", L("Fichier trop volumineux (512 Mo maximum dans le navigateur).",
          "File too large (512 MB max in the browser)."));
        return;
      }
      mode = "file";
      fileInfo.textContent = f.name + " · " + (f.size / 1024).toFixed(1) + " KiB";
      msg(status, "", L("Calcul en cours…", "Hashing…"));
      f.arrayBuffer().then(function (buf) { return show(new Uint8Array(buf)); });
    }

    text.addEventListener("input", debounce(fromText, 150));
    file.addEventListener("change", fromFile);
    cmp.addEventListener("input", compare);
    upper.addEventListener("change", function () { mode === "file" ? fromFile() : fromText(); });
    fromText();
  }

  /* ---------- Encodeur / décodeur ---------- */
  function b64encode(bytes) {
    var bin = "";
    for (var i = 0; i < bytes.length; i += 0x8000) bin += String.fromCharCode.apply(null, bytes.subarray(i, i + 0x8000));
    return btoa(bin);
  }
  function b64decode(str) {
    var s = str.replace(/\s+/g, "").replace(/-/g, "+").replace(/_/g, "/");
    if (s.length % 4 === 1) throw new Error("length");
    while (s.length % 4) s += "=";
    var bin = atob(s), out = new Uint8Array(bin.length);
    for (var i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
    return out;
  }
  function bytesToText(bytes) {
    try {
      return { text: new TextDecoder("utf-8", { fatal: true }).decode(bytes), binary: false };
    } catch (e) {
      return { text: toHex(bytes).replace(/(..)(?!$)/g, "$1 "), binary: true };
    }
  }
  var CODECS = {
    base64: {
      enc: function (s) { return b64encode(enc.encode(s)); },
      dec: function (s) { return bytesToText(b64decode(s)); }
    },
    base64url: {
      enc: function (s) { return b64encode(enc.encode(s)).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, ""); },
      dec: function (s) { return bytesToText(b64decode(s)); }
    },
    url: {
      enc: function (s) { return encodeURIComponent(s); },
      dec: function (s) { return { text: decodeURIComponent(s.replace(/\+/g, " ")), binary: false }; }
    },
    hex: {
      enc: function (s) { return toHex(enc.encode(s)); },
      dec: function (s) {
        var h = s.replace(/0x/gi, "").replace(/[\s:,\\x-]/g, "");
        if (!/^[0-9a-f]*$/i.test(h) || h.length % 2) throw new Error("hex");
        var out = new Uint8Array(h.length / 2);
        for (var i = 0; i < out.length; i++) out[i] = parseInt(h.substr(i * 2, 2), 16);
        return bytesToText(out);
      }
    },
    html: {
      enc: function (s) { return esc(s); },
      dec: function (s) {
        var d = new DOMParser().parseFromString("<!doctype html><body>" + s.replace(/</g, "&lt;"), "text/html");
        return { text: d.body.textContent, binary: false };
      }
    }
  };

  function initEncoder() {
    var input = $("#ed-input"), output = $("#ed-output"), fmt = $("#ed-format"), status = $("#ed-status");
    function go(dir) {
      msg(status, "", "");
      try {
        var c = CODECS[fmt.value];
        if (dir === "enc") {
          output.value = c.enc(input.value);
        } else {
          var r = c.dec(input.value.trim());
          output.value = r.text;
          if (r.binary) msg(status, "warn", L("Le résultat n'est pas du texte : il est affiché en hexadécimal.",
            "The result isn't text, so it's shown as hexadecimal."));
        }
      } catch (e) {
        output.value = "";
        msg(status, "bad", L("Entrée invalide pour ce format.", "Invalid input for this format."));
      }
    }
    $("#ed-encode").addEventListener("click", function () { go("enc"); });
    $("#ed-decode").addEventListener("click", function () { go("dec"); });
    $("#ed-swap").addEventListener("click", function () {
      input.value = output.value;
      output.value = "";
      msg(status, "", "");
    });
  }

  /* ---------- Décodeur JWT ---------- */
  function initJwt() {
    var input = $("#jw-input"), status = $("#jw-status"), head = $("#jw-header"), body = $("#jw-payload");
    var claims = $("#jw-claims"), warn = $("#jw-warn");
    var NAMES = {
      iss: ["émetteur", "issuer"], sub: ["sujet", "subject"], aud: ["audience", "audience"],
      iat: ["émis le", "issued at"], nbf: ["valide à partir du", "not before"], exp: ["expire le", "expires"],
      jti: ["identifiant", "token id"]
    };
    function date(v) {
      var d = new Date(v * 1000);
      return isNaN(d) ? esc(v) : esc(d.toLocaleString(lang() === "fr" ? "fr-FR" : "en-GB")) + " <small>(" + esc(v) + ")</small>";
    }
    function json(part) {
      var r = bytesToText(b64decode(part));
      if (r.binary) throw new Error("binary");
      return JSON.parse(r.text);
    }
    function clear() {
      head.textContent = ""; body.textContent = ""; claims.innerHTML = ""; msg(warn, "", "");
    }
    function update() {
      var tok = input.value.trim().replace(/^bearer\s+/i, "");
      clear();
      if (!tok) { msg(status, "", ""); return; }
      var parts = tok.split(".");
      if (parts.length === 5) {
        msg(status, "warn", L("C'est un JWE (jeton chiffré) : son contenu ne peut pas être lu sans la clé.",
          "This is a JWE (encrypted token): its content can't be read without the key."));
        try { head.textContent = JSON.stringify(json(parts[0]), null, 2); } catch (e) {}
        return;
      }
      if (parts.length !== 3) {
        msg(status, "bad", L("Format invalide : un JWT contient trois parties séparées par des points.",
          "Invalid format: a JWT has three parts separated by dots."));
        return;
      }
      var h, p;
      try { h = json(parts[0]); p = json(parts[1]); } catch (e) {
        msg(status, "bad", L("Impossible de décoder l'en-tête ou le contenu (Base64URL ou JSON invalide).",
          "Could not decode the header or payload (invalid Base64URL or JSON)."));
        return;
      }
      head.textContent = JSON.stringify(h, null, 2);
      body.textContent = JSON.stringify(p, null, 2);

      var now = Date.now() / 1000, rows = [];
      if (h.alg) rows.push([L("algorithme", "algorithm"), esc(h.alg)]);
      Object.keys(NAMES).forEach(function (k) {
        if (p[k] === undefined) return;
        var v = /^(iat|nbf|exp)$/.test(k) && typeof p[k] === "number" ? date(p[k]) : esc(Array.isArray(p[k]) ? p[k].join(", ") : p[k]);
        rows.push([L(NAMES[k][0], NAMES[k][1]) + " <small>(" + k + ")</small>", v]);
      });
      claims.innerHTML = rows.map(function (r) {
        return '<div class="tool-stat"><span class="tool-stat__k">' + r[0] + '</span><span class="tool-stat__v">' + r[1] + "</span></div>";
      }).join("");

      if (typeof p.exp === "number" && p.exp < now) {
        msg(status, "bad", L("Jeton <strong>expiré</strong>.", "Token <strong>expired</strong>."));
      } else if (typeof p.nbf === "number" && p.nbf > now) {
        msg(status, "warn", L("Jeton <strong>pas encore valide</strong> (nbf dans le futur).", "Token <strong>not valid yet</strong> (nbf in the future)."));
      } else if (typeof p.exp === "number") {
        msg(status, "ok", L("Jeton dans sa période de validité.", "Token within its validity period."));
      } else {
        msg(status, "warn", L("Aucune date d'expiration (exp) : ce jeton reste valable indéfiniment.", "No expiry (exp): this token never expires."));
      }

      var w = [];
      var alg = String(h.alg || "").toLowerCase();
      if (!alg || alg === "none") {
        w.push(L("<strong>alg: none</strong> : jeton non signé. Un serveur qui l'accepte peut être contourné.",
          "<strong>alg: none</strong>: unsigned token. A server that accepts it can be bypassed."));
      } else if (/^hs/.test(alg)) {
        w.push(L("Signature HMAC à secret partagé : sa robustesse dépend entièrement de la longueur du secret.",
          "Shared-secret HMAC signature: its strength depends entirely on the secret's length."));
      }
      if (h.jku || h.x5u) w.push(L("L'en-tête pointe vers une clé distante (jku/x5u) : le serveur doit restreindre les URL acceptées.",
        "The header points to a remote key (jku/x5u): the server must restrict accepted URLs."));
      if (h.kid && /[\/\\.'";]/.test(String(h.kid))) w.push(L("Le kid contient des caractères inhabituels : vérifie qu'il n'est pas utilisé tel quel dans un chemin ou une requête.",
        "The kid contains unusual characters: make sure it isn't used as-is in a path or query."));
      if (/(passw|secret|pwd|card|iban)/i.test(JSON.stringify(p))) w.push(L("Le contenu semble contenir une donnée sensible : un JWT signé n'est pas chiffré, tout le monde peut le lire.",
        "The payload seems to hold sensitive data: a signed JWT isn't encrypted, anyone can read it."));
      w.push(L("La signature n'est pas vérifiée ici : décoder un jeton ne prouve pas qu'il est authentique.",
        "The signature isn't verified here: decoding a token doesn't prove it's genuine."));
      msg(warn, "warn", "<ul><li>" + w.join("</li><li>") + "</li></ul>");
    }
    input.addEventListener("input", debounce(update, 120));
    update();
  }

  /* ---------- IOC : extraction, defang, refang ---------- */
  var FILE_EXT = ("exe dll sys bat cmd ps1 psm1 vbs js jse wsf hta lnk msi scr cpl jar py sh pl rb php asp aspx jsp " +
    "txt log csv json xml yml yaml ini cfg conf dat tmp bak html htm css md doc docx xls xlsx xlsm ppt pptx pdf rtf " +
    "png jpg jpeg gif bmp svg ico zip rar 7z gz tar tgz iso img vhd bin elf so dylib apk ipa dmg pkg mov mp4 mp3 avi wav").split(" ");
  var RE = {
    url: /\b(?:https?|ftp):\/\/[^\s"'<>()\[\]{}]+/gi,
    email: /\b[a-z0-9._%+-]+@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z]{2,24}\b/gi,
    ipv4: /\b(?:(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.){3}(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\b/g,
    domain: /\b(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z][a-z0-9-]{1,23}\b/gi,
    sha256: /\b[a-f0-9]{64}\b/gi,
    sha1: /\b[a-f0-9]{40}\b/gi,
    md5: /\b[a-f0-9]{32}\b/gi,
    cve: /\bCVE-\d{4}-\d{4,7}\b/gi
  };
  function trimUrl(u) { return u.replace(/[.,;:!?'"]+$/, ""); }
  function isDomain(d) {
    var tld = d.split(".").pop().toLowerCase();
    return FILE_EXT.indexOf(tld) === -1 && /[a-z]/i.test(tld) && !/^\d+$/.test(tld);
  }
  function isPrivate(ip) {
    var o = ip.split(".").map(Number);
    return o[0] === 10 || o[0] === 127 || (o[0] === 172 && o[1] >= 16 && o[1] <= 31) ||
      (o[0] === 192 && o[1] === 168) || (o[0] === 169 && o[1] === 254) || o[0] === 0 || o[0] >= 224;
  }
  function refang(s) {
    return s
      .replace(/h(?:xx|\*\*|XX)p(s?)/gi, "http$1")
      .replace(/f(?:xx|XX)p/gi, "ftp")
      .replace(/\[:\/\/\]|\[:\]\/\//g, "://")
      .replace(/\s*[\[\(\{]\s*(?:\.|dot)\s*[\]\)\}]\s*/gi, ".")
      .replace(/\s*[\[\(\{]\s*(?:@|at)\s*[\]\)\}]\s*/gi, "@")
      .replace(/\[:\]/g, ":");
  }
  function defangHost(h) { return h.replace(/\./g, "[.]"); }
  function defangUrl(u) {
    var m = u.match(/^([a-z]+):\/\/([^\/?#]*)(.*)$/i);
    if (!m) return u;
    var scheme = m[1].replace(/^http/i, "hxxp").replace(/^ftp/i, "fxp");
    return scheme + "://" + defangHost(m[2]) + m[3];
  }
  function defang(s) {
    return s
      .replace(RE.url, function (u) { var t = trimUrl(u); return defangUrl(t) + u.slice(t.length); })
      .replace(RE.email, function (e) { return e.replace("@", "[@]").replace(/\./g, "[.]"); })
      .replace(RE.ipv4, defangHost)
      .replace(RE.domain, function (d) { return isDomain(d) ? defangHost(d) : d; });
  }
  function uniq(arr) {
    var seen = {}, out = [];
    arr.forEach(function (x) { var k = x.toLowerCase(); if (!seen[k]) { seen[k] = 1; out.push(x); } });
    return out;
  }
  function extract(s) {
    var t = refang(s);
    var urls = uniq((t.match(RE.url) || []).map(trimUrl));
    var emails = uniq(t.match(RE.email) || []);
    var ips = uniq(t.match(RE.ipv4) || []);
    var domains = uniq((t.match(RE.domain) || []).filter(isDomain).map(function (d) { return d.toLowerCase(); }));
    var sha256 = uniq(t.match(RE.sha256) || []);
    var noSha256 = t.replace(RE.sha256, " ");
    var sha1 = uniq(noSha256.match(RE.sha1) || []);
    var md5s = uniq(noSha256.replace(RE.sha1, " ").match(RE.md5) || []);
    var cves = uniq((t.match(RE.cve) || []).map(function (c) { return c.toUpperCase(); }));
    return [
      ["URL", urls, "url"], [L("Domaines", "Domains"), domains, "domain"], ["IPv4", ips, "ip"],
      ["Emails", emails, "email"], ["SHA-256", sha256], ["SHA-1", sha1], ["MD5", md5s], ["CVE", cves]
    ];
  }

  function initIoc() {
    var input = $("#io-input"), outBox = $("#io-results"), status = $("#io-status");
    var defOut = $("#io-defang-out"), outText = $("#io-text");

    function renderExtract() {
      var groups = extract(input.value), total = 0, wantDefang = defOut.checked;
      outBox.innerHTML = "";
      outText.parentNode.hidden = true;
      groups.forEach(function (g) {
        if (!g[1].length) return;
        total += g[1].length;
        var items = g[1].map(function (v) {
          if (!wantDefang) return v;
          if (g[2] === "url") return defangUrl(v);
          if (g[2] === "email") return v.replace("@", "[@]").replace(/\./g, "[.]");
          if (g[2] === "domain" || g[2] === "ip") return defangHost(v);
          return v;
        });
        var wrap = document.createElement("div");
        wrap.className = "ioc-group";
        var headEl = document.createElement("div");
        headEl.className = "ioc-group__head";
        var label = document.createElement("span");
        label.innerHTML = g[0] + " (" + g[1].length + ")";
        headEl.appendChild(label);
        var text = items.join("\n");
        headEl.appendChild(makeCopy(function () { return text; }));
        var pre = document.createElement("pre");
        pre.className = "tool-output";
        if (g[2] === "ip") {
          pre.innerHTML = g[1].map(function (ip, i) {
            return esc(items[i]) + (isPrivate(ip) ? '  <small style="color:var(--muted)">' + L("(privée/réservée)", "(private/reserved)") + "</small>" : "");
          }).join("\n");
        } else {
          pre.textContent = text;
        }
        wrap.appendChild(headEl);
        wrap.appendChild(pre);
        outBox.appendChild(wrap);
      });
      if (!input.value.trim()) msg(status, "", "");
      else if (total) msg(status, "ok", L(total + " indicateur(s) trouvé(s), doublons retirés.", total + " indicator(s) found, duplicates removed."));
      else msg(status, "warn", L("Aucun indicateur trouvé.", "No indicators found."));
    }
    function renderText(fn) {
      outBox.innerHTML = "";
      msg(status, "", "");
      outText.textContent = fn(input.value);
      outText.parentNode.hidden = false;
    }
    $("#io-extract").addEventListener("click", renderExtract);
    $("#io-defang").addEventListener("click", function () { renderText(defang); });
    $("#io-refang").addEventListener("click", function () { renderText(refang); });
    defOut.addEventListener("change", function () { if (outBox.children.length) renderExtract(); });
    $("#io-text-copy").appendChild(makeCopy(function () { return outText.textContent; }));
  }

  /* ---------- Démarrage ---------- */
  var INIT = { generator: initGenerator, checker: initChecker, hash: initHash, encoder: initEncoder, jwt: initJwt, ioc: initIoc };
  function start() {
    applyPlaceholders();
    var main = document.querySelector("main[data-tool]");
    if (main && INIT[main.getAttribute("data-tool")]) INIT[main.getAttribute("data-tool")]();
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start);
  else start();
})();
