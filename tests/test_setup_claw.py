"""Tests for setup_claw.py"""

import os
import sys
import tempfile
import textwrap
from unittest import mock

import pytest

# Add parent directory to path so we can import setup_claw
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import setup_claw


# ─── parse_version ───

class TestParseVersion:
    def test_standard_version(self):
        assert setup_claw.parse_version("v22.1.0") == (22, 1, 0)

    def test_plain_version(self):
        assert setup_claw.parse_version("22.1.0") == (22, 1, 0)

    def test_embedded_version(self):
        assert setup_claw.parse_version("node v22.3.1 linux") == (22, 3, 1)

    def test_no_match(self):
        assert setup_claw.parse_version("no version here") == (0, 0, 0)

    def test_single_digit(self):
        assert setup_claw.parse_version("1.2.3") == (1, 2, 3)

    def test_large_numbers(self):
        assert setup_claw.parse_version("100.200.300") == (100, 200, 300)


# ─── Color helpers ───

class TestColorHelpers:
    def test_green_with_color(self):
        with mock.patch.object(setup_claw, '_USE_COLOR', True):
            result = setup_claw.green("ok")
            assert "\033[32m" in result
            assert "ok" in result

    def test_green_without_color(self):
        with mock.patch.object(setup_claw, '_USE_COLOR', False):
            assert setup_claw.green("ok") == "ok"

    def test_red_without_color(self):
        with mock.patch.object(setup_claw, '_USE_COLOR', False):
            assert setup_claw.red("fail") == "fail"

    def test_yellow_without_color(self):
        with mock.patch.object(setup_claw, '_USE_COLOR', False):
            assert setup_claw.yellow("warn") == "warn"

    def test_cyan_without_color(self):
        with mock.patch.object(setup_claw, '_USE_COLOR', False):
            assert setup_claw.cyan("info") == "info"

    def test_bold_without_color(self):
        with mock.patch.object(setup_claw, '_USE_COLOR', False):
            assert setup_claw.bold("title") == "title"


# ─── check_git ───

class TestCheckGit:
    def test_git_found(self):
        with mock.patch.object(setup_claw, 'which', return_value='/usr/bin/git'):
            with mock.patch.object(setup_claw, 'run_cmd') as mock_run:
                mock_run.return_value = mock.Mock(returncode=0, stdout="git version 2.43.0\n")
                assert setup_claw.check_git() is True

    def test_git_not_found(self):
        with mock.patch.object(setup_claw, 'which', return_value=None):
            assert setup_claw.check_git() is False

    def test_git_error(self):
        with mock.patch.object(setup_claw, 'which', return_value='/usr/bin/git'):
            with mock.patch.object(setup_claw, 'run_cmd') as mock_run:
                mock_run.return_value = mock.Mock(returncode=1)
                assert setup_claw.check_git() is False


# ─── check_node ───

class TestCheckNode:
    def test_node_found_meets_version(self):
        with mock.patch.object(setup_claw, 'which', return_value='/usr/bin/node'):
            with mock.patch.object(setup_claw, 'run_cmd') as mock_run:
                mock_run.return_value = mock.Mock(returncode=0, stdout="v22.5.0\n")
                ok, ver = setup_claw.check_node()
                assert ok is True
                assert ver == "22.5.0"

    def test_node_found_too_old(self):
        with mock.patch.object(setup_claw, 'which', return_value='/usr/bin/node'):
            with mock.patch.object(setup_claw, 'run_cmd') as mock_run:
                mock_run.return_value = mock.Mock(returncode=0, stdout="v18.17.0\n")
                ok, ver = setup_claw.check_node()
                assert ok is False
                assert ver == "18.17.0"

    def test_node_not_found(self):
        with mock.patch.object(setup_claw, 'which', return_value=None):
            ok, ver = setup_claw.check_node()
            assert ok is False
            assert ver == "not found"

    def test_node_exact_minimum(self):
        with mock.patch.object(setup_claw, 'which', return_value='/usr/bin/node'):
            with mock.patch.object(setup_claw, 'run_cmd') as mock_run:
                mock_run.return_value = mock.Mock(returncode=0, stdout="v22.0.0\n")
                ok, ver = setup_claw.check_node()
                assert ok is True

    def test_node_error(self):
        with mock.patch.object(setup_claw, 'which', return_value='/usr/bin/node'):
            with mock.patch.object(setup_claw, 'run_cmd') as mock_run:
                mock_run.return_value = mock.Mock(returncode=1, stdout="")
                ok, ver = setup_claw.check_node()
                assert ok is False
                assert ver == "error running node"


# ─── check_curl ───

class TestCheckCurl:
    def test_curl_found(self):
        with mock.patch.object(setup_claw, 'which', return_value='/usr/bin/curl'):
            assert setup_claw.check_curl() is True

    def test_curl_not_found(self):
        with mock.patch.object(setup_claw, 'which', return_value=None):
            assert setup_claw.check_curl() is False


# ─── system_info ───

class TestSystemInfo:
    def test_returns_dict_with_expected_keys(self):
        info = setup_claw.system_info()
        expected_keys = {"os", "os_version", "arch", "python", "user", "home", "shell"}
        assert expected_keys == set(info.keys())

    def test_os_is_string(self):
        info = setup_claw.system_info()
        assert isinstance(info["os"], str)
        assert len(info["os"]) > 0


# ─── detect_shell_profile ───

class TestDetectShellProfile:
    def test_zsh_preferred_when_shell_is_zsh(self):
        with mock.patch.dict(os.environ, {"SHELL": "/bin/zsh"}):
            zshrc = setup_claw.SHELL_PROFILES['zsh']
            with mock.patch('os.path.exists', side_effect=lambda p: p == zshrc):
                result = setup_claw.detect_shell_profile()
                assert result == zshrc

    def test_bashrc_when_shell_is_bash(self):
        with mock.patch.dict(os.environ, {"SHELL": "/bin/bash"}):
            bashrc = setup_claw.SHELL_PROFILES['bash']
            with mock.patch('os.path.exists', side_effect=lambda p: p == bashrc):
                result = setup_claw.detect_shell_profile()
                assert result == bashrc

    def test_none_when_no_profile_exists(self):
        with mock.patch.dict(os.environ, {"SHELL": "/bin/fish"}):
            with mock.patch('os.path.exists', return_value=False):
                result = setup_claw.detect_shell_profile()
                assert result is None


# ─── _read_existing_keys ───

class TestReadExistingKeys:
    def test_reads_both_keys(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.bashrc', delete=False) as f:
            f.write('export ANTHROPIC_API_KEY="sk-ant-test123"\n')
            f.write('export OPENAI_API_KEY="sk-openai-test456"\n')
            f.flush()
            keys = setup_claw._read_existing_keys(f.name)
        os.unlink(f.name)
        assert keys["ANTHROPIC_API_KEY"] == "sk-ant-test123"
        assert keys["OPENAI_API_KEY"] == "sk-openai-test456"

    def test_no_keys(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.bashrc', delete=False) as f:
            f.write('# just a comment\nexport PATH="/usr/bin"\n')
            f.flush()
            keys = setup_claw._read_existing_keys(f.name)
        os.unlink(f.name)
        assert keys == {}

    def test_missing_file(self):
        keys = setup_claw._read_existing_keys("/nonexistent/path/.bashrc")
        assert keys == {}


# ─── _write_key ───

class TestWriteKey:
    def test_write_new_key(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.bashrc', delete=False) as f:
            f.write("# existing content\n")
            f.flush()
            setup_claw._write_key(f.name, "ANTHROPIC_API_KEY", "sk-ant-new")
            with open(f.name) as rf:
                content = rf.read()
        os.unlink(f.name)
        assert 'export ANTHROPIC_API_KEY="sk-ant-new"' in content
        assert "# existing content" in content

    def test_overwrite_existing_key(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.bashrc', delete=False) as f:
            f.write('export OPENAI_API_KEY="old-key"\n')
            f.flush()
            setup_claw._write_key(f.name, "OPENAI_API_KEY", "new-key")
            with open(f.name) as rf:
                content = rf.read()
        os.unlink(f.name)
        assert 'export OPENAI_API_KEY="new-key"' in content
        assert "old-key" not in content

    def test_write_to_new_file(self):
        path = tempfile.mktemp(suffix='.bashrc')
        try:
            setup_claw._write_key(path, "ANTHROPIC_API_KEY", "sk-test")
            with open(path) as f:
                content = f.read()
            assert 'export ANTHROPIC_API_KEY="sk-test"' in content
        finally:
            if os.path.exists(path):
                os.unlink(path)

    def test_preserves_other_content(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.bashrc', delete=False) as f:
            f.write('export PATH="/usr/local/bin:$PATH"\n')
            f.write('alias ll="ls -la"\n')
            f.flush()
            setup_claw._write_key(f.name, "OPENAI_API_KEY", "sk-test")
            with open(f.name) as rf:
                content = rf.read()
        os.unlink(f.name)
        assert 'export PATH="/usr/local/bin:$PATH"' in content
        assert 'alias ll="ls -la"' in content
        assert 'export OPENAI_API_KEY="sk-test"' in content


# ─── run_prerequisite_checks ───

class TestRunPrerequisiteChecks:
    def test_all_pass(self):
        with mock.patch.object(setup_claw, 'check_git', return_value=True), \
             mock.patch.object(setup_claw, 'check_node', return_value=(True, "22.5.0")), \
             mock.patch.object(setup_claw, 'check_curl', return_value=True), \
             mock.patch.object(setup_claw, '_USE_COLOR', False):
            result = setup_claw.run_prerequisite_checks()
            assert result is True

    def test_node_fails(self):
        with mock.patch.object(setup_claw, 'check_git', return_value=True), \
             mock.patch.object(setup_claw, 'check_node', return_value=(False, "18.0.0")), \
             mock.patch.object(setup_claw, 'check_curl', return_value=True), \
             mock.patch.object(setup_claw, '_USE_COLOR', False):
            result = setup_claw.run_prerequisite_checks()
            assert result is False

    def test_git_fails(self):
        with mock.patch.object(setup_claw, 'check_git', return_value=False), \
             mock.patch.object(setup_claw, 'check_node', return_value=(True, "22.0.0")), \
             mock.patch.object(setup_claw, 'check_curl', return_value=True), \
             mock.patch.object(setup_claw, '_USE_COLOR', False):
            result = setup_claw.run_prerequisite_checks()
            assert result is False

    def test_all_fail(self):
        with mock.patch.object(setup_claw, 'check_git', return_value=False), \
             mock.patch.object(setup_claw, 'check_node', return_value=(False, "not found")), \
             mock.patch.object(setup_claw, 'check_curl', return_value=False), \
             mock.patch.object(setup_claw, '_USE_COLOR', False):
            result = setup_claw.run_prerequisite_checks()
            assert result is False


# ─── Integration: script imports cleanly ───

class TestModuleIntegrity:
    def test_constants_defined(self):
        assert setup_claw.MIN_NODE_VERSION == (22, 0, 0)
        assert 'openclaw.ai' in setup_claw.INSTALL_CMD
        assert 'docs.openclaw.ai' in setup_claw.DOCS_URL

    def test_shell_profiles_defined(self):
        assert 'bash' in setup_claw.SHELL_PROFILES
        assert 'zsh' in setup_claw.SHELL_PROFILES
