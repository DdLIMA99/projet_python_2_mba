"""Singleton data loader for transactions dataset."""

import os
from typing import Optional

import pandas as pd

# Module-level singleton DataFrame
_df: Optional[pd.DataFrame] = None

# In-memory set of logically deleted transaction IDs
_deleted_ids: set = set()


def _clean(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and normalise the raw transactions DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Raw DataFrame loaded from CSV.

    Returns
    -------
    pd.DataFrame
        Cleaned DataFrame with normalised types and derived columns.
    """
    df = df.copy()

    # --- amount : strip "$" and convert to float ----------------------
    df["amount"] = (
        df["amount"]
        .astype(str)
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.strip()
    )
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0)

    # --- string columns : fill NaN and cast --------------------------
    df["errors"] = df["errors"].fillna("").astype(str)
    df["use_chip"] = df["use_chip"].fillna("Unknown").astype(str)
    df["merchant_city"] = df["merchant_city"].fillna("").astype(str)
    df["merchant_state"] = (
        df["merchant_state"].fillna("").astype(str)
    )
    df["zip"] = df["zip"].fillna("").astype(str)
    df["mcc"] = df["mcc"].fillna("").astype(str)
    df["date"] = df["date"].astype(str)

    # --- id / client_id / merchant_id / card_id : cast to str --------
    df["id"] = df["id"].astype(str)
    df["client_id"] = df["client_id"].astype(str)
    df["merchant_id"] = df["merchant_id"].astype(str)
    df["card_id"] = df["card_id"].astype(str)

    # --- isFraud : derived from errors (non-empty = fraud) -----------
    df["isFraud"] = (df["errors"].str.strip() != "").astype(int)

    return df


def load_data(path: Optional[str] = None) -> pd.DataFrame:
    """Load the transactions CSV into a DataFrame (singleton).

    Parameters
    ----------
    path : Optional[str]
        Path to the CSV file. If None, uses the
        TRANSACTIONS_CSV_PATH environment variable or the
        default path 'data/transactions_data.csv'.

    Returns
    -------
    pd.DataFrame
        The loaded and cleaned transactions DataFrame.

    Raises
    ------
    FileNotFoundError
        If the CSV file does not exist at the given path.
    """
    global _df
    if _df is None:
        default_path: str = os.getenv(
            "TRANSACTIONS_CSV_PATH",
            "data/transactions_data.csv",
        )
        csv_path: str = path if path is not None else default_path
        if not os.path.exists(csv_path):
            raise FileNotFoundError(
                f"Dataset not found at: {csv_path}"
            )
        _df = _clean(pd.read_csv(csv_path))
    return _df


def get_data() -> pd.DataFrame:
    """Return the loaded DataFrame, excluding deleted rows.

    Returns
    -------
    pd.DataFrame
        Active transactions (not logically deleted).

    Raises
    ------
    RuntimeError
        If the dataset has not been loaded yet.
    """
    if _df is None:
        raise RuntimeError(
            "Dataset not loaded. Call load_data() first."
        )
    if _deleted_ids:
        return _df[~_df["id"].isin(_deleted_ids)].copy()
    return _df.copy()


def set_data(df: pd.DataFrame) -> None:
    """Inject a DataFrame directly (used in tests).

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to use as the dataset.
    """
    global _df
    _df = _clean(df)


def mark_deleted(transaction_id: str) -> None:
    """Mark a transaction as logically deleted.

    Parameters
    ----------
    transaction_id : str
        The ID of the transaction to delete.
    """
    _deleted_ids.add(transaction_id)


def is_deleted(transaction_id: str) -> bool:
    """Check if a transaction is logically deleted.

    Parameters
    ----------
    transaction_id : str
        The ID to check.

    Returns
    -------
    bool
        True if the transaction is deleted, False otherwise.
    """
    return transaction_id in _deleted_ids


def reset_data() -> None:
    """Reset the singleton (used in tests).

    Clears the DataFrame and the deleted IDs set.
    """
    global _df
    _df = None
    _deleted_ids.clear()
