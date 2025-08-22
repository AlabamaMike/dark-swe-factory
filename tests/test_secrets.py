import pytest


@pytest.mark.usefixtures("monkeypatch")
class TestSecretsProvider:
    def _install_dummies(self, monkeypatch, value: str = "vault-value"):
        # Dummy secret object with .value
        class DummySecret:
            def __init__(self, v: str):
                self.value = v

        # Track calls to verify caching
        class DummyClient:
            def __init__(self, *a, **k):
                self.calls = 0

            def get_secret(self, name: str):
                self.calls += 1
                return DummySecret(value)

        class DummyCred:
            def __init__(self, *a, **k):
                pass

        # Patch Azure SDK classes used by SecretsProvider
        monkeypatch.setenv("DSF_KEYVAULT_ENABLED", "true")
        monkeypatch.setenv("DSF_KEYVAULT_URI", "https://dummy.vault")
        monkeypatch.setenv("AZURE_AUTHORITY_HOST", "https://login.microsoftonline.com/")

        # Import here to ensure patches take effect only in test scope
        from services.orchestrator.integrations import secrets as secrets_mod

        # Replace classes with dummies
        monkeypatch.setattr(secrets_mod, "DefaultAzureCredential", DummyCred, raising=True)
        dummy_client = DummyClient()

        class DummySecretClient:
            def __init__(self, *a, **k):
                # return singleton dummy_client
                pass

            def get_secret(self, name: str):
                return dummy_client.get_secret(name)

        monkeypatch.setattr(secrets_mod, "SecretClient", DummySecretClient, raising=True)
        return secrets_mod.SecretsProvider.from_env(), dummy_client

    def test_env_fallback_preferred(self, monkeypatch):
        provider, dummy_client = self._install_dummies(monkeypatch)
        # Provide env override for the secret name
        monkeypatch.setenv("TEST_SECRET", "env-value")
        assert provider.get_secret("TEST_SECRET") == "env-value"
        # Ensure vault was not called because env was used
        assert dummy_client.calls == 0

    def test_vault_used_when_env_missing_and_cache(self, monkeypatch):
        provider, dummy_client = self._install_dummies(monkeypatch, value="vault-abc")
        # No env for this name; should hit vault once and then cache
        assert provider.get_secret("NO_ENV_SECRET") == "vault-abc"
        assert provider.get_secret("NO_ENV_SECRET") == "vault-abc"
        assert dummy_client.calls == 1

    def test_default_returned_when_disabled(self, monkeypatch):
        # Disable Key Vault
        monkeypatch.setenv("DSF_KEYVAULT_ENABLED", "false")
        from services.orchestrator.integrations.secrets import SecretsProvider

        provider = SecretsProvider.from_env()
        assert provider.get_secret("MISSING", default="fallback") == "fallback"
