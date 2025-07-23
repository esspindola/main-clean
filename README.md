# OCR Invoice Processing Backend 2.0

Professional-grade invoice OCR system with YOLOv5 custom model and multi-OCR engines for maximum precision.

## 🚀 Features

### AI-Powered Invoice Processing
- **YOLOv5 Custom Model**: Trained specifically for invoice field detection (18 classes)
- **Multi-OCR Engines**: Tesseract, EasyOCR, and CRAFT for maximum text extraction accuracy
- **Intelligent Rotation Correction**: Automatic detection and correction of document orientation
- **Advanced Table Detection**: Structural analysis of invoice tables and line items

### Professional Architecture
- **RESTful API**: Clean, well-documented endpoints with Swagger UI
- **Docker Support**: Complete containerization with multi-stage builds
- **Production Ready**: Gunicorn, Nginx, Redis integration
- **Comprehensive Logging**: Structured logging with rotation
- **Health Monitoring**: Health checks and system metrics

### Supported Formats
- **Images**: PNG, JPG, JPEG, TIFF, BMP
- **PDF**: Multi-page PDF processing with high DPI conversion
- **Languages**: Spanish and English OCR support

## 🏗️ Architecture

```
backend-ocr/
├── app/
│   ├── api/v1/           # REST API endpoints
│   ├── core/             # Core components (config, ML models)
│   ├── models/           # Pydantic data models
│   ├── services/         # Business logic services
│   └── utils/            # Utility functions
├── models/               # YOLOv5 trained models
├── uploads/              # File upload storage
├── logs/                 # Application logs
└── docker-compose.yml    # Complete deployment stack
```

## 🔧 Quick Start

### Option 1: Docker Deployment (Recommended)

```bash
# Build and start all services
docker-compose up --build

# The API will be available at:
# - Backend: http://localhost:8001
# - Swagger UI: http://localhost:8001/docs/
# - Nginx: http://localhost:8080
```

### Option 2: Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export FLASK_ENV=development
export TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata

# Run the application
python run.py
```

## 📡 API Endpoints

### Invoice Processing
```http
POST /api/v1/invoice/process
Content-Type: multipart/form-data

# Parameters:
# - file: Invoice file (PDF or image)
# - enhance_ocr: Enable OCR enhancement (default: true)
# - rotation_correction: Enable rotation correction (default: true)
# - confidence_threshold: Detection threshold (default: 0.25)
```

### Health Monitoring
```http
GET /api/v1/health              # Basic health check
GET /api/v1/health/detailed     # Detailed system status
GET /api/v1/health/ready        # Readiness probe
GET /api/v1/health/live         # Liveness probe
```

### Order Management
```http
GET /api/v1/orders              # List all orders
POST /api/v1/orders/archive     # Archive processed invoice
GET /api/v1/orders/{id}         # Get specific order
GET /api/v1/orders/stats        # Order statistics
```

## 🔍 API Response Format

```json
{
  "success": true,
  "message": "Invoice processed successfully",
  "metadata": {
    "ruc": "1791354400001",
    "invoice_number": "005-002-000002389",
    "date": "14/02/2020",
    "company_name": "AUDIOAUTO S.A.",
    "subtotal": "$610.00",
    "iva": "$73.20",
    "total": "$683.20"
  },
  "line_items": [
    {
      "description": "SUSTITUCION SISTEMA CR",
      "quantity": "1",
      "unit_price": "$610.00",
      "total_price": "$610.00",
      "confidence": 0.95
    }
  ],
  "processing_time": 2.34
}
```

## 🎯 YOLOv5 Detected Classes

The custom trained model detects 18 specific invoice fields:

1. **logo** - Company logo
2. **R.U.C** - Tax identification number
3. **numero_factura** - Invoice number
4. **fecha_hora** - Date and time
5. **razon_social** - Company name
6. **cantidad** - Quantity
7. **descripcion** - Description
8. **precio_unitario** - Unit price
9. **precio_total** - Total price
10. **subtotal** - Subtotal
11. **iva** - Tax (IVA)
12. **Descripcion** - Alternative description
13. **Cantidad** - Alternative quantity
14. **unidades** - Units
15. **unidad** - Unit
16. **Cajas_cantidad** - Box quantity
17. **Articulo** - Article
18. **Nombre_del_producto** - Product name

## ⚙️ Configuration

### Environment Variables

```bash
# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False
HOST=0.0.0.0
PORT=5000

# OCR Configuration
TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata
TESSERACT_CMD=tesseract

# Model Configuration
MODEL_PATH=models/best.pt
YOLO_CONFIDENCE_THRESHOLD=0.25

# File Upload
MAX_CONTENT_LENGTH=52428800  # 50MB
UPLOAD_FOLDER=uploads

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/ocr_backend.log
```

### Docker Environment

```yaml
# docker-compose.yml
services:
  ocr-backend:
    ports:
      - "8001:5000"  # External port 8001
    environment:
      - FLASK_ENV=production
      - TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata
```

## 🔄 Model Training

Your custom YOLOv5 model is located at:
```
yolov5/runs/train/exp_retrain/weights/best.pt
```

To retrain or fine-tune:
```bash
cd yolov5
python train.py --data ../datasets/data.yaml --cfg yolov5s.yaml --weights yolo5s.pt --epochs 100
```

## 🔧 Performance Optimization

### OCR Optimization
- **Multi-engine Processing**: Combines Tesseract + EasyOCR results
- **Image Enhancement**: Automatic contrast, noise reduction, sharpening
- **Resolution Upscaling**: Enhances low-DPI images to 300 DPI
- **Rotation Correction**: Detects and corrects 0°, 90°, 180°, 270° rotations

### System Optimization
- **Multi-stage Docker**: Optimized container size
- **Gunicorn Workers**: Configured for optimal throughput
- **Redis Caching**: Optional caching layer
- **Nginx Reverse Proxy**: Load balancing and static file serving

## 📊 Monitoring

### Health Checks
```bash
# Basic health
curl http://localhost:8001/api/v1/health

# Detailed system status
curl http://localhost:8001/api/v1/health/detailed

# Docker health check
docker-compose ps
```

### Logs
```bash
# View application logs
docker-compose logs -f ocr-backend

# View all service logs
docker-compose logs -f
```

## 🚀 Production Deployment

### 1. Using Docker Compose (Recommended)
```bash
# Production deployment
docker-compose -f docker-compose.yml up -d

# Scale backend service
docker-compose up -d --scale ocr-backend=3
```

### 2. Manual Deployment
```bash
# Install system dependencies
apt-get update && apt-get install -y tesseract-ocr tesseract-ocr-spa poppler-utils

# Install Python dependencies
pip install -r requirements.txt

# Run with Gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 2 --threads 4 --timeout 300 main:app
```

## 🔒 Security Features

- **File Validation**: Magic number verification and size limits
- **Secure Uploads**: Sanitized filenames and temporary storage
- **CORS Protection**: Configurable origin restrictions
- **Input Validation**: Comprehensive parameter validation
- **Error Handling**: Secure error messages without information leakage

## 📈 API Testing

### Using cURL
```bash
# Test invoice processing
curl -X POST http://localhost:8001/api/v1/invoice/process \
  -F "file=@invoice.pdf" \
  -F "enhance_ocr=true" \
  -F "confidence_threshold=0.25"

# Test health endpoint
curl http://localhost:8001/api/v1/health/detailed
```

### Using Swagger UI
Open http://localhost:8001/docs/ in your browser for interactive API testing.

## 🛠️ Troubleshooting

### Common Issues

1. **Model not found**
   ```bash
   # Check if model exists
   ls -la models/best.pt
   # Use fallback model if needed
   ```

2. **OCR not working**
   ```bash
   # Verify Tesseract installation
   tesseract --version
   # Check language data
   ls $TESSDATA_PREFIX
   ```

3. **Docker build fails**
   ```bash
   # Clean Docker cache
   docker system prune -a
   # Rebuild without cache
   docker-compose build --no-cache
   ```

### Performance Issues
- Increase Docker memory allocation (minimum 4GB recommended)
- Monitor disk space for uploads and logs
- Check OCR engine performance with different image types

## 📄 License

MIT License - See LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For issues and questions:
- Check the troubleshooting section
- Review application logs
- Test with the Swagger UI interface
- Verify Docker container health

---

**Professional OCR Backend v2.0** - Built with ❤️ for maximum invoice processing accuracy.