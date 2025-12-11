
from pathlib import Path
from typing import Callable, Iterable, Optional

import pandas as pd

REQUIRED_COLUMNS = ("Date", "Close", "Open")
OPTIONAL_COLUMNS = ("High", "Low", "Volume")


def _validate_columns(columns: Iterable[str], file_name: str) -> list[str]:
    """Ensure required columns exist and determine which optional columns are present."""

    column_set = set(columns)
    missing = [column for column in REQUIRED_COLUMNS if column not in column_set]
    if missing:
        raise ValueError(
            f"Dataset '{file_name}' is missing required columns: {', '.join(missing)}"
        )

    available_optional = [column for column in OPTIONAL_COLUMNS if column in column_set]
    return available_optional


def load_into_stock_data_set(
    file_name: str,
    *,
    data_dir: Optional[Path] = None,
    fetcher: Optional[Callable[[str], pd.DataFrame]] = None,
) -> pd.DataFrame:
    """Return a stock ``DataFrame`` from CSV or an optional API fetcher.

    The function validates schema, fills missing optional fields with ``NaN``, and
    ensures date indices are strictly increasing with no duplicates.

    Args:
        file_name: Base filename (without extension) for the CSV in ``raw_data``.
        data_dir: Override directory for CSV lookup. Defaults to the bundled
            ``raw_data`` directory.
        fetcher: Optional callable that accepts ``file_name`` and returns a
            ``pandas.DataFrame`` shaped like the validated CSV. Use this to load
            data from an API when available.
    """

    if fetcher:
        df = fetcher(file_name)
        source_description = "fetcher"
    else:
        resolved_dir = data_dir or Path(__file__).resolve().parent / "raw_data"
        data_location = resolved_dir / f"{file_name}.csv"
        if not data_location.exists():
            raise FileNotFoundError(
                f"Could not find dataset for '{file_name}' at {data_location}"
            )
        df = pd.read_csv(data_location)
        source_description = str(data_location)

    available_optional = _validate_columns(df.columns, file_name)
    desired_columns = list(REQUIRED_COLUMNS) + available_optional
    for optional_column in OPTIONAL_COLUMNS:
        if optional_column not in available_optional:
            df[optional_column] = pd.NA

    df = df[desired_columns + [column for column in OPTIONAL_COLUMNS if column not in available_optional]]
    df["Date"] = pd.to_datetime(df["Date"], errors="raise")
    df = df.set_index("Date")

    if df.index.has_duplicates:
        duplicate_dates = df.index[df.index.duplicated()].unique().strftime("%Y-%m-%d")
        raise ValueError(
            f"Dataset '{file_name}' from {source_description} has duplicate dates: {', '.join(duplicate_dates)}"
        )

    if not df.index.is_monotonic_increasing:
        raise ValueError(
            f"Dataset '{file_name}' from {source_description} must have dates in strictly increasing order"
        )

    return df
