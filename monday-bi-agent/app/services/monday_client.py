from __future__ import annotations

import requests
from typing import Dict, List, Optional, Tuple

from app.config import settings
from app.models import BoardColumn, BoardData, BoardItem


class MondayAPIError(Exception):
    pass


class MondayClient:
    def __init__(self) -> None:
        self.url = settings.monday_api_url
        self.headers = {
            "Authorization": settings.monday_api_token,
            "Content-Type": "application/json",
            "API-Version": settings.monday_api_version,
        }

    def _post(self, query: str, variables: Optional[Dict] = None) -> Dict:
        payload = {"query": query, "variables": variables or {}}
        resp = requests.post(self.url, headers=self.headers, json=payload, timeout=60)

        if resp.status_code != 200:
            raise MondayAPIError(f"HTTP {resp.status_code}: {resp.text}")

        data = resp.json()
        if "errors" in data and data["errors"]:
            raise MondayAPIError(str(data["errors"]))

        if "data" not in data:
            raise MondayAPIError(f"Malformed response: {data}")

        return data["data"]

    def list_boards(self, limit: int = 100) -> List[Dict]:
        query = """
        query ListBoards($limit: Int!) {
          boards(limit: $limit) {
            id
            name
          }
        }
        """
        data = self._post(query, {"limit": limit})
        return data["boards"]

    def find_board_by_name(self, board_name: str) -> Dict:
        boards = self.list_boards(limit=200)
        exact = [b for b in boards if b["name"].strip().lower() == board_name.strip().lower()]
        if exact:
            return exact[0]

        partial = [b for b in boards if board_name.strip().lower() in b["name"].strip().lower()]
        if partial:
            return partial[0]

        raise MondayAPIError(f"Board not found: {board_name}")

    def get_board_columns(self, board_id: str) -> List[BoardColumn]:
        query = """
        query GetBoardColumns($boardId: [ID!]!) {
          boards(ids: $boardId) {
            id
            name
            columns {
              id
              title
              type
            }
          }
        }
        """
        data = self._post(query, {"boardId": [board_id]})
        board = data["boards"][0]
        return [BoardColumn(id=c["id"], title=c["title"], type=c["type"]) for c in board["columns"]]

    def get_all_board_items(self, board_id: str, page_size: int = 200) -> List[BoardItem]:
        # Cursor pagination through items_page to avoid over-fetching.
        query = """
        query GetItemsPage($boardId: ID!, $limit: Int!, $cursor: String) {
          boards(ids: [$boardId]) {
            id
            name
            items_page(limit: $limit, cursor: $cursor) {
              cursor
              items {
                id
                name
                column_values {
                  id
                  text
                  value
                  type
                  column {
                    title
                  }
                }
              }
            }
          }
        }
        """

        all_items: List[BoardItem] = []
        cursor = None

        while True:
            data = self._post(query, {"boardId": board_id, "limit": page_size, "cursor": cursor})
            board = data["boards"][0]
            page = board["items_page"]
            items = page["items"]

            for item in items:
                cv_map = {}
                for cv in item["column_values"]:
                    title = cv["column"]["title"]
                    cv_map[title] = {
                        "id": cv["id"],
                        "text": cv.get("text"),
                        "value": cv.get("value"),
                        "type": cv.get("type"),
                    }
                all_items.append(
                    BoardItem(
                        id=str(item["id"]),
                        name=item["name"],
                        column_values=cv_map,
                    )
                )

            cursor = page.get("cursor")
            if not cursor:
                break

        return all_items

    def get_board_data(self, board_name: str) -> BoardData:
        board = self.find_board_by_name(board_name)
        board_id = str(board["id"])
        columns = self.get_board_columns(board_id)
        items = self.get_all_board_items(board_id)
        return BoardData(
            board_id=board_id,
            board_name=board["name"],
            columns=columns,
            items=items,
        )

    def fetch_deals_and_work_orders(self) -> Tuple[BoardData, BoardData]:
        deals = self.get_board_data(settings.deals_board_name)
        work_orders = self.get_board_data(settings.work_orders_board_name)
        return deals, work_orders