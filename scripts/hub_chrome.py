"""Shared homepage-style chrome for hub subpages (knowledge-base, etc.)."""

HEADER_SOCIAL = """
<nav class="header-social" aria-label="Site links">
  <a class="header-social-link" href="https://github.com/three-cats-lsp" rel="noopener noreferrer" target="_blank" title="GitHub">
    <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.4 5.4 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65S9 18 9 18v4"/><path d="M9 18c-4.51 2-5-2-7-2"/></svg>
    <span>GitHub</span>
  </a>
  <a class="header-social-link" href="https://www.instagram.com/threecats_lsp" rel="noopener noreferrer" target="_blank" title="Instagram">
    <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect x="2" y="2" width="20" height="20" rx="5"/><circle cx="12" cy="12" r="4"/><path d="M17.5 6.5h.01"/></svg>
    <span>Instagram</span>
  </a>
  <a class="header-social-link" href="https://www.thingiverse.com/Roman_Markovtsev/designs" rel="noopener noreferrer" target="_blank" title="Thingiverse">
    <img class="header-social-icon-img" src="https://www.thingiverse.com/favicon.ico" alt="" width="16" height="16"/>
    <span>Thingiverse</span>
  </a>
  <button class="header-social-link header-social-button" type="button" onclick="shareToolkit()" title="Share this page">
    <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="m8.59 13.51 6.83 3.98M15.41 6.51l-6.82 3.98"/></svg>
    <span>Share</span>
  </button>
</nav>"""

PROMO_SECTION = """
<section class="hub-promo" aria-label="Community and support">
  <div class="hub-promo-card hub-promo-ig">
    <p>Follow <a href="https://www.instagram.com/threecats_lsp" rel="noopener noreferrer" target="_blank">@threecats_lsp</a> on Instagram for new gadget releases, build updates, and dive content.</p>
    <a class="btn btn-primary hub-promo-btn" href="https://www.instagram.com/threecats_lsp" rel="noopener noreferrer" target="_blank">
      <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect x="2" y="2" width="20" height="20" rx="5"/><circle cx="12" cy="12" r="4"/><path d="M17.5 6.5h.01"/></svg>
      Follow on Instagram
    </a>
  </div>
  <div class="hub-promo-card hub-promo-donate">
    <p>LSP D-Planner+, T-Viewer, and Get In Water are free and open-source. If they help your diving, consider supporting development.</p>
    <a class="hub-donate-btn" href="https://paypal.me/ThreeCatsLSP" rel="noopener noreferrer" target="_blank">
      <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor" aria-hidden="true"><path d="M7.076 21.337H2.47a.641.641 0 0 1-.633-.74L4.944 3.72a.77.77 0 0 1 .758-.643h6.58c2.753 0 4.667.568 5.694 1.688.9 1.972.741 4.906-.474 7.98-.01.026-.024.05-.036.076l-.4.77c-.972 1.87-2.638 2.82-4.95 2.82h-1.2c-.414 0-.75.336-.814.745l-.65 4.12-.028.18-.636 4.031a.64.64 0 0 1-.633.54z"/></svg>
      Donate via PayPal
    </a>
  </div>
</section>"""

SHARE_SCRIPT = """
<script>
function shareToolkit() {
  const data = { title: document.title, url: location.href };
  if (navigator.share) {
    navigator.share(data).catch(function () {});
    return;
  }
  navigator.clipboard.writeText(location.href).catch(function () {
    prompt("Copy this link:", location.href);
  });
}
</script>"""
