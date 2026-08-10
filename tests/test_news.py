"""Tests for core/news.py - aggregate_sentiment and match_news_to_movers."""

from core.news import aggregate_sentiment, match_news_to_movers, MOVEMENT_KEYWORDS


class TestAggregateSentiment:
    """Tests for aggregate_sentiment function."""

    def test_empty_list(self):
        result = aggregate_sentiment([])
        assert result["label"] == "Neutral"
        assert result["score"] == 0.0
        assert result["total"] == 0

    def test_all_positive(self):
        items = [
            {"sentiment": "Positive", "sentiment_score": 0.8},
            {"sentiment": "Positive", "sentiment_score": 0.6},
        ]
        result = aggregate_sentiment(items)
        assert result["label"] == "Bullish"
        assert result["positive"] == 2
        assert result["negative"] == 0
        assert result["total"] == 2
        assert result["score"] > 0.05

    def test_all_negative(self):
        items = [
            {"sentiment": "Negative", "sentiment_score": -0.7},
            {"sentiment": "Negative", "sentiment_score": -0.5},
        ]
        result = aggregate_sentiment(items)
        assert result["label"] == "Bearish"
        assert result["negative"] == 2
        assert result["score"] < -0.05

    def test_mixed_neutral(self):
        items = [
            {"sentiment": "Positive", "sentiment_score": 0.3},
            {"sentiment": "Negative", "sentiment_score": -0.3},
            {"sentiment": "Neutral", "sentiment_score": 0.0},
        ]
        result = aggregate_sentiment(items)
        assert result["label"] == "Neutral"
        assert result["positive"] == 1
        assert result["negative"] == 1
        assert result["neutral"] == 1
        assert result["total"] == 3

    def test_score_rounding(self):
        items = [{"sentiment": "Positive", "sentiment_score": 0.333333}]
        result = aggregate_sentiment(items)
        assert result["score"] == 0.333


class TestMatchNewsToMovers:
    """Tests for match_news_to_movers function."""

    def test_no_movers_below_threshold(self):
        news = [{"title": "AAPL earnings beat", "ticker": "AAPL", "link": ""}]
        changes = {"AAPL": 0.5}  # Below 1% threshold
        result = match_news_to_movers(news, changes)
        assert result == {}

    def test_mover_with_matching_news(self):
        news = [
            {"title": "AAPL earnings beat expectations", "ticker": "AAPL", "link": "https://example.com"},
        ]
        changes = {"AAPL": 3.5}
        result = match_news_to_movers(news, changes)
        assert "AAPL" in result
        assert result["AAPL"]["change"] == 3.5
        assert len(result["AAPL"]["reasons"]) == 1
        assert result["AAPL"]["reasons"][0]["category"] == "Earnings Report"

    def test_mover_without_news(self):
        news = [{"title": "Some other news", "ticker": "MSFT", "link": ""}]
        changes = {"AAPL": 5.0}
        result = match_news_to_movers(news, changes)
        assert "AAPL" not in result  # No matching ticker news

    def test_negative_mover(self):
        news = [
            {"title": "TSLA downgrade by analyst", "ticker": "TSLA", "link": ""},
        ]
        changes = {"TSLA": -4.2}
        result = match_news_to_movers(news, changes)
        assert "TSLA" in result
        assert result["TSLA"]["change"] == -4.2
        assert result["TSLA"]["reasons"][0]["category"] == "Analyst Downgrade"

    def test_unknown_category_defaults_to_market_news(self):
        news = [
            {"title": "Something happened at AAPL today", "ticker": "AAPL", "link": ""},
        ]
        changes = {"AAPL": 2.0}
        result = match_news_to_movers(news, changes)
        assert result["AAPL"]["reasons"][0]["category"] == "Market News"

    def test_max_three_reasons(self):
        news = [
            {"title": f"News {i} about earnings", "ticker": "AAPL", "link": ""}
            for i in range(5)
        ]
        changes = {"AAPL": 2.0}
        result = match_news_to_movers(news, changes)
        assert len(result["AAPL"]["reasons"]) == 3


class TestMovementKeywords:
    """Tests for MOVEMENT_KEYWORDS dict."""

    def test_keywords_not_empty(self):
        assert len(MOVEMENT_KEYWORDS) > 10

    def test_all_values_are_strings(self):
        for key, val in MOVEMENT_KEYWORDS.items():
            assert isinstance(key, str)
            assert isinstance(val, str)
