"""Tests for core/style.py — layout helpers and constants."""

from core.style import (
    COLORS, REGIME_COLORS, PLOTLY_LAYOUT,
    kite_layout, heatmap_layout, PAGE_CSS,
)


class TestColorConstants:
    """Verify color palettes are defined correctly."""

    def test_colors_has_eight_entries(self):
        assert len(COLORS) == 8

    def test_colors_are_hex(self):
        for c in COLORS:
            assert c.startswith("#") and len(c) == 7

    def test_regime_colors_has_four_regimes(self):
        expected = {"Low Volatility", "Normal", "High Volatility", "Crisis"}
        assert set(REGIME_COLORS.keys()) == expected

    def test_regime_colors_are_hex(self):
        for c in REGIME_COLORS.values():
            assert c.startswith("#")


class TestKiteLayout:
    """Test the kite_layout helper."""

    def test_default_height(self):
        layout = kite_layout()
        assert layout["height"] == 380

    def test_custom_height(self):
        layout = kite_layout(height=500)
        assert layout["height"] == 500

    def test_overrides_applied(self):
        layout = kite_layout(height=400, hovermode="closest")
        assert layout["hovermode"] == "closest"
        assert layout["height"] == 400

    def test_inherits_plotly_defaults(self):
        layout = kite_layout()
        assert layout["paper_bgcolor"] == PLOTLY_LAYOUT["paper_bgcolor"]
        assert layout["font"] == PLOTLY_LAYOUT["font"]


class TestHeatmapLayout:
    """Test the heatmap_layout helper."""

    def test_default_height(self):
        layout = heatmap_layout()
        assert layout["height"] == 350

    def test_custom_height(self):
        layout = heatmap_layout(height=500)
        assert layout["height"] == 500

    def test_has_transparent_background(self):
        layout = heatmap_layout()
        assert layout["paper_bgcolor"] == "rgba(0,0,0,0)"


class TestPageCSS:
    """Verify the CSS string contains expected selectors."""

    def test_css_contains_style_tag(self):
        assert "<style>" in PAGE_CSS
        assert "</style>" in PAGE_CSS

    def test_css_contains_inter_font(self):
        assert "Inter" in PAGE_CSS

    def test_css_contains_mobile_breakpoint(self):
        assert "@media (max-width: 768px)" in PAGE_CSS

    def test_css_contains_metric_styling(self):
        assert "stMetric" in PAGE_CSS

    def test_css_contains_page_header(self):
        assert ".page-header" in PAGE_CSS
