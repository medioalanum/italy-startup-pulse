from startup_pulse.pdf_source import parse_region_table, parse_sector_table


def test_parse_region_table() -> None:
    records = parse_region_table(
        "1 LOMBARDIA 3390 27,86 3,98\n2 LAZIO 1414 11,62 2,45", "2025-Q3"
    )
    assert [(record.name, record.startup_count) for record in records] == [
        ("LOMBARDIA", 3390),
        ("LAZIO", 1414),
    ]


def test_parse_sector_table() -> None:
    records = parse_sector_table(
        "Agricoltura e attività connesse TOTALE 85 0,70 1,25\n"
        "Servizi alle imprese TOTALE 9782 80,39 7,82",
        "2025-Q3",
    )
    assert [(record.name, record.startup_count) for record in records] == [
        ("Agricoltura e attività connesse", 85),
        ("Servizi alle imprese", 9782),
    ]
