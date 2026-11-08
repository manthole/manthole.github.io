/* Outils e-mail de manthole.github.io :
   - analyseur d'en-têtes (data-tool="headers") : tout est analysé dans le navigateur, rien n'est envoyé ;
   - vérificateur DNS d'un domaine (data-tool="dns") : requêtes DNS publiques via DNS-over-HTTPS
     (Cloudflare 1.1.1.1), seul le nom de domaine saisi quitte le navigateur.
   Textes en 5 langues : un <span lang> par langue, masqués par css/cyber.css. */
(function () {
  "use strict";

  var LANGS = ["fr", "en", "es", "pt", "de"];
  function M(fr, en, es, pt, de) { return { fr: fr, en: en, es: es, pt: pt, de: de }; }
  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  /* t : objet M() ; vars : valeurs déjà échappées, insérées à la place de {nom} */
  function T(t, vars) {
    return LANGS.map(function (l) {
      var s = t[l] || t.en;
      Object.keys(vars || {}).forEach(function (k) { s = s.split("{" + k + "}").join(vars[k]); });
      return '<span lang="' + l + '">' + s + "</span>";
    }).join("");
  }
  function $(sel) { return document.querySelector(sel); }
  function finding(level, msg, vars) {
    return { level: level, html: T(msg, vars) };
  }
  function renderFindings(ul, list) {
    var order = { bad: 0, warn: 1, info: 2, ok: 3 };
    list.sort(function (a, b) { return order[a.level] - order[b.level]; });
    ul.innerHTML = list.map(function (f) {
      return '<li class="mail-f mail-f--' + f.level + '"><span class="mail-f__icon" aria-hidden="true">' +
        { bad: "✗", warn: "!", info: "i", ok: "✓" }[f.level] + "</span><span>" + f.html + "</span></li>";
    }).join("");
  }
  function badge(level, label) {
    return '<span class="mail-badge mail-badge--' + level + '">' + label + "</span>";
  }

  /* Domaine « organisationnel » (approximation sans la Public Suffix List complète) */
  var MULTI = ["co.uk", "org.uk", "ac.uk", "gov.uk", "com.au", "net.au", "org.au", "co.nz", "co.jp", "ne.jp", "or.jp",
    "com.br", "com.mx", "co.za", "com.tr", "com.cn", "gouv.fr", "asso.fr", "co.in", "com.sg", "com.hk", "co.kr",
    "com.ar", "com.es", "com.pt", "co.il", "com.pl", "co.at", "com.be"];
  function orgDomain(d) {
    var p = String(d || "").toLowerCase().replace(/\.$/, "").split(".").filter(Boolean);
    if (p.length <= 2) return p.join(".");
    return MULTI.indexOf(p.slice(-2).join(".")) >= 0 ? p.slice(-3).join(".") : p.slice(-2).join(".");
  }
  function isIp(s) { return /^(?:\d{1,3}\.){3}\d{1,3}$/.test(s) || (/:/.test(s) && /^[0-9a-f:.]+$/i.test(s)); }
  function isPrivate(ip) {
    if (/:/.test(ip)) return /^(?:::1$|f[cd]|fe80)/i.test(ip);
    var p = ip.split(".").map(Number);
    return p[0] === 10 || p[0] === 127 || (p[0] === 172 && p[1] >= 16 && p[1] <= 31) || (p[0] === 192 && p[1] === 168) ||
      (p[0] === 169 && p[1] === 254) || (p[0] === 100 && p[1] >= 64 && p[1] <= 127) || p[0] === 0;
  }

  /* =====================================================================
     Analyseur d'en-têtes
     ===================================================================== */
  var H = {
    noHeaders: M("Aucune en-tête reconnue. Colle les en-têtes brutes du message (« Afficher l'original » dans Gmail, « Afficher la source » ailleurs).",
      "No header recognised. Paste the raw message headers (“Show original” in Gmail, “View source” elsewhere).",
      "No se reconoce ningún encabezado. Pega los encabezados en bruto del mensaje («Mostrar original» en Gmail, «Ver código fuente» en otros).",
      "Nenhum cabeçalho reconhecido. Cola os cabeçalhos brutos da mensagem («Mostrar original» no Gmail, «Ver código-fonte» noutros).",
      "Kein Header erkannt. Füge die rohen Header der Nachricht ein („Original anzeigen“ in Gmail, „Quelltext anzeigen“ anderswo)."),
    parsed: M("{n} en-têtes analysées, {h} serveurs traversés.", "{n} headers analysed, {h} servers crossed.", "{n} encabezados analizados, {h} servidores atravesados.", "{n} cabeçalhos analisados, {h} servidores atravessados.", "{n} Header analysiert, {h} Server durchlaufen."),
    spfPass: M("SPF réussi : le serveur d'envoi est autorisé pour <code>{d}</code>.", "SPF pass: the sending server is authorised for <code>{d}</code>.", "SPF correcto: el servidor de envío está autorizado para <code>{d}</code>.", "SPF aprovado: o servidor de envio está autorizado para <code>{d}</code>.", "SPF bestanden: Der sendende Server ist für <code>{d}</code> autorisiert."),
    spfFail: M("SPF en échec ({r}) : le serveur d'envoi n'est pas autorisé à envoyer pour <code>{d}</code>.", "SPF failed ({r}): the sending server is not authorised to send for <code>{d}</code>.", "SPF fallido ({r}): el servidor de envío no está autorizado a enviar por <code>{d}</code>.", "SPF falhou ({r}): o servidor de envio não está autorizado a enviar por <code>{d}</code>.", "SPF fehlgeschlagen ({r}): Der sendende Server darf nicht für <code>{d}</code> senden."),
    spfWeak: M("SPF non concluant ({r}) pour <code>{d}</code>.", "SPF inconclusive ({r}) for <code>{d}</code>.", "SPF no concluyente ({r}) para <code>{d}</code>.", "SPF inconclusivo ({r}) para <code>{d}</code>.", "SPF nicht eindeutig ({r}) für <code>{d}</code>."),
    spfNone: M("Aucun résultat SPF trouvé dans les en-têtes.", "No SPF result found in the headers.", "No se encontró ningún resultado SPF en los encabezados.", "Nenhum resultado SPF encontrado nos cabeçalhos.", "Kein SPF-Ergebnis in den Headern gefunden."),
    dkimPass: M("DKIM valide : le message est signé par <code>{d}</code> et n'a pas été modifié.", "DKIM valid: the message is signed by <code>{d}</code> and was not altered.", "DKIM válido: el mensaje está firmado por <code>{d}</code> y no se ha modificado.", "DKIM válido: a mensagem está assinada por <code>{d}</code> e não foi alterada.", "DKIM gültig: Die Nachricht ist von <code>{d}</code> signiert und wurde nicht verändert."),
    dkimFail: M("Signature DKIM invalide ({r}) : message modifié en route ou signature falsifiée.", "Invalid DKIM signature ({r}): message altered in transit or forged signature.", "Firma DKIM no válida ({r}): mensaje modificado en tránsito o firma falsificada.", "Assinatura DKIM inválida ({r}): mensagem alterada em trânsito ou assinatura falsificada.", "Ungültige DKIM-Signatur ({r}): Nachricht unterwegs verändert oder Signatur gefälscht."),
    dkimNone: M("Pas de signature DKIM vérifiée.", "No verified DKIM signature.", "Ninguna firma DKIM verificada.", "Nenhuma assinatura DKIM verificada.", "Keine verifizierte DKIM-Signatur."),
    dmarcPass: M("DMARC réussi pour <code>{d}</code> : le domaine affiché dans « De » est authentifié.", "DMARC pass for <code>{d}</code>: the domain shown in “From” is authenticated.", "DMARC correcto para <code>{d}</code>: el dominio mostrado en «De» está autenticado.", "DMARC aprovado para <code>{d}</code>: o domínio mostrado em «De» está autenticado.", "DMARC bestanden für <code>{d}</code>: Die in „Von“ angezeigte Domain ist authentifiziert."),
    dmarcFail: M("DMARC en échec pour <code>{d}</code> : l'expéditeur affiché n'est pas authentifié. Signe classique d'usurpation.", "DMARC failed for <code>{d}</code>: the displayed sender is not authenticated. A classic spoofing sign.", "DMARC fallido para <code>{d}</code>: el remitente mostrado no está autenticado. Señal clásica de suplantación.", "DMARC falhou para <code>{d}</code>: o remetente mostrado não está autenticado. Sinal clássico de usurpação.", "DMARC fehlgeschlagen für <code>{d}</code>: Der angezeigte Absender ist nicht authentifiziert. Ein klassisches Spoofing-Zeichen."),
    dmarcNone: M("Pas de résultat DMARC exploitable ({r}).", "No usable DMARC result ({r}).", "Ningún resultado DMARC utilizable ({r}).", "Nenhum resultado DMARC utilizável ({r}).", "Kein verwertbares DMARC-Ergebnis ({r})."),
    replyTo: M("La réponse partira vers <code>{r}</code>, un autre domaine que l'expéditeur (<code>{f}</code>) : technique courante de fraude au président et de phishing.", "Replies will go to <code>{r}</code>, a different domain from the sender (<code>{f}</code>): a common CEO-fraud and phishing technique.", "La respuesta irá a <code>{r}</code>, un dominio distinto del remitente (<code>{f}</code>): técnica habitual de fraude del CEO y phishing.", "A resposta irá para <code>{r}</code>, um domínio diferente do remetente (<code>{f}</code>): técnica comum de fraude do CEO e phishing.", "Antworten gehen an <code>{r}</code>, eine andere Domain als der Absender (<code>{f}</code>): eine gängige CEO-Fraud- und Phishing-Technik."),
    displaySpoof: M("Le nom affiché contient l'adresse <code>{n}</code>, mais le vrai expéditeur est <code>{f}</code> : usurpation par le nom d'affichage.", "The display name contains the address <code>{n}</code>, but the real sender is <code>{f}</code>: display-name spoofing.", "El nombre mostrado contiene la dirección <code>{n}</code>, pero el remitente real es <code>{f}</code>: suplantación por nombre visible.", "O nome mostrado contém o endereço <code>{n}</code>, mas o verdadeiro remetente é <code>{f}</code>: usurpação pelo nome de apresentação.", "Der Anzeigename enthält die Adresse <code>{n}</code>, der echte Absender ist aber <code>{f}</code>: Spoofing über den Anzeigenamen."),
    returnPath: M("Adresse de retour (<code>{r}</code>) d'un autre domaine que l'expéditeur (<code>{f}</code>). Normal pour une newsletter ou un service d'envoi, suspect sinon.", "Return path (<code>{r}</code>) on a different domain from the sender (<code>{f}</code>). Normal for a newsletter or mailing service, suspicious otherwise.", "Dirección de retorno (<code>{r}</code>) de otro dominio que el remitente (<code>{f}</code>). Normal en un boletín o servicio de envío, sospechoso si no.", "Endereço de retorno (<code>{r}</code>) de outro domínio que o remetente (<code>{f}</code>). Normal numa newsletter ou serviço de envio, suspeito caso contrário.", "Rücklaufadresse (<code>{r}</code>) auf einer anderen Domain als der Absender (<code>{f}</code>). Normal bei Newslettern oder Versanddiensten, sonst verdächtig."),
    puny: M("Le domaine de l'expéditeur <code>{d}</code> est en punycode : il peut imiter un domaine connu avec des caractères d'un autre alphabet.", "The sender's domain <code>{d}</code> is punycode: it may imitate a known domain with characters from another alphabet.", "El dominio del remitente <code>{d}</code> está en punycode: puede imitar un dominio conocido con caracteres de otro alfabeto.", "O domínio do remetente <code>{d}</code> está em punycode: pode imitar um domínio conhecido com caracteres de outro alfabeto.", "Die Absender-Domain <code>{d}</code> ist Punycode: Sie kann mit Zeichen eines anderen Alphabets eine bekannte Domain imitieren."),
    free: M("Expéditeur sur une messagerie gratuite (<code>{d}</code>) : à vérifier si le message prétend venir d'une entreprise.", "Sender on a free mail service (<code>{d}</code>): check it if the message claims to come from a company.", "Remitente en un correo gratuito (<code>{d}</code>): compruébalo si el mensaje dice venir de una empresa.", "Remetente num correio gratuito (<code>{d}</code>): verifica se a mensagem diz vir de uma empresa.", "Absender bei einem kostenlosen Mail-Dienst (<code>{d}</code>): prüfen, wenn die Nachricht angeblich von einer Firma stammt."),
    delay: M("Le message est resté {t} entre deux serveurs (étape {i}) : file d'attente, filtrage ou horloge décalée.", "The message spent {t} between two servers (hop {i}): queueing, filtering or clock skew.", "El mensaje pasó {t} entre dos servidores (salto {i}): cola, filtrado o reloj desfasado.", "A mensagem esteve {t} entre dois servidores (salto {i}): fila de espera, filtragem ou relógio desfasado.", "Die Nachricht lag {t} zwischen zwei Servern (Hop {i}): Warteschlange, Filterung oder falsch gehende Uhr."),
    origin: M("Adresse IP d'origine probable : <code>{ip}</code> (premier serveur public de la chaîne).", "Likely origin IP: <code>{ip}</code> (first public server in the chain).", "IP de origen probable: <code>{ip}</code> (primer servidor público de la cadena).", "IP de origem provável: <code>{ip}</code> (primeiro servidor público da cadeia).", "Wahrscheinliche Ursprungs-IP: <code>{ip}</code> (erster öffentlicher Server der Kette)."),
    trust: M("Résultats lus dans l'en-tête Authentication-Results la plus haute, ajoutée par <code>{s}</code>. Les en-têtes plus bas peuvent avoir été écrits par l'expéditeur lui-même.", "Results read from the topmost Authentication-Results header, added by <code>{s}</code>. Lower headers may have been written by the sender itself.", "Resultados leídos en el encabezado Authentication-Results más alto, añadido por <code>{s}</code>. Los encabezados inferiores pueden haberlos escrito el propio remitente.", "Resultados lidos no cabeçalho Authentication-Results mais acima, adicionado por <code>{s}</code>. Os cabeçalhos mais abaixo podem ter sido escritos pelo próprio remetente.", "Ergebnisse aus dem obersten Authentication-Results-Header, hinzugefügt von <code>{s}</code>. Weiter unten stehende Header kann der Absender selbst geschrieben haben."),
    lbl: {
      from: M("De", "From", "De", "De", "Von"), replyTo: M("Répondre à", "Reply-To", "Responder a", "Responder a", "Antwort an"),
      returnPath: M("Adresse de retour", "Return-Path", "Dirección de retorno", "Endereço de retorno", "Rücklaufadresse"),
      to: M("À", "To", "Para", "Para", "An"), subject: M("Objet", "Subject", "Asunto", "Assunto", "Betreff"),
      date: M("Date", "Date", "Fecha", "Data", "Datum"), msgid: M("Message-ID", "Message-ID", "Message-ID", "Message-ID", "Message-ID"),
      client: M("Logiciel d'envoi", "Mailer", "Programa de envío", "Programa de envio", "Mailprogramm"),
      origIp: M("IP de l'expéditeur", "Sender IP", "IP del remitente", "IP do remetente", "Absender-IP"),
      dkimSig: M("Signature DKIM", "DKIM signature", "Firma DKIM", "Assinatura DKIM", "DKIM-Signatur")
    },
    hopFrom: M("de", "from", "de", "de", "von"), hopBy: M("reçu par", "received by", "recibido por", "recebido por", "empfangen von"),
    priv: M("privée", "private", "privada", "privada", "privat"),
    start: M("départ", "start", "salida", "partida", "Start"),
    noDate: M("date illisible", "unreadable date", "fecha ilegible", "data ilegível", "Datum unlesbar"),
    lookup: M("rechercher", "look up", "buscar", "pesquisar", "nachschlagen")
  };
  var FREE = ["gmail.com", "googlemail.com", "outlook.com", "hotmail.com", "hotmail.fr", "live.com", "live.fr", "msn.com", "yahoo.com", "yahoo.fr",
    "aol.com", "icloud.com", "me.com", "gmx.com", "gmx.de", "gmx.fr", "web.de", "proton.me", "protonmail.com", "laposte.net", "orange.fr",
    "wanadoo.fr", "free.fr", "sfr.fr", "yandex.com", "yandex.ru", "mail.ru", "zoho.com", "mail.com"];

  function decodeWords(s) {
    return String(s).replace(/=\?([^?\s]+)\?([BbQq])\?([^?]*)\?=(?:\s+(?==\?))?/g, function (all, cs, enc, txt) {
      try {
        var arr = [], i;
        if (enc.toUpperCase() === "B") {
          var bin = atob(txt.replace(/\s/g, ""));
          for (i = 0; i < bin.length; i++) arr.push(bin.charCodeAt(i));
        } else {
          txt = txt.replace(/_/g, " ");
          for (i = 0; i < txt.length; i++) {
            if (txt[i] === "=" && /^[0-9A-F]{2}$/i.test(txt.substr(i + 1, 2))) { arr.push(parseInt(txt.substr(i + 1, 2), 16)); i += 2; }
            else arr.push(txt.charCodeAt(i) & 255);
          }
        }
        return new TextDecoder(cs.toLowerCase().replace(/\*.*$/, "")).decode(new Uint8Array(arr));
      } catch (e) { return all; }
    });
  }
  function parseHeaders(raw) {
    raw = String(raw).replace(/\r\n?/g, "\n").replace(/^\s+/, "");
    var end = raw.search(/\n[ \t]*\n/);
    if (end > 0) raw = raw.slice(0, end);
    var list = [];
    raw.split("\n").forEach(function (line) {
      if (/^[ \t]/.test(line) && list.length) { list[list.length - 1].value += " " + line.trim(); return; }
      var m = line.match(/^([!-9;-~]+):[ \t]?(.*)$/);
      if (m) list.push({ name: m[1], key: m[1].toLowerCase(), value: m[2].trim() });
    });
    return list;
  }
  function addr(v) {
    if (!v) return null;
    v = decodeWords(v);
    var m = v.match(/<\s*([^<>\s]+@[^<>\s]+)\s*>/);
    var email = m ? m[1] : (v.match(/[^\s<>"',;:()]+@[^\s<>"',;:()]+/) || [""])[0];
    var name = m ? v.slice(0, v.indexOf("<")).trim().replace(/^"|"$/g, "").trim() : "";
    email = email.toLowerCase().replace(/^mailto:/, "");
    return { email: email, name: name, domain: (email.split("@")[1] || "").replace(/[>.]+$/, "") };
  }
  function parseReceived(v) {
    var semi = v.lastIndexOf(";");
    var date = semi >= 0 ? v.slice(semi + 1).trim() : "";
    var body = semi >= 0 ? v.slice(0, semi) : v;
    var pick = function (re) { var m = body.match(re); return m ? m[1] : ""; };
    var fromClause = /^\s*by\s/i.test(body) ? "" : body.split(/\sby\s/i)[0];
    var ip = "";
    var cands = (fromClause.match(/\[(?:IPv6:)?[0-9a-fA-F:.]{3,}\]|\((?:\d{1,3}\.){3}\d{1,3}\)|\b(?:\d{1,3}\.){3}\d{1,3}\b/g) || []);
    /* la dernière IP de la clause « from » est celle qui s'est réellement connectée
       (ex. « from [192.168.1.23] (unknown [198.51.100.77]) ») */
    for (var i = cands.length - 1; i >= 0; i--) {
      var c = cands[i].replace(/^[[(](?:IPv6:)?|[\])]$/g, "");
      if (isIp(c)) { ip = c; break; }
    }
    var t = Date.parse(date.replace(/\s*\([^)]*\)\s*$/, "").replace(/\s+/g, " "));
    return { from: pick(/(?:^|\s)from\s+([^\s;()]+)/i), by: pick(/(?:^|\s)by\s+([^\s;()]+)/i), proto: pick(/\swith\s+([^\s;()]+)/i), ip: ip, date: date, t: isNaN(t) ? null : t };
  }
  function parseAuthResults(v) {
    var server = (v.split(";")[0] || "").trim().split(/\s/)[0];
    var res = { server: server };
    var dmarcPolicy = (v.match(/\bp=([a-z]+)/i) || [])[1];
    var plain = v;
    for (var k = 0; k < 3; k++) plain = plain.replace(/\([^()]*\)/g, " ");
    plain.split(";").slice(1).forEach(function (part) {
      var m = part.match(/^\s*([a-z-]+)\s*=\s*([a-z]+)/i);
      if (!m) return;
      var method = m[1].toLowerCase(), result = m[2].toLowerCase();
      var props = {};
      (part.match(/[a-z]+\.[a-z-]+=[^\s;]+/gi) || []).forEach(function (p) { var i = p.indexOf("="); props[p.slice(0, i).toLowerCase()] = p.slice(i + 1).replace(/^"|"$/g, ""); });
      if (method === "dkim") {
        (res.dkim = res.dkim || []).push({ result: result, d: (props["header.d"] || props["header.i"] || "").replace(/^@/, "").replace(/^[^@]*@/, "").toLowerCase() });
      } else if (!res[method]) {
        res[method] = { result: result, props: props };
      }
    });
    if (res.dmarc && dmarcPolicy) res.dmarc.policy = dmarcPolicy.toLowerCase();
    return res;
  }
  function dur(ms) {
    var s = Math.round(ms / 1000);
    if (s < 60) return s + " s";
    if (s < 3600) return Math.round(s / 60) + " min";
    if (s < 86400) return (s / 3600).toFixed(1).replace(/\.0$/, "") + " h";
    return Math.round(s / 86400) + " j";
  }

  function analyzeHeaders(raw) {
    var list = parseHeaders(raw);
    var get = function (k) { for (var i = 0; i < list.length; i++) if (list[i].key === k) return list[i].value; return ""; };
    var all = function (k) { return list.filter(function (h) { return h.key === k; }).map(function (h) { return h.value; }); };
    var out = { count: list.length, findings: [] };
    if (!list.length || (!get("from") && !all("received").length)) return out;
    var F = out.findings;
    var from = addr(get("from")), reply = addr(get("reply-to")), rp = addr(get("return-path")) || addr(get("envelope-from"));
    out.from = from; out.reply = reply; out.rp = rp;
    out.subject = decodeWords(get("subject")); out.to = decodeWords(get("to")); out.date = get("date"); out.msgid = get("message-id");
    out.client = get("x-mailer") || get("user-agent");
    out.xip = (get("x-originating-ip") || get("x-sender-ip")).replace(/[[\]\s]/g, "");
    var sig = get("dkim-signature");
    out.dkimSig = sig ? { d: (sig.match(/\bd=([^;\s]+)/) || [])[1] || "", s: (sig.match(/\bs=([^;\s]+)/) || [])[1] || "", a: (sig.match(/\ba=([^;\s]+)/) || [])[1] || "" } : null;

    /* chemin : les Received les plus hauts sont les plus récents */
    var hops = all("received").map(parseReceived).reverse();
    out.hops = hops;
    for (var i = 1; i < hops.length; i++) {
      hops[i].delta = hops[i].t != null && hops[i - 1].t != null ? hops[i].t - hops[i - 1].t : null;
      if (hops[i].delta != null && hops[i].delta > 3600 * 1000) F.push(finding("warn", H.delay, { t: dur(hops[i].delta), i: i + 1 }));
    }
    var origin = "";
    for (i = 0; i < hops.length; i++) if (hops[i].ip && !isPrivate(hops[i].ip)) { origin = hops[i].ip; break; }
    if (out.xip && isIp(out.xip) && !isPrivate(out.xip)) origin = out.xip;
    out.origin = origin;
    if (origin) F.push(finding("info", H.origin, { ip: esc(origin) }));

    /* authentification : en-tête Authentication-Results la plus haute */
    var ar = all("authentication-results");
    var auth = ar.length ? parseAuthResults(ar[0]) : {};
    out.auth = auth;
    if (ar.length && auth.server) F.push(finding("info", H.trust, { s: esc(auth.server) }));
    var fromDom = from ? from.domain : "";
    var spf = auth.spf ? auth.spf.result : "";
    var rspf = get("received-spf");
    if (!spf && rspf) spf = (rspf.match(/^\s*([a-z]+)/i) || ["", ""])[1].toLowerCase();
    var spfDom = (auth.spf && (auth.spf.props["smtp.mailfrom"] || "").replace(/^.*@/, "")) || (rp ? rp.domain : "") || fromDom;
    out.spf = spf;
    if (spf === "pass") F.push(finding("ok", H.spfPass, { d: esc(spfDom) }));
    else if (spf === "fail") F.push(finding("bad", H.spfFail, { r: "fail", d: esc(spfDom) }));
    else if (spf === "softfail") F.push(finding("warn", H.spfFail, { r: "softfail", d: esc(spfDom) }));
    else if (spf) F.push(finding("warn", H.spfWeak, { r: esc(spf), d: esc(spfDom) }));
    else F.push(finding("info", H.spfNone));

    var dk = auth.dkim || [];
    var dkPass = dk.filter(function (x) { return x.result === "pass"; })[0];
    out.dkim = dkPass ? "pass" : dk.length ? dk[0].result : "";
    if (dkPass) F.push(finding("ok", H.dkimPass, { d: esc(dkPass.d || (out.dkimSig && out.dkimSig.d) || "?") }));
    else if (dk.length && dk[0].result !== "none") F.push(finding("bad", H.dkimFail, { r: esc(dk[0].result) }));
    else F.push(finding("warn", H.dkimNone));

    var dm = auth.dmarc ? auth.dmarc.result : "";
    out.dmarc = dm;
    if (dm === "pass") F.push(finding("ok", H.dmarcPass, { d: esc(fromDom) }));
    else if (dm === "fail") F.push(finding("bad", H.dmarcFail, { d: esc(fromDom) }));
    else F.push(finding("warn", H.dmarcNone, { r: esc(dm || "—") }));

    /* incohérences d'identité */
    if (from && reply && reply.domain && fromDom && orgDomain(reply.domain) !== orgDomain(fromDom))
      F.push(finding("bad", H.replyTo, { r: esc(reply.email), f: esc(from.email) }));
    if (from && from.name) {
      var inName = (from.name.match(/[^\s<>"'()]+@[^\s<>"'()]+/) || [])[0];
      if (inName && orgDomain(inName.split("@")[1]) !== orgDomain(fromDom)) F.push(finding("bad", H.displaySpoof, { n: esc(inName), f: esc(from.email) }));
    }
    if (from && rp && rp.domain && fromDom && orgDomain(rp.domain) !== orgDomain(fromDom))
      F.push(finding(dm === "pass" ? "info" : "warn", H.returnPath, { r: esc(rp.email), f: esc(from.email) }));
    if (/(^|\.)xn--/i.test(fromDom)) F.push(finding("warn", H.puny, { d: esc(fromDom) }));
    if (FREE.indexOf(fromDom) >= 0) F.push(finding("info", H.free, { d: esc(fromDom) }));
    return out;
  }

  function initHeaders() {
    var input = $("#eh-input"), status = $("#eh-status"), results = $("#eh-results");
    function kv(label, value, mono) {
      if (!value) return "";
      return "<dt>" + T(label) + "</dt><dd" + (mono ? ' class="mail-mono"' : "") + ">" + value + "</dd>";
    }
    function who(a) {
      if (!a || !a.email) return "";
      return (a.name ? esc(a.name) + " " : "") + '<span class="mail-mono">&lt;' + esc(a.email) + "&gt;</span>";
    }
    function authBadge(name, r) {
      var level = r === "pass" ? "ok" : r === "fail" ? "bad" : r ? "warn" : "info";
      return '<div class="mail-auth__item">' + badge(level, esc(r || "—")) + "<strong>" + name + "</strong></div>";
    }
    function run() {
      var raw = input.value;
      if (!raw.trim()) { status.className = "tool-msg"; status.innerHTML = ""; results.hidden = true; return; }
      var a = analyzeHeaders(raw);
      if (!a.findings.length) {
        status.className = "tool-msg tool-msg--warn"; status.innerHTML = T(H.noHeaders); results.hidden = true; return;
      }
      status.className = "tool-msg"; status.innerHTML = T(H.parsed, { n: a.count, h: a.hops.length });
      renderFindings($("#eh-findings"), a.findings);
      $("#eh-auth").innerHTML = authBadge("SPF", a.spf) + authBadge("DKIM", a.dkim) + authBadge("DMARC", a.dmarc);
      var L = H.lbl;
      $("#eh-ident").innerHTML =
        kv(L.from, who(a.from)) + kv(L.replyTo, who(a.reply)) + kv(L.returnPath, who(a.rp)) + kv(L.to, esc(a.to)) +
        kv(L.subject, esc(a.subject)) + kv(L.date, esc(a.date)) + kv(L.msgid, esc(a.msgid), true) + kv(L.client, esc(a.client)) +
        kv(L.origIp, a.xip ? esc(a.xip) : "", true) +
        kv(L.dkimSig, a.dkimSig ? esc("d=" + a.dkimSig.d + "  s=" + a.dkimSig.s + "  a=" + a.dkimSig.a) : "", true);
      $("#eh-hops").innerHTML = a.hops.map(function (h, i) {
        var ipHtml = "";
        if (h.ip) {
          ipHtml = ' <span class="mail-ip' + (h.ip === a.origin ? " mail-ip--origin" : "") + '">' + esc(h.ip) + "</span>" +
            (isPrivate(h.ip) ? ' <span class="mail-tag">' + T(H.priv) + "</span>"
              : ' <a class="mail-tag mail-tag--link" href="https://www.abuseipdb.com/check/' + encodeURIComponent(h.ip) + '" rel="noopener noreferrer" target="_blank">AbuseIPDB ›</a>');
        }
        var delay = i === 0 ? T(H.start) : h.delta == null ? T(H.noDate) : (h.delta < 0 ? "−" : "+") + dur(Math.abs(h.delta));
        return '<li class="mail-hop' + (h.delta != null && h.delta > 3600000 ? " mail-hop--slow" : "") + '">' +
          '<span class="mail-hop__delay">' + delay + "</span>" +
          '<div class="mail-hop__body">' + (h.from || h.ip ? "<div>" + T(H.hopFrom) + ' <span class="mail-mono">' + esc(h.from) + "</span>" + ipHtml + "</div>" : "") +
          '<div class="mail-hop__by">' + T(H.hopBy) + ' <span class="mail-mono">' + esc(h.by || "?") + "</span>" + (h.proto ? ' <span class="mail-tag">' + esc(h.proto) + "</span>" : "") + "</div>" +
          '<div class="mail-hop__date">' + esc(h.date) + "</div></div></li>";
      }).join("");
      $("#eh-hops-wrap").hidden = !a.hops.length;
      results.hidden = false;
    }
    var timer;
    input.addEventListener("input", function () { clearTimeout(timer); timer = setTimeout(run, 250); });
    $("#eh-run").addEventListener("click", run);
    $("#eh-sample").addEventListener("click", function () { input.value = SAMPLE; run(); });
  }
  /* Exemple fictif (domaines et adresses réservés à la documentation : RFC 2606 et RFC 5737) */
  var SAMPLE = [
    "Delivered-To: alice@example.org",
    "Received: by 2002:a05:6a10:8b0e:0:0:0:0 with SMTP id k14csp512345pxq;",
    "        Mon, 2 Nov 2026 08:14:52 -0800 (PST)",
    "Authentication-Results: mx.example.org;",
    "       dkim=none;",
    "       spf=softfail (example.org: domain of transitioning billing@paiement-secure.example.net does not designate 203.0.113.45 as permitted sender) smtp.mailfrom=billing@paiement-secure.example.net;",
    "       dmarc=fail (p=REJECT sp=REJECT dis=QUARANTINE) header.from=example.com",
    "Received: from mail.paiement-secure.example.net (mail.paiement-secure.example.net. [203.0.113.45])",
    "        by mx.example.org with ESMTPS id a1si2345678wrx.12.2026.11.02.09.14.51",
    "        for <alice@example.org>; Mon, 02 Nov 2026 08:14:51 -0800 (PST)",
    "Received: from [192.168.1.23] (unknown [198.51.100.77])",
    "        by mail.paiement-secure.example.net (Postfix) with ESMTPSA id 4F2A1C0042",
    "        for <alice@example.org>; Mon, 2 Nov 2026 16:12:03 +0000 (UTC)",
    "Return-Path: <billing@paiement-secure.example.net>",
    "From: \"Service Client example.com <support@example.com>\" <support@example.com>",
    "Reply-To: facturation@example-support.example.net",
    "To: alice@example.org",
    "Subject: =?UTF-8?B?Vm90cmUgY29tcHRlIHNlcmEgc3VzcGVuZHUgc291cyAyNGg=?=",
    "Date: Mon, 2 Nov 2026 17:12:01 +0100",
    "Message-ID: <20261102161201.4F2A1C0042@mail.paiement-secure.example.net>",
    "X-Mailer: PHPMailer 6.8.0",
    "MIME-Version: 1.0",
    "Content-Type: text/html; charset=UTF-8"
  ].join("\n");

  /* =====================================================================
     Vérificateur DNS (SPF, DMARC, MX, DKIM, MTA-STS, TLS-RPT, DNSSEC)
     ===================================================================== */
  var D = {
    bad: M("Nom de domaine invalide.", "Invalid domain name.", "Nombre de dominio no válido.", "Nome de domínio inválido.", "Ungültiger Domainname."),
    loading: M("Interrogation du DNS…", "Querying DNS…", "Consultando el DNS…", "A consultar o DNS…", "DNS wird abgefragt …"),
    net: M("Résolution DNS impossible : réseau indisponible ou requête bloquée (bloqueur, pare-feu).", "DNS resolution failed: network unavailable or request blocked (blocker, firewall).", "No se pudo resolver el DNS: red no disponible o petición bloqueada (bloqueador, cortafuegos).", "Não foi possível resolver o DNS: rede indisponível ou pedido bloqueado (bloqueador, firewall).", "DNS-Auflösung fehlgeschlagen: Netzwerk nicht verfügbar oder Anfrage blockiert (Blocker, Firewall)."),
    nx: M("Le domaine <code>{d}</code> n'existe pas dans le DNS.", "The domain <code>{d}</code> does not exist in DNS.", "El dominio <code>{d}</code> no existe en el DNS.", "O domínio <code>{d}</code> não existe no DNS.", "Die Domain <code>{d}</code> existiert im DNS nicht."),
    done: M("Résultats pour <code>{d}</code>, obtenus à l'instant.", "Results for <code>{d}</code>, fetched just now.", "Resultados para <code>{d}</code>, obtenidos ahora mismo.", "Resultados para <code>{d}</code>, obtidos agora mesmo.", "Ergebnisse für <code>{d}</code>, gerade abgerufen."),
    mxNone: M("Aucun serveur MX : le domaine ne reçoit pas d'e-mails (ou utilise l'adresse A en repli).", "No MX server: the domain does not receive mail (or falls back to its A record).", "Ningún servidor MX: el dominio no recibe correo (o usa su registro A como respaldo).", "Nenhum servidor MX: o domínio não recebe e-mails (ou usa o registo A como alternativa).", "Kein MX-Server: Die Domain empfängt keine E-Mails (oder nutzt ersatzweise den A-Eintrag)."),
    mxNull: M("MX nul (<code>0 .</code>) : le domaine déclare explicitement ne recevoir aucun e-mail.", "Null MX (<code>0 .</code>): the domain explicitly declares it receives no mail.", "MX nulo (<code>0 .</code>): el dominio declara explícitamente que no recibe correo.", "MX nulo (<code>0 .</code>): o domínio declara explicitamente que não recebe e-mails.", "Null-MX (<code>0 .</code>): Die Domain erklärt ausdrücklich, keine E-Mails zu empfangen."),
    mxOk: M("{n} serveur(s) de réception déclaré(s).", "{n} receiving server(s) declared.", "{n} servidor(es) de recepción declarado(s).", "{n} servidor(es) de receção declarado(s).", "{n} Empfangsserver deklariert."),
    spfNone: M("Aucun enregistrement SPF : n'importe quel serveur peut envoyer au nom de ce domaine sans être rejeté par SPF.", "No SPF record: any server can send on behalf of this domain without being rejected by SPF.", "Ningún registro SPF: cualquier servidor puede enviar en nombre de este dominio sin que SPF lo rechace.", "Nenhum registo SPF: qualquer servidor pode enviar em nome deste domínio sem ser rejeitado pelo SPF.", "Kein SPF-Eintrag: Jeder Server kann im Namen dieser Domain senden, ohne von SPF abgewiesen zu werden."),
    spfMulti: M("{n} enregistrements SPF : il n'en faut qu'un, sinon SPF renvoie une erreur permanente (permerror).", "{n} SPF records: there must be only one, otherwise SPF returns a permanent error (permerror).", "{n} registros SPF: solo debe haber uno; si no, SPF devuelve un error permanente (permerror).", "{n} registos SPF: só deve haver um, caso contrário o SPF devolve um erro permanente (permerror).", "{n} SPF-Einträge: Es darf nur einen geben, sonst liefert SPF einen permanenten Fehler (permerror)."),
    spfHard: M("SPF strict (<code>-all</code>) : les serveurs non listés sont rejetés.", "Strict SPF (<code>-all</code>): unlisted servers are rejected.", "SPF estricto (<code>-all</code>): los servidores no listados se rechazan.", "SPF estrito (<code>-all</code>): os servidores não listados são rejeitados.", "Striktes SPF (<code>-all</code>): Nicht gelistete Server werden abgewiesen."),
    spfSoft: M("SPF souple (<code>~all</code>) : les serveurs non listés sont seulement marqués. Acceptable si DMARC est en <code>quarantine</code> ou <code>reject</code>.", "Soft SPF (<code>~all</code>): unlisted servers are only flagged. Acceptable if DMARC is set to <code>quarantine</code> or <code>reject</code>.", "SPF flexible (<code>~all</code>): los servidores no listados solo se marcan. Aceptable si DMARC está en <code>quarantine</code> o <code>reject</code>.", "SPF flexível (<code>~all</code>): os servidores não listados são apenas marcados. Aceitável se o DMARC estiver em <code>quarantine</code> ou <code>reject</code>.", "Weiches SPF (<code>~all</code>): Nicht gelistete Server werden nur markiert. Akzeptabel, wenn DMARC auf <code>quarantine</code> oder <code>reject</code> steht."),
    spfOpen: M("SPF inefficace (<code>{q}</code>) : il ne protège pas contre l'usurpation.", "Ineffective SPF (<code>{q}</code>): it does not protect against spoofing.", "SPF ineficaz (<code>{q}</code>): no protege contra la suplantación.", "SPF ineficaz (<code>{q}</code>): não protege contra a usurpação.", "Wirkungsloses SPF (<code>{q}</code>): Es schützt nicht vor Spoofing."),
    spfLookups: M("{n} recherches DNS pour évaluer le SPF (limite : 10).", "{n} DNS lookups to evaluate SPF (limit: 10).", "{n} consultas DNS para evaluar el SPF (límite: 10).", "{n} consultas DNS para avaliar o SPF (limite: 10).", "{n} DNS-Abfragen zur SPF-Auswertung (Grenze: 10)."),
    spfTooMany: M("{n} recherches DNS pour évaluer le SPF : au-delà de 10, le SPF échoue (permerror) chez les destinataires.", "{n} DNS lookups to evaluate SPF: above 10, SPF fails (permerror) at recipients.", "{n} consultas DNS para evaluar el SPF: por encima de 10, el SPF falla (permerror) en los destinatarios.", "{n} consultas DNS para avaliar o SPF: acima de 10, o SPF falha (permerror) nos destinatários.", "{n} DNS-Abfragen zur SPF-Auswertung: Über 10 schlägt SPF beim Empfänger fehl (permerror)."),
    spfPtr: M("Le mécanisme <code>ptr</code> est déconseillé (lent, peu fiable) par la RFC 7208.", "The <code>ptr</code> mechanism is discouraged (slow, unreliable) by RFC 7208.", "El mecanismo <code>ptr</code> está desaconsejado (lento, poco fiable) por la RFC 7208.", "O mecanismo <code>ptr</code> é desaconselhado (lento, pouco fiável) pela RFC 7208.", "Der Mechanismus <code>ptr</code> wird von RFC 7208 nicht empfohlen (langsam, unzuverlässig)."),
    dmarcNone: M("Aucune politique DMARC : les destinataires ne savent pas quoi faire d'un message usurpant ce domaine.", "No DMARC policy: recipients don't know what to do with a message spoofing this domain.", "Ninguna política DMARC: los destinatarios no saben qué hacer con un mensaje que suplanta este dominio.", "Nenhuma política DMARC: os destinatários não sabem o que fazer com uma mensagem que usurpa este domínio.", "Keine DMARC-Richtlinie: Empfänger wissen nicht, was sie mit einer Nachricht tun sollen, die diese Domain fälscht."),
    dmarcInherit: M("Pas de DMARC sur ce sous-domaine : c'est celui du domaine <code>{o}</code> qui s'applique.", "No DMARC on this subdomain: the policy of <code>{o}</code> applies.", "Sin DMARC en este subdominio: se aplica la del dominio <code>{o}</code>.", "Sem DMARC neste subdomínio: aplica-se o do domínio <code>{o}</code>.", "Kein DMARC auf dieser Subdomain: Es gilt die Richtlinie von <code>{o}</code>."),
    dmarcReject: M("DMARC en <code>reject</code> : les messages usurpant le domaine sont refusés.", "DMARC set to <code>reject</code>: messages spoofing the domain are refused.", "DMARC en <code>reject</code>: los mensajes que suplantan el dominio se rechazan.", "DMARC em <code>reject</code>: as mensagens que usurpam o domínio são recusadas.", "DMARC auf <code>reject</code>: Nachrichten, die die Domain fälschen, werden abgewiesen."),
    dmarcQuar: M("DMARC en <code>quarantine</code> : les messages usurpant le domaine finissent en spam.", "DMARC set to <code>quarantine</code>: messages spoofing the domain land in spam.", "DMARC en <code>quarantine</code>: los mensajes que suplantan el dominio acaban en spam.", "DMARC em <code>quarantine</code>: as mensagens que usurpam o domínio vão para o spam.", "DMARC auf <code>quarantine</code>: Nachrichten, die die Domain fälschen, landen im Spam."),
    dmarcMon: M("DMARC en <code>none</code> : simple surveillance, aucun message usurpé n'est bloqué. Étape suivante : <code>quarantine</code> puis <code>reject</code>.", "DMARC set to <code>none</code>: monitoring only, no spoofed message is blocked. Next step: <code>quarantine</code>, then <code>reject</code>.", "DMARC en <code>none</code>: solo supervisión, no se bloquea ningún mensaje suplantado. Siguiente paso: <code>quarantine</code> y luego <code>reject</code>.", "DMARC em <code>none</code>: apenas monitorização, nenhuma mensagem usurpada é bloqueada. Próximo passo: <code>quarantine</code> e depois <code>reject</code>.", "DMARC auf <code>none</code>: nur Überwachung, keine gefälschte Nachricht wird blockiert. Nächster Schritt: <code>quarantine</code>, dann <code>reject</code>."),
    dmarcInvalid: M("Enregistrement DMARC mal formé (il doit commencer par <code>v=DMARC1; p=…</code>).", "Malformed DMARC record (it must start with <code>v=DMARC1; p=…</code>).", "Registro DMARC mal formado (debe empezar por <code>v=DMARC1; p=…</code>).", "Registo DMARC mal formado (deve começar por <code>v=DMARC1; p=…</code>).", "Fehlerhafter DMARC-Eintrag (er muss mit <code>v=DMARC1; p=…</code> beginnen)."),
    dmarcPct: M("La politique ne s'applique qu'à {p} % des messages (<code>pct={p}</code>).", "The policy only applies to {p}% of messages (<code>pct={p}</code>).", "La política solo se aplica al {p} % de los mensajes (<code>pct={p}</code>).", "A política só se aplica a {p} % das mensagens (<code>pct={p}</code>).", "Die Richtlinie gilt nur für {p} % der Nachrichten (<code>pct={p}</code>)."),
    dmarcRua: M("Pas d'adresse de rapports (<code>rua</code>) : le propriétaire ne voit pas qui envoie en son nom.", "No report address (<code>rua</code>): the owner can't see who sends on its behalf.", "Sin dirección de informes (<code>rua</code>): el propietario no ve quién envía en su nombre.", "Sem endereço de relatórios (<code>rua</code>): o proprietário não vê quem envia em seu nome.", "Keine Berichtsadresse (<code>rua</code>): Der Inhaber sieht nicht, wer in seinem Namen sendet."),
    dmarcSp: M("Les sous-domaines sont moins protégés (<code>sp={s}</code>) que le domaine principal.", "Subdomains are less protected (<code>sp={s}</code>) than the main domain.", "Los subdominios están menos protegidos (<code>sp={s}</code>) que el dominio principal.", "Os subdomínios estão menos protegidos (<code>sp={s}</code>) do que o domínio principal.", "Subdomains sind schwächer geschützt (<code>sp={s}</code>) als die Hauptdomain."),
    parked: M("Domaine qui n'envoie pas d'e-mails ? Publie <code>v=spf1 -all</code> et <code>v=DMARC1; p=reject</code> pour empêcher qu'on l'usurpe.", "Domain that sends no mail? Publish <code>v=spf1 -all</code> and <code>v=DMARC1; p=reject</code> to stop it being spoofed.", "¿Un dominio que no envía correo? Publica <code>v=spf1 -all</code> y <code>v=DMARC1; p=reject</code> para evitar que lo suplanten.", "Domínio que não envia e-mails? Publica <code>v=spf1 -all</code> e <code>v=DMARC1; p=reject</code> para impedir que o usurpem.", "Domain, die keine E-Mails sendet? Veröffentliche <code>v=spf1 -all</code> und <code>v=DMARC1; p=reject</code>, damit sie nicht gefälscht wird."),
    dkimOk: M("Clé DKIM trouvée pour le sélecteur <code>{s}</code> ({k}).", "DKIM key found for selector <code>{s}</code> ({k}).", "Clave DKIM encontrada para el selector <code>{s}</code> ({k}).", "Chave DKIM encontrada para o seletor <code>{s}</code> ({k}).", "DKIM-Schlüssel für Selektor <code>{s}</code> gefunden ({k})."),
    dkimWeak: M("Clé DKIM du sélecteur <code>{s}</code> trop courte ({k}) : 2048 bits recommandés.", "DKIM key for selector <code>{s}</code> is too short ({k}): 2048 bits recommended.", "La clave DKIM del selector <code>{s}</code> es demasiado corta ({k}): se recomiendan 2048 bits.", "A chave DKIM do seletor <code>{s}</code> é demasiado curta ({k}): recomendam-se 2048 bits.", "DKIM-Schlüssel des Selektors <code>{s}</code> ist zu kurz ({k}): 2048 Bit empfohlen."),
    dkimRevoked: M("Le sélecteur <code>{s}</code> existe mais sa clé est révoquée (<code>p=</code> vide).", "Selector <code>{s}</code> exists but its key is revoked (empty <code>p=</code>).", "El selector <code>{s}</code> existe pero su clave está revocada (<code>p=</code> vacío).", "O seletor <code>{s}</code> existe mas a sua chave está revogada (<code>p=</code> vazio).", "Selektor <code>{s}</code> existiert, aber sein Schlüssel ist widerrufen (leeres <code>p=</code>)."),
    dkimMissing: M("Aucune clé DKIM pour le sélecteur <code>{s}</code>.", "No DKIM key for selector <code>{s}</code>.", "Ninguna clave DKIM para el selector <code>{s}</code>.", "Nenhuma chave DKIM para o seletor <code>{s}</code>.", "Kein DKIM-Schlüssel für Selektor <code>{s}</code>."),
    dkimNoneFound: M("Aucune clé DKIM trouvée parmi les sélecteurs courants. Le nom du sélecteur figure dans l'en-tête <code>DKIM-Signature</code> (<code>s=</code>) d'un message reçu de ce domaine.", "No DKIM key found among common selectors. The selector name is in the <code>DKIM-Signature</code> header (<code>s=</code>) of a message from this domain.", "No se encontró ninguna clave DKIM entre los selectores habituales. El nombre del selector figura en el encabezado <code>DKIM-Signature</code> (<code>s=</code>) de un mensaje de este dominio.", "Nenhuma chave DKIM encontrada entre os seletores comuns. O nome do seletor está no cabeçalho <code>DKIM-Signature</code> (<code>s=</code>) de uma mensagem deste domínio.", "Unter den gängigen Selektoren wurde kein DKIM-Schlüssel gefunden. Der Selektorname steht im Header <code>DKIM-Signature</code> (<code>s=</code>) einer Nachricht dieser Domain."),
    mtasts: M("MTA-STS publié : les serveurs qui le respectent n'envoient à ce domaine qu'en TLS vérifié.", "MTA-STS published: servers that honour it only deliver to this domain over verified TLS.", "MTA-STS publicado: los servidores que lo respetan solo entregan a este dominio con TLS verificado.", "MTA-STS publicado: os servidores que o respeitam só entregam a este domínio com TLS verificado.", "MTA-STS veröffentlicht: Server, die es beachten, liefern an diese Domain nur über verifiziertes TLS."),
    mtastsNo: M("Pas de MTA-STS : le chiffrement TLS vers ce domaine reste opportuniste (contournable par un attaquant sur le réseau).", "No MTA-STS: TLS to this domain stays opportunistic (an on-path attacker can strip it).", "Sin MTA-STS: el cifrado TLS hacia este dominio sigue siendo oportunista (un atacante en la red puede eliminarlo).", "Sem MTA-STS: a cifra TLS para este domínio continua oportunista (um atacante na rede pode removê-la).", "Kein MTA-STS: TLS zu dieser Domain bleibt opportunistisch (ein Angreifer im Netz kann es entfernen)."),
    tlsrpt: M("Rapports TLS (TLS-RPT) activés.", "TLS reporting (TLS-RPT) enabled.", "Informes TLS (TLS-RPT) activados.", "Relatórios TLS (TLS-RPT) ativados.", "TLS-Berichte (TLS-RPT) aktiviert."),
    dnssec: M("Zone signée DNSSEC et validée par le résolveur : les réponses ne peuvent pas être falsifiées en route.", "Zone signed with DNSSEC and validated by the resolver: answers cannot be forged in transit.", "Zona firmada con DNSSEC y validada por el resolutor: las respuestas no pueden falsificarse en tránsito.", "Zona assinada com DNSSEC e validada pelo resolvedor: as respostas não podem ser falsificadas em trânsito.", "Zone mit DNSSEC signiert und vom Resolver validiert: Antworten können unterwegs nicht gefälscht werden."),
    dnssecNo: M("Zone non signée DNSSEC.", "Zone not signed with DNSSEC.", "Zona no firmada con DNSSEC.", "Zona não assinada com DNSSEC.", "Zone nicht mit DNSSEC signiert."),
    cards: { mx: "MX", spf: "SPF", dmarc: "DMARC", dkim: "DKIM", mtasts: "MTA-STS / TLS-RPT", dnssec: "DNSSEC" },
    none: M("aucun", "none", "ninguno", "nenhum", "keiner"),
    present: M("présent", "present", "presente", "presente", "vorhanden"),
    missing: M("absent", "missing", "ausente", "ausente", "fehlt"),
    keyBits: M("RSA ≈ {b} bits", "RSA ≈ {b} bits", "RSA ≈ {b} bits", "RSA ≈ {b} bits", "RSA ≈ {b} Bit")
  };
  var SELECTORS = ["default", "selector1", "selector2", "google", "k1", "s1", "s2", "dkim", "mail", "smtp", "mx", "key1"];

  function txtData(s) {
    var parts = String(s).match(/"((?:[^"\\]|\\.)*)"/g);
    return parts ? parts.map(function (p) { return p.slice(1, -1).replace(/\\(.)/g, "$1"); }).join("") : String(s);
  }
  function doh(name, type) {
    return fetch("https://cloudflare-dns.com/dns-query?name=" + encodeURIComponent(name) + "&type=" + type, {
      headers: { accept: "application/dns-json" }, cache: "no-store", credentials: "omit", referrerPolicy: "no-referrer"
    }).then(function (r) {
      if (!r.ok) throw new Error("HTTP " + r.status);
      return r.json();
    });
  }
  function answers(resp, typeNum) {
    return (resp && resp.Answer || []).filter(function (a) { return a.type === typeNum; });
  }
  function txts(resp) { return answers(resp, 16).map(function (a) { return txtData(a.data); }); }

  function normalizeDomain(v) {
    v = String(v || "").trim().toLowerCase();
    if (!v) return "";
    if (v.indexOf("@") >= 0 && v.indexOf("/") < 0) v = v.split("@").pop();
    try { v = new URL(/^[a-z]+:\/\//.test(v) ? v : "http://" + v).hostname; } catch (e) { return ""; }
    v = v.replace(/\.$/, "");
    if (!/^(?=.{1,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9-]{2,63}$/.test(v) || isIp(v)) return "";
    return v;
  }

  /* compte récursif des recherches DNS d'un SPF (include, a, mx, ptr, exists, redirect) */
  function spfLookups(record, budget) {
    var terms = record.split(/\s+/).slice(1);
    var count = 0, nested = [];
    terms.forEach(function (t) {
      var m = t.replace(/^[+\-~?]/, "").toLowerCase();
      if (/^(include:|a\b|a:|a\/|mx\b|mx:|mx\/|ptr|exists:)/.test(m) || /^redirect=/.test(m)) count++;
      var target = (m.match(/^include:(.+)$/) || m.match(/^redirect=(.+)$/) || [])[1];
      if (target && !/%\{/.test(target)) nested.push(target);
    });
    if (budget.left <= 0 || !nested.length) return Promise.resolve(count);
    return Promise.all(nested.map(function (n) {
      if (budget.left-- <= 0) return 0;
      return doh(n, "TXT").then(function (r) {
        var rec = txts(r).filter(function (x) { return /^v=spf1(\s|$)/i.test(x); })[0];
        return rec ? spfLookups(rec, budget) : 0;
      }).catch(function () { return 0; });
    })).then(function (sub) { return sub.reduce(function (a, b) { return a + b; }, count); });
  }
  function tags(rec) {
    var o = {};
    rec.split(";").forEach(function (p) { var i = p.indexOf("="); if (i > 0) o[p.slice(0, i).trim().toLowerCase()] = p.slice(i + 1).trim(); });
    return o;
  }
  function dkimInfo(rec) {
    var t = tags(rec), p = (t.p || "").replace(/\s/g, "");
    if (!p) return { revoked: true };
    if ((t.k || "rsa").toLowerCase() === "ed25519") return { label: "Ed25519", weak: false };
    var bytes = Math.floor(p.length * 3 / 4);
    var bits = bytes < 120 ? 512 : bytes < 200 ? 1024 : bytes < 400 ? 2048 : 4096;
    return { label: T(D.keyBits, { b: bits }), weak: bits < 2048 };
  }

  function initDns() {
    var input = $("#dn-domain"), selIn = $("#dn-selector"), status = $("#dn-status"), results = $("#dn-results"), btn = $("#dn-run");
    var seq = 0;
    function card(id, level, title, body, raw) {
      return '<section class="mail-card mail-card--' + level + '"><h4>' + badge(level, { ok: "✓", warn: "!", bad: "✗", info: "i" }[level]) + " " + title + "</h4>" +
        body + (raw ? '<pre class="mail-raw">' + raw + "</pre>" : "") + "</section>";
    }
    function run() {
      var dom = normalizeDomain(input.value);
      if (!dom) { status.className = "tool-msg tool-msg--warn"; status.innerHTML = T(D.bad); results.hidden = true; return; }
      input.value = dom;
      var my = ++seq;
      status.className = "tool-msg"; status.innerHTML = T(D.loading);
      btn.disabled = true;
      var org = orgDomain(dom);
      var sel = (selIn.value || "").trim().toLowerCase().replace(/[^a-z0-9._-]/g, "");
      Promise.all([
        doh(dom, "MX"), doh(dom, "TXT"), doh("_dmarc." + dom, "TXT"),
        org !== dom ? doh("_dmarc." + org, "TXT") : Promise.resolve(null),
        doh("_mta-sts." + dom, "TXT"), doh("_smtp._tls." + dom, "TXT"),
        Promise.all((sel ? [sel] : SELECTORS).map(function (s) {
          return doh(s + "._domainkey." + dom, "TXT").then(function (r) { return { s: s, recs: txts(r).filter(function (x) { return /p=/i.test(x); }) }; }).catch(function () { return { s: s, recs: [] }; });
        }))
      ]).then(function (r) {
        if (my !== seq) return;
        var mxR = r[0], txtR = r[1];
        if (mxR.Status === 3) { status.className = "tool-msg tool-msg--bad"; status.innerHTML = T(D.nx, { d: esc(dom) }); results.hidden = true; return null; }
        var F = [], html = "";
        /* MX */
        var mx = answers(mxR, 15).map(function (a) { var p = a.data.split(/\s+/); return { pr: +p[0], host: (p[1] || "").replace(/\.$/, "") }; })
          .sort(function (a, b) { return a.pr - b.pr; });
        var nullMx = mx.length === 1 && (mx[0].host === "" || mx[0].host === ".");
        var mxLevel = mx.length ? "ok" : "info";
        var mxMsg = nullMx ? D.mxNull : mx.length ? D.mxOk : D.mxNone;
        html += card("mx", mxLevel, D.cards.mx, "<p>" + T(mxMsg, { n: mx.length }) + "</p>",
          mx.length && !nullMx ? mx.map(function (m) { return esc(m.pr + "  " + m.host); }).join("\n") : "");
        /* SPF */
        var spfs = txts(txtR).filter(function (x) { return /^v=spf1(\s|$)/i.test(x); });
        var spfLevel = "bad", spfHtml = "", allQ = "";
        if (!spfs.length) { F.push(finding("bad", D.spfNone)); spfHtml = "<p>" + T(D.spfNone) + "</p>"; }
        else if (spfs.length > 1) { F.push(finding("bad", D.spfMulti, { n: spfs.length })); spfHtml = "<p>" + T(D.spfMulti, { n: spfs.length }) + "</p>"; }
        else {
          var all = (spfs[0].match(/\s([+\-~?]?)all\s*$/i) || []);
          allQ = all.length ? (all[1] || "+") : "";
          var redirect = /\sredirect=/i.test(spfs[0]);
          if (allQ === "-") { spfLevel = "ok"; F.push(finding("ok", D.spfHard)); spfHtml = "<p>" + T(D.spfHard) + "</p>"; }
          else if (allQ === "~") { spfLevel = "warn"; F.push(finding("warn", D.spfSoft)); spfHtml = "<p>" + T(D.spfSoft) + "</p>"; }
          else if (redirect && !allQ) { spfLevel = "ok"; }
          else { var q = allQ ? allQ + "all" : "?all"; F.push(finding("bad", D.spfOpen, { q: esc(q) })); spfHtml = "<p>" + T(D.spfOpen, { q: esc(q) }) + "</p>"; }
          if (/\sptr(\s|:|$)/i.test(spfs[0])) { F.push(finding("warn", D.spfPtr)); spfHtml += "<p>" + T(D.spfPtr) + "</p>"; if (spfLevel === "ok") spfLevel = "warn"; }
        }
        /* DMARC */
        var dmarcs = txts(r[2]).filter(function (x) { return /^v=DMARC1/i.test(x.trim()); });
        var inherited = false;
        if (!dmarcs.length && r[3]) { dmarcs = txts(r[3]).filter(function (x) { return /^v=DMARC1/i.test(x.trim()); }); inherited = dmarcs.length > 0; }
        var dmLevel = "bad", dmHtml = "", policy = "";
        if (!dmarcs.length) { F.push(finding("bad", D.dmarcNone)); dmHtml = "<p>" + T(D.dmarcNone) + "</p>"; }
        else {
          var t = tags(dmarcs[0]);
          policy = (t.p || "").toLowerCase();
          if (inherited) dmHtml += "<p>" + T(D.dmarcInherit, { o: esc(org) }) + "</p>";
          if (inherited && t.sp) policy = t.sp.toLowerCase();
          if (policy === "reject") { dmLevel = "ok"; F.push(finding("ok", D.dmarcReject)); dmHtml += "<p>" + T(D.dmarcReject) + "</p>"; }
          else if (policy === "quarantine") { dmLevel = "ok"; F.push(finding("ok", D.dmarcQuar)); dmHtml += "<p>" + T(D.dmarcQuar) + "</p>"; }
          else if (policy === "none") { dmLevel = "warn"; F.push(finding("warn", D.dmarcMon)); dmHtml += "<p>" + T(D.dmarcMon) + "</p>"; }
          else { F.push(finding("bad", D.dmarcInvalid)); dmHtml += "<p>" + T(D.dmarcInvalid) + "</p>"; }
          if (t.pct && +t.pct < 100) { F.push(finding("warn", D.dmarcPct, { p: esc(t.pct) })); dmHtml += "<p>" + T(D.dmarcPct, { p: esc(t.pct) }) + "</p>"; if (dmLevel === "ok") dmLevel = "warn"; }
          if (!t.rua) { F.push(finding("info", D.dmarcRua)); dmHtml += "<p>" + T(D.dmarcRua) + "</p>"; }
          if (!inherited && t.sp && t.sp.toLowerCase() === "none" && policy !== "none") { F.push(finding("warn", D.dmarcSp, { s: "none" })); dmHtml += "<p>" + T(D.dmarcSp, { s: "none" }) + "</p>"; }
        }
        if ((!mx.length || nullMx) && !(allQ === "-" && policy === "reject")) F.push(finding("info", D.parked));
        /* DKIM */
        var found = r[6].filter(function (x) { return x.recs.length; });
        var dkLevel = "info", dkHtml = "", dkRaw = "";
        if (found.length) {
          dkLevel = "ok";
          found.forEach(function (f) {
            var info = dkimInfo(f.recs[0]);
            if (info.revoked) { dkHtml += "<p>" + T(D.dkimRevoked, { s: esc(f.s) }) + "</p>"; return; }
            if (info.weak) { dkLevel = "warn"; F.push(finding("warn", D.dkimWeak, { s: esc(f.s), k: info.label })); dkHtml += "<p>" + T(D.dkimWeak, { s: esc(f.s), k: info.label }) + "</p>"; }
            else { F.push(finding("ok", D.dkimOk, { s: esc(f.s), k: info.label })); dkHtml += "<p>" + T(D.dkimOk, { s: esc(f.s), k: info.label }) + "</p>"; }
            dkRaw += esc(f.s + "._domainkey  " + f.recs[0].slice(0, 160) + (f.recs[0].length > 160 ? "…" : "")) + "\n";
          });
        } else if (sel) { dkLevel = "warn"; dkHtml = "<p>" + T(D.dkimMissing, { s: esc(sel) }) + "</p>"; F.push(finding("warn", D.dkimMissing, { s: esc(sel) })); }
        else { dkHtml = "<p>" + T(D.dkimNoneFound) + "</p>"; }
        /* MTA-STS, TLS-RPT */
        var sts = txts(r[4]).filter(function (x) { return /^v=STSv1/i.test(x); })[0];
        var rpt = txts(r[5]).filter(function (x) { return /^v=TLSRPTv1/i.test(x); })[0];
        var stsHtml = "<p>" + T(sts ? D.mtasts : D.mtastsNo) + "</p>" + (rpt ? "<p>" + T(D.tlsrpt) + "</p>" : "");
        /* DNSSEC */
        var ad = !!(mxR.AD || txtR.AD);
        F.push(finding(ad ? "ok" : "info", ad ? D.dnssec : D.dnssecNo));
        var budget = { left: 20 };
        return (spfs.length === 1 ? spfLookups(spfs[0], budget) : Promise.resolve(null)).then(function (n) {
          if (my !== seq) return;
          if (n != null) {
            if (n > 10) { spfLevel = "bad"; F.push(finding("bad", D.spfTooMany, { n: n })); spfHtml += "<p>" + T(D.spfTooMany, { n: n }) + "</p>"; }
            else spfHtml += "<p>" + T(D.spfLookups, { n: n }) + "</p>";
          }
          html += card("spf", spfLevel, D.cards.spf, spfHtml, spfs.map(esc).join("\n"));
          html += card("dmarc", dmLevel, D.cards.dmarc, dmHtml, dmarcs.map(esc).join("\n"));
          html += card("dkim", dkLevel, D.cards.dkim, dkHtml, dkRaw.trim());
          html += card("mtasts", sts ? "ok" : "info", D.cards.mtasts, stsHtml, [sts, rpt].filter(Boolean).map(esc).join("\n"));
          html += card("dnssec", ad ? "ok" : "info", D.cards.dnssec, "<p>" + T(ad ? D.dnssec : D.dnssecNo) + "</p>", "");
          renderFindings($("#dn-findings"), F);
          $("#dn-cards").innerHTML = html;
          status.className = "tool-msg"; status.innerHTML = T(D.done, { d: esc(dom) });
          results.hidden = false;
        });
      }).catch(function () {
        if (my !== seq) return;
        status.className = "tool-msg tool-msg--bad"; status.innerHTML = T(D.net); results.hidden = true;
      }).then(function () { if (my === seq) btn.disabled = false; });
    }
    btn.addEventListener("click", run);
    $("#dn-form").addEventListener("submit", function (e) { e.preventDefault(); run(); });
    Array.prototype.forEach.call(document.querySelectorAll("[data-dn-example]"), function (b) {
      b.addEventListener("click", function () { input.value = b.getAttribute("data-dn-example"); selIn.value = ""; run(); });
    });
  }

  function start() {
    var main = document.querySelector("main[data-tool]");
    var tool = main && main.getAttribute("data-tool");
    if (tool === "headers") initHeaders();
    if (tool === "dns") initDns();
  }
  if (typeof document === "undefined") { /* Node : tests */ }
  else if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start);
  else start();
  if (typeof module !== "undefined") module.exports = { analyzeHeaders: analyzeHeaders, parseHeaders: parseHeaders, decodeWords: decodeWords, orgDomain: orgDomain, normalizeDomain: normalizeDomain, dkimInfo: dkimInfo, txtData: txtData, parseReceived: parseReceived };
})();
