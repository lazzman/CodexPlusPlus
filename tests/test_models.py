from codex_session_delete.models import BulkExportResult, DeleteResult, DeleteStatus, ExportResult, ExportStatus, SessionRef


def test_session_ref_requires_session_id():
    try:
        SessionRef(session_id="", title="Untitled")
    except ValueError as exc:
        assert "session_id" in str(exc)
    else:
        raise AssertionError("SessionRef accepted an empty session_id")


def test_delete_result_serializes_to_json_dict():
    result = DeleteResult(
        status=DeleteStatus.LOCAL_DELETED,
        session_id="abc123",
        message="Deleted locally",
        undo_token="undo-1",
        backup_path="C:/tmp/backup.json",
    )

    assert result.to_dict() == {
        "status": "local_deleted",
        "session_id": "abc123",
        "message": "Deleted locally",
        "undo_token": "undo-1",
        "backup_path": "C:/tmp/backup.json",
    }


def test_export_result_serializes_to_json_dict():
    result = ExportResult(
        status=ExportStatus.EXPORTED,
        session_id="abc123",
        message="Exported",
        filename="example.md",
        markdown="# Example\n",
    )

    assert result.to_dict() == {
        "status": "exported",
        "session_id": "abc123",
        "message": "Exported",
        "filename": "example.md",
        "markdown": "# Example\n",
    }


def test_bulk_export_result_serializes_zip_payload():
    result = BulkExportResult(
        status=ExportStatus.EXPORTED,
        message="已导出 1/1 个会话为 ZIP",
        filename="codex-sessions-1-of-1.zip",
        zip_base64="emlw",
        exported_count=1,
        failed_count=0,
        failures=[],
    )

    assert result.zip_bytes() == b"zip"
    assert result.to_dict() == {
        "status": "exported",
        "message": "已导出 1/1 个会话为 ZIP",
        "filename": "codex-sessions-1-of-1.zip",
        "zip_base64": "emlw",
        "exported_count": 1,
        "failed_count": 0,
        "failures": [],
    }
