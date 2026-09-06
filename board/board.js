/* assay board renderer. Reads window.ASSAY_SNAPSHOT (written by `assay board`)
   and paints the desk. No framework, no build step, no network: the snapshot
   is a plain object loaded from data.js, so the page opens from a file. */
(function () {
  var S = window.ASSAY_SNAPSHOT;
  if (!S) return;

  function el(id) { return document.getElementById(id); }
  function pct(x) { return (x >= 0 ? "+" : "") + (x * 100).toFixed(1) + "%"; }
  function commas(n) {
    var s = Math.abs(n).toFixed(2).split(".");
    s[0] = s[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    return (n < 0 ? "-" : "") + s.join(".");
  }
  function usd(x) { return "$" + commas(Number(x)); }

  el("src").textContent = "source: " + S.source;
  el("holt").textContent = S.holt ? "Holt on" : "Holt off";
  el("gen").textContent = "snapshot " + S.generated;

  // stat tiles
  var st = S.stats;
  var tiles = [
    ["scanned", st.scanned, ""],
    ["fired", st.fired, "green"],
    ["open", st.open, ""],
    ["equity", usd(st.equity), ""],
    ["return", pct(st.ret), st.ret >= 0 ? "green" : "red"]
  ];
  el("stats").innerHTML = tiles.map(function (t) {
    return '<div class="tile"><div class="n ' + t[2] + '">' + t[1] +
           '</div><div class="l">' + t[0] + '</div></div>';
  }).join("");

  // feed
  function row(m) {
    var fire = m.verdict === "FIRE";
    var edgeCls = m.edge >= 0 ? "pos" : "neg";
    var barCls = fire ? "" : "dim";
    var verd = fire
      ? '<span class="verd fire">FIRE</span> <span class="mono">' + m.side + " " + usd(m.stake) + "</span>"
      : '<span class="verd pass">pass</span> <span class="why">' + m.reason + "</span>";
    return '<tr class="' + (fire ? "fire" : "pass") + '" data-fire="' + fire + '">' +
      '<td><div class="q">' + m.question + '</div><div class="cat">' + m.category + '</div></td>' +
      '<td class="r mono">' + (m.price * 100).toFixed(1) + '%</td>' +
      '<td class="r mono">' + (m.estimate * 100).toFixed(1) + '%</td>' +
      '<td class="r ' + edgeCls + '">' + pct(m.edge) + '</td>' +
      '<td><div class="bar-wrap"><div class="bar-fill ' + barCls + '" style="width:' + m.score + '%"></div></div></td>' +
      '<td>' + verd + '</td></tr>';
  }
  function paintFeed(filter) {
    var rows = S.markets.filter(function (m) { return filter === "fire" ? m.verdict === "FIRE" : true; });
    el("feedbody").innerHTML = rows.map(row).join("");
  }
  paintFeed("all");

  el("f-all").onclick = function () { setFilter("all"); };
  el("f-fire").onclick = function () { setFilter("fire"); };
  function setFilter(f) {
    el("f-all").className = "fbtn" + (f === "all" ? " on" : "");
    el("f-fire").className = "fbtn" + (f === "fire" ? " on" : "");
    paintFeed(f);
  }
  document.addEventListener("keydown", function (e) {
    if (e.key === "f") setFilter(el("f-fire").className.indexOf("on") < 0 ? "fire" : "all");
  });

  // desk
  el("desk").innerHTML = S.desk.map(function (a) {
    var idle = a.status.indexOf("idle") === 0;
    return '<li><span class="dot ' + (idle ? "idle" : "") + '"></span>' +
      '<span class="ag">' + a.handle + '</span>' +
      '<span class="role">' + a.role + '</span>' +
      '<span class="stat">' + a.status + '</span></li>';
  }).join("");

  // book
  el("bookret").textContent = pct(S.stats.ret);
  if (S.book.length) {
    el("book").innerHTML = S.book.map(function (p) {
      var cls = p.pnl >= 0 ? "pos" : "neg";
      return '<li><span class="bq">' + p.side + " · " + p.question + '</span>' +
        '<span class="' + cls + '">' + usd(p.pnl) + '</span></li>';
    }).join("");
  } else {
    el("book").innerHTML = '<li><span class="muted">no open positions</span></li>';
  }
  el("bookfoot").textContent = "cash " + usd(S.stats.cash) + "   ·   exposure " + usd(S.stats.exposure);

  // rules
  var r = S.limits;
  var rules = [
    [pct(r.min_edge), "min edge"],
    ["$" + r.min_liquidity.toLocaleString("en-US"), "min liquidity"],
    [r.min_hours + "h", "min to resolve"],
    [(r.max_position_frac * 100) + "%", "max position"],
    [(r.max_exposure_frac * 100) + "%", "max exposure"],
    [r.max_per_category, "max / category"]
  ];
  el("rules").innerHTML = rules.map(function (x) {
    return '<div class="rule"><div class="rv">' + x[0] + '</div><div class="rl">' + x[1] + '</div></div>';
  }).join("");

  // clock
  function tick() {
    var d = new Date();
    el("clock").textContent = d.toTimeString().slice(0, 8);
  }
  tick(); setInterval(tick, 1000);
})();
