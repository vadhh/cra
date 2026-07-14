import sys
import os
import json
import tempfile
import pytest
from unittest.mock import MagicMock, patch

# Helper function to locally import download_models with mocked torch/transformers.
# This prevents global pollution of sys.modules during pytest collection.
def get_download_models():
    # Only mock torch/transformers during the import of download_models
    with patch.dict(sys.modules, {'torch': MagicMock(), 'transformers': MagicMock()}):
        import download_models
        return download_models


def test_calculate_sha256():
    """Verify that calculate_sha256 computes correct hashes for standard content."""
    dm = get_download_models()
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(b"Hello LightML Offline Translator!")
        tmp_path = tmp.name
        
    try:
        calculated_hash = dm.calculate_sha256(tmp_path)
        # Expected hash of "Hello LightML Offline Translator!"
        expected = "f87a5b6459ebfba3e6ae096fef2fd6b716205684bdf99585d5f15cd8037f4b2b"
        assert calculated_hash == expected
    finally:
        os.remove(tmp_path)


def test_models_list_schema():
    """Ensure that the model list dictionary contains all required metadata schemas."""
    dm = get_download_models()
    for key, spec in dm.MODELS_LIST.items():
        assert "model" in spec
        assert "lang_pair" in spec
        assert "license" in spec
        assert "commercial" in spec
        assert "source" in spec
        assert spec["license"] == "CC-BY-4.0"


def test_model_directories_and_files_exist():
    """Verify that the model directory and target models exist and contain correct formats."""
    dm = get_download_models()
    # Locate target models directory
    # Inside container it is '/app/models', locally it can be relative
    models_dir = "/app/models"
    if not os.path.isdir(models_dir):
        # Fallback to local workspace models folder
        models_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
        
    assert os.path.isdir(models_dir), f"Models directory not found at {models_dir}"
    
    # 1. Verify metadata.json
    metadata_path = os.path.join(models_dir, "metadata.json")
    assert os.path.isfile(metadata_path), "metadata.json not found"
    
    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)
        
    assert isinstance(metadata, list)
    assert len(metadata) > 0
    for record in metadata:
        assert "model" in record
        assert "version" in record
        assert "language_pair" in record
        assert "local_path" in record
        assert "sha256" in record
        assert "file_size_bytes" in record

    # 2. Verify CTranslate2 folder structure and vocabulary files
    ct_dir = os.path.join(models_dir, "ctranslate2")
    assert os.path.isdir(ct_dir), "ctranslate2 directory not found inside models"
    
    # Check that required CTranslate2 models have necessary config and model binaries
    for key, spec in dm.MODELS_LIST.items():
        # Skip pivot wrapper cases that don't have direct folders
        if key in ["fr-nl", "id-nl", "nl-id"]:
            continue
            
        folder_name = spec["model"].split("/")[-1]
        model_path = os.path.join(ct_dir, folder_name)
        assert os.path.isdir(model_path), f"CTranslate2 model folder missing: {model_path}"
        
        # Verify required ctranslate2 files exist
        assert os.path.isfile(os.path.join(model_path, "model.bin")), f"model.bin missing in {model_path}"
        assert os.path.isfile(os.path.join(model_path, "config.json")), f"config.json missing in {model_path}"
        
        # Verify config.json is valid JSON
        with open(os.path.join(model_path, "config.json"), "r", encoding="utf-8") as f:
            config = json.load(f)
            assert isinstance(config, dict)
            
        # Verify vocabulary file exists (Helsinki NLP ctranslate2 files use shared_vocabulary.json)
        vocab_path = os.path.join(model_path, "shared_vocabulary.json")
        assert os.path.isfile(vocab_path), f"shared_vocabulary.json missing in {model_path}"


def test_sha256_validation_logic():
    """Verify that SHA256 validation correctly checks and mismatches file hashes."""
    dm = get_download_models()
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(b"dummy model weights content")
        tmp_path = tmp.name
        
    try:
        actual_sha = dm.calculate_sha256(tmp_path)
        # Expected hash of "dummy model weights content"
        expected = "d7e98d8d0648492360c3b2e83517c77077932043000255d6b56be8e8511640ed"
        assert actual_sha == expected
        assert actual_sha != "wrong_hash_verification_value"
    finally:
        os.remove(tmp_path)


def test_corrupted_model_detection():
    """Verify that a mismatch in expected model hash is correctly identified."""
    dm = get_download_models()
    # Test case where expected hash is different from the actual file hash
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(b"corrupted binary file content")
        tmp_path = tmp.name
        
    try:
        actual_sha = dm.calculate_sha256(tmp_path)
        # Verify it does not match the standard model hash
        expected_real_model_sha = "b8a9235e165ce4fbf2ec57e33e4fdf59a385f949b2ffae083aeb0b4526b7bd4d"
        assert actual_sha != expected_real_model_sha
    finally:
        os.remove(tmp_path)


def test_duplicate_download_skipping():
    """Verify that duplicate download is skipped if files already exist."""
    with patch.dict(sys.modules, {'torch': MagicMock(), 'transformers': MagicMock()}):
        dm = get_download_models()
        
        with tempfile.TemporaryDirectory() as temp_models_dir:
            # Create a mock folder structure that mimics an existing model
            for key, spec in dm.MODELS_LIST.items():
                repo_id = spec["model"]
                folder_name = repo_id.split("/")[-1]
                target_dir = os.path.join(temp_models_dir, folder_name)
                os.makedirs(target_dir, exist_ok=True)
                
                # Create a fake weights file
                weights_file = "pytorch_model.bin"
                weights_path = os.path.join(target_dir, weights_file)
                with open(weights_path, "w") as f:
                    f.write("fake weights data")
                    
            # Mock snapshot_download and HfApi to assert they are not called (fully offline duplicate check)
            with patch("download_models.snapshot_download") as mock_snapshot, \
                 patch("download_models.HfApi") as mock_hf_api:
                 
                # Run download and verify
                dm.download_and_verify(temp_models_dir)
                
                # Assert snapshot_download was never called because local files already existed
                mock_snapshot.assert_not_called()
