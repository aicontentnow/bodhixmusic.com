/* BODHI X player dock and page swapper.
   One player for the whole site. Play an album from any room and it loads into the dock at the
   bottom of the screen. While the dock is loaded, links inside the site swap the page content
   instead of reloading, so the music keeps playing from page to page.
   The SEASØNS room runs its own drawing code, so while the dock is playing it opens inside a frame. */
(function () {
  "use strict";
  var inFrame = window.top !== window.self;
  var ORIGIN = location.origin;

  function isInternal(a) {
    if (!a || !a.href || a.target === "_blank" || a.hasAttribute("download")) return false;
    var u = new URL(a.href, location.href);
    if (u.origin !== ORIGIN) return false;
    if (/\.(jpg|png|svg|mp3|pdf|xml|txt|woff2?)$/i.test(u.pathname)) return false;
    return true;
  }

  /* Inside the SEASØNS frame: hand every site link to the page around it. */
  if (inFrame) {
    document.addEventListener("click", function (e) {
      var a = e.target.closest && e.target.closest("a");
      if (!isInternal(a) || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
      e.preventDefault();
      window.parent.postMessage({ bxNav: a.href }, ORIGIN);
    });
    return;
  }

  var CSS = [
    "#bx-dock{position:fixed;left:0;right:0;bottom:0;z-index:9999;background:#F6F3EA;color:#282623;border-top:1px solid #D8D2C6;box-shadow:0 -8px 24px rgba(40,38,35,.12);font-family:Inter,system-ui,sans-serif;padding-bottom:env(safe-area-inset-bottom,0px)}",
    "#bx-dock[hidden]{display:none}",
    "#bx-dock .dk-bar{display:flex;align-items:center;gap:12px;max-width:960px;margin:0 auto;padding:8px max(12px,env(safe-area-inset-left,0px))}",
    "#bx-dock .dk-cover{width:44px;height:44px;flex:none;object-fit:cover;display:block;background:#ECE8DE}",
    "#bx-dock .dk-text{flex:1;min-width:0;display:flex;flex-direction:column;gap:2px}",
    "#bx-dock .dk-kicker{font-size:10px;letter-spacing:.24em;text-transform:uppercase;color:#6E685F}",
    "#bx-dock .dk-title{font-size:14px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}",
    "#bx-dock .dk-title a{color:inherit;text-decoration:none}",
    "#bx-dock .dk-title a:hover{text-decoration:underline}",
    "#bx-dock button{flex:none;width:44px;height:44px;display:grid;place-items:center;background:none;border:1px solid #D8D2C6;color:#282623;cursor:pointer;padding:0}",
    "#bx-dock button:hover,#bx-dock button:focus-visible{background:#282623;color:#F6F3EA;border-color:#282623}",
    "#bx-dock button svg{width:16px;height:16px}",
    "#bx-dock .dk-player{max-width:960px;margin:0 auto;padding:0 max(12px,env(safe-area-inset-left,0px)) 8px;height:128px;overflow:hidden;transition:height .25s}",
    "#bx-dock.min .dk-player{height:0;padding-bottom:0}",
    "#bx-dock.min .dk-toggle svg{transform:rotate(180deg)}",
    "#bx-dock iframe{border:0;width:100%;height:120px;display:block;background:#fff}",
    "html.bx-docked body{padding-bottom:calc(var(--bx-dock-h,200px) + env(safe-area-inset-bottom,0px))}",
    "#bx-shell-frame{position:fixed;left:0;right:0;top:0;width:100%;border:0;background:#F6F3EA;bottom:var(--bx-dock-h,200px);height:calc(100% - var(--bx-dock-h,200px))}",
    ".play-album{cursor:pointer}",
    "h1[tabindex=\"-1\"]:focus{outline:none}",
    "@media (prefers-reduced-motion:reduce){#bx-dock .dk-player{transition:none}}"
  ].join("\n");

  var style = document.createElement("style");
  style.setAttribute("data-bx-keep", "");
  style.textContent = CSS;
  document.head.appendChild(style);

  var dock = document.createElement("div");
  dock.id = "bx-dock";
  dock.hidden = true;
  dock.setAttribute("role", "region");
  dock.setAttribute("aria-label", "Music player");
  dock.innerHTML =
    '<div class="dk-bar">' +
    '<img class="dk-cover" alt="" width="44" height="44">' +
    '<div class="dk-text"><span class="dk-kicker">In the player</span><span class="dk-title"><a class="dk-link" href="/"></a></span></div>' +
    '<button class="dk-toggle" type="button" aria-expanded="true" aria-label="Hide the player controls"><svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3 6l5 5 5-5" fill="none" stroke="currentColor" stroke-width="1.5"/></svg></button>' +
    '<button class="dk-close" type="button" aria-label="Stop and close the player"><svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3 3l10 10M13 3L3 13" fill="none" stroke="currentColor" stroke-width="1.5"/></svg></button>' +
    "</div>" +
    '<div class="dk-player"></div>';
  document.body.appendChild(dock);

  var playerBox = dock.querySelector(".dk-player");
  var loaded = null;

  function setDockHeight() {
    var h = dock.hidden ? 0 : dock.getBoundingClientRect().height;
    document.documentElement.style.setProperty("--bx-dock-h", h + "px");
  }
  window.addEventListener("resize", setDockHeight);
  playerBox.addEventListener("transitionend", setDockHeight);

  function markButtons() {
    document.querySelectorAll(".play-album").forEach(function (b) {
      var on = loaded && b.dataset.album === loaded.album;
      b.classList.toggle("is-loaded", !!on);
      var label = b.querySelector(".pa-label");
      if (label) label.textContent = on ? "In the player below" : (b.dataset.label || "Play " + b.dataset.title);
    });
  }

  function load(d) {
    if (loaded && loaded.album === d.album) {
      dock.classList.remove("min");
      dock.querySelector(".dk-toggle").setAttribute("aria-expanded", "true");
      setTimeout(setDockHeight, 300);
      return;
    }
    loaded = d;
    var bg = "ffffff", link = "282623";
    playerBox.innerHTML = '<iframe title="' + d.title.replace(/"/g, "&quot;") + ' on Bandcamp" src="https://bandcamp.com/EmbeddedPlayer/album=' + d.album +
      "/size=large/bgcol=" + bg + "/linkcol=" + link + '/tracklist=false/artwork=none/transparent=true/" seamless></iframe>';
    var cover = dock.querySelector(".dk-cover");
    if (d.cover) { cover.src = d.cover; cover.hidden = false; } else { cover.hidden = true; }
    var l = dock.querySelector(".dk-link");
    l.textContent = d.title + (d.room ? " · " + d.room : "");
    l.href = d.roomHref || "/";
    dock.hidden = false;
    dock.classList.remove("min");
    document.documentElement.classList.add("bx-docked");
    setDockHeight();
    setTimeout(setDockHeight, 300);
    markButtons();
  }

  function closeDock() {
    loaded = null;
    playerBox.innerHTML = "";
    dock.hidden = true;
    document.documentElement.classList.remove("bx-docked");
    setDockHeight();
    markButtons();
  }

  dock.querySelector(".dk-close").addEventListener("click", closeDock);
  dock.querySelector(".dk-toggle").addEventListener("click", function () {
    var min = dock.classList.toggle("min");
    this.setAttribute("aria-expanded", String(!min));
    this.setAttribute("aria-label", min ? "Show the player controls" : "Hide the player controls");
    setTimeout(setDockHeight, 300);
  });

  document.addEventListener("click", function (e) {
    var b = e.target.closest && e.target.closest(".play-album");
    if (!b) return;
    e.preventDefault();
    load({ album: b.dataset.album, title: b.dataset.title, room: b.dataset.room, roomHref: b.dataset.roomHref, cover: b.dataset.cover });
  });

  /* ---------- page swapping while the dock is loaded ---------- */
  var busy = false;
  var swapped = false;

  function swapHead(newDoc) {
    var keep = function (el) { return el.hasAttribute("data-bx-keep"); };
    var isPageAsset = function (el) {
      return el.tagName === "STYLE" || (el.tagName === "LINK" && /stylesheet|preload|icon|canonical|apple-touch-icon/.test(el.rel));
    };
    var old = Array.prototype.filter.call(document.head.children, function (el) { return isPageAsset(el) && !keep(el); });
    var incoming = Array.prototype.filter.call(newDoc.head.children, function (el) { return isPageAsset(el); });
    var waits = [];
    incoming.forEach(function (el) {
      var n = document.importNode(el, true);
      if (n.tagName === "LINK" && n.rel === "stylesheet") {
        waits.push(new Promise(function (res) { n.onload = n.onerror = res; setTimeout(res, 1500); }));
      }
      document.head.insertBefore(n, style);
    });
    document.title = newDoc.title;
    var tc = newDoc.querySelector('meta[name="theme-color"]'), mine = document.querySelector('meta[name="theme-color"]');
    if (tc && mine) mine.setAttribute("content", tc.getAttribute("content"));
    return Promise.all(waits).then(function () { old.forEach(function (el) { el.remove(); }); });
  }

  function clearBody() {
    Array.prototype.slice.call(document.body.childNodes).forEach(function (n) { if (n !== dock) n.remove(); });
  }

  function render(url, html, push) {
    var doc = new DOMParser().parseFromString(html, "text/html");
    var isolate = !!doc.querySelector('meta[name="bx-isolate"]');
    if (isolate) {
      var src = new URL(url.href); src.searchParams.set("in-shell", "1");
      return swapHead(document.implementation.createHTMLDocument(doc.title)).then(function () {
        document.title = doc.title;
        document.body.className = "";
        document.body.removeAttribute("style");
        clearBody();
        var f = document.createElement("iframe");
        f.id = "bx-shell-frame";
        f.title = doc.title;
        f.src = src.pathname + src.search + src.hash;
        document.body.insertBefore(f, dock);
        document.documentElement.classList.add("bx-shell");
        finish(url, push, true);
      });
    }
    return swapHead(doc).then(function () {
      document.documentElement.classList.remove("bx-shell");
      document.body.className = doc.body.className;
      clearBody();
      Array.prototype.slice.call(doc.body.childNodes).forEach(function (n) {
        if (n.nodeType === 1 && n.tagName === "SCRIPT") return;
        document.body.insertBefore(document.importNode(n, true), dock);
      });
      finish(url, push, false);
    });
  }

  function finish(url, push, isolated) {
    swapped = true;
    if (push) history.pushState({ bx: 1 }, "", url.pathname + url.search + url.hash);
    if (!isolated && url.hash) {
      var t = document.getElementById(decodeURIComponent(url.hash.slice(1)));
      if (t) { t.scrollIntoView(); } else { window.scrollTo(0, 0); }
    } else if (push) {
      window.scrollTo(0, 0);
    }
    markButtons();
    var h1 = document.querySelector("h1");
    if (h1 && !isolated) { h1.setAttribute("tabindex", "-1"); h1.focus({ preventScroll: true }); }
  }

  function go(href, push) {
    var url = new URL(href, location.href);
    if (busy) return;
    if (push && url.pathname === location.pathname && url.search === location.search && url.hash) {
      history.pushState({ bx: 1 }, "", url.hash);
      var t = document.getElementById(decodeURIComponent(url.hash.slice(1)));
      if (t) t.scrollIntoView({ behavior: "smooth" });
      return;
    }
    busy = true;
    fetch(url.pathname + url.search, { credentials: "same-origin" })
      .then(function (r) {
        if (!r.ok && r.status !== 404) throw new Error(r.status);
        return r.text();
      })
      .then(function (html) { return render(url, html, push); })
      .catch(function () { location.href = url.href; })
      .then(function () { busy = false; });
  }

  document.addEventListener("click", function (e) {
    if (!loaded || e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    var a = e.target.closest && e.target.closest("a");
    if (!isInternal(a)) return;
    e.preventDefault();
    go(a.href, true);
  });

  window.addEventListener("message", function (e) {
    if (e.origin !== ORIGIN || !e.data || !e.data.bxNav) return;
    if (loaded) go(e.data.bxNav, true); else location.href = e.data.bxNav;
  });

  window.addEventListener("popstate", function () {
    if (loaded) go(location.href, false);
    else if (swapped) location.reload();
  });

  history.replaceState({ bx: 1 }, "", location.href);
})();
