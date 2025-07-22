from notion.api_connection import get_missions_db
import json

if __name__ == "__main__":
    # Example usage

    def main() -> None:
        missions_db = get_missions_db()
        print(missions_db)
        with open("missions_db.json", "w") as f:
            json.dump(missions_db, f, indent=4)

    main()
