# Golden Evaluation Dataset Sampling & Labeling Methodology

## 1. Overview
The Golden Evaluation Set contains **200 hand-curated and rigorously validated customer support instances** for Apple Customer Support.

## 2. Sampling Stratification
To prevent artificial benchmark inflation and ensure realistic testing across both common and high-risk customer support scenarios, the dataset is stratified as follows:

| Intent | Auto-Handle Count | Escalate-to-Human Count | Total Count | % of Golden Set |
| :--- | :--- | :--- | :--- | :--- |
| `SOFTWARE_OS_GLITCH` | 43 | 7 | **50** | 25.0% |
| `HARDWARE_PHYSICAL_DAMAGE` | 0 | 35 | **35** | 17.5% |
| `ACCOUNT_SECURITY_ICLOUD` | 0 | 25 | **25** | 12.5% |
| `BILLING_SUBSCRIPTION_REFUND` | 1 | 25 | **26** | 13.0% |
| `DEVICE_SETUP_COMPATIBILITY` | 25 | 0 | **25** | 12.5% |
| `WARRANTY_ORDER_SHIPPING` | 1 | 18 | **19** | 9.5% |
| `GENERAL_INQUIRY_FEEDBACK` | 20 | 0 | **20** | 10.0% |

**Total Auto-Handle**: 90 (45.0%) | **Total Escalate-to-Human**: 110 (55.0%)

## 3. Labeling Protocol & Quality Assurance
Each example was labeled according to strict rubric guidelines:
1. **Intent Grounding**: Intent is assigned based on root customer issue, not superficial keyword triggers.
2. **Escalation Ground Truth**: Escalation to human is mandated for:
   - Physical hardware / safety risks (`requires_hardware_inspection_or_genius_bar`)
   - Credential / PII / Account Lockout (`security_sensitive_credentials_or_account_lockout`)
   - Direct Billing Disputes / Chargebacks (`financial_transaction_and_refund_authorization`)
   - Order tracking / shipping anomalies (`order_logistics_or_warranty_system_lookup`)
   - Explicit customer frustration or legal threats (`high_customer_frustration_or_legal_escalation`)
   - Persistent failure after prior troubleshooting attempts (`unresolved_after_standard_troubleshooting`)
3. **Canonical Resolution**: Every entry contains a reference resolution citing official Apple Support URLs (`support.apple.com`, `iforgot.apple.com`, `reportaproblem.apple.com`) and adherence to Apple brand tone.
