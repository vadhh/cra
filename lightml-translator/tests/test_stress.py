import pytest
import concurrent.futures
import resource
from app.services.translation_service import TranslationService

@pytest.fixture
def translation_service():
    return TranslationService()

def get_memory_mb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0

def test_stress_sequential_500(translation_service):
    """Simulate 500 sequential translation requests to detect memory leaks and regression."""
    text = "De overeenkomst is bindend en de overmacht treedt in werking."
    
    # Warm up
    translation_service.translate_document(text, "nl", "en")
    
    mem_start = get_memory_mb()
    
    for i in range(500):
        res = translation_service.translate_document(text, "nl", "en")
        assert "agreement" in res.translated_text.lower()
        
    mem_end = get_memory_mb()
    mem_leak = max(0.0, mem_end - mem_start)
    
    print(f"\nSequential 500 test completed.")
    print(f"  Start Memory: {mem_start:.2f} MB")
    print(f"  End Memory:   {mem_end:.2f} MB")
    print(f"  Memory Grow:  {mem_leak:.2f} MB")
    
    # Assert that memory growth is negligible (e.g. less than 15 MB)
    assert mem_leak < 15.0

def test_stress_concurrent_100(translation_service):
    """Simulate 100 concurrent translation requests to check thread safety and concurrency control."""
    text = "De werkgever en de werknemer sluiten een arbeidsovereenkomst."
    
    # Warm up
    translation_service.translate_document(text, "nl", "en")
    
    def worker():
        res = translation_service.translate_document(text, "nl", "en")
        return res.translated_text

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(worker) for _ in range(100)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
    assert len(results) == 100
    for r in results:
        assert "employer" in r.lower() or "contract" in r.lower() or "employee" in r.lower()
