from __future__ import annotations

import logging
import os
import time
from typing import Optional

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient


class SecretsProvider:
    """
    Loads secrets from Azure Key Vault when enabled, with environment variable fallback.
    - Enable with DSF_KEYVAULT_ENABLED=true and set DSF_KEYVAULT_URI (e.g., https://<name>.vault.azure.net/)
    - Uses DefaultAzureCredential (MSI in Azure, Azure CLI locally)
    - Caches secrets in-process to reduce calls
    """

    def __init__(self, enabled: bool, vault_uri: Optional[str] = None):
        self._enabled = enabled and bool(vault_uri)
        self._vault_uri = vault_uri
        self._cache: dict[str, Optional[str]] = {}
        self._client: Optional[SecretClient] = None
        if self._enabled:
            try:
                cred = DefaultAzureCredential()
                self._client = SecretClient(vault_url=vault_uri, credential=cred)
            except Exception as e:
                logging.warning("Key Vault client init failed; falling back to env: %s", e)
                self._enabled = False

    @classmethod
    def from_env(cls) -> "SecretsProvider":
        enabled = os.getenv("DSF_KEYVAULT_ENABLED", "false").lower() in {"1", "true", "yes"}
        uri = os.getenv("DSF_KEYVAULT_URI")
        return cls(enabled=enabled, vault_uri=uri)

    def get_secret(self, name: str, default: Optional[str] = None) -> Optional[str]:
        # Cached
        if name in self._cache:
            return self._cache[name]

        # Env fallback first for convenience (allows overrides)
        env_val = os.getenv(name)
        if env_val:
            self._cache[name] = env_val
            return env_val

        # Key Vault
        if not self._enabled or not self._client:
            self._cache[name] = default
            return default
        # Simple retries for transient issues
        backoff = 0.5
        for attempt in range(3):
            try:
                secret = self._client.get_secret(name)
                value = secret.value
                self._cache[name] = value
                return value
            except Exception as e:
                if attempt == 2:
                    logging.warning("Key Vault get_secret failed for %s: %s", name, e)
                    break
                time.sleep(backoff)
                backoff *= 2
        self._cache[name] = default
        return default
