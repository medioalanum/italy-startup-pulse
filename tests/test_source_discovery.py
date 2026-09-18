from startup_pulse.source_discovery import discover_latest_report


def test_discover_latest_quarterly_report_ignores_annual_and_credit_reports():
    html = """
    <a href="/annual.pdf">Annual report 2025</a>
    <a href="/2_trimestre_2025.pdf">Secondo trimestre 2025</a>
    <a href="/3_trimestre_2025.pdf">Terzo trimestre 2025</a>
    <a href="/4_trimestre_2025_fondo.pdf">Quarto trimestre 2025 Fondo</a>
    """
    report = discover_latest_report(html, "https://example.test/reports")
    assert report.quarter == "2025-Q3"
    assert report.url == "https://example.test/3_trimestre_2025.pdf"
