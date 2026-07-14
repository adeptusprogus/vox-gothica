(function () {
  "use strict";

  var roll = document.getElementById("collegium-roll");
  if (!roll) return;

  var repo = roll.dataset.repo || "adeptusprogus/vox-gothica";

  function esc(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function effigies(entry) {
    if (entry.avatar) {
      return (
        "<span class='effigies'><img src='" +
        esc(entry.avatar) +
        "' alt='' loading='lazy'></span>"
      );
    }
    return "<span class='effigies glyphus'>⚙</span>";
  }

  function card(entry) {
    var inner =
      effigies(entry) +
      "<span class='corpus-magi'><span class='nomen-magi'>" +
      esc(entry.display) +
      "</span><span class='titulus-magi'>" +
      esc(entry.title) +
      "</span></span>";

    if (entry.url) {
      return (
        "<a class='magus-carta' href='" +
        esc(entry.url) +
        "' target='_blank' rel='noopener noreferrer'>" +
        inner +
        "</a>"
      );
    }
    return "<div class='magus-carta'>" + inner + "</div>";
  }

  function pinnedLogins(p) {
    var logins = [];
    var github = p.github;
    if (Array.isArray(github)) {
      github.forEach(function (g) {
        if (g) logins.push(String(g).toLowerCase());
      });
    } else if (github) {
      logins.push(String(github).toLowerCase());
    }
    (p.aliases || []).forEach(function (a) {
      if (a) logins.push(String(a).toLowerCase());
    });
    return logins;
  }

  function apiForPinned(p, byLogin) {
    var logins = pinnedLogins(p);
    for (var i = 0; i < logins.length; i++) {
      if (byLogin[logins[i]]) return byLogin[logins[i]];
    }
    return null;
  }

  function mergeRoll(config, apiContributors) {
    var byLogin = {};
    (apiContributors || []).forEach(function (c) {
      byLogin[c.login.toLowerCase()] = c;
    });

    var seen = {};
    var out = [];

    (config.pinned || []).forEach(function (p) {
      pinnedLogins(p).forEach(function (login) {
        seen[login] = true;
      });
      var api = apiForPinned(p, byLogin);
      out.push({
        display: p.display || (api && api.login) || p.github || "Unknown",
        title: p.title || config.default_title || "Contributor",
        avatar: api && api.avatar_url,
        url: p.url || (api && api.html_url),
      });
    });

    (apiContributors || []).forEach(function (c) {
      var login = c.login.toLowerCase();
      if (seen[login]) return;
      seen[login] = true;
      out.push({
        display: c.login,
        title: config.default_title || "Contributor",
        avatar: c.avatar_url,
        url: c.html_url,
      });
    });

    return out;
  }

  function render(entries) {
    roll.innerHTML = entries.map(card).join("");
  }

  function showError() {
    roll.innerHTML =
      "<div class='magus-carta'><span class='effigies glyphus'>⚙</span><span class='corpus-magi'><span class='nomen-magi'>Collegium unavailable</span><span class='titulus-magi'>The noosphere is silent — see <a href='https://github.com/" +
      esc(repo) +
      "/graphs/contributors'>GitHub contributors</a>.</span></span></div>";
  }

  Promise.all([
    fetch("contributors.json").then(function (r) {
      if (!r.ok) throw new Error("contributors.json");
      return r.json();
    }),
    fetch("https://api.github.com/repos/" + repo + "/contributors?per_page=100").then(
      function (r) {
        if (!r.ok) throw new Error("github api");
        return r.json();
      }
    ),
  ])
    .then(function (parts) {
      render(mergeRoll(parts[0], parts[1]));
    })
    .catch(showError);
})();
