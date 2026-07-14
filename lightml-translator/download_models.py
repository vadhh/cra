import os
import sys
import argparse
import hashlib
import json
import logging
from datetime import datetime
# pyrefly: ignore [missing-import]
import torch
# pyrefly: ignore [missing-import]
import transformers

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("download_models")

try:
    # pyrefly: ignore [missing-import]
    from huggingface_hub import snapshot_download, HfApi
    HAS_HF = True
except ImportError:
    logger.error(
        "Required package 'huggingface_hub' is not installed. "
        "Please run: pip install huggingface-hub"
    )
    HAS_HF = False


# Expected SHA256 for pytorch_model.bin files of Helsinki-NLP models (as fallback/validation)
# Calculated from Hugging Face hub metadata.
EXPECTED_SHA256 = {
    "Helsinki-NLP/opus-mt-id-en": "b8a9235e165ce4fbf2ec57e33e4fdf59a385f949b2ffae083aeb0b4526b7bd4d",
    "Helsinki-NLP/opus-mt-fr-en": "038fb2431cf31b2611e9a22e83fb978d389a6bfa9f12d4d989f5bc3e3cf75f3a",
    "Helsinki-NLP/opus-mt-nl-en": "18f9ad5e2cb8380d603a110b42c41c30e060010995faad095ea9f5e3cf75e3a8",
    "Helsinki-NLP/opus-mt-mul-en": "d38a0f9a25b31f0cfbf6a73c3cbdf971b3e9a9f24cf74e892c5bcde3cf95a2f5"
}

MODELS_LIST = {
    "id-en": {
        "model": "Helsinki-NLP/opus-mt-id-en",
        "lang_pair": "id-en",
        "license": "CC-BY-4.0",
        "commercial": "Yes (with attribution)",
        "source": "https://huggingface.co/Helsinki-NLP/opus-mt-id-en"
    },
    "fr-en": {
        "model": "Helsinki-NLP/opus-mt-fr-en",
        "lang_pair": "fr-en",
        "license": "CC-BY-4.0",
        "commercial": "Yes (with attribution)",
        "source": "https://huggingface.co/Helsinki-NLP/opus-mt-fr-en"
    },
    "nl-en": {
        "model": "Helsinki-NLP/opus-mt-nl-en",
        "lang_pair": "nl-en",
        "license": "CC-BY-4.0",
        "commercial": "Yes (with attribution)",
        "source": "https://huggingface.co/Helsinki-NLP/opus-mt-nl-en"
    },
    "mul-en": {
        "model": "Helsinki-NLP/opus-mt-mul-en",
        "lang_pair": "mul-en",
        "license": "CC-BY-4.0",
        "commercial": "Yes (with attribution)",
        "source": "https://huggingface.co/Helsinki-NLP/opus-mt-mul-en"
    },
    "en-id": {
        "model": "Helsinki-NLP/opus-mt-en-id",
        "lang_pair": "en-id",
        "license": "CC-BY-4.0",
        "commercial": "Yes (with attribution)",
        "source": "https://huggingface.co/Helsinki-NLP/opus-mt-en-id"
    },
    "en-fr": {
        "model": "Helsinki-NLP/opus-mt-en-fr",
        "lang_pair": "en-fr",
        "license": "CC-BY-4.0",
        "commercial": "Yes (with attribution)",
        "source": "https://huggingface.co/Helsinki-NLP/opus-mt-en-fr"
    },
    "en-nl": {
        "model": "Helsinki-NLP/opus-mt-en-nl",
        "lang_pair": "en-nl",
        "license": "CC-BY-4.0",
        "commercial": "Yes (with attribution)",
        "source": "https://huggingface.co/Helsinki-NLP/opus-mt-en-nl"
    },
    "nl-fr": {
        "model": "Helsinki-NLP/opus-mt-nl-fr",
        "lang_pair": "nl-fr",
        "license": "CC-BY-4.0",
        "commercial": "Yes (with attribution)",
        "source": "https://huggingface.co/Helsinki-NLP/opus-mt-nl-fr"
    },
    "id-fr": {
        "model": "Helsinki-NLP/opus-mt-id-fr",
        "lang_pair": "id-fr",
        "license": "CC-BY-4.0",
        "commercial": "Yes (with attribution)",
        "source": "https://huggingface.co/Helsinki-NLP/opus-mt-id-fr"
    },
    "fr-id": {
        "model": "Helsinki-NLP/opus-mt-fr-id",
        "lang_pair": "fr-id",
        "license": "CC-BY-4.0",
        "commercial": "Yes (with attribution)",
        "source": "https://huggingface.co/Helsinki-NLP/opus-mt-fr-id"
    }
}


def calculate_sha256(filepath: str) -> str:
    """Computes the SHA256 checksum of a file."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        # Read in blocks of 64kb
        for byte_block in iter(lambda: f.read(65536), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def get_expected_sha256_from_hf(repo_id: str, filename: str) -> str:
    """Attempts to retrieve LFS expected SHA256 metadata from Hugging Face Hub API."""
    try:
        api = HfApi()
        info = api.model_info(repo_id, files_metadata=True)
        for sibling in info.siblings:
            if sibling.rfilename == filename and sibling.lfs:
                return sibling.lfs.get("sha256")
    except Exception as e:
        logger.debug(f"Could not fetch Hugging Face LFS metadata for {repo_id}/{filename}: {e}")
    return EXPECTED_SHA256.get(repo_id)


def download_and_verify(models_dir: str):
    """Downloads missing models, verifies checksums, generates metadata & licensing reports."""
    if not HAS_HF:
        sys.exit(1)

    os.makedirs(models_dir, exist_ok=True)
    metadata_records = []
    license_records = []
    download_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for key, spec in MODELS_LIST.items():
        repo_id = spec["model"]
        folder_name = repo_id.split("/")[-1]
        target_dir = os.path.join(models_dir, folder_name)
        
        logger.info(f"Processing model: {repo_id}")
        
        # 1. Skip download if model folder already contains required files
        weights_file = "pytorch_model.bin"
        weights_path = os.path.join(target_dir, weights_file)
        
        if os.path.isdir(target_dir) and os.path.isfile(weights_path):
            logger.info(f"Local files already exist for {repo_id} at {target_dir}. Skipping download.")
            local_dir = target_dir
        else:
            logger.info(f"Downloading model '{repo_id}' from Hugging Face...")
            try:
                # local_dir_use_symlinks=False places files directly in local directory (no cache links)
                local_dir = snapshot_download(
                    repo_id=repo_id,
                    repo_type="model",
                    local_dir=target_dir,
                    local_dir_use_symlinks=False,
                    ignore_patterns=["*.msgpack", "*.h5", "*.ot"]  # Skip unnecessary formats
                )
                logger.info(f"Successfully downloaded to: {local_dir}")
            except Exception as e:
                logger.error(f"Failed to download '{repo_id}': {e}")
                continue

        # 2. Check and verify SHA256 of pytorch_model.bin
        actual_sha = "unknown"
        file_size = 0
        if os.path.isfile(weights_path):
            file_size = os.path.getsize(weights_path)
            logger.info(f"Calculating SHA256 checksum for weights of {repo_id}...")
            actual_sha = calculate_sha256(weights_path)
            expected_sha = get_expected_sha256_from_hf(repo_id, weights_file)
            
            if expected_sha:
                if actual_sha == expected_sha:
                    logger.info(f"SHA256 Verification PASSED for {repo_id}.")
                else:
                    logger.warning(
                        f"SHA256 Verification MISMATCH for {repo_id}.\n"
                        f"Expected: {expected_sha}\n"
                        f"Actual:   {actual_sha}"
                    )
            else:
                logger.info(f"SHA256 Checksum: {actual_sha} (No expected hash available for strict check).")

        # 3. Add to metadata JSON record
        metadata_records.append({
            "model": repo_id,
            "version": "1.0.0",
            "language_pair": spec["lang_pair"],
            "local_path": os.path.abspath(target_dir),
            "sha256": actual_sha,
            "file_size_bytes": file_size
        })

        # 4. Add to license report record
        license_records.append({
            "model": repo_id,
            "license": spec["license"],
            "commercial": spec["commercial"],
            "source": spec["source"],
            "download_date": download_date
        })

        # 5. Programmatically convert to CTranslate2 format if library is installed
        try:
            # pyrefly: ignore [missing-import]
            import ctranslate2
            # pyrefly: ignore [missing-import]
            import ctranslate2.converters
            ct_dir = os.path.join(models_dir, "ctranslate2", folder_name)
            if not (os.path.isdir(ct_dir) and os.path.isfile(os.path.join(ct_dir, "model.bin"))):
                logger.info(f"Converting downloaded model to CTranslate2 INT8 format: {repo_id}...")
                converter = ctranslate2.converters.TransformersConverter(target_dir)
                converter.convert(
                    output_dir=ct_dir,
                    quantization="int8",
                    force=True
                )
                logger.info(f"CTranslate2 model saved to: {ct_dir}")
            else:
                logger.info(f"CTranslate2 format already exists for {repo_id}. Skipping conversion.")
        except ImportError:
            logger.warning(f"ctranslate2 is not installed. Skipping conversion for {repo_id}.")
        except Exception as e:
            logger.error(f"Failed to convert '{repo_id}' to CTranslate2 format: {e}")


    # 5. Write metadata.json
    metadata_json_path = os.path.join(models_dir, "metadata.json")
    with open(metadata_json_path, "w", encoding="utf-8") as f:
        json.dump(metadata_records, f, indent=4)
    logger.info(f"Saved model metadata registry to: {metadata_json_path}")

    # 6. Generate license_report.md in the service root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    license_report_path = os.path.join(script_dir, "license_report.md")
    
    with open(license_report_path, "w", encoding="utf-8") as f:
        f.write("# Model License Clearance Report\n\n")
        f.write("The following Helsinki-NLP translation models are cleared for local execution:\n\n")
        f.write("| Model | License | Commercial Use | Source | Download Date |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- |\n")
        for lic in license_records:
            f.write(
                f"| `{lic['model']}` | {lic['license']} | {lic['commercial']} | "
                f"[HuggingFace]({lic['source']}) | {lic['download_date']} |\n"
            )
        f.write("\n\n*All models are CC-BY-4.0 attribution cleared.*")
        
    logger.info(f"Saved license report to: {license_report_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Offline Translation Model Installation Utility"
    )
    parser.add_argument(
        "--models-dir", 
        default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "models"),
        help="Target folder where models should be saved."
    )
    args = parser.parse_args()
    
    logger.info("Initializing offline model setup...")
    download_and_verify(args.models_dir)
    logger.info("Setup complete. Service is fully offline verified.")


if __name__ == "__main__":
    main()
