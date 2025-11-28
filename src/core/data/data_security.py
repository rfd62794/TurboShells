"""
Data Security for TurboShells

This module contains only security and encryption logic,
following Single Responsibility Principle.
"""

import json
import hashlib
import hmac
import os
import secrets
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64


class SecurityManager:
    """Security features for data protection"""

    def __init__(self, encryption_key: Optional[bytes] = None):
        self.encryption_enabled = True
        self.checksum_enabled = True

        # Generate or use provided encryption key
        if encryption_key:
            self.encryption_key = encryption_key
        else:
            self.encryption_key = self._generate_encryption_key()

        self.fernet = Fernet(self.encryption_key)

    def _generate_encryption_key(self) -> bytes:
        """Generate encryption key from secure sources"""
        password = self._load_secret(
            env_var="TURBO_SHELLS_ENCRYPTION_PASSWORD",
            config_key="encryption_password",
            fallback_factory=self._derive_machine_password,
        )
        salt = self._load_secret(
            env_var="TURBO_SHELLS_ENCRYPTION_SALT",
            config_key="encryption_salt",
            fallback_factory=self._load_or_generate_local_salt,
        )

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key

    def _load_secret(
        self,
        *,
        env_var: str,
        config_key: str,
        fallback_factory,
    ) -> bytes:
        """Load a secret from env, optional config file, or fallback factory."""
        secret = os.getenv(env_var)
        if secret:
            return secret.encode("utf-8")

        config_path = os.getenv("TURBO_SHELLS_SECURITY_CONFIG")
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as config_file:
                    config_data = json.load(config_file)
                config_secret = config_data.get(config_key)
                if config_secret:
                    return config_secret.encode("utf-8")
            except (OSError, json.JSONDecodeError):
                # Fall back to computed secret if config is inaccessible
                pass

        return fallback_factory()

    def _derive_machine_password(self) -> bytes:
        """Create a per-machine password for local development."""
        machine_id = os.environ.get(
            "COMPUTERNAME", os.environ.get("HOSTNAME", "localhost")
        )
        user_id = os.environ.get("USERNAME", os.environ.get("USER", "user"))
        return f"turbo_shells_{machine_id}_{user_id}".encode("utf-8")

    def _load_or_generate_local_salt(self) -> bytes:
        """Persist a salt on disk for local usage when none is provided."""
        salt_file = os.path.join(os.path.dirname(__file__), ".turbo_shells_salt")
        try:
            if os.path.exists(salt_file):
                with open(salt_file, "rb") as f:
                    return f.read()

            salt = secrets.token_bytes(32)
            with open(salt_file, "wb") as f:
                f.write(salt)
            return salt
        except (OSError, IOError):
            machine_id = os.environ.get(
                "COMPUTERNAME", os.environ.get("HOSTNAME", "localhost")
            )
            return f"turbo_shells_salt_{machine_id}".encode("utf-8")

    def calculate_checksum(self, data: Dict[str, Any]) -> str:
        """Calculate SHA-256 checksum for data"""
        if not self.checksum_enabled:
            return ""

        data_string = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(data_string.encode("utf-8")).hexdigest()

    def verify_checksum(self, data: Dict[str, Any], expected_checksum: str) -> bool:
        """Verify data integrity with checksum"""
        if not self.checksum_enabled or not expected_checksum:
            return True

        actual_checksum = self.calculate_checksum(data)
        return hmac.compare_digest(actual_checksum, expected_checksum)

    def encrypt_data(self, data: str) -> bytes:
        """Encrypt data with Fernet symmetric encryption"""
        if not self.encryption_enabled:
            return data.encode("utf-8")

        return self.fernet.encrypt(data.encode("utf-8"))

    def decrypt_data(self, encrypted_data: bytes) -> str:
        """Decrypt data with Fernet symmetric encryption"""
        if not self.encryption_enabled:
            return encrypted_data.decode("utf-8")

        try:
            return self.fernet.decrypt(encrypted_data).decode("utf-8")
        except Exception as e:
            raise ValueError(f"Decryption failed: {e}")

    def sign_data(self, data: Dict[str, Any]) -> str:
        """Create HMAC signature for data"""
        data_string = json.dumps(data, sort_keys=True, default=str)
        signature = hmac.new(
            self.encryption_key, data_string.encode("utf-8"), hashlib.sha256
        ).hexdigest()
        return signature

    def verify_signature(self, data: Dict[str, Any], signature: str) -> bool:
        """Verify HMAC signature for data"""
        data_string = json.dumps(data, sort_keys=True, default=str)
        expected_signature = hmac.new(
            self.encryption_key, data_string.encode("utf-8"), hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(signature, expected_signature)

    def sanitize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize data for privacy protection"""
        # Remove or mask sensitive fields
        sensitive_fields = ["player_id", "session_stats", "transaction_history"]

        sanitized = data.copy()
        for field in sensitive_fields:
            if field in sanitized:
                if isinstance(sanitized[field], str):
                    # Mask string fields
                    sanitized[field] = "*" * len(sanitized[field])
                elif isinstance(sanitized[field], dict):
                    # Remove dict fields
                    sanitized[field] = {}
                elif isinstance(sanitized[field], list):
                    # Clear list fields
                    sanitized[field] = []

        return sanitized


# ============================================================================
# GLOBAL SECURITY MANAGER INSTANCE
# ============================================================================

security_manager = SecurityManager()
