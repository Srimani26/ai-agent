"""
moa.py — Mixture-of-Agents helper for ARIA

Sends a prompt to several "proposer" models in parallel via FreeLLMAPI,
then returns their draft answers so ARIA's main Gemini call can act as
the "aggregator" and write one final, synthesized response.
"""

import concurrent.futures
import requests
import streamlit as st

PROPOSER_MODELS = [
    "auto:fast",
    "gemini-2.0-flash",
]

PROPOSER_TIMEOUT_SECONDS = 20


def _call_freellmapi(model: str, prompt: str):
    base_url = st.secrets.get("FREELLMAPI_URL", "http://localhost:3001/v1")
    api_key = st.secrets.get("FREELLMAPI_KEY", "")

    if not api_key:
        return None

    try:
        resp = requests.post(
            base_url.rstrip("/") + "/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 800,
            },
            timeout=PROPOSER_TIMEOUT_SECONDS,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
    except Exception:
        return None


def get_proposer_drafts(prompt: str):
    drafts = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(PROPOSER_MODELS)) as executor:
        futures = {
            executor.submit(_call_freellmapi, model, prompt): model
            for model in PROPOSER_MODELS
        }
        for future in concurrent.futures.as_completed(futures, timeout=PROPOSER_TIMEOUT_SECONDS + 5):
            result = future.result()
            if result:
                drafts.append(result)
    return drafts


def build_aggregator_prompt(user_prompt: str, drafts):
    if not drafts:
        return user_prompt

    draft_block = "\n\n".join(
        f"--- Draft {i+1} ---\n{d}" for i, d in enumerate(drafts)
    )

    return (
        f"{user_prompt}\n\n"
        "---\n"
        "You have access to draft answers from other AI models below. "
        "Use them as reference material only — pull in anything genuinely useful, "
        "correct any mistakes you notice in them, and ignore anything wrong or irrelevant. "
        "Write ONE final, complete answer in your own voice. Do not mention that you "
        "were given drafts or reference other models.\n\n"
        f"{draft_block}"
    )
