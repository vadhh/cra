# Offline Translation Model Installation Guide

This document describes how to setup, verify, and run the **LightML Translation Service** in a completely offline environment.

---

## 1. Quick Installation (CLI Downloader)

The installation script retrieves the Helsinki-NLP models, packages the tokenizers, and configures files inside the local `models/` directory.

From the root of the project, run:
```bash
python download_models.py
```

### Custom Directory Configuration
To download models to a custom storage path, use the `--models-dir` option:
```bash
python download_models.py --models-dir /path/to/custom/models/
```

---

## 2. Offline Production Setup

For high-security, internet-isolated environments, perform the following steps:

1. **Download Phase (Internet Connected)**:
   Run `python download_models.py` on an internet-connected workstation. This creates the local directory structures under `models/` containing:
   * `opus-mt-id-en/` (Indonesian to English)
   * `opus-mt-fr-en/` (French to English)
   * `opus-mt-nl-en/` (Dutch to English)
   * `opus-mt-mul-en/` (Multilingual fallback)
   * `metadata.json` (Registry index)
   * `license_report.md` (Licensing verification)

2. **Transfer Phase**:
   Tar the model files and move them to the secure offline environment:
   ```bash
   tar -czvf lightml_models.tar.gz models/
   ```
   Unpack the tarball inside the offline `lightml-translator/` directory.

3. **Runtime Configuration**:
   The service requires `LIGHTML_MODELS_DIR` environment variable to point to the unpacked `models/` folder:
   ```bash
   export LIGHTML_MODELS_DIR=/app/models
   ```
   At runtime, `local_files_only=True` is forced to ensure **zero network requests** are made. If model folders are missing, the service falls back to multilingual or returns source texts gracefully without throwing runtime crashes.

---

## 3. Verification Process

After the download finishes, the downloader performs two levels of checks:

1. **SHA256 Checksum Validation**:
   The calculated SHA256 of the model weight file (`pytorch_model.bin`) is checked against Hugging Face LFS metadata. The results are stored in `models/metadata.json`.

2. **License Clearance**:
   The downloader compiles a licensing table inside `license_report.md` detailing:
   * CC-BY-4.0 license confirmation
   * Commercial permission rights
   * Resource URLs
   * Download timestamps

---

## 4. Troubleshooting

| Symptom | Cause | Resolution |
| :--- | :--- | :--- |
| `local_files_only=True` raised `OSError` | Model files are incomplete or path is incorrect. | Ensure `LIGHTML_MODELS_DIR` points to the correct directory containing the model subfolders. |
| `HuggingFace Hub connection timeout` | The downloader requires internet access. | Ensure you are on an active connection. For offline environments, download on a connected machine first, then copy the folder over. |
| `Out of Memory (OOM)` | High CPU/GPU usage when loading models simultaneously. | Increase process RAM. MarianMT models load lazily and are cached in memory (approx. 300MB per language pair). |
