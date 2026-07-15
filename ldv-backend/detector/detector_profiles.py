"""
detector_profiles.py — Contract Profile Foundation (Sprint 1).

Implements independent JSON schema validation, profiles registry loading,
and in-memory profile management.
"""
from __future__ import annotations

import os
import json
import logging
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

_DIR = os.path.dirname(os.path.abspath(__file__))
_SCHEMA_PATH = os.path.join(_DIR, "contract_profile.schema.json")
_REGISTRY_PATH = os.path.join(_DIR, "profiles", "profiles.json")
_ALIAS_INDEX_CACHE: Optional[Dict[str, str]] = None
_NAME_INDEX_CACHE: Optional[Dict[str, str]] = None
_RULES_PATH = os.path.join(_DIR, "profiles", "rules_classification.json")


class ProfileValidationError(ValueError):
    """Raised when a contract profile does not conform to the schema or registry constraints."""
    pass


def validate_profile(profile: Dict[str, Any], rules_dict: Optional[Dict[str, Any]] = None) -> None:
    """Validate profile dictionary against structural rules derived from JSON schema."""
    # 1. Root Required Keys
    required_root = [
        "profile_id", "version", "validation_status", "review_date",
        "metadata", "coverage", "classification", "required_clauses"
      ]
    for key in required_root:
        if key not in profile:
            raise ProfileValidationError(f"Missing required root key: '{key}'")

    # 2. Type validations for root keys
    if not isinstance(profile["profile_id"], str) or not profile["profile_id"].strip():
        raise ProfileValidationError("profile_id must be a non-empty string")
    if not isinstance(profile["version"], str) or not re.match(r"^\d+\.\d+\.\d+$", profile["version"]):
        raise ProfileValidationError("version must follow semantic versioning format (e.g. X.Y.Z)")
    if not isinstance(profile["validation_status"], str):
        raise ProfileValidationError("validation_status must be a string")
    
    valid_states = {"validated", "beta", "preparation", "archived", "custom", "stable"}
    if profile["validation_status"].strip().lower() not in valid_states:
        raise ProfileValidationError(f"validation_status '{profile['validation_status']}' must be one of: Validated, Beta, Preparation, Archived, Custom")

    if not isinstance(profile["review_date"], str) or not re.match(r"^\d{4}-\d{2}-\d{2}$", profile["review_date"]):
        raise ProfileValidationError("review_date must follow ISO date format YYYY-MM-DD")
    if not isinstance(profile["metadata"], dict):
        raise ProfileValidationError("metadata must be a dictionary")
    if not isinstance(profile["coverage"], dict):
        raise ProfileValidationError("coverage must be a dictionary")
    if not isinstance(profile["classification"], dict):
        raise ProfileValidationError("classification must be a dictionary")
    if not isinstance(profile["required_clauses"], list):
        raise ProfileValidationError("required_clauses must be a list")

    # 3. Metadata validation
    meta = profile["metadata"]
    for k in ["display_name", "family"]:
        if k not in meta or not isinstance(meta[k], str) or not meta[k].strip():
            raise ProfileValidationError(f"metadata.{k} must be a non-empty string")
    if "aliases" in meta:
        if not isinstance(meta["aliases"], list) or not all(isinstance(a, str) for a in meta["aliases"]):
            raise ProfileValidationError("metadata.aliases must be a list of strings")
    if "release_stage" in meta:
        rs = meta["release_stage"]
        if not isinstance(rs, str) or rs.strip().lower() not in ["alpha", "beta", "stable", "ga"]:
            raise ProfileValidationError("metadata.release_stage must be one of: alpha, beta, stable, ga")

    # 4. Coverage validation
    cov = profile["coverage"]
    for k in ["languages", "jurisdictions"]:
        if k not in cov or not isinstance(cov[k], list):
            raise ProfileValidationError(f"coverage.{k} must be a list")
            
    allowed_langs = {"en", "id", "fr", "nl", "de", "generic", "test"}
    for lang in cov["languages"]:
        if not isinstance(lang, str) or lang.strip().lower() not in allowed_langs:
            raise ProfileValidationError(f"Invalid language '{lang}' in coverage.languages")
            
    allowed_jurisdictions = {"indonesia", "united states", "netherlands", "france", "england & wales", "belgium", "global", "united kingdom", "generic", "test"}
    for jur in cov["jurisdictions"]:
        if not isinstance(jur, str) or jur.strip().lower() not in allowed_jurisdictions:
            raise ProfileValidationError(f"Invalid jurisdiction '{jur}' in coverage.jurisdictions")

    # 5. Classification validation
    cls_block = profile["classification"]
    if "nli_hypothesis" not in cls_block or not isinstance(cls_block["nli_hypothesis"], str) or not cls_block["nli_hypothesis"].strip():
        raise ProfileValidationError("classification.nli_hypothesis must be a non-empty string")
    if "keyword_overrides" in cls_block:
        ko = cls_block["keyword_overrides"]
        if not isinstance(ko, dict):
            raise ProfileValidationError("classification.keyword_overrides must be a dictionary")
        for lang, words in ko.items():
            if not isinstance(words, list) or not all(isinstance(w, str) for w in words):
                raise ProfileValidationError(f"classification.keyword_overrides.{lang} must be a list of strings")

    # 6. Required clauses validation
    for idx, c in enumerate(profile["required_clauses"]):
        if not isinstance(c, dict) or "clause_id" not in c or not isinstance(c["clause_id"], str) or not c["clause_id"].strip():
            raise ProfileValidationError(f"required_clauses[{idx}] must be a dict with a non-empty 'clause_id'")
        
        cid = c["clause_id"]
        if rules_dict and cid not in rules_dict:
            raise ProfileValidationError(f"required_clauses[{idx}].clause_id '{cid}' is not a recognized rule in classification layer")

        if "severity_override" in c and not isinstance(c["severity_override"], str):
            raise ProfileValidationError(f"required_clauses[{idx}].severity_override must be a string")
        if "custom_report_wording" in c:
            if not isinstance(c["custom_report_wording"], dict):
                raise ProfileValidationError(f"required_clauses[{idx}].custom_report_wording must be a dict")

    # 7. Recommended clauses validation
    if "recommended_clauses" in profile:
        if not isinstance(profile["recommended_clauses"], list):
            raise ProfileValidationError("recommended_clauses must be a list")
        for idx, c in enumerate(profile["recommended_clauses"]):
            if not isinstance(c, dict) or "clause_id" not in c or not isinstance(c["clause_id"], str) or not c["clause_id"].strip():
                raise ProfileValidationError(f"recommended_clauses[{idx}] must be a dict with a non-empty 'clause_id'")
            
            cid = c["clause_id"]
            if rules_dict and cid not in rules_dict:
                raise ProfileValidationError(f"recommended_clauses[{idx}].clause_id '{cid}' is not a recognized rule in classification layer")

            if "custom_report_wording" in c and not isinstance(c["custom_report_wording"], dict):
                raise ProfileValidationError(f"recommended_clauses[{idx}].custom_report_wording must be a dict")

    # 8. Risky clauses lists (dangerous, abusive, leonine)
    for category in ["dangerous_clauses", "abusive_clauses", "leonine_clauses"]:
        if category in profile:
            if not isinstance(profile[category], list):
                raise ProfileValidationError(f"{category} must be a list")
            for idx, c in enumerate(profile[category]):
                if not isinstance(c, dict) or "clause_id" not in c or not isinstance(c["clause_id"], str):
                    raise ProfileValidationError(f"{category}[{idx}] must be a dict with a 'clause_id'")
                
                cid = c["clause_id"]
                if rules_dict and cid not in rules_dict:
                    raise ProfileValidationError(f"{category}[{idx}].clause_id '{cid}' is not a recognized rule in classification layer")

    # 9. Legal references validation
    if "legal_references" in profile:
        if not isinstance(profile["legal_references"], list):
            raise ProfileValidationError("legal_references must be a list")
        for idx, ref in enumerate(profile["legal_references"]):
            if not isinstance(ref, dict):
                raise ProfileValidationError(f"legal_references[{idx}] must be a dictionary")
            for k in ["finding_id", "jurisdiction", "article"]:
                if k not in ref or not isinstance(ref[k], str) or not ref[k].strip():
                    raise ProfileValidationError(f"legal_references[{idx}].{k} must be a non-empty string")

    # 10. Scoring block validation
    if "scoring" in profile:
        so = profile["scoring"]
        if not isinstance(so, dict):
            raise ProfileValidationError("scoring must be a dictionary")
        
        # weights
        if "weights" in so:
            w = so["weights"]
            if not isinstance(w, dict):
                raise ProfileValidationError("scoring.weights must be a dictionary")
            for key, val in w.items():
                if key not in ["missing_required_fallback", "red_flag_high", "red_flag_medium", "l2_unique", "no_governing_law", "no_venue"]:
                    raise ProfileValidationError(f"scoring.weights contains unrecognized weight key '{key}'")
                if not isinstance(val, int):
                    raise ProfileValidationError(f"scoring.weights.{key} must be an integer")
                    
        # missing_clause_weights, dangerous_clause_weights, abusive_clause_weights
        for group in ["missing_clause_weights", "dangerous_clause_weights", "abusive_clause_weights"]:
            if group in so:
                weights_dict = so[group]
                if not isinstance(weights_dict, dict) or not all(isinstance(k, str) and isinstance(v, int) for k, v in weights_dict.items()):
                    raise ProfileValidationError(f"scoring.{group} must be a dict mapping strings to integers")
                    
        # jurisdiction_adjustments
        if "jurisdiction_adjustments" in so:
            ja = so["jurisdiction_adjustments"]
            if not isinstance(ja, dict):
                raise ProfileValidationError("scoring.jurisdiction_adjustments must be a dictionary")
            for j_name, j_weights in ja.items():
                if not isinstance(j_weights, dict):
                    raise ProfileValidationError(f"scoring.jurisdiction_adjustments.{j_name} must be a dictionary")
                for key, val in j_weights.items():
                    if key not in ["missing_required_fallback", "red_flag_high", "red_flag_medium", "l2_unique", "no_governing_law", "no_venue"]:
                        raise ProfileValidationError(f"scoring.jurisdiction_adjustments.{j_name} contains unrecognized weight key '{key}'")
                    if not isinstance(val, int):
                        raise ProfileValidationError(f"scoring.jurisdiction_adjustments.{j_name}.{key} must be an integer")



class ProfileManager:
    """Manages contract profile loading, validation, and registry coordination."""

    def __init__(self, registry_path: str = _REGISTRY_PATH):
        self.registry_path = registry_path
        self._profiles: Dict[str, Dict[str, Any]] = {}
        self._registry: Dict[str, Any] = {}
        self._rules: Dict[str, Any] = {}
        self.load_registry()
        self.load_rules_classification()
        self.validate_registry()

    def validate_registry(self) -> None:
        """Validate the registry for duplicate IDs, duplicate aliases, and profile conflicts."""
        seen_ids = set()
        seen_aliases = {}
        
        for pid in self.list_profiles():
            p = self.get_profile(pid)
            p_id = p["profile_id"]
            
            if p_id in seen_ids:
                raise ProfileValidationError(f"Duplicate profile ID content detected: '{p_id}' in registry mapping '{pid}'")
            seen_ids.add(p_id)
            
            aliases = p["metadata"].get("aliases", [])
            for alias in aliases:
                a_clean = alias.strip().lower()
                if a_clean in seen_aliases:
                    raise ProfileValidationError(
                        f"Duplicate alias '{alias}' detected between profiles '{pid}' and '{seen_aliases[a_clean]}'"
                    )
                seen_aliases[a_clean] = pid


    def load_registry(self) -> None:
        """Load profile registry from profiles.json."""
        if not os.path.exists(self.registry_path):
            raise FileNotFoundError(f"Registry file not found at {self.registry_path}")
        
        try:
            with open(self.registry_path, "r", encoding="utf-8") as f:
                self._registry = json.load(f)
        except Exception as e:
            raise ProfileValidationError(f"Failed to parse registry: {e}")

        if "profiles" not in self._registry or not isinstance(self._registry["profiles"], dict):
            raise ProfileValidationError("Registry profiles must be a dictionary mapping profile IDs to filenames")

    def load_rules_classification(self) -> None:
        """Load generic and contract-specific rules classification metadata."""
        rules_path = os.path.join(os.path.dirname(self.registry_path), "rules_classification.json")
        if not os.path.exists(rules_path):
            raise FileNotFoundError(f"Rules classification layer not found at {rules_path}")

        try:
            with open(rules_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._rules = data.get("rules", {})
        except Exception as e:
            raise ProfileValidationError(f"Failed to parse rules classification file: {e}")

    def list_profiles(self) -> List[str]:
        """Return list of registered profile IDs."""
        return list(self._registry.get("profiles", {}).keys())

    def list_families(self) -> Dict[str, Any]:
        """Return the dictionary of configured families."""
        return self._registry.get("families", {})

    def get_profile(self, profile_id: str) -> Dict[str, Any]:
        """Load, validate, cache, and return the requested profile by ID."""
        if profile_id in self._profiles:
            return self._profiles[profile_id]

        profiles_map = self._registry.get("profiles", {})
        if profile_id not in profiles_map:
            raise ValueError(f"Profile ID '{profile_id}' not found in registry.")

        filename = profiles_map[profile_id]
        profile_path = os.path.join(os.path.dirname(self.registry_path), filename)
        
        if not os.path.exists(profile_path):
            raise FileNotFoundError(f"Profile configuration file not found: {profile_path}")

        try:
            with open(profile_path, "r", encoding="utf-8") as f:
                profile_data = json.load(f)
        except Exception as e:
            raise ProfileValidationError(f"Failed to parse profile JSON {filename}: {e}")

        # Schema Validation with rules classification lookup
        validate_profile(profile_data, self._rules)
        
        if profile_data["profile_id"] != profile_id:
            raise ProfileValidationError(f"Profile ID mismatch: filename registers '{profile_id}' but content has '{profile_data['profile_id']}'")

        self._profiles[profile_id] = profile_data
        return profile_data

    def clear_cache(self) -> None:
        """Clear cache of loaded profile definitions."""
        global _ALIAS_INDEX_CACHE, _NAME_INDEX_CACHE
        self._profiles.clear()
        _ALIAS_INDEX_CACHE = None
        _NAME_INDEX_CACHE = None
        try:
            from detector.detector_distilbert import clear_classification_cache
            clear_classification_cache()
        except Exception as e:
            logger.warning("Failed to clear classifier spec cache: %s", e)

    def _build_indexes(self) -> None:
        global _ALIAS_INDEX_CACHE, _NAME_INDEX_CACHE
        if _ALIAS_INDEX_CACHE is not None:
            return
            
        alias_index = {}
        name_index = {}
        active = self._registry.get("profiles", {})
        inactive = self._registry.get("inactive_profiles", {})
        
        for pid, filename in list(active.items()) + list(inactive.items()):
            try:
                profile_path = os.path.join(os.path.dirname(self.registry_path), filename)
                with open(profile_path, "r", encoding="utf-8") as f:
                    p = json.load(f)
                
                dname = p.get("metadata", {}).get("display_name", "").strip().lower()
                if dname:
                    name_index[dname] = pid
                    
                aliases = p.get("metadata", {}).get("aliases", [])
                for alias in aliases:
                    alias_index[alias.strip().lower()] = pid
            except Exception as e:
                logger.warning("Failed to index profile %s: %s", pid, e)
                
        _ALIAS_INDEX_CACHE = alias_index
        _NAME_INDEX_CACHE = name_index

    def resolve_profile_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Resolve a profile by ID, display name, or aliases (case-insensitive)."""
        name_clean = name.strip().lower()
        active_profiles = self.list_profiles()
        
        # 1. Try direct ID lookup
        for pid in active_profiles:
            if pid.lower() == name_clean:
                return self.get_profile(pid)
                
        # 2. Try fast memory index lookup
        self._build_indexes()
        
        pid = _NAME_INDEX_CACHE.get(name_clean)
        if pid and pid in active_profiles:
            return self.get_profile(pid)
            
        pid = _ALIAS_INDEX_CACHE.get(name_clean)
        if pid and pid in active_profiles:
            return self.get_profile(pid)
            
        return None

    def save_registry(self) -> None:
        """Write self._registry dict back to profiles.json."""
        try:
            with open(self.registry_path, "w", encoding="utf-8") as f:
                json.dump(self._registry, f, indent=2)
                f.write("\n")
        except Exception as e:
            raise ProfileValidationError(f"Failed to write registry: {e}")

    def activate_profile(self, profile_id: str) -> None:
        """Move profile from inactive_profiles to active profiles registry."""
        inactive = self._registry.setdefault("inactive_profiles", {})
        active = self._registry.setdefault("profiles", {})
        
        if profile_id in active:
            return # Already active
            
        if profile_id not in inactive:
            raise ValueError(f"Profile ID '{profile_id}' not found in inactive registry.")
            
        active[profile_id] = inactive.pop(profile_id)
        self.save_registry()
        self.clear_cache()

    def deactivate_profile(self, profile_id: str) -> None:
        """Move profile from active profiles to inactive_profiles registry."""
        inactive = self._registry.setdefault("inactive_profiles", {})
        active = self._registry.setdefault("profiles", {})
        
        if profile_id in inactive:
            return # Already inactive
            
        if profile_id not in active:
            raise ValueError(f"Profile ID '{profile_id}' not found in active registry.")
            
        inactive[profile_id] = active.pop(profile_id)
        self.save_registry()
        self.clear_cache()

    def publish_profile(self, profile_id: str, profile_data: Dict[str, Any]) -> None:
        """Validate, backup current version (if exists), write file, and register."""
        # 1. Validate
        validate_profile(profile_data, self._rules)
        if profile_data.get("profile_id") != profile_id:
            raise ProfileValidationError("Payload profile_id does not match URL profile ID")
            
        # Ensure target directories exist
        profiles_dir = os.path.dirname(self.registry_path)
        history_dir = os.path.join(profiles_dir, "history")
        os.makedirs(history_dir, exist_ok=True)
        
        # 2. Check if current profile exists to back up
        filename = f"{profile_id}.json"
        profile_path = os.path.join(profiles_dir, filename)
        
        if os.path.exists(profile_path):
            try:
                with open(profile_path, "r", encoding="utf-8") as f:
                    old_data = json.load(f)
                old_ver = old_data.get("version", "unknown")
                # Copy to history
                history_path = os.path.join(history_dir, f"{profile_id}_v{old_ver}.json")
                with open(history_path, "w", encoding="utf-8") as f:
                    json.dump(old_data, f, indent=2)
                    f.write("\n")
            except Exception as e:
                logger.warning("Could not backup profile %s: %s", profile_id, e)
                
        # 3. Write new profile data
        try:
            with open(profile_path, "w", encoding="utf-8") as f:
                json.dump(profile_data, f, indent=2)
                f.write("\n")
        except Exception as e:
            raise ProfileValidationError(f"Failed to write profile definition: {e}")
            
        # 4. Update registry mapping (activate it by default upon publish)
        active = self._registry.setdefault("profiles", {})
        inactive = self._registry.setdefault("inactive_profiles", {})
        
        active[profile_id] = filename
        if profile_id in inactive:
            inactive.pop(profile_id)
            
        self.save_registry()
        self._profiles[profile_id] = profile_data # Update cache

    def rollback_profile(self, profile_id: str, target_version: str) -> None:
        """Roll back active profile definition to a version stored in history."""
        if not re.match(r"^[a-zA-Z0-9_]+$", profile_id):
            raise ValueError("Invalid profile ID format")
        if not re.match(r"^[a-zA-Z0-9.-]+$", target_version):
            raise ValueError("Invalid version format")

        profiles_dir = os.path.dirname(self.registry_path)
        history_path = os.path.join(profiles_dir, "history", f"{profile_id}_v{target_version}.json")
        
        # Prevent path traversal
        abs_history_dir = os.path.abspath(os.path.join(profiles_dir, "history"))
        abs_history_path = os.path.abspath(history_path)
        if not abs_history_path.startswith(abs_history_dir + os.sep):
            raise PermissionError("Path traversal attempt blocked")

        if not os.path.exists(history_path):
            raise FileNotFoundError(f"Rollback target version 'v{target_version}' not found in history for profile '{profile_id}'")
            
        try:
            with open(history_path, "r", encoding="utf-8") as f:
                rollback_data = json.load(f)
        except Exception as e:
            raise ProfileValidationError(f"Failed to read rollback file: {e}")
            
        # Save as current profile path
        profile_path = os.path.join(profiles_dir, f"{profile_id}.json")
        try:
            with open(profile_path, "w", encoding="utf-8") as f:
                json.dump(rollback_data, f, indent=2)
                f.write("\n")
        except Exception as e:
            raise ProfileValidationError(f"Failed to write rolled-back profile file: {e}")
            
        # Ensure it is active
        active = self._registry.setdefault("profiles", {})
        inactive = self._registry.setdefault("inactive_profiles", {})
        
        active[profile_id] = f"{profile_id}.json"
        if profile_id in inactive:
            inactive.pop(profile_id)
            
        self.save_registry()
        self.clear_cache()




if __name__ == "__main__":
    # Self-test validation block when run directly
    print("Running Contract Profiles Foundation verification...")
    try:
        manager = ProfileManager()
        profiles = manager.list_profiles()
        print(f"Registered profiles found: {profiles}")
        
        for pid in profiles:
            p = manager.get_profile(pid)
            print(f"  - Verified profile '{pid}' v{p['version']} [{p['validation_status']}]")
            
        print("Verification OK. All registry-mapped profiles validated successfully against schema rules.")
    except Exception as exc:
        print(f"Verification FAILED: {exc}")
        import sys
        sys.exit(1)
