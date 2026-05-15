from pathlib import Path


def test_readme_has_issues_feedback_without_group_or_sponsor_links():
    text = Path("README.md").read_text(encoding="utf-8")

    assert "GitHub Issues" in text
    assert "https://github.com/BigPizzaV3/CodexPlusPlus/issues" in text
    for forbidden in ("交流群", "discussion-group-qr", "赞赏", "请我喝杯咖啡", "RawChat", "sponsor-alipay", "sponsor-wechat"):
        assert forbidden not in text


def test_readme_includes_codex_plus_icon_and_toc():
    text = Path("README.md").read_text(encoding="utf-8")

    assert '<img src="docs/images/codex-plus-plus.png"' in text
    assert 'width="160"' in text
    assert "![Codex++ 设置面板](docs/images/settings-panel.png)" in text
    assert Path("docs/images/settings-panel.png").exists()
    assert "## 目录" in text
    assert "- [Windows 使用](#windows-使用)" in text
    assert "- [Fork 维护策略](#fork-维护策略)" in text
    assert "- [常见问题](#常见问题)" in text


def test_readme_has_badges_language_switch_and_project_charts():
    text = Path("README.md").read_text(encoding="utf-8")

    assert '<a href="README_EN.md">English</a>' in text
    assert "[English](README_EN.md)" not in text
    assert "img.shields.io/github/v/release/BigPizzaV3/CodexPlusPlus" in text
    assert "img.shields.io/github/stars/BigPizzaV3/CodexPlusPlus" in text
    assert "contrib.rocks/image?repo=BigPizzaV3/CodexPlusPlus" in text
    assert "api.star-history.com/svg?repos=BigPizzaV3/CodexPlusPlus" in text


def test_readme_documents_provider_sync_as_no_session_loss():
    text = Path("README.md").read_text(encoding="utf-8")

    assert "Provider 同步" in text
    assert "切换 model_provider" in text
    assert "不丢历史会话" in text


def test_readme_documents_personal_fork_sync_policy():
    text = Path("README.md").read_text(encoding="utf-8")

    assert "本仓库是个人 Fork 的同步维护版本" in text
    assert "监控 `origin` 的开放 PR 和 `origin/main`" in text
    assert "不自动合入开放 PR" in text
    assert "rebase 到 `origin/main`" in text
    assert "只推送到 `fork/main`，不推送到 `origin`" in text


def test_english_readme_exists_and_matches_core_sections():
    text = Path("README_EN.md").read_text(encoding="utf-8")

    assert "# Codex++" in text
    assert '<a href="README.md">中文</a>' in text
    assert "[中文](README.md)" not in text
    assert "Provider Sync" in text
    assert "switch model_provider without losing historical conversations" in text
    assert "personally maintained fork" in text
    assert "Open upstream PRs are monitored" in text
    assert "pushed only to `fork/main`, never to `origin`" in text
    assert "img.shields.io/github/v/release/BigPizzaV3/CodexPlusPlus" in text
    assert "contrib.rocks/image?repo=BigPizzaV3/CodexPlusPlus" in text
    assert "api.star-history.com/svg?repos=BigPizzaV3/CodexPlusPlus" in text
    for forbidden in ("discussion group", "buy me a coffee", "RawChat", "sponsor-alipay", "sponsor-wechat"):
        assert forbidden not in text


def test_readme_links_lINUX_do_without_image():
    text = Path("README.md").read_text(encoding="utf-8")

    assert "## 友情链接" in text
    assert "[LINUX DO](https://linux.do)" in text
    assert "docs/images/linux-do.png" not in text
