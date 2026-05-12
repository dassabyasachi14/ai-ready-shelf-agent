import os


def get_secret(key: str, default: str = "") -> str:
    """Read a secret from st.secrets (Streamlit Cloud) or os.environ (local).

    Tries st.secrets first so Streamlit Cloud always wins; falls back to
    os.environ / .env for local development.
    """
    try:
        import streamlit as st
        val = st.secrets.get(key, None)
        if val is not None:
            return str(val)
    except Exception:
        pass
    return os.getenv(key, default)
