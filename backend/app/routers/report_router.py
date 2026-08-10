from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.services.report_service import ReportService
from app.utils.export_utils import ExportUtils


def get_current_user():
    class MockUser:
        id = 1
        username = "test_user"
    return MockUser()


router = APIRouter(prefix="/reports", tags=["Reporting & Insights"])


@router.get("/performance")
def get_student_performance_report(
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    """
    Retrieves dynamic performance analytics report for the current user.
    """
    return ReportService.generate_student_performance_report(db, user_id=current_user.id)


@router.get("/session/{session_id}")
def get_session_report(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    """
    Retrieves end-of-session summary report.
    """
    report = ReportService.generate_session_report(db, session_id=session_id)
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session report not found")
    return report


@router.get("/export/performance/csv")
def export_performance_report_csv(
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    """
    Exports the student performance report as a downloadable CSV file.
    """
    report_data = ReportService.generate_student_performance_report(db, user_id=current_user.id)
    csv_content = ExportUtils.generate_student_csv(report_data)

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=performance_report_user_{current_user.id}.csv"}
    )


@router.get("/export/session/{session_id}/csv")
def export_session_report_csv(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    """
    Exports a completed practice session report as a downloadable CSV file.
    """
    session_report = ReportService.generate_session_report(db, session_id=session_id)
    if not session_report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session report not found")

    csv_content = ExportUtils.generate_session_csv(session_report)

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=session_report_{session_id}.csv"}
    )
