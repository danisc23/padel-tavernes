from unittest.mock import patch

from flask import Response


@patch("app.api.greedy_players.scrap_greedy_players")
def test_get_returns_response(mock_scrap_greedy_players, client) -> None:
    mock_scrap_greedy_players.return_value = []
    response = client.get("/api/padelvuestro.es/greedy-players/?sport=padel")
    assert isinstance(response, Response)


@patch("app.api.greedy_players.scrap_greedy_players")
def test_get_returns_json_response_with_greedy_players(mock_scrap_greedy_players, client) -> None:
    mock_scrap_greedy_players.return_value = [
        {"name": "Player1", "count": 2, "different_dates": 3, "dates": ["2024-06-11", "2024-06-12", "2024-06-13"]},
        {"name": "Player2", "count": 1, "different_dates": 3, "dates": ["2024-06-11", "2024-06-12", "2024-06-13"]},
    ]

    response = client.get("/api/padelvuestro.es/greedy-players/?sport=padel")
    print(response.data)
    print("HIJO DE PUTA")
    json_data = response.get_json()

    assert isinstance(json_data, list)
    assert len(json_data) == 2
    assert json_data[0]["name"] == "Player1"
    assert json_data[0]["count"] == 2
    assert json_data[0]["different_dates"] == 3
    assert json_data[0]["dates"] == ["2024-06-11", "2024-06-12", "2024-06-13"]
    assert json_data[1]["name"] == "Player2"
    assert json_data[1]["count"] == 1
    assert json_data[1]["different_dates"] == 3
    assert json_data[1]["dates"] == ["2024-06-11", "2024-06-12", "2024-06-13"]
