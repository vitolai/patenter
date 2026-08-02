#!/usr/bin/env python3
"""patenter test suite — smoke tests for core functionality."""

import sys
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from patenter import (
    google_patents_url,
    google_patents_xhr_url,
    google_patents_detail_xhr_url,
    espacenet_url,
    uspto_url,
    web_search_api_hint,
    agent_search_hint,
    normalize_assignee,
    translate_cpc,
    render_jinja2,
    fetch_all_xhr_pages,
    VERSION,
)


class TestURLBuilders:
    def test_google_patents_basic(self):
        url = google_patents_url("wireless charging")
        assert "patents.google.com" in url
        assert "wireless+charging" in url

    def test_google_patents_with_filters(self):
        url = google_patents_url("AI", "US", "2020", "2025", "PATENT")
        assert "country=US" in url
        assert "before=filing:2020" in url
        assert "after=filing:2025" in url

    def test_google_patents_xhr_basic(self):
        url = google_patents_xhr_url("wireless charging")
        assert "patents.google.com/xhr/query" in url
        assert "wireless" in url

    def test_google_patents_xhr_with_filters(self):
        url = google_patents_xhr_url("AI", "US", "2020", "2025", "PATENT")
        assert "patents.google.com/xhr/query" in url
        assert "country" in url

    def test_google_patents_detail_xhr(self):
        url = google_patents_detail_xhr_url("patent/US12345678B2/en")
        assert "patents.google.com/xhr/patent" in url
        assert "US12345678B2" in url
        assert "/en/en" not in url

    def test_espacenet_url(self):
        url = espacenet_url("hybrid bonding")
        assert "espacenet.com" in url
        assert "hybrid+bonding" in url

    def test_uspto_url(self):
        url = uspto_url("semiconductor")
        assert "ppubs.uspto.gov" in url
        assert "semiconductor" in url

    def test_web_search_api_hint(self):
        hint = web_search_api_hint("AI patents", "brave")
        assert "brave" in hint.lower()

    def test_agent_search_hint(self):
        hint = agent_search_hint("wireless charging")
        assert "web_search" in hint
        assert "wireless charging" in hint


class TestNormalizeAssignee:
    def test_strip_inc(self):
        assert normalize_assignee("Qualcomm Inc.") == "Qualcomm"

    def test_strip_ltd(self):
        assert normalize_assignee("Acme Co., Ltd.") == "Acme"

    def test_strip_gmbh(self):
        assert normalize_assignee("Bosch GmbH") == "Bosch"

    def test_strip_corp(self):
        assert normalize_assignee("Acme Corp.") == "Acme"

    def test_no_change(self):
        assert normalize_assignee("Tesla") == "Tesla"

    def test_strip_chinese(self):
        result = normalize_assignee("华为技术有限公司")
        assert result in ("华为技术", "华为")


class TestCPCTranslation:
    def test_known_code(self):
        result = translate_cpc("G06N")
        assert "AI" in result or "machine learning" in result.lower()

    def test_b33y(self):
        result = translate_cpc("B33Y")
        assert "3D printing" in result or "additive" in result.lower()

    def test_h01l(self):
        result = translate_cpc("H01L")
        assert "semiconductor" in result.lower()

    def test_unknown_code(self):
        result = translate_cpc("ZZ99")
        assert result == "ZZ99"


class TestJinja2Render:
    BASE = Path(__file__).parent.parent

    def test_render_simple(self):
        result = render_jinja2("portfolio-comparison-html.jinja", {
            "title": "Test",
            "subtitle": "Test subtitle",
            "companies": [],
            "comparison_matrix": [],
            "tech_overlap": [],
            "white_space": [],
            "strategic": [],
            "caveats": [],
            "data_source": "test",
            "date_start": "2025",
            "date_end": "2026",
            "queries_sent": 0,
            "patents_received": 0,
            "patents_cited": 0,
            "version": "0.4.0",
            "generation_date": "2026-08-02",
        })
        assert "<!DOCTYPE html>" in result
        assert "Test" in result


class TestFetchXhrPagination:
    def test_fetch_xhr_page_zero(self):
        result = fetch_all_xhr_pages("test query", "20250101", "20260101", max_pages=1)
        assert "total" in result
        assert "pages" in result
        assert "patents" in result
        assert isinstance(result["patents"], list)


class TestVersion:
    def test_version_exists(self):
        assert VERSION is not None
        assert len(VERSION) > 0

    def test_version_is_v04(self):
        assert VERSION.startswith("0.4")


class TestSkillFiles:
    BASE = Path(__file__).parent.parent

    @pytest.mark.parametrize("skill", [
        "prior-art-search", "patent-summary", "patent-comparison",
        "core-patent-finder", "portfolio-study", "portfolio-comparison",
        "fto-analysis", "landscape-visualizer",
    ])
    def test_skill_md_exists(self, skill):
        path = self.BASE / "skills" / skill / "SKILL.md"
        assert path.exists(), f"Missing: {path}"

    @pytest.mark.parametrize("ref", [
        "search-strategy.md", "claim-mapping.md", "fto-process.md",
        "portfolio-triage.md", "cpc-translation.md", "name-normalization.md",
    ])
    def test_reference_exists(self, ref):
        path = self.BASE / "references" / ref
        assert path.exists(), f"Missing: {path}"

    @pytest.mark.parametrize("tmpl", [
        "summary-template.md", "comparison-template.md",
        "portfolio-report-template.md", "landscape-html-template.jinja",
        "portfolio-comparison-html.jinja",
    ])
    def test_template_exists(self, tmpl):
        path = self.BASE / "templates" / tmpl
        assert path.exists(), f"Missing: {path}"

    @pytest.mark.parametrize("agent", [
        "prior-art-searcher.md", "patent-analyst.md", "portfolio-auditor.md",
    ])
    def test_agent_exists(self, agent):
        path = self.BASE / "agents" / agent
        assert path.exists(), f"Missing: {path}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
