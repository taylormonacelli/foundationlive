import logging
import pathlib

import dotenv
import platformdirs

_logger = logging.getLogger(__name__)

package = __name__.split(".")[0]
package = "foundationlive"

appname = package
appauthor = "taylor"

user_data_path = pathlib.Path(platformdirs.user_data_dir(appname, appauthor))
env_path = user_data_path / ".env"

template_str = """
FOUNDATIONLIVE_TEMPLATES_OUTPUT_DIRECTORY=~/Library/Application Support/foundationlive/
FOUNDATIONLIVE_GOOGLESHEETS_AUTH_JSON_FILE_PATH=~/Library/Application Support/foundationlive/foundationlive-381012-3f86434e1aa2.json
FOUNDATIONLIVE_DATA_PATH=~/Documents/time_data.yaml
FOUNDATIONLIVE_GOOGLESHEETS_WORKBOOK_NAME=Copy of streambox / taylor / timesheet
HOURLY_RATE=100.00
""".strip()  # noqa: E501


def init():
    env_path.parent.mkdir(exist_ok=True, parents=True)
    if not env_path.exists():
        env_path.write_text(template_str)


def debug(config):
    for key, value in config.items():
        print(f"{key=}")
        print(f"{value=}")


init()
config = dotenv.dotenv_values(env_path)

x = config["FOUNDATIONLIVE_GOOGLESHEETS_AUTH_JSON_FILE_PATH"]
config["FOUNDATIONLIVE_GOOGLESHEETS_AUTH_JSON_FILE_PATH"] = pathlib.Path(x).expanduser()

x = config["FOUNDATIONLIVE_DATA_PATH"]
config["FOUNDATIONLIVE_DATA_PATH"] = pathlib.Path(x).expanduser()


def show_config():
    print(f"{env_path}")
    debug(config)


if __name__ == "__main__":
    print(env_path)
    debug(config)
