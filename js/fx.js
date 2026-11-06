/* Effets communs du site (kit repris de la page Actus).
   - Les éléments [data-reveal] apparaissent en cascade quand ils entrent à l'écran.
   - Sans JavaScript, ou si l'utilisateur réduit les animations, tout est visible d'emblée.
   Chargé dans <head> pour poser la classe fx-js avant le premier affichage (pas de clignotement). */
(function () {
  "use strict";
  var root = document.documentElement;
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (!reduce && "IntersectionObserver" in window) root.classList.add("fx-js");

  function init() {
    var els = Array.prototype.slice.call(document.querySelectorAll("[data-reveal]"));
    // délai en cascade selon le rang parmi les éléments révélés du même parent (style posé
    // par le CSSOM : autorisé par la CSP, contrairement à un attribut style="")
    var rank = new Map();
    els.forEach(function (el) {
      var i = rank.get(el.parentNode) || 0;
      rank.set(el.parentNode, i + 1);
      el.style.setProperty("--d", Math.min(i, 8) * 70 + "ms");
    });
    if (!root.classList.contains("fx-js")) {
      els.forEach(function (el) { el.classList.add("is-in"); });
    } else {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting) {
            e.target.classList.add("is-in");
            io.unobserve(e.target);
          }
        });
      }, { rootMargin: "0px 0px -6% 0px", threshold: 0.06 });
      els.forEach(function (el) { io.observe(el); });
    }

    // page 404 : affiche le chemin demandé (texte brut, jamais interprété comme du HTML)
    var p = document.querySelector("[data-path]");
    if (p) {
      var path = location.pathname;
      try { path = decodeURIComponent(path); } catch (err) { /* chemin mal encodé : affiché tel quel */ }
      p.textContent = path.slice(0, 120);
    }
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
