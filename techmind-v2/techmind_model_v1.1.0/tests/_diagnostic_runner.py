import runpy
import sys
import traceback
from pathlib import Path

SMOKE_TEST = Path('C:\\Users\\MAMÁ\\Downloads\\export\\techmind_model\\tests\\smoke_test.py')
TRACEBACK_FILE = Path('C:\\Users\\MAMÁ\\Downloads\\export\\techmind_model\\reports\\smoke_test_traceback.txt')

try:
    runpy.run_path(
        str(SMOKE_TEST),
        run_name="__main__"
    )

except BaseException:
    detalle = traceback.format_exc()

    TRACEBACK_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    TRACEBACK_FILE.write_text(
        detalle,
        encoding="utf-8"
    )

    print(
        detalle,
        file=sys.stderr,
        flush=True
    )

    raise
