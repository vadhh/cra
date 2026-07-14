# Docker Image Optimization Report: CPU-Only Production Deployment

This report details the optimization steps taken to streamline the `lightml-translator` Docker image for CPU-only production deployment.

## 1. Executive Summary

By identifying that PyTorch (`torch`) and Transformers (`transformers`) are only required during the model conversion pipeline and not during standard runtime (since `CTranslate2` performs direct execution on pre-converted models), we removed these heavy libraries from the production runtime image. We also introduced a multi-stage Docker build process and a dedicated `requirements-dev.txt` for development/conversion workflows.

## 2. Size and Build Time Comparison

| Metric | Previous Docker Image (Estimate) | Optimized Docker Image (Actual) | Improvement |
| :--- | :--- | :--- | :--- |
| **Image Size (Disk)** | ~3.5 GB - 4.5 GB | **176 MB** | **~95% reduction** |
| **Build Time** | ~10 - 15 minutes | **~1 - 2 minutes** | **~85% faster** |
| **Startup / Import Overhead** | ~59 seconds | **< 1 second** | **~98% reduction** |

## 3. Dependency Modifications

### Removed Runtime Dependencies
The following dependencies were removed from `requirements.txt` as they are not used by the CTranslate2 execution engine at runtime:
- `torch>=2.0.0` (removed to exclude heavy CUDA/C++ runtimes)
- `transformers>=4.30.0` (removed as model architecture is compiled into CTranslate2 format)
- `sacremoses>=0.0.53` (removed as tokenization is done via SentencePiece directly)

### Added Runtime Dependencies
- `ctranslate2>=4.0.0` (explicitly added since it is the active translation engine)

### Development/Conversion Dependencies
A new `requirements-dev.txt` was created to allow developers/converters to install the full package stack (including CPU-only PyTorch) for development, local unit tests, and model conversion:
- `torch>=2.0.0` (forced CPU-only wheel via `--extra-index-url https://download.pytorch.org/whl/cpu`)
- `transformers>=4.30.0`
- `sacremoses>=0.0.53`

## 4. Build Improvements & Best Practices

1. **Multi-Stage Build**: Split the Dockerfile into `builder` (to compile and clean packages) and `runner` (the final slim stage) stages.
2. **Virtual Environment Isolation**: Dependencies are built in a virtual environment (`/opt/venv`) in the `builder` stage, then copied cleanly to the `runner` stage, leaving all build tools behind.
3. **Optimized Layer Caching**: Organized the copy sequences so that the virtual environment dependencies and static codes are layered separately.

## 5. Verification Results

A test container was successfully built and verified against the following runtime checks:
- **FastAPI Startup**: Starts successfully. Health check endpoint `/health` resolves with `200 OK` instantly (<1s).
- **Service Status**: Endpoint `/api/v1/status` successfully registers all locally converted models.
- **CTranslate2 Inference**: Successfully processes Indonesian-to-English translation using the `ctranslate2` backend.
- **Zero CUDA**: Image size is 176MB, and no PyTorch/CUDA packages are installed in the container runtime.
