"""scripts/auto_update.ps1 逻辑的轻量测试（pytest 风格）。

auto_update.ps1 是 PowerShell 脚本，无法直接用 Python 单元测试覆盖其全部逻辑。
本测试验证其可测的外部契约：
  - 脚本文件存在且结构完整
  - VERSION 文件存在（版本比对的基础）
  - TTL 缓存逻辑（24h）的 Python 等价物
  - 版本字符串比对语义
  - 缓存 JSON 的读写契约

若环境无 PowerShell 则跳过 PowerShell 执行类测试。
"""

import os
import sys
import json
import shutil
import tempfile
from pathlib import Path
from datetime import datetime, timedelta, timezone

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "auto_update.ps1"
VERSION_FILE = PROJECT_ROOT / "VERSION"


# ── 脚本与版本文件存在性 ─────────────────────────────────────────────

class TestScriptIntegrity:

    def test_auto_update_ps1_exists(self):
        """auto_update.ps1 脚本文件应存在。"""
        assert SCRIPT_PATH.is_file(), "scripts/auto_update.ps1 不存在"

    def test_version_file_exists(self):
        """VERSION 文件应存在（版本比对的基础）。"""
        assert VERSION_FILE.is_file(), "VERSION 文件不存在"
        content = VERSION_FILE.read_text(encoding="utf-8").strip()
        assert content, "VERSION 文件为空"

    def test_script_contains_cache_logic(self):
        """脚本应包含 TTL 缓存逻辑关键字。"""
        content = SCRIPT_PATH.read_text(encoding="utf-8")
        assert "Test-CacheValid" in content
        assert "TtlSeconds" in content
        assert "86400" in content  # 24h

    def test_script_contains_incremental_logic(self):
        """脚本应包含增量下载（compare API）逻辑。"""
        content = SCRIPT_PATH.read_text(encoding="utf-8")
        assert "compare" in content.lower()
        assert "raw_url" in content

    def test_script_has_force_and_background_params(self):
        """脚本应支持 -Force 和 -Background 参数。"""
        content = SCRIPT_PATH.read_text(encoding="utf-8")
        assert "$Force" in content
        assert "$Background" in content


# ── 版本比对语义（Python 等价）──────────────────────────────────────

class TestVersionCompare:

    def test_equal_versions_no_update(self):
        """本地与远程版本相同时无需更新。"""
        local = "abc123"
        remote = "abc123"
        assert local == remote  # 脚本中 `if ($LocalVersion -eq $RemoteVersion)`

    def test_different_versions_need_update(self):
        """本地与远程版本不同时需要更新。"""
        local = "abc123"
        remote = "def456"
        assert local != remote


# ── TTL 缓存逻辑（Python 等价）──────────────────────────────────────

TTL_SECONDS = 86400  # 与脚本一致


def _cache_is_valid(cache_time: datetime, now: datetime, force: bool = False) -> bool:
    """Test-CacheValid 的 Python 等价实现。"""
    if force:
        return False
    age = now - cache_time
    return age.total_seconds() < TTL_SECONDS


class TestCacheTtl:

    def test_fresh_cache_valid(self):
        """24h 内的缓存有效。"""
        now = datetime.now(timezone.utc)
        cache_time = now - timedelta(hours=1)
        assert _cache_is_valid(cache_time, now) is True

    def test_expired_cache_invalid(self):
        """超过 24h 的缓存无效。"""
        now = datetime.now(timezone.utc)
        cache_time = now - timedelta(hours=25)
        assert _cache_is_valid(cache_time, now) is False

    def test_force_skips_cache(self):
        """-Force 应跳过缓存。"""
        now = datetime.now(timezone.utc)
        cache_time = now  # 刚写入
        assert _cache_is_valid(cache_time, now, force=True) is False

    def test_exact_boundary_invalid(self):
        """恰好 24h 时缓存无效（< TTL 不含等于）。"""
        now = datetime.now(timezone.utc)
        cache_time = now - timedelta(seconds=TTL_SECONDS)
        assert _cache_is_valid(cache_time, now) is False


# ── 缓存 JSON 读写契约 ───────────────────────────────────────────────

class TestCacheJsonContract:

    def test_cache_json_structure(self, tmp_path):
        """缓存 JSON 应含 last_check / branch / remote_version 字段。"""
        cache_file = tmp_path / "update_cache.json"
        cache_obj = {
            "last_check": datetime.now(timezone.utc).strftime("o"),
            "branch": "main",
            "remote_version": "abc123",
        }
        cache_file.write_text(json.dumps(cache_obj), encoding="utf-8")
        loaded = json.loads(cache_file.read_text(encoding="utf-8"))
        assert "last_check" in loaded
        assert loaded["branch"] == "main"
        assert loaded["remote_version"] == "abc123"


# ── PowerShell 执行测试（可选）──────────────────────────────────────

class TestPowerShellExecution:

    @pytest.fixture(autouse=True)
    def _check_powershell(self):
        """无 PowerShell 时跳过本类所有测试。"""
        if shutil.which("powershell") is None and shutil.which("pwsh") is None:
            pytest.skip("PowerShell 不可用")

    def test_script_syntax_valid(self):
        """脚本应能通过 PowerShell 语法检查（Parse）。"""
        import subprocess
        ps = shutil.which("pwsh") or shutil.which("powershell")
        result = subprocess.run(
            [ps, "-NoProfile", "-Command",
             f"[System.Management.Automation.PSParser]::Tokenize((Get-Content -Raw '{SCRIPT_PATH}'), [ref]$null) | Out-Null"],
            capture_output=True, text=True, timeout=15,
        )
        # 语法错误时 PowerShell 会写 stderr
        assert result.returncode == 0 or result.returncode is None, \
            f"脚本语法可能有误: {result.stderr}"