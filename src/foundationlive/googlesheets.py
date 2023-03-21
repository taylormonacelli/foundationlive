import csv
import hashlib
import logging
import pathlib
import tempfile

import gspread
import gspread.exceptions
import oauth2client.service_account

from . import config as configmod

_logger = logging.getLogger(__name__)

spreadsheet_name = configmod.config["FOUNDATIONLIVE_GOOGLESHEETS_SPREADSHEET_NAME"]
credentials_path = pathlib.Path(
    pathlib.Path(configmod.config["FOUNDATIONLIVE_GOOGLESHEETS_AUTH_JSON_FILE_PATH"])
)

data_dir = credentials_path.parent
last_run_csv_path = data_dir / "cached_last_run.csv"


def get_file_checksum(path: pathlib.Path) -> str:
    checksum = ""
    if not path.exists():
        return checksum

    with open(path, "rb") as f:
        bytes = f.read()  # read entire file as bytes
        checksum = hashlib.sha256(bytes).hexdigest()

    return checksum


def no_change(data: str) -> bool:
    if not last_run_csv_path.exists():
        return False

    last_hash = get_file_checksum(last_run_csv_path)

    tmpfile = tempfile.NamedTemporaryFile(delete=False)
    contents = data

    path = pathlib.Path(tmpfile.name).resolve()

    data = contents.encode(encoding="UTF-8")
    tmpfile.write(data)
    tmpfile.close()

    new_hash = get_file_checksum(path)

    _logger.debug(f"{new_hash=}")
    _logger.debug(f"{last_hash=}")

    if last_hash == new_hash:
        return True

    return False


def main(csv_file):
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    creds = (
        oauth2client.service_account.ServiceAccountCredentials.from_json_keyfile_name(
            credentials_path, scopes
        )
    )
    client = gspread.authorize(creds)
    spreadsheet = client.open(spreadsheet_name)
    worksheet_title = "Sheet1"
    sheet = spreadsheet.worksheet(worksheet_title)
    sheet.clear()

    if no_change(csv_file):
        msg = "skipping update googlge docs because " "last run is same as current run "
        _logger.debug(msg)
        return

    spreadsheet.values_update(
        worksheet_title,
        params={"valueInputOption": "USER_ENTERED"},
        body={"values": list(csv.reader(csv_file.splitlines()))},
    )

    last_run_csv_path.write_text(csv_file)


if __name__ == "__main__":
    main()
