from fastapi import APIRouter, Depends, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.services.reporting_service import ReportingService
from app.utils.report_exporter import ReportExporter
from app.database.database import get_db

router = APIRouter(prefix="/api", tags=["Reports"])

@router.get("/reports/student/{student_id}")
def get_student_report(student_id: int, db: Session = Depends(get_db)):
    service = ReportingService(db)
    return service.get_student_performance_summary(student_id)

@router.post("/sessions/{session_id}/complete")
def complete_practice_session(session_id: int, db: Session = Depends(get_db)):
    service = ReportingService(db)
    session_summary = service.get_session_report(session_id)
    return {"message": "Session completed successfully.", "summary": session_summary}

@router.get("/reports/student/{student_id}/export/pdf")
def export_student_pdf(student_id: int, db: Session = Depends(get_db)):
    service = ReportingService(db)
    report_data = service.get_student_performance_summary(student_id)
    pdf_buffer = ReportExporter.generate_student_pdf(report_data)
    
    headers = {'Content-Disposition': f'attachment; filename="student_{student_id}_report.pdf"'}
    return StreamingResponse(pdf_buffer, media_type="application/pdf", headers=headers)

@router.get("/reports/student/{student_id}/export/csv")
def export_student_csv(student_id: int, db: Session = Depends(get_db)):
    service = ReportingService(db)
    report_data = service.get_student_performance_summary(student_id)
    csv_data = ReportExporter.generate_student_csv(report_data)
    
    headers = {'Content-Disposition': f'attachment; filename="student_{student_id}_report.csv"'}
    return Response(content=csv_data, media_type="text/csv", headers=headers)
