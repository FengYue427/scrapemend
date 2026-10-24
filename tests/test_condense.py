"""Tests for HTML condensing — the token-saving pre-pass before healing."""

from __future__ import annotations

from scrapemend.condense import condense

NOISY = """
<html>
  <head>
    <style>.x { color: red; }</style>
    <script>var tracking = 1; doStuff();</script>
  </head>
  <body>
    <div class="product" data-track="abc" style="margin:0" onclick="go()">
      <h1 id="name" class="title">Widget</h1>
      <span class="price" data-currency="usd">$5.00</span>
    </div>
    <noscript>enable js</noscript>
  </body>
</html>
"""


def test_drops_script_and_style_content():
    out = condense(NOISY)
    assert "tracking" not in out
    assert "color: red" not in out
    assert "enable js" not in out


def test_keeps_class_and_id_drops_noise_attrs():
    out = condense(NOISY)
    # Structural hooks the model needs must survive.
    assert "product" in out
    assert "title" in out
    assert 'id="name"' in out or "name" in out
    # Noise attributes must be gone.
    assert "data-track" not in out
    assert "onclick" not in out
    assert "margin:0" not in out


def test_preserves_the_actual_data_text():
    out = condense(NOISY)
    assert "Widget" in out
    assert "$5.00" in out


def test_respects_length_limit():
    big = "<body>" + "<div class='a'>x</div>" * 10000 + "</body>"
    out = condense(big, limit=500)
    assert len(out) <= 500


def test_malformed_html_does_not_crash():
    out = condense("<div class='a'><span>unclosed")
    assert isinstance(out, str)
    assert "unclosed" in out
