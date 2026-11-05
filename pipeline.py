import argparse
import html
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.request import urlopen
from zipfile import ZipFile

import duckdb

SOURCE = "https://s3.amazonaws.com/tripdata/202401-citibike-tripdata.csv.zip"
WORK = Path("work")
DATABASE = WORK / "citibike.duckdb"


def ingest(archive_path):
    with tempfile.TemporaryDirectory(dir=WORK) as directory:
        temp = Path(directory)
        if archive_path is None:
            archive_path = temp / "trips.zip"
            with urlopen(SOURCE, timeout=120) as response, archive_path.open("wb") as output:
                shutil.copyfileobj(response, output)
        csv_files = []
        with ZipFile(archive_path) as archive:
            for member in archive.infolist():
                name = Path(member.filename)
                if name.suffix.lower() != ".csv" or "__MACOSX" in name.parts:
                    continue
                csv_path = temp / f"{len(csv_files)}.csv"
                with archive.open(member) as source, csv_path.open("wb") as output:
                    shutil.copyfileobj(source, output)
                csv_files.append(str(csv_path))
        if not csv_files:
            raise ValueError("El ZIP no contiene archivos CSV.")
        with duckdb.connect(str(DATABASE)) as connection:
            connection.execute(
                """create or replace table raw_trips as
                select ride_id, started_at, ended_at, start_station_name
                from read_csv(?, all_varchar = true, union_by_name = true)""",
                [csv_files],
            )


def bars(rows):
    peak = max((count for _, count in rows), default=1)
    return "".join(
        f'<li><span>{html.escape(label)}</span>'
        f'<meter min="0" max="{peak}" value="{count}" aria-label="{html.escape(label)}">'
        f'{count}</meter><strong>{count:,}</strong></li>'
        for label, count in rows
    )


def render(custom_archive):
    with duckdb.connect(str(DATABASE), read_only=True) as connection:
        raw = connection.execute("select count(*) from raw_trips").fetchone()[0]
        clean = connection.execute("select count(*) from trips").fetchone()[0]
        sections = []
        for metric, title, order in (
            ("day", "Viajes por día", "label"),
            ("hour", "Viajes por hora de salida", "label"),
            ("station", "Diez estaciones con más salidas", "rides desc, label limit 10"),
        ):
            rows = connection.execute(
                f"select label, rides from activity where metric = ? order by {order}", [metric]
            ).fetchall()
            sections.append(f"<section><h2>{title}</h2><ul>{bars(rows)}</ul></section>")
    period = "Archivo local" if custom_archive else "Nueva York · enero de 2024"
    template = Path("dashboard.html").read_text(encoding="utf-8")
    site = Path("site")
    site.mkdir(exist_ok=True)
    (site / "index.html").write_text(template.format(
        period=period, raw=f"{raw:,}", clean=f"{clean:,}",
        rejected=f"{raw - clean:,}", sections="".join(sections)
    ), encoding="utf-8")
    print(f"Filas de origen: {raw:,} | Viajes válidos: {clean:,} | Descartadas: {raw - clean:,}")


def main():
    parser = argparse.ArgumentParser(description="Construye el dashboard de Citi Bike.")
    parser.add_argument("--archive", type=Path, help="ZIP local para pruebas o reproducción")
    args = parser.parse_args()
    WORK.mkdir(exist_ok=True)
    ingest(args.archive)
    subprocess.run([sys.executable, "-m", "dbt.cli.main", "build", "--profiles-dir", "."], check=True)
    render(args.archive is not None)


if __name__ == "__main__":
    main()
