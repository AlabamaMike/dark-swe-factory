from __future__ import annotations

import base64
import hashlib
import hmac
from dataclasses import dataclass
from typing import Optional

import httpx


def verify_signature(secret: str, signature_header: str, payload: bytes) -> bool:
    """Verify GitHub webhook signature (sha256=...)."""
    if not signature_header or not signature_header.startswith("sha256="):
        return False
    digest = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    expected = f"sha256={digest}"
    # Constant time comparison
    return hmac.compare_digest(expected, signature_header)


@dataclass
class GitHubClient:
    repo: str  # e.g., "owner/name"
    token: str
    api_base: str = "https://api.github.com"
    default_branch: str = "main"

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "dsf-bot",
        }

    def _request(self, method: str, path: str, **kwargs) -> httpx.Response:
        url = f"{self.api_base}{path}"
        headers = self._headers()
        headers.update(kwargs.pop("headers", {}))
        with httpx.Client(timeout=15) as client:
            resp = client.request(method, url, headers=headers, **kwargs)
        if resp.status_code >= 400:
            raise RuntimeError(f"GitHub API error {resp.status_code}: {resp.text}")
        return resp

    def get_branch_ref(self, branch: str) -> Optional[str]:
        r = self._request("GET", f"/repos/{self.repo}/git/ref/heads/{branch}")
        if r.status_code == 404:
            return None
        data = r.json()
        return data.get("object", {}).get("sha")

    def get_default_branch_sha(self) -> str:
        r = self._request("GET", f"/repos/{self.repo}")
        data = r.json()
        default_branch = data.get("default_branch", self.default_branch)
        r2 = self._request("GET", f"/repos/{self.repo}/git/ref/heads/{default_branch}")
        return r2.json()["object"]["sha"]

    def create_branch(self, branch: str, from_sha: Optional[str] = None) -> None:
        sha = from_sha or self.get_default_branch_sha()
        self._request(
            "POST",
            f"/repos/{self.repo}/git/refs",
            json={"ref": f"refs/heads/{branch}", "sha": sha},
        )

    def create_or_update_file(self, path: str, content: str, message: str, branch: str) -> None:
        # Try get existing to fetch sha
        sha: Optional[str] = None
        r = self._request(
            "GET",
            f"/repos/{self.repo}/contents/{path}",
            params={"ref": branch},
        )
        if r.status_code == 200:
            sha = r.json().get("sha")
        payload = {
            "message": message,
            "content": base64.b64encode(content.encode()).decode(),
            "branch": branch,
        }
        if sha:
            payload["sha"] = sha
        self._request("PUT", f"/repos/{self.repo}/contents/{path}", json=payload)

    def create_pull_request(self, branch: str, title: str, body: str = "") -> int:
        r = self._request(
            "POST",
            f"/repos/{self.repo}/pulls",
            json={"title": title, "head": branch, "base": self.default_branch, "body": body},
        )
        return r.json()["number"]
