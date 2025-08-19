from typing import Any, List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app import models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=schemas.operation.OperationList)
def get_operations(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    document_type: Optional[str] = None,
    debit_account: Optional[str] = None,
    credit_account: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    description_contains: Optional[str] = None,
    template_type: Optional[str] = None,
    file_id: Optional[int] = None,
) -> Any:
    """
    Retrieve accounting operations with filtering and pagination.
    """
    # Start with a base query for all operations
    query = db.query(models.AccountingOperation).join(
        models.UploadedFile,
        models.AccountingOperation.file_id == models.UploadedFile.id
    )
    
    # Apply filters if provided
    filters = []
    
    if start_date:
        filters.append(models.AccountingOperation.operation_date >= start_date)
    
    if end_date:
        filters.append(models.AccountingOperation.operation_date <= end_date)
    
    if document_type:
        filters.append(models.AccountingOperation.document_type.ilike(f"%{document_type}%"))
    
    if debit_account:
        filters.append(models.AccountingOperation.debit_account.ilike(f"%{debit_account}%"))
    
    if credit_account:
        filters.append(models.AccountingOperation.credit_account.ilike(f"%{credit_account}%"))
    
    if min_amount is not None:
        filters.append(models.AccountingOperation.amount >= min_amount)
    
    if max_amount is not None:
        filters.append(models.AccountingOperation.amount <= max_amount)
    
    if description_contains:
        filters.append(models.AccountingOperation.description.ilike(f"%{description_contains}%"))
    
    if template_type:
        filters.append(models.AccountingOperation.template_type == template_type)
    
    if file_id:
        filters.append(models.AccountingOperation.file_id == file_id)
    
    if filters:
        query = query.filter(and_(*filters))
    
    # Get total count for pagination
    total = query.count()
    
    # Apply pagination and ordering
    operations = query.order_by(models.AccountingOperation.operation_date.desc()).offset(skip).limit(limit).all()
    
    return {"items": operations, "total": total}


@router.get("/{operation_id}", response_model=schemas.operation.Operation)
def get_operation(
    *,
    db: Session = Depends(deps.get_db),
    operation_id: int
) -> Any:
    """
    Get a specific accounting operation by ID.
    """
    operation = db.query(models.AccountingOperation).filter(
        models.AccountingOperation.id == operation_id
    ).first()
    
    if not operation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Operation not found"
        )
    
    return operation


@router.get("/statistics/summary", response_model=dict)
def get_operations_summary(
    db: Session = Depends(deps.get_db),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> Any:
    """
    Get summary statistics about accounting operations.
    """
    # Base query for all operations
    query = db.query(models.AccountingOperation)
    
    # Apply date filters if provided
    if start_date:
        query = query.filter(models.AccountingOperation.operation_date >= start_date)
    
    if end_date:
        query = query.filter(models.AccountingOperation.operation_date <= end_date)
    
    # Get total count
    total_operations = query.count()
    
    # Get sum of amounts
    total_amount = db.query(
        db.func.sum(models.AccountingOperation.amount)
    ).select_from(
        models.AccountingOperation
    )
    
    if start_date:
        total_amount = total_amount.filter(models.AccountingOperation.operation_date >= start_date)
    
    if end_date:
        total_amount = total_amount.filter(models.AccountingOperation.operation_date <= end_date)
    
    total_amount = total_amount.scalar() or 0
    
    # Get counts by template type
    template_counts = db.query(
        models.AccountingOperation.template_type,
        db.func.count(models.AccountingOperation.id)
    )
    
    if start_date:
        template_counts = template_counts.filter(models.AccountingOperation.operation_date >= start_date)
    
    if end_date:
        template_counts = template_counts.filter(models.AccountingOperation.operation_date <= end_date)
    
    template_counts = template_counts.group_by(
        models.AccountingOperation.template_type
    ).all()
    
    template_counts_dict = {template: count for template, count in template_counts}
    
    return {
        "total_operations": total_operations,
        "total_amount": float(total_amount),
        "template_counts": template_counts_dict
    }


@router.get("/export", response_model=dict)
def export_operations(
    db: Session = Depends(deps.get_db),
    # Include the same filters as get_operations
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    document_type: Optional[str] = None,
    debit_account: Optional[str] = None,
    credit_account: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    description_contains: Optional[str] = None,
    template_type: Optional[str] = None,
    file_id: Optional[int] = None,
) -> Any:
    """
    Export accounting operations to CSV/Excel.
    
    This is a placeholder for the export functionality.
    In a real implementation, this would generate and return a file.
    """
    # In a real implementation, this would generate and return a file
    # For now, we'll just return a message
    return {
        "message": "Export functionality will be implemented in a future version.",
        "filter_params": {
            "start_date": start_date,
            "end_date": end_date,
            "document_type": document_type,
            "debit_account": debit_account,
            "credit_account": credit_account,
            "min_amount": min_amount,
            "max_amount": max_amount,
            "description_contains": description_contains,
            "template_type": template_type,
            "file_id": file_id
        }
    }