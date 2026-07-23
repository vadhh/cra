# Alias Review

## Objective
The objective of this document is to evaluate alias overlaps and collisions identified in [registry_v1.json](file:///mnt/c/Users/ADVAN/cra/ldv-backend/detector/profiles/registry_v1.json), presenting recommendations to prevent routing conflicts in the zero-shot classifier.

---

## 1. Collision Analysis

### Alias: `saas agreement`
- **Profiles Involved**: `software_license` (registry alias) and `saas_agreement` (active profile)
- **Status**: Collision. A document matching "saas agreement" will resolve to `software_license` in the registry instead of the specialized `saas_agreement` profile.
- **Preferred Canonical Assignment**: `saas_agreement`
- **Recommendation**: **Rename**. Remove `'saas agreement'` from the aliases list of `software_license` in [registry_v1.json](file:///mnt/c/Users/ADVAN/cra/ldv-backend/detector/profiles/registry_v1.json), keeping it exclusively under the `saas_agreement` profile.

### Alias: `joint venture agreement`
- **Profiles Involved**: `partnership_agreement` and `joint_venture_agreement`
- **Status**: Collision. Overlaps between general partnership and joint venture definitions.
- **Preferred Canonical Assignment**: `joint_venture_agreement`
- **Recommendation**: **Rename**. Remove `'joint venture agreement'` from the aliases list of `partnership_agreement` in [registry_v1.json](file:///mnt/c/Users/ADVAN/cra/ldv-backend/detector/profiles/registry_v1.json). General partnerships should be identified via `'partnership agreement'` or `'partnership contract'`.

### Alias: `perjanjian kerjasama` (Indonesian)
- **Profiles Involved**: `partnership_agreement` and `cooperation_agreement`
- **Status**: Collision. "Perjanjian kerjasama" translates generally to "cooperation agreement" but is often colloquially used for business partnerships.
- **Preferred Canonical Assignment**: `cooperation_agreement`
- **Recommendation**: **Rename**. Remove `'perjanjian kerjasama'` from the aliases list of `partnership_agreement` in [registry_v1.json](file:///mnt/c/Users/ADVAN/cra/ldv-backend/detector/profiles/registry_v1.json). Use `'perjanjian kemitraan'` as the primary alias for `partnership_agreement` in Indonesian.

### Alias: `samenwerkingsovereenkomst` (Dutch)
- **Profiles Involved**: `partnership_agreement` and `cooperation_agreement`
- **Status**: Collision. "Samenwerkingsovereenkomst" refers to general cooperation.
- **Preferred Canonical Assignment**: `cooperation_agreement`
- **Recommendation**: **Rename**. Remove `'samenwerkingsovereenkomst'` from the aliases list of `partnership_agreement` in [registry_v1.json](file:///mnt/c/Users/ADVAN/cra/ldv-backend/detector/profiles/registry_v1.json). Use `'maatschapsovereenkomst'` or `'vennootschapscontract'` for partnership.

---

## 2. Summary Matrix

| Conflicting Alias | Language | Profiles Sharing Alias | Recommended Assignment | Action |
| :--- | :--- | :--- | :--- | :--- |
| `'saas agreement'` | English | `software_license`, `saas_agreement` | `saas_agreement` | **Rename** (Remove from `software_license`) |
| `'joint venture agreement'` | English | `partnership_agreement`, `joint_venture_agreement` | `joint_venture_agreement` | **Rename** (Remove from `partnership_agreement`) |
| `'perjanjian kerjasama'` | Indonesian | `partnership_agreement`, `cooperation_agreement` | `cooperation_agreement` | **Rename** (Remove from `partnership_agreement`) |
| `'samenwerkingsovereenkomst'` | Dutch | `partnership_agreement`, `cooperation_agreement` | `cooperation_agreement` | **Rename** (Remove from `partnership_agreement`) |
