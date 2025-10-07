import os
import json
from typing import Any, Dict, List, Optional, Tuple

import streamlit as st
from supabase import create_client, Client

# ---------- Supabase client and auth helpers ----------

@st.cache_resource
def get_supabase() -> Optional[Client]:
    try:
        url = st.secrets.get("SUPABASE_URL")
        key = st.secrets.get("SUPABASE_ANON_KEY")
    except Exception:
        url = None
        key = None
    if not url or not key:
        return None
    sb = create_client(url, key)

    # Restore session from st.session_state if available (first creation only)
    try:
        sess = st.session_state.get("_sb_session")
        if sess and isinstance(sess, dict):
            access_token = sess.get("access_token")
            refresh_token = sess.get("refresh_token")
            if access_token and refresh_token:
                sb.auth.set_session(access_token, refresh_token)
    except Exception:
        pass
    return sb


def apply_session_from_state() -> None:
    """Ensure the cached Supabase client has the current session from st.session_state.
    Safe to call on every rerun. No-op if not configured or no tokens present.
    """
    sb = get_supabase()
    if not sb:
        return
    try:
        sess = st.session_state.get("_sb_session")
        if sess and isinstance(sess, dict):
            at = sess.get("access_token")
            rt = sess.get("refresh_token")
            if at and rt:
                sb.auth.set_session(at, rt)
    except Exception:
        pass


def is_supabase_configured() -> bool:
    try:
        return bool(st.secrets.get("SUPABASE_URL") and st.secrets.get("SUPABASE_ANON_KEY"))
    except Exception:
        return False


def get_current_user_id() -> Optional[str]:
    # Fast-path: return cached user id if present
    try:
        uid = st.session_state.get("_sb_user_id")
        if isinstance(uid, str) and uid:
            return uid
    except Exception:
        pass
    sb = get_supabase()
    if not sb:
        return None
    try:
        res = sb.auth.get_user()
        if res and res.user:
            try:
                st.session_state["_sb_user_id"] = res.user.id
            except Exception:
                pass
            return res.user.id
    except Exception:
        pass
    return None


def sign_in(email: str, password: str) -> Tuple[bool, str]:
    sb = get_supabase()
    if not sb:
        return False, "Supabase is not configured."
    try:
        res = sb.auth.sign_in_with_password({"email": email, "password": password})
        if res and res.session:
            st.session_state["_sb_session"] = {
                "access_token": res.session.access_token,
                "refresh_token": res.session.refresh_token,
            }
            # Cache user id to avoid get_user() on every rerun
            try:
                if getattr(res, "user", None) and getattr(res.user, "id", None):
                    st.session_state["_sb_user_id"] = res.user.id
                else:
                    got = sb.auth.get_user()
                    if got and got.user:
                        st.session_state["_sb_user_id"] = got.user.id
            except Exception:
                pass
        return True, "Signed in"
    except Exception as e:
        return False, str(e)


def sign_up(email: str, password: str) -> Tuple[bool, str]:
    sb = get_supabase()
    if not sb:
        return False, "Supabase is not configured."
    try:
        res = sb.auth.sign_up({"email": email, "password": password})
        if res and res.session:
            st.session_state["_sb_session"] = {
                "access_token": res.session.access_token,
                "refresh_token": res.session.refresh_token,
            }
            # Cache user id
            try:
                if getattr(res, "user", None) and getattr(res.user, "id", None):
                    st.session_state["_sb_user_id"] = res.user.id
                else:
                    got = sb.auth.get_user()
                    if got and got.user:
                        st.session_state["_sb_user_id"] = got.user.id
            except Exception:
                pass
            return True, "Account created. Check your email for verification if required."
        # Some projects require email verification before a session is returned.
        # In that case, immediately attempt sign-in (works if email already existed or verification not required).
        try:
            login = sb.auth.sign_in_with_password({"email": email, "password": password})
            if login and login.session:
                st.session_state["_sb_session"] = {
                    "access_token": login.session.access_token,
                    "refresh_token": login.session.refresh_token,
                }
                return True, "Signed in"
        except Exception:
            pass
        return True, "Account request received. If verification is required, check your email."
    except Exception as e:
        msg = str(e)
        # Gracefully handle rate-limit/cooldown messages by attempting sign-in immediately
        if "For security purposes" in msg or "request this after" in msg:
            try:
                login = sb.auth.sign_in_with_password({"email": email, "password": password})
                if login and login.session:
                    st.session_state["_sb_session"] = {
                        "access_token": login.session.access_token,
                        "refresh_token": login.session.refresh_token,
                    }
                    try:
                        if getattr(login, "user", None) and getattr(login.user, "id", None):
                            st.session_state["_sb_user_id"] = login.user.id
                        else:
                            got = sb.auth.get_user()
                            if got and got.user:
                                st.session_state["_sb_user_id"] = got.user.id
                    except Exception:
                        pass
                    return True, "Signed in"
            except Exception:
                # Hide the noisy cooldown text
                return False, "Please try signing in with the same email and password."
        return False, msg


def sign_out() -> None:
    sb = get_supabase()
    if not sb:
        return
    try:
        sb.auth.sign_out()
    except Exception:
        pass
    st.session_state.pop("_sb_session", None)
    st.session_state.pop("_sb_user_id", None)


# ---------- Data operations (per-user) ----------

# Table: client_configs
# Columns: id (uuid), user_id (uuid), client_name (text), config (jsonb), updated_at (timestamptz)


@st.cache_data(ttl=120)
def list_client_names(user_id: str) -> List[str]:
    sb = get_supabase()
    if not sb:
        return []
    try:
        res = sb.table("client_configs").select("client_name").eq("user_id", user_id).execute()
        names = sorted({row["client_name"] for row in (res.data or []) if row.get("client_name")})
        return list(names)
    except Exception:
        return []


def fetch_client_config(user_id: str, client_name: str) -> Optional[Dict[str, Any]]:
    sb = get_supabase()
    if not sb:
        return None
    try:
        res = (
            sb.table("client_configs")
            .select("config")
            .eq("user_id", user_id)
            .eq("client_name", client_name)
            .single()
            .execute()
        )
        if res.data and isinstance(res.data, dict):
            return res.data.get("config")
    except Exception:
        return None
    return None


def upsert_client_config(user_id: str, client_name: str, config: Dict[str, Any]) -> bool:
    sb = get_supabase()
    if not sb:
        return False
    try:
        payload = {
            "user_id": user_id,
            "client_name": client_name,
            "config": config,
        }
        # Use upsert on unique (user_id, client_name)
        # Note: supabase-py expects a comma-separated string for on_conflict
        sb.table("client_configs").upsert(payload, on_conflict="user_id,client_name").execute()
        return True
    except Exception as e:
        try:
            # Surface a hint in debug messages for troubleshooting in the app
            if "debug_messages" in st.session_state:
                st.session_state.debug_messages.append(f"[Supabase] upsert_client_config failed: {str(e)}")
        except Exception:
            pass
        return False


# Table: client_sessions
# Columns: id, user_id, client_name, filename, display_name, timestamp, created_date, description, data_types (jsonb), session_data (jsonb)


def list_sessions(user_id: str, client_name: str) -> List[Dict[str, Any]]:
    sb = get_supabase()
    if not sb:
        return []
    try:
        res = (
            sb.table("client_sessions")
            .select("filename, display_name, timestamp, created_date, description, data_types")
            .eq("user_id", user_id)
            .eq("client_name", client_name)
            .order("timestamp", desc=True)
            .execute()
        )
        return res.data or []
    except Exception:
        return []


def save_session(user_id: str, client_name: str, filename: str, metadata: Dict[str, Any], session_data: Dict[str, Any]) -> bool:
    sb = get_supabase()
    if not sb:
        return False
    try:
        payload = {
            "user_id": user_id,
            "client_name": client_name,
            "filename": filename,
            "display_name": metadata.get("display_name", filename.replace(".json", "")),
            "timestamp": metadata.get("timestamp"),
            "created_date": metadata.get("created_date"),
            "description": metadata.get("description"),
            "data_types": metadata.get("data_types", []),
            "session_data": session_data,
        }
        # unique (user_id, client_name, filename)
        # supabase-py expects a comma-separated string for on_conflict
        sb.table("client_sessions").upsert(payload, on_conflict="user_id,client_name,filename").execute()
        return True
    except Exception as e:
        try:
            if "debug_messages" in st.session_state:
                st.session_state.debug_messages.append(f"[Supabase] save_session failed: {str(e)}")
        except Exception:
            pass
        return False


def fetch_session(user_id: str, client_name: str, filename: str) -> Optional[Dict[str, Any]]:
    sb = get_supabase()
    if not sb:
        return None
    try:
        res = (
            sb.table("client_sessions")
            .select("session_data")
            .eq("user_id", user_id)
            .eq("client_name", client_name)
            .eq("filename", filename)
            .single()
            .execute()
        )
        if res.data and isinstance(res.data, dict):
            return res.data.get("session_data")
    except Exception:
        return None
    return None


def delete_session(user_id: str, client_name: str, filename: str) -> bool:
    sb = get_supabase()
    if not sb:
        return False
    try:
        sb.table("client_sessions").delete().eq("user_id", user_id).eq("client_name", client_name).eq("filename", filename).execute()
        return True
    except Exception:
        return False
