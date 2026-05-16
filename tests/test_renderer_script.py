import subprocess
from pathlib import Path


def test_renderer_script_exists_and_parses_with_node():
    script = Path("codex_session_delete/inject/renderer-inject.js")
    assert script.exists()
    result = subprocess.run(["node", "--check", str(script)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_renderer_script_contains_hover_delete_contract():
    text = Path("codex_session_delete/inject/renderer-inject.js").read_text(encoding="utf-8")
    assert "codex-delete-button" in text
    assert "codex-session-actions" in text
    assert "MutationObserver" in text
    assert "confirmDelete" in text
    assert "/delete" in text
    assert "/undo" in text


def test_renderer_script_supports_codex_sidebar_thread_attributes():
    text = Path("codex_session_delete/inject/renderer-inject.js").read_text(encoding="utf-8")
    start = text.index("function sessionRows")
    end = text.index("\n\n  function archivePageHintVisible", start)
    session_rows_code = text[start:end]
    assert "const selectors" in text
    assert "sidebarThread" in text
    assert "data-app-action-sidebar-thread-id" in text
    assert "threadTitle" in text
    assert "data-thread-title" in text
    assert "selectors.sidebarThread" in session_rows_code
    assert "a[href*='session']" not in session_rows_code
    assert "conversation" not in session_rows_code
    assert "thread" not in session_rows_code.replace("sidebarThread", "")
    assert "hasSessionHint" not in session_rows_code


def test_renderer_script_positions_delete_button_without_affecting_layout():
    text = Path("codex_session_delete/inject/renderer-inject.js").read_text(encoding="utf-8")
    start = text.index(".${actionGroupClass} {")
    end = text.index("\n      .${actionButtonClass}", start)
    action_group_style = text[start:end]
    assert "position: static" in action_group_style
    assert "flex: 0 0 auto" in action_group_style
    assert "gap: 6px" in action_group_style
    assert "margin-right: 6px" in action_group_style
    assert "display: inline-flex" in text
    assert "[data-codex-delete-row=\"true\"]:focus-within .${actionGroupClass}" in text
    assert "right: var(--codex-session-action-right, 48px)" not in text




def test_renderer_script_has_no_ad_or_sponsor_runtime_ui():
    text = Path("codex_session_delete/inject/renderer-inject.js").read_text(encoding="utf-8")

    forbidden = [
        'data-codex-plus-tab="sponsor"',
        'data-codex-plus-tab="support"',
        'data-codex-plus-panel="sponsor"',
        'data-codex-plus-panel="support"',
        "推荐内容",
        "赞助商推荐",
        "普通推荐",
        "请作者喝咖啡",
        "请我喝杯咖啡",
        "codex-plus-sponsor",
        "codex-plus-ad-",
        "fetchCodexPlusAds",
        "renderCodexPlusAds",
        'postJson("/ads", {})',
        "window.__CODEX_PLUS_SPONSOR_IMAGES__",
        "sponsor-alipay.jpg",
        "sponsor-wechat.jpg",
        "rawchat-sponsor.jpg",
        "rawchat.cn",
        "0029.org",
    ]
    for needle in forbidden:
        assert needle not in text


def test_renderer_script_has_retry_attempt_controls_setting_and_config_writes():
    text = Path("codex_session_delete/inject/renderer-inject.js").read_text(encoding="utf-8")

    assert "retryAttemptControls: false" in text
    assert "重试次数控制" in text
    assert "data-codex-plus-setting=\"retryAttemptControls\"" in text
    assert "retryAttemptLimitValue = 100" in text
    assert "retryFixedDelayMs = 1000" in text
    assert "bestOfNAtomKey = \"composer-best-of-n\"" in text
    assert "persistedAtomPrefix = \"codex:persisted-atom:\"" in text
    assert "applyRetryAttemptControls()" in text
    assert "installRetryFixedDelayPatch()" in text
    assert "retryDelayLooksExponential(delay)" in text
    assert "[2000, 4000, 8000, 16000, 30000].includes(ms)" in text
    assert "retryTimerStackLooksRelevant()" in text
    assert "app-server-manager-signals-C1h8B-R-.js" in text
    assert "setPersistedCodexAtom(bestOfNAtomKey, attempts, signals)" in text
    assert "if (!configPayload) return { status: \"failed\", message: \"Codex config read failed\" }" in text
    assert "model_providers.${providerId}.request_max_retries" in text
    assert "model_providers.${providerId}.stream_max_retries" in text
    assert "batch-write-config-value" in text
    assert "reloadUserConfig: true" in text
    assert "window.__codexPlusRetryAttemptControls" in text


def test_renderer_script_contains_conversation_timeline_contract():
    text = Path("codex_session_delete/inject/renderer-inject.js").read_text(encoding="utf-8")

    assert "codex-conversation-timeline" in text
    assert "codex-conversation-timeline-marker" in text
    assert "codex-conversation-timeline-tooltip" in text
    assert "codex-conversation-timeline-target" in text
    assert "codexConversationTimelineVersion" in text
    assert "refreshConversationTimeline" in text
    assert "truncateTimelineQuestion" in text
    assert "timelineQuestionLimit = 40" in text
    assert "timelineMinTopPercent" in text
    assert "timelineMaxTopPercent" in text



def test_renderer_script_detects_user_questions_for_timeline_without_sidebar_scan():
    text = Path("codex_session_delete/inject/renderer-inject.js").read_text(encoding="utf-8")
    start = text.index("function conversationTimelineQuestions")
    end = text.index("\n\n  function refreshConversationTimeline", start)
    timeline_detection_code = text[start:end]

    assert "conversationTimelineRoot" in timeline_detection_code
    assert "conversationTimelineQuestionCandidates" in timeline_detection_code
    assert "data-message-author-role=\"user\"" in text
    assert "data-testid=\"conversation-turn\"" in text
    assert "thread-scroll-container" in text
    assert "bg-token-foreground/5" in text
    assert "items-end" in text
    assert "visibleTimelineNode" in timeline_detection_code
    assert "timelineNodeId" in timeline_detection_code
    assert "main" in timeline_detection_code
    assert "selectors.sidebarThread" not in timeline_detection_code
    assert "document.body.textContent" not in timeline_detection_code
    assert "extractTimelineQuestionText" in timeline_detection_code



def test_renderer_script_refreshes_conversation_timeline_from_scan_loop():
    text = Path("codex_session_delete/inject/renderer-inject.js").read_text(encoding="utf-8")
    deferred_start = text.index("function scanDeferred")
    deferred_end = text.index("\n\n  function runScanStep", deferred_start)
    scan_deferred_code = text[deferred_start:deferred_end]
    extension_start = text.index("function isExtensionUiNode")
    extension_end = text.index("\n\n  const scanRelevantSelector", extension_start)
    extension_code = text[extension_start:extension_end]
    relevant_start = text.index("const scanRelevantSelector")
    relevant_end = text.index("\n\n  function isScanRelevantNode", relevant_start)
    relevant_code = text[relevant_start:relevant_end]
    chat_start = text.index("function isChatContentMutation")
    chat_end = text.index("\n\n  function shouldScheduleScan", chat_start)
    chat_code = text[chat_start:chat_end]

    assert "refreshConversationTimeline()" in scan_deferred_code
    assert ".codex-conversation-timeline" in extension_code
    assert "[data-message-author-role]" in relevant_code
    assert "[data-testid=\"conversation-turn\"]" in relevant_code
    assert "[class*=\"user-message\"]" in relevant_code
    assert "nodeLooksLikeTimelineQuestion(node)" in text
    assert "main .prose" in chat_code
    assert "return false" in chat_code



def test_renderer_script_timeline_uses_stable_hover_and_scroll_behavior():
    text = Path("codex_session_delete/inject/renderer-inject.js").read_text(encoding="utf-8")
    assert "top: calc(72px + 12px)" in text
    assert "bottom: calc(28px + 12px)" in text
    assert "width: max-content" in text
    assert "max-width: min(320px, calc(100vw - 72px))" in text
    assert "overflow: hidden" in text
    assert "text-overflow: ellipsis" in text
    assert "z-index: 2147482501" in text
    assert "pointer-events: none" in text
    assert "scrollTimelineTarget" in text
    assert "nearestTimelineScroller" in text
    assert "timelineScrollerViewportTop(scroller)" in text
    assert "scrollTo({" in text
    assert "behavior: \"smooth\"" in text
    assert "aria-describedby" in text
    assert "role\", \"tooltip\"" in text
    assert "keydown" in text[text.index("function createConversationTimelineMarker"):text.index("\n\n  function prepareTimelineQuestions")]
    assert "click" not in text[text.index("function createConversationTimelineMarker"):text.index("\n\n  function refreshConversationTimeline")]
    assert "pointerup" in text[text.index("function createConversationTimelineMarker"):text.index("\n\n  function refreshConversationTimeline")]



def test_renderer_script_timeline_positions_questions_by_scroll_location():
    text = Path("codex_session_delete/inject/renderer-inject.js").read_text(encoding="utf-8")
    start = text.index("function timelineScrollerViewportTop")
    end = text.index("\n\n  function removeConversationTimeline", start)
    marker_top_code = text[start:end]

    assert "timelineRawMarkerTop" in marker_top_code
    assert "timelineMarkerTops" in marker_top_code
    assert "getBoundingClientRect" in marker_top_code
    assert "timelineScrollableHeight(scroller)" in marker_top_code
    assert "timelineMaxMarkerGapPercent" in marker_top_code
    assert "questions.indexOf(question)" not in marker_top_code



def test_renderer_script_timeline_has_codex_plus_menu_toggle():
    text = Path("codex_session_delete/inject/renderer-inject.js").read_text(encoding="utf-8")

    assert "conversationTimeline: true" in text
    assert "对话 Timeline" in text
    assert "data-codex-plus-setting=\"conversationTimeline\"" in text
    assert "codexPlusSettings().conversationTimeline" in text
    assert "removeConversationTimeline()" in text[text.index("function refreshConversationTimeline"):text.index("\n\n  function scanLightweight")]



def test_renderer_script_enables_plugin_entry_for_api_key_users():
    text = Path("codex_session_delete/inject/renderer-inject.js").read_text(encoding="utf-8")
    start = text.index("function pluginEntryButton")
    end = text.index("\n\n  function unblockPluginInstallButtons", start)
    plugin_entry_code = text[start:end]
    assert "enablePluginEntry" in plugin_entry_code
    assert "pluginEntryButton" in plugin_entry_code
    assert "nav[role=\"navigation\"] button.h-token-nav-row.w-full" in text
    assert "svg path[d^=\"M7.94562 14.0277\"]" in text
    assert "selectors.pluginNavButton" in plugin_entry_code
    assert "selectors.pluginSvgPath" in plugin_entry_code
    assert "document.querySelectorAll(\"button\")" not in plugin_entry_code
    assert "disabled = false" in plugin_entry_code
    assert "removeAttribute(\"disabled\")" in plugin_entry_code
    assert "setAuthMethod(\"chatgpt\")" in text
    assert "插件 - 已解锁" in plugin_entry_code
    assert "Plugins - Unlocked" in plugin_entry_code
    assert "labelUnlockedPluginEntry" in plugin_entry_code
    assert "childNodes" in plugin_entry_code
    assert "node.nodeType === 3" in plugin_entry_code
    assert "labelTextNode.nodeValue" in plugin_entry_code
    assert ".textContent = /^Plugins" not in plugin_entry_code
    assert "__reactFiber" in text
    assert "/skills/plugins" not in text
    assert "skillProps.onClick" not in text
    assert "unblockButtonElement(pluginButton)" in plugin_entry_code
    assert "function reactPropsFor(element)" in text
    assert "event.stopImmediatePropagation?.()" in text[text.index("function installPluginReactOnClickFallback"):text.index("\n\n  function labelForcedInstallButton")]
    assert "props.onClick(new MouseEvent(\"click\", { bubbles: true, cancelable: true, view: window }))" in text


def test_renderer_script_unblocks_connector_unavailable_plugin_install_buttons_without_full_body_text_scan():
    text = Path("codex_session_delete/inject/renderer-inject.js").read_text(encoding="utf-8")
    start = text.index("function pluginInstallCandidates")
    end = text.index("\n  let cachedSessionRows", start)
    plugin_unlock_code = text[start:end]
    assert "unblockPluginInstallButtons" in plugin_unlock_code
    assert "pluginInstallCandidates" in plugin_unlock_code
    assert "button:disabled.w-full.justify-center" in text
    assert "[role=\"button\"][aria-disabled=\"true\"].cursor-not-allowed" in text
    assert "selectors.disabledInstallButton" in plugin_unlock_code
    assert "document.body.textContent" not in plugin_unlock_code
    assert "button.disabled = false" in plugin_unlock_code
    assert "removeAttribute(\"aria-disabled\")" in plugin_unlock_code
    assert "labelForcedInstallButton" in plugin_unlock_code
    assert "强制安装" in plugin_unlock_code
    assert "installPluginReactOnClickFallback(button)" in plugin_unlock_code


def test_renderer_script_debounces_mutation_observer_scan():
    text = Path("codex_session_delete/inject/renderer-inject.js").read_text(encoding="utf-8")
    assert "scanLightweight" in text
    assert "scanDeferred" in text
    assert "runScanStep" in text
    assert "codexSessionDeleteScanFailures" in text
    assert "runScanStep(scanLightweight)" in text
    assert "requestAnimationFrame(() => runScanStep(scanDeferred))" in text
    assert "if (window.__codexSessionDeleteScanPending) return" in text
    assert "setTimeout(runScheduledScan, 200)" in text
    assert "setTimeout(() => runScanStep(scanDeferred), 50)" not in text
    assert "codexSessionDeleteAttachButtonFailures" in text
    assert "tryAttachButton" in text
    assert "tryAttachButton(row)" in text
    assert "sessionRows().forEach(attachButton)" not in text
    assert "new MutationObserver(scheduleScan)" in text
    assert "new MutationObserver(scan)" not in text
    assert "scan();" in text
    assert "window.__codexProjectMoveApplyProjection" in text
    assert "window.__codexSessionDeleteObserver" in text


def test_renderer_script_ignores_chat_content_mutations_before_scheduling_scan():
    text = Path("codex_session_delete/inject/renderer-inject.js").read_text(encoding="utf-8")
    start = text.index("function isExtensionUiNode")
    end = text.index("\n\n  function runScheduledScan", start)
    should_schedule_code = text[start:end]
    assert "isChatContentMutation" in should_schedule_code
    assert "data-message-author-role" in should_schedule_code
    assert "data-testid=\"conversation-turn\"" in should_schedule_code
    assert "main .prose" in should_schedule_code
    assert "if (isChatContentMutation(mutation)) return false" in should_schedule_code
    should_start = text.index("function shouldScheduleScan")
    should_end = text.index("\n\n  function runScheduledScan", should_start)
    should_schedule_only = text[should_start:should_end]
    assert "nodeSelfOrAncestorMatchesScanRelevance(target)" in should_schedule_only
    assert "const changedNodes = [...Array.from(mutation.addedNodes), ...Array.from(mutation.removedNodes)]" in should_schedule_only
    assert "changedNodes.some((node) => node.nodeType === 1 && isScanRelevantNode(node))" in should_schedule_only
    assert "Array.from(mutation.addedNodes).some((node) => node.nodeType === 1 && isScanRelevantNode(node))" in should_schedule_code
    assert "selectors.sidebarThread" in should_schedule_code
    assert "selectors.appHeader" in should_schedule_code


def test_renderer_script_chat_filter_keeps_relevant_node_escape_hatch():
    text = Path("codex_session_delete/inject/renderer-inject.js").read_text(encoding="utf-8")
    start = text.index("const scanRelevantSelector")
    end = text.index("\n\n  function isChatContentMutation", start)
    relevant_code = text[start:end]
    assert "node.matches?.(scanRelevantSelector)" in relevant_code
    assert "node.querySelector?.(scanRelevantSelector)" in relevant_code
    assert "nodeLooksLikeTimelineQuestion(node)" in relevant_code
    assert "selectors.archiveNav" in relevant_code
    assert "selectors.disabledInstallButton" in relevant_code
    assert "button[aria-label=\"已归档对话\"]" in text
    assert "button:disabled.w-full.justify-center" in text


def test_renderer_script_supports_bulk_export_and_bulk_move_contracts():
    text = Path("codex_session_delete/inject/renderer-inject.js").read_text(encoding="utf-8")

    assert "bulkExport: true" in text
    assert "批量导出 ZIP" in text
    assert "codex-bulk-export-checkbox" in text
    assert "codex-bulk-export-bar" in text
    assert "/export-markdown-zip" in text
    assert "downloadZip(result.filename, result.zip_base64)" in text
    assert "批量移动" in text
    assert "codex-bulk-move-checkbox" in text
    assert "codex-bulk-move-progress" in text
    assert "/move-thread-projectless" in text
    assert "window.__codexBulkMoveFailures" in text


def test_renderer_script_reuses_project_move_dialog_for_single_and_bulk_move():
    text = Path("codex_session_delete/inject/renderer-inject.js").read_text(encoding="utf-8")
    shared_start = text.index("function centerProjectMoveDialogPanel")
    shared_end = text.index("\n\n  function openBulkProjectMoveMenu", shared_start)
    shared_code = text[shared_start:shared_end]
    bulk_start = text.index("function openBulkProjectMoveMenu")
    bulk_end = text.index("\n\n  function finishProjectMove", bulk_start)
    bulk_code = text[bulk_start:bulk_end]
    single_start = text.index("async function openProjectMoveMenuForRow")
    single_end = text.index("\n\n  function installDeleteButtonEventDelegation", single_start)
    single_code = text[single_start:single_end]

    assert "function openProjectMoveDialog({ title, ariaLabel, onSelectTarget })" in shared_code
    assert "function renderProjectMoveDialogTargets(overlay, close, onSelectTarget)" in shared_code
    assert "centerProjectMoveDialogPanel(panel)" in shared_code
    assert "position:" not in shared_code
    assert "anchor:" not in shared_code
    assert "getBoundingClientRect()" not in shared_code
    assert 'kind === "anchor"' not in shared_code
    assert "加载项目中..." in shared_code
    assert "没有可用目标" in shared_code
    assert "showToast(`加载项目失败：" in shared_code
    assert "await onSelectTarget(target)" in shared_code
    assert "clickEvent.target === overlay" in shared_code
    assert 'keyEvent.key === "Escape"' in shared_code

    assert "openProjectMoveDialog({" in bulk_code
    assert "position:" not in bulk_code
    assert "onSelectTarget: moveSelectedSessionsToTarget" in bulk_code
    assert "projectMoveTargets()" not in bulk_code
    assert "codex-project-move-item" not in bulk_code

    assert "openProjectMoveDialog({" in single_code
    assert "position:" not in single_code
    assert "anchor: button" not in single_code
    assert "onSelectTarget: (target) => applyProjectMove(row, button, ref, target)" in single_code
    assert "projectMoveTargets()" not in single_code
    assert "codex-project-move-item" not in single_code


def test_renderer_script_backend_repair_uses_bridge_timeout_and_http_fallback():
    text = Path("codex_session_delete/inject/renderer-inject.js").read_text(encoding="utf-8")

    assert "window.__codexSessionDeleteBridge(path, payload, bridgeTimeoutMs)" in text
    assert "path !== \"/backend/status\" && path !== \"/backend/repair\"" in text
    assert "postHelperJson(path, payload, 5000)" in text
    assert "helperFetch(path, options, timeoutMs)" in text
    assert "后端已断开" in text


def test_renderer_script_archive_scan_relevance_has_text_fallback():
    text = Path("codex_session_delete/inject/renderer-inject.js").read_text(encoding="utf-8")

    assert "function nodeLooksLikeArchivePageContent(node)" in text
    assert "text.includes(\"取消归档\")" in text
    assert "archiveTitleTexts.has(text)" in text
    assert "nodeLooksLikeArchivePageContent(node)" in text[text.index("function isScanRelevantNode"):text.index("\n\n  function isChatContentMutation")]
    assert "[role=\"button\"][aria-disabled=\"true\"].cursor-not-allowed" in text


def test_renderer_script_clears_focus_and_removes_deleted_rows():
    text = Path("codex_session_delete/inject/renderer-inject.js").read_text(encoding="utf-8")
    assert "removeDeletedRow(row, button, ref)" in text
    assert "function releaseDeleteFocus" in text
    assert "releaseDeleteFocus(row, button)" in text
    assert "button.blur()" in text
    assert "document.activeElement.blur()" in text
    assert "row.remove()" in text
    assert "row.style.display = \"none\"" not in text


def test_renderer_script_tracks_locally_deleted_rows_and_restores_after_undo():
    text = Path("codex_session_delete/inject/renderer-inject.js").read_text(encoding="utf-8")

    assert "const locallyDeletedSessionIds = window.__codexPlusLocallyDeletedSessionIds || new Set()" in text
    assert "function rememberDeletedSession(ref)" in text
    assert "function forgetDeletedSession(sessionId)" in text
    assert "function pruneLocallyDeletedSessionRows()" in text
    assert "data-codex-locally-deleted" in text
    assert "hideDeletedRow(row)" in text
    assert "showRestoredRow(row)" in text
    assert "locallyDeletedSessionIds.add(`local:${normalized}`)" in text
    assert "locallyDeletedSessionIds.delete(`local:${normalized}`)" in text
    assert "if (result.status === \"undone\" || result.session_id) forgetDeletedSession(result.session_id)" in text
    assert "rememberDeletedSession(ref);\n        removeDeletedRow(row, button, ref)" in text
    assert "rememberDeletedSession(ref);\n        hideDeletedRow(row)" in text
    assert "pruneLocallyDeletedSessionRows();" in text


def test_renderer_script_uses_in_page_confirm_and_stops_early_pointer_events():
    text = Path("codex_session_delete/inject/renderer-inject.js").read_text(encoding="utf-8")
    assert "confirm(" not in text
    assert "codex-delete-confirm-popover" in text
    assert "function confirmDelete(title, anchor)" in text
    assert "window.__codexSessionDeleteConfirmCleanup?.()" in text
    assert "anchor?.getBoundingClientRect?.()" in text
    assert "popover.dataset.placement = placement" in text
    assert "popover.style.left = `${left}px`" in text
    assert "popover.style.visibility = \"visible\"" in text
    assert "confirmDelete(ref.title, button)" in text
    assert "confirmDelete(ref.title, deleteButton)" in text
    assert "confirmDelete(`全部 ${currentRows.length} 个归档会话`, button)" in text
    assert "codex-delete-confirm-overlay" not in text
    assert "popover.setAttribute(\"aria-label\", `删除会话：${title}`)" in text
    assert "stopImmediatePropagation" in text
    assert "\"pointerdown\", \"mousedown\", \"mouseup\", \"touchstart\"" in text


def test_renderer_script_reloads_after_deleting_current_session():
    text = Path("codex_session_delete/inject/renderer-inject.js").read_text(encoding="utf-8")
    assert "isCurrentSessionRow" in text
    assert "window.location.href.includes(ref.session_id)" in text
    assert "window.location.reload()" in text


def test_renderer_script_toast_does_not_capture_page_interactions():
    text = Path("codex_session_delete/inject/renderer-inject.js").read_text(encoding="utf-8")
    assert "z-index: 2147483000" in text
    assert "pointer-events: none" in text
    assert "pointer-events: auto" in text


def test_renderer_script_sidebar_actions_are_accessible_icon_buttons():
    text = Path("codex_session_delete/inject/renderer-inject.js").read_text(encoding="utf-8")

    assert "sessionActionButtonConfigs" in text
    assert "function configureSessionActionButton(button, kind, busy = false)" in text
    assert "button.dataset.codexActionKind = kind" in text
    assert "button.dataset.codexActionIconVersion = \"1\"" in text
    assert "button.setAttribute(\"aria-label\", label)" in text
    assert "button.title = label" in text
    assert "button.innerHTML = config.icon" in text
    assert "移动会话" in text
    assert "导出 Markdown" in text
    assert "删除会话" in text
    assert "configureSessionActionButton(moveButton, \"move\")" in text
    assert "configureSessionActionButton(exportButton, \"export\")" in text
    assert "configureSessionActionButton(deleteButton, \"delete\")" in text
    assert "function sidebarNativeArchiveButton(row)" in text
    assert "if (!row?.matches?.(selectors.sidebarThread)) return null" in text
    assert "Array.from(row.querySelectorAll(\"button\")).find(isSidebarNativeArchiveButton)" in text
    assert "button.getAttribute?.(\"aria-label\")" in text
    assert "button.getAttribute?.(\"title\")" in text
    assert "button.textContent" in text
    assert "text === \"归档对话\"" in text
    assert "lower === \"archive\"" in text
    assert "lower.includes(\"conversation\") || lower.includes(\"chat\")" in text
    assert "return { root: rowContentRoot(row) || row, archiveButton: null }" in text
    assert "const { root, archiveButton } = sidebarActionMountTarget(row)" in text
    assert "root.dataset.codexSessionActionContainer = \"true\"" in text
    assert "root.insertBefore(group, archiveButton)" in text
    assert "archiveButton.appendChild(group)" not in text
    assert "row.appendChild(group)" not in text
    assert "right: var(--codex-session-action-right, 48px)" not in text
    assert "pointer-events: none;" in text
    assert "pointer-events: auto;" in text
    assert ".${actionButtonClass} svg" in text
    assert "width: 16px !important" in text
    assert "height: 16px !important" in text
    assert "data-codex-action-kind=\"delete\"]:hover" in text
    assert "--codex-plus-action-color" in text


def test_renderer_script_sidebar_actions_mount_before_native_archive_button():
    text = Path("codex_session_delete/inject/renderer-inject.js").read_text(encoding="utf-8")
    mount_start = text.index("function sidebarArchiveLabelText")
    mount_end = text.index("\n\n  function stopActionButtonEvent", mount_start)
    mount_code = text[mount_start:mount_end]
    attach_start = text.index("function attachButton")
    attach_end = text.index("\n\n  function tryAttachButton", attach_start)
    attach_code = text[attach_start:attach_end]

    assert "function sidebarNativeArchiveButton(row)" in mount_code
    assert "if (!row?.matches?.(selectors.sidebarThread)) return null" in mount_code
    assert "row.querySelectorAll(\"button\")" in mount_code
    assert "button.getAttribute?.(\"aria-label\")" in mount_code
    assert "button.getAttribute?.(\"title\")" in mount_code
    assert "button.textContent" in mount_code
    assert "text === \"归档对话\"" in mount_code
    assert "lower === \"archive\"" in mount_code
    assert "/\\barchive\\b/.test(lower)" in mount_code
    assert "lower.includes(\"conversation\") || lower.includes(\"chat\")" in mount_code
    assert "text.includes(\"取消归档\")" in mount_code
    assert "text.includes(\"已归档\")" in mount_code
    assert "lower.includes(\"unarchive\")" in mount_code
    assert "lower.includes(\"archived conversations\")" in mount_code
    assert "button.closest?.(`.${actionGroupClass}`)" in mount_code
    assert "return { root: rowContentRoot(row) || row, archiveButton: null }" in mount_code
    assert "const mountReady = actionGroupMountReady(row, existingGroup)" in attach_code
    assert "if (archiveButton && archiveButton.parentElement === root)" in attach_code
    assert "root.insertBefore(group, archiveButton)" in attach_code
    assert "root.appendChild(group)" in attach_code
    assert "archiveButton.appendChild(group)" not in text
    assert "archiveButton.insertBefore(group" not in text
    assert "row.appendChild(group)" not in text


def test_renderer_script_sidebar_delete_opens_on_pointerup_when_click_is_unreliable():
    text = Path("codex_session_delete/inject/renderer-inject.js").read_text(encoding="utf-8")
    assert "openDeleteConfirm" in text
    assert "codexDeleteVersion = \"8\"" in text
    assert "actionGroupFromRow" in text
    assert "removeActionGroups(row)" in text
    assert "row.dataset.codexDeleteRow = \"false\"" in text
    assert "installDeleteButtonEventDelegation" in text
    assert "codexSessionDeleteDocumentDeleteHandler" in text
    assert "document.addEventListener(\"pointerup\", handler, true)" in text
    assert "document.addEventListener(\"click\", handler, true)" in text
    assert "deleteButton.dataset.codexDeleteVersion = codexDeleteVersion" in text


def test_renderer_script_removes_orphaned_projected_rows_when_thread_is_missing():
    text = Path("codex_session_delete/inject/renderer-inject.js").read_text(encoding="utf-8")
    assert "function isThreadMissingResult" in text
    assert "Thread not found in local storage" in text
    assert "function removeOrphanedProjectedRow" in text
    assert "setProjectlessThreadIds(ref, \"remove\")" in text
    assert "clearThreadWorkspaceHints(ref)" in text
    assert "已移除本地列表中的失效会话" in text


    text = Path("codex_session_delete/inject/renderer-inject.js").read_text(encoding="utf-8")
    assert "updateDeleteButtonOffsets" in text
    assert "codexDeleteStyleVersion = \"13\"" in text
    assert "codexActionGroupVersion = \"5\"" in text
    assert "right: var(--codex-session-action-confirm-right, 66px)" not in text
    assert "确认" in text
    assert "归档对话" in text
    assert "button.getAttribute(\"aria-label\")" in text
    assert "label === \"归档对话\"" in text
    assert "button.classList.contains(exportButtonClass)" in text


    text = Path("codex_session_delete/inject/renderer-inject.js").read_text(encoding="utf-8")
    archive_visible_start = text.index("function archivedPageVisible")
    archive_visible_end = text.index("\n\n  function sessionRefFromRow", archive_visible_start)
    archive_visible_code = text[archive_visible_start:archive_visible_end]
    assert "archivePageHintVisible" in text
    assert "button[aria-label=\"已归档对话\"]" in text
    assert "button[aria-label=\"Archived conversations\"]" in text
    assert "bg-token-list-hover-background" in text
    assert "archivedPageVisible" in text
    assert "document.body.textContent" not in archive_visible_code
    assert "archivedSessionRows" in text
    assert "archivedPageRows" in text
    assert "installArchivedDeleteAllButton" in text
    assert "if (!archivePageHintVisible()) return []" in text
    assert "if (!archivePageHintVisible())" in text
    assert "删除全部归档" in text
    assert "deleteArchivedSessions" in text
    assert "attachArchivedPageDeleteButton" in text
    assert "resolveArchivedThread" in text
    assert "stopArchivedButtonEvent" in text
    assert "[\"pointerdown\", \"mousedown\", \"mouseup\", \"touchstart\"].forEach((eventName) => {\n      button.addEventListener(eventName, stopArchivedButtonEvent, true);" in text
    assert "pointerup" in text
    assert "button.addEventListener(\"pointerup\", openArchivedDeleteAllConfirm, true)" in text
    assert "archivedRefFromRow(row)" in text
    assert "reactArchivedThreadFromNode" in text
    assert "archivedThreadFromRow" in text
    assert "props.archivedThread?.id" in text
    assert "archivedThread.id || archivedThread.sessionId" in text
    assert "replace(/\\d{4}年\\d{1,2}月\\d{1,2}日.*$/, \"\")" in text
    assert "const titleMatches = sessionRows().map(sessionRefFromRow)" not in text
    assert "document.querySelectorAll(\"[data-codex-archive-delete-all]\").forEach((node) => node.remove())" not in text
    assert "const existingButton = document.querySelector(\"[data-codex-archive-delete-all]\")" in text
    assert "positionArchivedDeleteAllButton" in text
    assert "function archiveTitleTextRect(title)" in text
    assert "document.createTreeWalker(title, NodeFilter.SHOW_TEXT)" in text
    assert "range.selectNodeContents(node)" in text
    assert "range.getBoundingClientRect()" in text
    assert "const titleRect = archiveTitleTextRect(title)" in text
    assert "titleRect.right + gap" in text
    assert "top: `${titleRect.top + titleRect.height / 2}px`" in text
    assert "transform: \"translateY(-50%)\"" in text
    assert "if (existingButton.parentElement !== document.body) document.body.appendChild(existingButton)" in text
    assert "positionArchivedDeleteAllButton(existingButton, title)" in text
    assert "runScanStep(installArchivedDeleteAllButton)" in text
    assert "existingButton?.remove()" in text
    assert "button.dataset.codexArchiveDeleteAllVersion = codexArchiveDeleteAllVersion" in text
    assert "data-codex-archive-delete-all" in text
    assert "codex-archive-action-bar" in text
    assert "codexDeleteStyleVersion" in text
    assert "style.dataset.codexDeleteStyleVersion" in text
    assert "position: fixed" in text
    assert "archiveTitleContainer" in text
    assert "archiveTitleCandidateVisible" in text
    assert "rect.width > 0 && rect.height > 0 && rect.x > 350" in text
    assert "element.closest?.(\".window-fx-sidebar-surface, nav\")" in text
    assert "data-codex-archive-title-inline" in text
    assert "title.dataset.codexArchiveTitleInline = \"true\"" in text
    assert "data-codex-archive-title-row" not in text
    assert "codexArchiveTitleRow" not in text
    assert "titleRow.dataset.codexArchiveTitleRow" not in text
    assert "--codex-plus-archive-color" in text
    assert "--codex-plus-archive-hover-background" in text
    assert "html[data-theme=\"dark\"]" in text
    assert "body[data-theme=\"dark\"]" in text
    assert "data-codex-archive-row-action=\"delete\"]:hover" in text
    assert "button.setAttribute(\"aria-label\", \"删除全部归档\")" in text
    assert "button.title = \"删除全部归档\"" in text
    assert "Element.prototype" not in text
    assert "CSSStyleDeclaration" not in text
    assert "已归档对话" in text
    assert "title.insertAdjacentElement(\"afterend\", button)" not in text
    assert "title.appendChild(button)" not in text
    assert "title.parentElement" not in text
    assert "document.body.appendChild(button)" in text
    assert "maxWidth: \"fit-content\"" in text
    assert "Object.assign(button.style" in text
    assert "cursor: \"pointer\"" in text
    assert "position: \"fixed\"" in text
    assert "data-codex-archive-page-row" in text
    assert "data-app-action-sidebar-thread-id" in text
    archive_attach_start = text.index("function attachArchivedPageDeleteButton")
    archive_attach_end = text.index("\n\n  function installArchivedDeleteAllButton", archive_attach_start)
    archive_attach_code = text[archive_attach_start:archive_attach_end]
    assert "取消归档" in text
    assert "已归档对话" in text
    assert "archiveRowFromUnarchiveButton" in text
    assert "[role=\"listitem\"], [role=\"row\"]" in text
    assert "Archived conversations" in text
    assert "data-codex-archive-row-action" in text
    assert "archiveActionGroupClass" not in text
    assert "archiveActionButtonConfigs" not in text
    assert "function configureArchiveActionButton(button, kind)" not in text
    assert "codexArchiveRowActionsVersion" not in text
    assert "function cleanupLegacyArchiveRowActionGroups(row)" in text
    assert "row.querySelectorAll(\".codex-archive-row-actions\").forEach((group) => {" in text
    assert "group.insertAdjacentElement(\"beforebegin\", unarchiveButton)" in text
    assert "group.remove()" in text
    assert "function configureArchiveTextButton(button, kind, label)" in text
    assert "button.dataset.codexArchiveRowAction = kind" in text
    assert "button.setAttribute(\"aria-label\", label)" in text
    assert "button.title = label" in text
    assert "button.textContent = kind === \"export\" ? \"导出\" : \"删除\"" in text
    assert "function archiveUnarchiveButtonFromRow(row)" in text
    assert "Array.from(row.querySelectorAll(\"button\")).find(isUnarchiveButton)" in text
    assert "function ensureArchiveRowActionGroup(row, unarchiveButton)" not in text
    assert "configureArchiveActionButton(unarchiveButton, \"unarchive\")" not in text
    assert "configureArchiveTextButton(exportButton, \"export\", \"导出 Markdown\")" in archive_attach_code
    assert "configureArchiveTextButton(deleteButton, \"delete\", \"删除归档对话\")" in archive_attach_code
    assert "restoreArchiveUnarchiveButton(unarchiveButton)" in archive_attach_code
    assert "unarchiveButton.textContent = \"取消归档\"" in text
    assert "insertAfter.insertAdjacentElement(\"afterend\", exportButton)" in archive_attach_code
    assert "insertAfter.insertAdjacentElement(\"afterend\", deleteButton)" in archive_attach_code
    assert "group.appendChild(exportButton)" not in archive_attach_code
    assert "group.appendChild(deleteButton)" not in archive_attach_code
    assert "installActionButtonEvents(row, unarchiveButton" not in text
    assert "const unarchiveButton = document.createElement(\"button\")" not in text


def test_renderer_script_uses_bridge_only_helper_calls():
    text = Path("codex_session_delete/inject/renderer-inject.js").read_text(encoding="utf-8")
    assert "window.__codexSessionDeleteBridge" in text
    assert "XMLHttpRequest" not in text
    assert 'postJson("/ads"' not in text
    assert "postJson(\"/delete\"" in text
    assert "postJson(\"/undo\"" in text
    assert "postJson(\"/archived-thread\"" in text
    assert "postJson(\"/export-markdown\"" in text
    assert "Blob([markdown]" in text


def test_renderer_script_uses_chinese_delete_toast_fallbacks():
    text = Path("codex_session_delete/inject/renderer-inject.js").read_text(encoding="utf-8")
    assert "删除成功" in text
    assert "删除失败" in text
    assert "撤销完成" in text
    assert "Delete failed" not in text
    assert "Deleted\"" not in text
    assert "Undo finished" not in text


def test_renderer_script_does_not_include_fast_mode_patch():
    text = Path("codex_session_delete/inject/renderer-inject.js").read_text(encoding="utf-8")
    assert "codexFastModeUnlockVersion" not in text
    assert "enableFastModeFeatureFlags" not in text
    assert "patchFastModeGates" not in text
    assert "patchGeneralSettingsSpeedGate" not in text
    assert "patchCodexPostForFastMode" not in text
    assert "recordFastModeDiagnostic" not in text
    assert "additionalSpeedTiers" not in text
    assert "bodyJsonString" not in text
    assert "forceChatGPTAuthForFastMode" not in text
    assert "codex-fast-mode-row" not in text


def test_renderer_script_includes_user_script_manager_ui_contract():
    text = Path("codex_session_delete/inject/renderer-inject.js").read_text(encoding="utf-8")

    assert "用户脚本" in text
    assert "启用用户脚本" in text
    assert "重新加载用户脚本" in text
    assert "禁用后需重载页面或重启 Codex++" in text
    assert "codexPlusUserScripts" in text
    assert "loadUserScripts" in text
    assert "renderUserScripts" in text
    assert "data-codex-user-scripts-enabled" in text
    assert "data-codex-user-script-key" in text
    assert "data-codex-user-scripts-reload" in text
    assert "/user-scripts/list" in text
    assert "/user-scripts/set-enabled" in text
    assert "/user-scripts/set-script-enabled" in text
    assert "/user-scripts/reload" in text
    assert "codex-plus-tab-button" in text
    assert "data-codex-plus-tab=\"home\"" in text
    assert "data-codex-plus-tab=\"userScripts\"" in text
    assert "data-codex-plus-panel=\"home\"" in text
    assert "data-codex-plus-panel=\"userScripts\"" in text
    assert "selectCodexPlusTab" in text
    assert "打开 DevTools" in text
    assert "data-codex-open-devtools" in text
    assert "/devtools/open" in text
    assert "后端连接" in text
    assert "data-codex-backend-status" in text
    assert "data-codex-backend-repair" in text
    assert "checkBackendStatus" in text
    assert "renderBackendStatus" in text
    assert "scheduleBackendHeartbeat" in text
    assert "setInterval(checkBackendStatus, 5000)" in text
    assert "scheduleBackendHeartbeat();\n    loadUserScripts();" not in text
    assert "installCodexPlusMenu();\n    scheduleBackendHeartbeat();" in text
    assert "withTimeout" in text
    assert "postHelperJson" in text
    assert "new Promise((resolve) => setTimeout(() => resolve(timeoutResult), timeoutMs))" in text
    assert "data-codex-backend-indicator" in text
    assert "codex-plus-backend-indicator" in text
    assert "/backend/status" in text
    assert "/backend/repair" in text

    assert "setAuthMethod(\"chatgpt\")" in text
    assert "patchFastModeGateOnObject" not in text
    assert "Codex++" in text
    assert "codexPlusVersion = \"1.0.7\"" in text
    assert "Codex++ ${codexPlusVersion}" in text
    assert "提出问题" in text
    assert "https://github.com/BigPizzaV3/CodexPlusPlus/issues" in text
    assert "window.open(issueUrl, \"_blank\")" in text
    assert "插件选项解锁" in text
    assert "特殊插件强制安装" in text
    assert "会话删除" in text
    assert "Markdown 导出" in text
    assert "原生菜单栏位置" in text
    assert "nativeMenuPlacement: true" in text
    assert "关于 Codex++" in text
    assert "https://github.com/BigPizzaV3/CodexPlusPlus" in text
    assert "codexPlusSettings" in text
    assert "pluginEntryUnlock" in text
    assert "forcePluginInstall" in text
    assert "sessionDelete" in text
    assert "markdownExport" in text
    assert "projectMove" in text
    assert "threadScrollRestore" in text
    assert "会话项目移动" in text
    assert "切换对话保留位置" in text
    assert "移动按钮" in text
    assert "codex-plus-modal-overlay" in text
    assert "codex-plus-modal-content" in text
    assert "codex-plus-modal-header" in text
    assert "codex-dialog-overlay" not in text
    assert "bg-token-dropdown-background/90" not in text
    assert "backdrop-blur-xl" not in text
    assert "codex-plus-menu-floating" in text
    assert "findNativeMenuInsertionPoint" in text
    assert "if (!codexPlusSettings().nativeMenuPlacement) return null" in text
    assert "right: var(--codex-plus-menu-right, 140px)" in text
    assert "left: auto" in text
    assert "pointer-events: auto" in text
    assert "-webkit-app-region: no-drag" in text
    assert ".codex-plus-trigger" in text
    assert "app-header-tint" in text
    assert "flex items-center gap-0.5" in text
    assert "codex-plus-menu-floating" in text
    assert "nativeButtonClass" in text
    assert "removeDuplicateCodexPlusMenus" in text
    assert "data-codex-plus-menu" in text
    assert "/^Codex\\+\\+ \\d+\\.\\d+\\.\\d+/.test((button.textContent || \"\").trim())" in text
    assert "codexPlusMenuVersion = `7:${codexPlusVersion}`" in text
    assert "codexPlusTriggerVersion = `6:${codexPlusVersion}`" in text
    assert "existing.dataset.codexPlusMenuVersion !== codexPlusMenuVersion" in text
    assert "trigger.dataset.codexPlusTriggerInstalled = codexPlusTriggerVersion" in text
    assert "function setCodexPlusTriggerLabel" in text
    assert ".codex-plus-trigger:hover" not in text
    assert "function pageHasCodexAppChrome" in text
    assert "if (!pageHasCodexAppChrome())" in text
    assert "existing?.remove();" in text[text.index("function installCodexPlusMenu"):text.index("\n\n  function reactFiberFrom", text.index("function installCodexPlusMenu"))]
    assert 'document.querySelector("header")' in text
    assert "function headerTitleRegion" in text
    assert "function isHeaderToolbarButton" in text
    assert 'button.closest(".ms-auto.flex.shrink-0.items-center")' in text
    assert "const titleRegion = headerTitleRegion(header);" in text
    assert "if (titleRegion?.contains?.(button)) return false;" in text
    assert ".map((button) => ({ button, rect: button.getBoundingClientRect() }))" in text
    assert ".filter(({ button, rect }) => isHeaderToolbarButton(button, header, rect))" in text
    relevant_start = text.index("const scanRelevantSelector")
    relevant_end = text.index("\n\n  function isScanRelevantNode", relevant_start)
    assert '"header"' in text[relevant_start:relevant_end]


def test_renderer_script_settings_tabs_stay_product_only():
    text = Path("codex_session_delete/inject/renderer-inject.js").read_text(encoding="utf-8")

    assert 'data-codex-plus-tab="home"' in text
    assert 'data-codex-plus-tab="userScripts"' in text
    assert 'data-codex-plus-panel="home"' in text
    assert 'data-codex-plus-panel="userScripts"' in text
    assert 'data-codex-plus-tab="sponsor"' not in text
    assert 'data-codex-plus-tab="support"' not in text
    assert "codex-plus-modal-content[data-codex-plus-active-tab=\"support\"]" not in text
    assert "codex-plus-modal-content[data-codex-plus-active-tab=\"sponsor\"]" not in text


def test_renderer_script_has_backend_provider_sync_toggle():
    text = Path("codex_session_delete/inject/renderer-inject.js").read_text(encoding="utf-8")

    assert "Provider 同步" in text
    assert "切换供应商（model_provider）时不丢任何历史会话" in text
    assert "避免历史对话因为供应商切换而消失" in text
    assert "data-codex-backend-setting=\"providerSyncEnabled\"" in text
    assert "/settings/get" in text
    assert "/settings/set" in text
    assert "loadBackendSettings" in text
    assert "setBackendSetting" in text


def test_renderer_script_can_move_sidebar_threads_between_projects():
    text = Path("codex_session_delete/inject/renderer-inject.js").read_text(encoding="utf-8")

    assert "codex-project-move-button" in text
    assert "codex-project-move-overlay" in text
    assert "codexProjectMoveVersion = \"2\"" in text
    assert "function moveSessionToProjectless" in text
    assert "function moveSessionToProject" in text
    assert "function projectMoveTargets" in text
    assert "function nativeProjectTargets" in text
    assert "data-app-action-sidebar-project-row" in text
    assert "data-app-action-sidebar-project-id" in text
    assert "data-app-action-sidebar-project-label" in text
    assert "get-global-state" in text
    assert "set-global-state" in text
    assert "projectless-thread-ids" in text
    assert "thread-workspace-root-hints" in text
    assert "electron-saved-workspace-roots" not in text
    assert "active-workspace-roots" not in text
    assert "project-order" not in text
    assert "function threadIdVariants" in text
    assert '`local:${bareId}`' in text
    assert "uniqueValues([...ids, ...variants])" in text
    assert "const variantSet = new Set(variants)" in text
    assert "ids.filter((id) => !variantSet.has(id))" in text
    assert "/thread-workspaces" not in text
    assert "/move-thread-workspace" in text
    assert "/thread-sort-key" in text
    assert "/thread-sort-keys" in text
    assert "hintKeys.forEach((id) => delete hints[id])" in text
    assert "hints[id] = targetCwd" not in text
    assert "codexProjectMoveProjection" in text
    assert "legacyProjectMoveOverridesKey" in text
    assert "function applyProjectMoveProjection" in text
    assert "scheduleProjectMoveProjection" in text
    assert "saveProjectMoveProjection(ref, target, target.sortMs || rowSortMs(row, ref, target))" in text
    assert "clearProjectMoveProjection(ref)" in text
    assert "refresh-recent-conversations-for-host" in text
    assert "function refreshAfterProjectMove" in text
    assert "function insertRowItemByTime" in text
    assert "function sortStateFromMoveResult" in text
    assert "function timestampMsFromPayload" in text
    assert "function relativeTimeLabel" in text
    assert "function updateRowTimeLabel" in text
    assert "dataset.codexProjectMoveTime" in text
    assert "function rowTimeLabelCandidates" in text
    assert "function cleanupRowTimeLabels" in text
    assert "function cleanupManagedStatusIconTimeNodes" in text
    assert "function nodeInsideStatusIcon" in text
    assert "function nodeLooksLikeTimeLabel" in text
    assert "className.includes(\"animate-spin\")" in text
    assert "node.children.length > 0" in text
    assert "data-codex-project-move-time-wrapper" in text
    assert "node.dataset?.codexProjectMoveTime !== \"true\"" in text
    assert "function rowSortMs" in text
    assert "function uuidV7TimestampMs" in text
    assert "function projectThreadList" in text
    assert "function applyChatsSortCorrection" in text
    assert "function scheduleChatsSortCorrection" in text
    assert "function reorderChatsRows" in text
    assert "window.__codexProjectMoveSortChats" in text
    assert "window.__codexProjectMoveRuntimeId" in text
    assert "__codexProjectMoveChatsSortTimer" in text
    assert "sortMsTrusted" in text
    assert "chatsSortDbRefreshIntervalMs" in text
    assert "data-app-action-sidebar-section-heading=\"Chats\"" in text
    assert "data-app-action-sidebar-project-list-id" in text
    assert "codexProjectMoveSortMs" in text
    assert "data-codex-project-move-injected-list" in text
    assert "codex-project-move-hidden" in text
    assert "window.__codexProjectMoveApplyProjection" in text
    assert "window.__codexProjectMoveTargets" in text
    assert "projectMoveButtonClass" in text
    assert "openProjectMoveMenuForRow" in text
    assert "existingMoveButton" in text
    assert "普通对话" in text


def test_renderer_script_contains_zed_remote_setting_and_menu_copy():
    text = Path("codex_session_delete/inject/renderer-inject.js").read_text(encoding="utf-8")

    assert "zedRemoteOpen" in text
    assert "Zed Remote open" in text
    assert "Open supported remote SSH file references in Zed without patching Codex.app." in text
    assert 'data-codex-plus-setting="zedRemoteOpen"' in text


def test_renderer_script_contains_zed_remote_probe_and_open_action():
    text = Path("codex_session_delete/inject/renderer-inject.js").read_text(encoding="utf-8")

    assert "codex-zed-remote-button" in text
    assert "codex-zed-open-in-menu-item" in text
    assert "Open in Zed Remote" in text
    assert "Zed Remote" in text
    assert 'postJson("/zed-remote/status", {})' in text
    assert 'postJson("/zed-remote/resolve-host", { hostId })' in text
    assert 'postJson("/zed-remote/open", nextRequest)' in text
    assert "function zedRemoteContext" in text
    assert "function zedRemoteFileCandidates" in text
    assert "function zedRemoteBestOpenRequest" in text
    assert "function refreshZedRemoteOpenInMenus" in text
    assert "function refreshZedRemoteOpenControls" in text
    assert "Cannot determine remote SSH host for this file" in text
    assert "settings" in text[text.index("function zedRemoteContext"):text.index("function zedRemoteFileCandidates")]


def test_renderer_script_removes_stale_zed_remote_controls_when_fail_closed():
    text = Path("codex_session_delete/inject/renderer-inject.js").read_text(encoding="utf-8")
    remove_start = text.index("function removeZedRemoteButtons")
    remove_end = text.index("\n\n  async function refreshZedRemoteOpenControls", remove_start)
    remove_code = text[remove_start:remove_end]
    start = text.index("async function refreshZedRemoteOpenControls")
    end = text.index("\n\n  function scanDeferred", start)
    refresh_code = text[start:end]

    assert "function removeZedRemoteButtons" in text
    assert "[data-codex-zed-remote-version]" in remove_code
    assert "delete node.dataset.codexZedRemoteVersion" in remove_code
    assert "removeZedRemoteButtons();\n      removeZedRemoteOpenInMenuItems();\n      return;" in refresh_code
    assert "const context = zedRemoteContext() || {};" in refresh_code
    assert "if (!status?.platformSupported || (!status.zedAppFound && !status.zedCliFound)) {\n        removeZedRemoteButtons();\n        removeZedRemoteOpenInMenuItems();\n        return;\n      }" in refresh_code
    assert "catch (_) {\n      removeZedRemoteButtons();\n      removeZedRemoteOpenInMenuItems();\n      return;\n    }" in refresh_code
    assert "removeZedRemoteButtons();\n    const candidates = zedRemoteFileCandidates(context);\n    candidates.forEach(attachZedRemoteButton);\n    refreshZedRemoteOpenInMenus(context);" in refresh_code


def test_renderer_script_adds_zed_remote_to_open_in_menu():
    text = Path("codex_session_delete/inject/renderer-inject.js").read_text(encoding="utf-8")
    start = text.index("function createZedRemoteOpenInMenuItem")
    end = text.index("\n\n  async function refreshZedRemoteOpenControls", start)
    menu_code = text[start:end]
    create_end = text.index("\n\n  function activateZedRemoteOpenInMenuItem", start)
    create_code = text[start:create_end]

    assert ">Zed<" in menu_code
    assert "Zed Remote" not in menu_code
    assert 'src="apps/zed.png"' in menu_code
    assert "codex-zed-open-in-menu-icon icon-sm" in menu_code
    assert "data-codex-zed-open-in-menu" in menu_code
    assert "bindZedRemoteOpenInMenuItem(item, \"injected\")" in menu_code
    assert "item.dataset.codexZedOpenInMenuVersion = zedRemoteOpenInMenuVersion" not in create_code
    assert "codexZedOpenInMenuBound" in menu_code
    assert "codexZedOpenInMenuActivatedAt" in menu_code
    assert "function activateZedRemoteOpenInMenuItem" in menu_code
    assert "const existingZedItem" in menu_code
    assert "bindZedRemoteOpenInMenuItem(existingZedItem, \"native\")" in menu_code
    assert "VS Code|Cursor|Antigravity" in menu_code
    assert "referenceItem.parentElement?.appendChild(createZedRemoteOpenInMenuItem(referenceItem));" in menu_code
    assert "document.dispatchEvent(new KeyboardEvent(\"keydown\", { key: \"Escape\"" in menu_code


def test_renderer_script_observes_native_open_in_menu_mounts():
    text = Path("codex_session_delete/inject/renderer-inject.js").read_text(encoding="utf-8")
    start = text.index("function shouldScheduleScan")
    end = text.index("\n\n  function runScheduledScan", start)
    schedule_code = text[start:end]

    assert "[role=\"menu\"], [data-radix-popper-content-wrapper]" in schedule_code


def test_renderer_script_handles_zed_remote_open_rejection_with_toast():
    text = Path("codex_session_delete/inject/renderer-inject.js").read_text(encoding="utf-8")
    start = text.index("async function openZedRemote")
    end = text.index("\n\n  function attachZedRemoteButton", start)
    open_code = text[start:end]

    assert "try {" in open_code
    assert "postJson(\"/zed-remote/open\", nextRequest)" in open_code
    assert "catch (error)" in open_code
    assert "showZedRemoteToast(error?.message || \"Cannot open this file in Zed Remote\")" in open_code


def test_renderer_script_zed_remote_uses_codex_remote_source_contract():
    text = Path("codex_session_delete/inject/renderer-inject.js").read_text(encoding="utf-8")
    zed_code = text[text.index("function zedRemoteContext"):text.index("\n\n  async function openZedRemote")]

    assert "hostConfig" in zed_code
    assert "supportsSsh" in zed_code
    assert "remoteWorkspaceRoot" in zed_code
    assert "remotePath" in zed_code
    assert "hostId.startsWith(\"remote-ssh-\")" in zed_code
    assert "open-in-targets" in zed_code
    assert "__reactFiber" in zed_code
    assert "__reactProps" in zed_code
    assert "JSON.parse" in zed_code


def test_renderer_script_zed_remote_has_fallback_for_hidden_remote_context():
    text = Path("codex_session_delete/inject/renderer-inject.js").read_text(encoding="utf-8")
    zed_code = text[text.index("function zedRemoteHostIdFromText"):text.index("\n\n  function zedRemoteContextFromSerializedState")]
    candidates_code = text[text.index("function zedRemoteFileCandidates"):text.index("\n\n  function zedRemoteBestOpenRequest")]

    assert "function zedRemoteFallbackContextForElement" in zed_code
    assert "\"remote-ssh-codex-managed:remote\"" in zed_code
    assert "\"/bin/repo/\"" in zed_code
    assert "zedRemoteFallbackContextForElement(node)" in candidates_code


def test_renderer_script_zed_remote_does_not_use_unscoped_broad_anchor_selector():
    text = Path("codex_session_delete/inject/renderer-inject.js").read_text(encoding="utf-8")
    start = text.index("function zedRemoteFileCandidates")
    end = text.index("\n\n  async function openZedRemote", start)
    candidates_code = text[start:end]

    assert '"code, a,' not in candidates_code
    assert '"code, a' not in candidates_code
    assert "getAttribute(\"href\")" not in candidates_code
    assert "context.workspaceRoot && !path.startsWith" in text
    assert "if (!candidateContext?.hostId && !candidateContext?.ssh?.host) return;" in candidates_code


def test_renderer_script_zed_remote_candidate_sources_are_structured():
    text = Path("codex_session_delete/inject/renderer-inject.js").read_text(encoding="utf-8")
    start = text.index("function zedRemoteFileCandidates")
    end = text.index("\n\n  async function openZedRemote", start)
    candidates_code = text[start:end]

    assert "[data-remote-path]" in candidates_code
    assert "[data-file-path]" in candidates_code
    assert "[data-path]" in candidates_code
    assert "data-open-in-targets" in candidates_code
    assert "zedRemotePathFromElementMetadata" in candidates_code
    assert "zedRemoteAnchorHasOpenFileMetadata" in candidates_code
    assert "span.inline-markdown, code, [class*='inlineMarkdown']" in candidates_code
    scan_relevance_code = text[text.index("const scanRelevantSelector"):text.index("function nodeSelfOrAncestorMatchesScanRelevance")]
    assert '"span.inline-markdown"' in scan_relevance_code
    assert "\"[class*='inlineMarkdown']\"" in scan_relevance_code


def test_runtime_renderer_asset_contains_zed_remote_open_controls():
    text = Path("assets/inject/renderer-inject.js").read_text(encoding="utf-8")

    assert "zedRemoteOpen" in text
    assert 'src="apps/zed.png"' in text
    assert 'postJson("/zed-remote/open", nextRequest)' in text
    assert 'data-codex-plus-setting="zedRemoteOpen"' in text
    assert "[role=\"menu\"], [data-radix-popper-content-wrapper]" in text

def test_renderer_script_has_thread_scroll_restore_toggle():
    text = Path("codex_session_delete/inject/renderer-inject.js").read_text(encoding="utf-8")

    assert "threadScrollRestore: true" in text
    assert "切换对话保留位置" in text
    assert "恢复到上一次浏览位置" in text
    assert 'data-codex-plus-setting="threadScrollRestore"' in text
    assert "codexThreadScrollKey" in text
    assert "codexThreadScrollVersion" in text


def test_renderer_script_persists_and_restores_thread_scroll_positions():
    text = Path("codex_session_delete/inject/renderer-inject.js").read_text(encoding="utf-8")

    assert "function readThreadScrollEntries" in text
    assert "function writeThreadScrollEntries" in text
    assert "function saveThreadScrollPositionNow" in text
    assert "function restoreThreadScrollPosition" in text
    assert "function scheduleThreadScrollRestore" in text
    assert "function syncThreadScrollState" in text
    assert "function currentThreadScroller" in text
    assert "function currentSessionRef" in text
    assert "function locationThreadId" in text
    assert "codexThreadScrollRestoreWindowMs = 3200" in text
    assert 'localStorage.getItem(codexThreadScrollKey)' in text
    assert 'localStorage.setItem(codexThreadScrollKey' in text
    assert "scrollTo({ top: targetTop, behavior: \"auto\" })" in text
    assert "codexThreadScrollRestoreDelaysMs" in text
    assert "codexThreadScrollMaxEntries = 120" in text


def test_renderer_script_tracks_thread_switches_for_scroll_restore():
    text = Path("codex_session_delete/inject/renderer-inject.js").read_text(encoding="utf-8")

    assert "function installThreadScrollNavigationCapture" in text
    assert "function installThreadScrollRouteHooks" in text
    assert "document.addEventListener(\"pointerdown\", navigationHandler, true)" in text
    assert "document.addEventListener(\"click\", clickHandler, true)" in text
    assert "document.addEventListener(\"keydown\", keyboardHandler, true)" in text
    assert "history[method] = function codexThreadScrollPatchedHistory" in text
    assert "window.__codexThreadScrollHandlers?.captureNavigation?.(sessionRefFromRow(row).session_id)" in text
    assert "function scheduleThreadScrollSyncAttempts" in text
    assert "function captureThreadScrollNavigation" in text
    assert "const sessionChanged = !!targetKey && targetKey !== runtime.activeSessionId" in text
    assert "runtime.pendingNavigation = { fromSessionId: runtime.activeSessionId, targetSessionId: targetKey, at: Date.now() }" in text
    assert "duplicatePendingTarget" in text
    assert "if (!duplicatePendingTarget) saveThreadScrollPositionNow();" in text
    assert "scheduleThreadScrollSyncAttempts(true)" in text
    assert "window.__codexThreadScrollHandlers?.captureNavigation?.(locationThreadId())" in text
    assert 'window.removeEventListener("popstate", window.__codexThreadScrollPopStateHandler, true)' in text
    assert 'window.removeEventListener("hashchange", window.__codexThreadScrollHashChangeHandler, true)' in text
    assert 'window.addEventListener("popstate", window.__codexThreadScrollPopStateHandler, true)' in text
    assert 'window.addEventListener("hashchange", window.__codexThreadScrollHashChangeHandler, true)' in text
    assert "document.addEventListener(\"visibilitychange\"" in text
    assert "codexThreadScrollRouteHooksVersion = \"dispatcher:2\"" in text
    assert "const prototypeMethod = typeof History !== \"undefined\" ? History.prototype?.[method] : null" in text
    assert "storedMethod?.name === \"codexThreadScrollPatchedHistory\"" in text
    assert "currentMethod?.name === \"codexThreadScrollPatchedHistory\"" in text
    assert 'mutation.type === "attributes" && mutation.attributeName === "aria-current"' in text
    assert 'attributes: true, attributeFilter: ["aria-current"]' in text
    assert "setTimeout(() => {" in text[text.index("function scheduleThreadScrollSync"):text.index("\n\n  function installThreadScrollRouteHooks")]
    assert "updateThreadScrollHandlers();" in text[text.index("function scanLightweight"):text.index("\n\n  function scanDeferred")]
    assert "scheduleThreadScrollSync(true);" in text[text.index("function scanLightweight"):text.index("\n\n  function scanDeferred")]
    assert "scheduleThreadScrollSync(true);" in text[text.index("function scanDeferred"):text.index("\n\n  function runScanStep")]
    sync_code = text[text.index("function syncThreadScrollState"):text.index("\n\n  function scheduleThreadScrollSyncAttempts")]
    assert "if (!nextSessionId) return;" in sync_code
    assert "saveThreadScrollPositionNow(runtime.activeSessionId, runtime.activeScroller)" not in sync_code


def test_renderer_script_prevents_native_autoscroll_from_overwriting_restored_position():
    text = Path("codex_session_delete/inject/renderer-inject.js").read_text(encoding="utf-8")

    assert "function clearThreadScrollRestoreLock" in text
    assert "function activeThreadScrollRestoreLock" in text
    assert "function startThreadScrollRestoreLock" in text
    assert "function prepareThreadScrollRestoreLock" in text
    assert "function currentThreadScrollRestoreLock" in text
    assert "function shouldBlockThreadScrollAutobottom" in text
    assert "function finiteScrollNumber" in text
    assert "top: finiteScrollNumber(value.top)" in text
    assert "top: finiteScrollNumber(scroller.scrollTop)" in text
    assert "function threadScrollIsReversed" in text
    assert 'flexDirection === "column-reverse"' in text
    assert "function threadScrollRange" in text
    assert "? { min: -extent, max: 0, bottom: 0 }" in text
    assert "codexThreadScrollListenerVersion = \"4\"" in text
    assert "let listenerReplaced = false" in text
    assert "listenerReplaced = true" in text
    assert "if (!listenerReplaced && runtime.activeScroller === scroller" in text
    assert "runtime.scrollListenerVersion !== codexThreadScrollListenerVersion" in text
    assert "runtime.scrollListenerVersion = codexThreadScrollListenerVersion" in text
    assert "threadScrollTargetTop(scroller, targetTop)" in text
    assert "return Math.max(range.min, Math.min(range.max, finiteScrollNumber(targetTop)))" in text
    assert "return Math.abs(range.bottom - finiteScrollNumber(top))" in text
    assert "function installThreadScrollProgrammaticScrollGuard" in text
    assert "codexThreadScrollProgrammaticGuardVersion = \"dispatcher:2\"" in text
    assert "window.__codexThreadScrollOriginals = window.__codexThreadScrollOriginals || {}" in text
    assert "window.__codexThreadScrollHandlers?.shouldBlockAutobottom" in text
    assert "function threadScrollNativePrototypeSnapshot" in text
    assert "document.createElement(\"iframe\")" in text
    assert "function threadScrollFunctionLooksGuarded" in text
    assert "function threadScrollOriginalFunction" in text
    assert "threadScrollFunctionLooksGuarded(current)" in text
    assert "nativeSnapshot.elementScrollTo" in text
    assert "Element.prototype.scrollTo = function codexThreadScrollGuardedScrollTo" in text
    assert "Element.prototype.scroll = function codexThreadScrollGuardedScroll" in text
    assert "Element.prototype.scrollBy = function codexThreadScrollGuardedScrollBy" in text
    assert "Element.prototype.scrollIntoView = function codexThreadScrollGuardedScrollIntoView" in text
    assert "window.scrollTo = function codexThreadScrollGuardedWindowScrollTo" in text
    assert "window.scroll = function codexThreadScrollGuardedWindowScroll" in text
    assert "window.scrollBy = function codexThreadScrollGuardedWindowScrollBy" in text
    assert 'Object.defineProperty(scrollTop.prototype, "scrollTop"' in text
    assert "runtime.applyingRestore = true" in text
    guard_code = text[text.index("function shouldBlockThreadScrollAutobottom"):text.index("\n\n  function scrollToRequestedTop")]
    assert "const lock = currentThreadScrollRestoreLock();" in guard_code
    assert "if (!lock || !codexPlusSettings().threadScrollRestore) return false;" in guard_code
    assert "if (runtime.applyingRestore || !guardScroller) return false;" in guard_code
    assert "if (activeThreadScrollRestoreLock(key)) return;" in text
    assert "installThreadScrollProgrammaticScrollGuard();" in text[text.index("function scanLightweight"):text.index("\n\n  function scanDeferred")]
    assert "shouldEnforceThreadScrollRestore" not in text
    assert "scheduleThreadScrollRestoreEnforcement" not in text
    assert "restoreEnforceRafId" not in text


def test_renderer_script_cancels_thread_scroll_restore_on_user_scroll_intent():
    text = Path("codex_session_delete/inject/renderer-inject.js").read_text(encoding="utf-8")

    assert "codexThreadScrollUserIntentWindowMs = 1200" in text
    assert "codexThreadScrollUserIntentVersion = \"dispatcher:2\"" in text
    assert "function cancelThreadScrollRestoreForUserIntent" in text
    assert "function userScrollIntentActive" in text
    assert "function markThreadScrollUserIntent" in text
    assert "function markThreadScrollKeyboardIntent" in text
    assert "function markThreadScrollPointerIntent" in text
    assert "function installThreadScrollUserIntentCapture" in text
    assert "function clearThreadScrollSyncTimers" in text
    assert "runtime.userCancelledRestoreSessionId = cancelledSessionId" in text
    assert "runtime.userScrollIntentUntil = Date.now() + codexThreadScrollUserIntentWindowMs" in text
    assert "window.__codexThreadScrollRestoreRevision = (window.__codexThreadScrollRestoreRevision || 0) + 1" in text
    assert "window.__codexThreadScrollSyncRevision = (window.__codexThreadScrollSyncRevision || 0) + 1" in text
    assert "clearThreadScrollRestoreTimers();" in text
    assert "clearThreadScrollSyncTimers();" in text
    assert "clearThreadScrollRestoreLock();" in text
    assert "function threadScrollRestoreCancelledForSession" in text
    assert "if (userScrollIntentActive() || threadScrollRestoreCancelledForSession(currentKey)) return;" in text
    assert 'document.addEventListener("wheel", window.__codexThreadScrollWheelIntentHandler' in text
    assert 'document.addEventListener("touchmove", window.__codexThreadScrollTouchIntentHandler' in text
    assert 'document.addEventListener("keydown", window.__codexThreadScrollKeyIntentHandler, true)' in text
    assert "installThreadScrollUserIntentCapture();" in text[text.index("function scanLightweight"):text.index("\n\n  function scanDeferred")]


def test_renderer_script_hardens_thread_scroll_storage_keys():
    text = Path("codex_session_delete/inject/renderer-inject.js").read_text(encoding="utf-8")

    assert "function validThreadScrollSessionKey" in text
    assert 'key === "__proto__"' in text
    assert 'key === "prototype"' in text
    assert 'key === "constructor"' in text
    assert "/^[A-Za-z0-9_.-]{8,128}$/.test(key)" in text
    assert "const entries = Object.create(null)" in text
    assert "const pruned = Object.create(null)" in text
    assert "window.__codexThreadScrollEntries = Object.create(null)" in text


def test_renderer_script_installs_thread_scroll_dispatcher_handlers():
    text = Path("codex_session_delete/inject/renderer-inject.js").read_text(encoding="utf-8")

    assert "function updateThreadScrollHandlers" in text
    assert "window.__codexThreadScrollHandlers = {" in text
    assert "shouldBlockAutobottom: shouldBlockThreadScrollAutobottom" in text
    assert "shouldBlockIntoView: shouldBlockThreadScrollIntoView" in text
    assert "markUserIntent: markThreadScrollUserIntent" in text
    assert "markKeyboardIntent: markThreadScrollKeyboardIntent" in text
    assert "markPointerIntent: markThreadScrollPointerIntent" in text
    assert "captureNavigation: captureThreadScrollNavigation" in text
    assert "saveNow: saveThreadScrollPositionNow" in text
    assert "prepareRestoreLock: prepareThreadScrollRestoreLock" in text
    assert "scheduleSyncAttempts: scheduleThreadScrollSyncAttempts" in text
