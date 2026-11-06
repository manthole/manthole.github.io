/* Préférences d'affichage : langue (français, anglais, espagnol, portugais, allemand) et mode
   sombre / clair (sombre par défaut, choix mémorisé sous la clé « mode » ; la clé « theme » est
   effacée à chaque chargement par le script du thème Hugo, d'où ce nom distinct).
   Chargé dans le <head> pour fixer <html lang> avant l'affichage de la page (pas de clignotement) ;
   css/cyber.css masque ensuite tous les éléments [lang] qui ne sont pas dans la langue choisie.
   Chaque texte existe dans les 5 langues (l'anglais sert de texte de repli si une traduction manque).
   Langue par défaut : le dernier choix du visiteur, sinon celle de son navigateur, sinon l'anglais. */
(function () {
  var root = document.documentElement;
  var LANGS = ["fr", "en", "es", "pt", "de"];
  var title = document.querySelector("title");
  var titleEn = document.title;

  function apply(lang) {
    root.lang = lang;
    if (title) document.title = (lang !== "en" && title.getAttribute("data-" + lang)) || titleEn;
    var items = document.querySelectorAll("[data-set-lang]");
    for (var i = 0; i < items.length; i++) {
      items[i].setAttribute("aria-checked", items[i].getAttribute("data-set-lang") === lang ? "true" : "false");
    }
  }

  function detect() {
    var saved = null;
    try { saved = localStorage.getItem("lang"); } catch (e) {}
    if (LANGS.indexOf(saved) >= 0) return saved;
    var prefs = navigator.languages && navigator.languages.length ? navigator.languages : [navigator.language || ""];
    for (var i = 0; i < prefs.length; i++) {
      var code = String(prefs[i]).slice(0, 2).toLowerCase();
      if (LANGS.indexOf(code) >= 0) return code;
    }
    return "en";
  }
  apply(detect());

  /* ---------- Mode sombre / clair ---------- */
  var META = { dark: "#0d1117", light: "#f5f7fa" };
  function applyMode(mode) {
    root.setAttribute("data-theme", mode);
    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.setAttribute("content", META[mode]);
    var btns = document.querySelectorAll(".mode-toggle");
    for (var i = 0; i < btns.length; i++) btns[i].setAttribute("aria-pressed", mode === "light" ? "true" : "false");
  }
  var savedMode = null;
  try { savedMode = localStorage.getItem("mode"); } catch (e) {}
  applyMode(savedMode === "light" ? "light" : "dark");

  function switchMode(btn) {
    var next = root.getAttribute("data-theme") === "light" ? "dark" : "light";
    try { localStorage.setItem("mode", next); } catch (e) {}
    var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduce) { applyMode(next); return; }
    if (document.startViewTransition) {
      // cercle qui s'étend depuis le bouton jusqu'au coin le plus éloigné
      var r = btn.getBoundingClientRect();
      var x = r.left + r.width / 2, y = r.top + r.height / 2;
      var radius = Math.hypot(Math.max(x, innerWidth - x), Math.max(y, innerHeight - y));
      var t = document.startViewTransition(function () { applyMode(next); });
      t.ready.then(function () {
        root.animate({ clipPath: ["circle(0px at " + x + "px " + y + "px)", "circle(" + radius + "px at " + x + "px " + y + "px)"] },
          { duration: 600, easing: "cubic-bezier(0.4, 0, 0.2, 1)", pseudoElement: "::view-transition-new(root)" });
      }).catch(function () {});
    } else {
      root.classList.add("mode-anim");
      applyMode(next);
      setTimeout(function () { root.classList.remove("mode-anim"); }, 400);
    }
  }

  /* ---------- Liste déroulante (menu accessible au clavier) ---------- */
  function menu() { return document.querySelector(".lang-menu"); }
  function items() { var m = menu(); return m ? Array.prototype.slice.call(m.querySelectorAll("[data-set-lang]")) : []; }

  function open(focusCurrent) {
    var m = menu();
    if (!m) return;
    m.classList.add("is-open");
    m.querySelector(".lang-switch").setAttribute("aria-expanded", "true");
    if (focusCurrent) {
      var cur = m.querySelector('[data-set-lang="' + root.lang + '"]') || items()[0];
      if (cur) cur.focus();
    }
  }
  function close(focusButton) {
    var m = menu();
    if (!m || !m.classList.contains("is-open")) return;
    m.classList.remove("is-open");
    var btn = m.querySelector(".lang-switch");
    btn.setAttribute("aria-expanded", "false");
    if (focusButton) btn.focus();
  }

  document.addEventListener("click", function (e) {
    var modeBtn = e.target.closest(".mode-toggle");
    if (modeBtn) { switchMode(modeBtn); return; }
    var choice = e.target.closest("[data-set-lang]");
    if (choice) {
      var lang = choice.getAttribute("data-set-lang");
      if (LANGS.indexOf(lang) < 0) return;
      apply(lang);
      try { localStorage.setItem("lang", lang); } catch (err) {}
      close(true);
      return;
    }
    if (e.target.closest(".lang-switch")) {
      var m = menu();
      if (m && m.classList.contains("is-open")) close(false);
      else open(e.detail === 0); // clavier (Entrée/Espace) : focus sur la langue active
      return;
    }
    if (!e.target.closest(".lang-menu")) close(false);
  });

  document.addEventListener("keydown", function (e) {
    var m = menu();
    if (!m) return;
    var inMenu = m.contains(document.activeElement);
    if (e.key === "Escape" && m.classList.contains("is-open")) {
      close(true);
      return;
    }
    if (!inMenu) return;
    var list = items();
    var i = list.indexOf(document.activeElement);
    if (e.key === "ArrowDown" || e.key === "ArrowUp") {
      e.preventDefault();
      if (!m.classList.contains("is-open")) { open(true); return; }
      var n = e.key === "ArrowDown" ? i + 1 : i - 1;
      list[(n + list.length) % list.length].focus();
    } else if (e.key === "Home" || e.key === "End") {
      if (!m.classList.contains("is-open")) return;
      e.preventDefault();
      list[e.key === "Home" ? 0 : list.length - 1].focus();
    } else if (e.key === "Tab" && m.classList.contains("is-open")) {
      close(false);
    }
  });

  document.addEventListener("DOMContentLoaded", function () { apply(root.lang); applyMode(root.getAttribute("data-theme")); });

  /* Anti-clickjacking. La protection normale (en-tête CSP frame-ancestors ou X-Frame-Options) est
     impossible sur GitHub Pages, et frame-ancestors est ignoré dans une balise <meta>. Si la page est
     chargée dans un cadre d'un autre site, on masque son contenu et on propose de l'ouvrir directement. */
  var framed = true;
  try { framed = window.top !== window.self; } catch (e) {}
  if (framed) {
    root.style.visibility = "hidden";
    document.addEventListener("DOMContentLoaded", function () {
      var a = document.createElement("a");
      a.href = location.href;
      a.target = "_top";
      a.rel = "noopener";
      a.textContent = "Ouvrir manthole.github.io / Open manthole.github.io";
      document.body.textContent = "";
      document.body.appendChild(a);
      root.style.visibility = "visible";
    });
  }
})();
