"""
Invoice Data Models
Pydantic models for request/response serialization and validation
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum


class InvoiceFieldType(str, Enum):
    """Enumeration of invoice field types detected by YOLOv5."""
    LOGO = "logo"
    RUC = "R.U.C"
    INVOICE_NUMBER = "numero_factura"
    DATE_TIME = "fecha_hora"
    COMPANY_NAME = "razon_social"
    QUANTITY = "cantidad"
    DESCRIPTION = "descripcion"
    UNIT_PRICE = "precio_unitario"
    TOTAL_PRICE = "precio_total"
    SUBTOTAL = "subtotal"
    IVA = "iva"


class BoundingBox(BaseModel):
    """Bounding box coordinates for detected objects."""
    xmin: float = Field(..., description="Left coordinate")
    ymin: float = Field(..., description="Top coordinate")
    xmax: float = Field(..., description="Right coordinate")
    ymax: float = Field(..., description="Bottom coordinate")
    
    @validator('xmin', 'ymin', 'xmax', 'ymax')
    def validate_coordinates(cls, v):
        if v < 0:
            raise ValueError('Coordinates must be non-negative')
        return v


class DetectionResult(BaseModel):
    """Single detection result from YOLOv5 model."""
    field_type: InvoiceFieldType = Field(..., description="Type of detected field")
    text: str = Field("", description="Extracted text content")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Detection confidence")
    bbox: BoundingBox = Field(..., description="Bounding box coordinates")
    ocr_confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="OCR confidence")


class InvoiceRow(BaseModel):
    """Single row of invoice line items."""
    description: str = Field(..., description="Product/service description")
    quantity: str = Field(..., description="Quantity or amount")
    unit_price: str = Field(..., description="Price per unit")
    total_price: str = Field(..., description="Total price for this item")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Row extraction confidence")
    
    class Config:
        schema_extra = {
            "example": {
                "description": "Servicio de consultoría técnica",
                "quantity": "2",
                "unit_price": "$150.00",
                "total_price": "$300.00",
                "confidence": 0.92
            }
        }


class InvoiceMetadata(BaseModel):
    """Invoice header metadata extracted from the document."""
    ruc: Optional[str] = Field(None, description="RUC number")
    invoice_number: Optional[str] = Field(None, description="Invoice number")
    date: Optional[str] = Field(None, description="Invoice date")
    company_name: Optional[str] = Field(None, description="Company name")
    subtotal: Optional[str] = Field(None, description="Subtotal amount")
    iva: Optional[str] = Field(None, description="IVA/Tax amount")
    total: Optional[str] = Field(None, description="Total amount")
    
    class Config:
        schema_extra = {
            "example": {
                "ruc": "1791354400001",
                "invoice_number": "005-002-000002389",
                "date": "14/02/2020",
                "company_name": "AUDIOAUTO S.A.",
                "subtotal": "$610.00",
                "iva": "$73.20",
                "total": "$683.20"
            }
        }


class ProcessDocumentRequest(BaseModel):
    """Request model for document processing."""
    file_type: str = Field(..., description="File type (pdf, image)")
    enhance_ocr: bool = Field(True, description="Enable OCR enhancement")
    rotation_correction: bool = Field(True, description="Enable rotation correction")
    confidence_threshold: float = Field(0.25, ge=0.1, le=0.9, description="Detection confidence threshold")
    
    class Config:
        schema_extra = {
            "example": {
                "file_type": "pdf",
                "enhance_ocr": True,
                "rotation_correction": True,
                "confidence_threshold": 0.25
            }
        }


class ProcessDocumentResponse(BaseModel):
    """Response model for document processing results."""
    success: bool = Field(..., description="Processing success status")
    message: str = Field(..., description="Processing message")
    metadata: Optional[InvoiceMetadata] = Field(None, description="Invoice metadata")
    line_items: List[InvoiceRow] = Field([], description="Invoice line items")
    detections: List[DetectionResult] = Field([], description="Raw detection results")
    processed_image: Optional[str] = Field(None, description="Base64 encoded processed image")
    processing_time: float = Field(..., description="Processing time in seconds")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Invoice processed successfully",
                "metadata": {
                    "ruc": "1791354400001",
                    "invoice_number": "005-002-000002389",
                    "total": "$683.20"
                },
                "line_items": [
                    {
                        "description": "Servicio técnico",
                        "quantity": "1",
                        "unit_price": "$610.00",
                        "total_price": "$610.00",
                        "confidence": 0.95
                    }
                ],
                "processing_time": 2.34
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response model."""
    success: bool = Field(False, description="Always false for errors")
    error: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    
    class Config:
        schema_extra = {
            "example": {
                "success": False,
                "error": "File format not supported",
                "error_code": "INVALID_FILE_FORMAT",
                "details": {"supported_formats": ["pdf", "png", "jpg", "jpeg"]}
            }
        }