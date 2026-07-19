from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, Response, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.deps import get_current_user
from app.db.session import get_db
from app.models.document import ProcessDocument
from app.models.project import Project
from app.models.user import User
from app.schemas.document import DocumentRead, DocumentUpdate
from app.services.document_processor import ensure_directory, extract_text_from_file


router = APIRouter()


def _get_project_or_404(db: Session, project_id: int, owner_id: int) -> Project:
    project = db.execute(
        select(Project).where(Project.id == project_id, Project.owner_id == owner_id)
    ).scalar_one_or_none()
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


@router.get("/{project_id}/documents", response_model=list[DocumentRead])
def list_documents(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[DocumentRead]:
    _get_project_or_404(db, project_id, current_user.id)
    documents = db.execute(
        select(ProcessDocument).where(ProcessDocument.project_id == project_id).order_by(ProcessDocument.created_at.desc())
    ).scalars().all()
    return [DocumentRead.model_validate(document) for document in documents]


@router.get("/{project_id}/documents/{document_id}", response_model=DocumentRead)
def get_document(
    project_id: int,
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentRead:
    _get_project_or_404(db, project_id, current_user.id)
    document = db.execute(
        select(ProcessDocument).where(
            ProcessDocument.id == document_id,
            ProcessDocument.project_id == project_id,
        )
    ).scalar_one_or_none()
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return DocumentRead.model_validate(document)


@router.get("/{project_id}/documents/{document_id}/download")
def download_document(
    project_id: int,
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_project_or_404(db, project_id, current_user.id)
    document = db.execute(
        select(ProcessDocument).where(
            ProcessDocument.id == document_id,
            ProcessDocument.project_id == project_id,
        )
    ).scalar_one_or_none()
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    file_path = Path(document.storage_path)
    if not file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document file not found")
    return FileResponse(path=str(file_path), filename=document.original_filename)

@router.post("/{project_id}/documents", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
def upload_document(
    project_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentRead:
    _get_project_or_404(db, project_id, current_user.id)

    upload_dir = ensure_directory(Path(settings.upload_dir) / f"project_{project_id}")
    original_filename = file.filename or "upload.bin"
    stored_filename = f"{uuid4().hex}_{Path(original_filename).name}"
    target_path = upload_dir / stored_filename
    content = file.file.read()
    target_path.write_bytes(content)
    extracted_text = extract_text_from_file(target_path)

    document = ProcessDocument(
        project_id=project_id,
        original_filename=original_filename,
        display_name=Path(original_filename).stem,
        stored_filename=stored_filename,
        mime_type=file.content_type,
        storage_path=str(target_path),
        extracted_text=extracted_text,
        file_size=len(content),
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return DocumentRead.model_validate(document)


@router.patch("/{project_id}/documents/{document_id}", response_model=DocumentRead)
def update_document(
    project_id: int,
    document_id: int,
    payload: DocumentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentRead:
    _get_project_or_404(db, project_id, current_user.id)
    document = db.execute(
        select(ProcessDocument).where(
            ProcessDocument.id == document_id,
            ProcessDocument.project_id == project_id,
        )
    ).scalar_one_or_none()
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(document, field, value)
    db.commit()
    db.refresh(document)
    return DocumentRead.model_validate(document)


@router.delete(
    "/{project_id}/documents/{document_id}",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
def delete_document(
    project_id: int,
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    _get_project_or_404(db, project_id, current_user.id)
    document = db.execute(
        select(ProcessDocument).where(
            ProcessDocument.id == document_id,
            ProcessDocument.project_id == project_id,
        )
    ).scalar_one_or_none()
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    file_path = Path(document.storage_path)
    if file_path.exists():
        file_path.unlink()
    db.delete(document)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
