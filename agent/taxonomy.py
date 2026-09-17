"""
Domain Taxonomy and Intent Definitions for Apple Customer Support.

Defines the 7 standard customer support intents derived from real AppleSupport
Twitter dialogues, along with unambiguous decision boundaries, prototypical queries,
and default escalation policies.
"""

from typing import Dict, List, Any
from dataclasses import dataclass, field

@dataclass
class IntentDefinition:
    name: str
    display_name: str
    description: str
    decision_boundary_note: str
    prototypical_examples: List[str]
    default_action: str  # "AUTO_HANDLE" or "ESCALATE_TO_HUMAN"
    default_escalation_reason: str = ""
    resolution_guideline: str = ""

INTENT_TAXONOMY: Dict[str, IntentDefinition] = {
    "SOFTWARE_OS_GLITCH": IntentDefinition(
        name="SOFTWARE_OS_GLITCH",
        display_name="Software & OS Glitch",
        description="Bugs, crashes, freezes, performance slowdowns, iOS/macOS update glitches, battery drain after update, keyboard/autocorrect issues, Wi-Fi/Bluetooth software drops.",
        decision_boundary_note="Use this for functional software issues where hardware is intact. If physical drop/water damage caused the issue, use HARDWARE_PHYSICAL_DAMAGE.",
        prototypical_examples=[
            "Since updating to iOS 11.1 my battery drops 40% in two hours and phone gets hot.",
            "My iPhone X screen freezes every time I open the camera app.",
            "The letter 'I' is being replaced with a weird symbol on my keyboard after the latest update.",
            "Apps keep crashing randomly on my iPad after restarting.",
            "Bluetooth disconnects every 5 minutes in my car since yesterday's update."
        ],
        default_action="AUTO_HANDLE",
        resolution_guideline="Acknowledge issue, inquire about exact OS version and device model, suggest standard non-destructive troubleshooting (restart, update patch, reset network settings), offer DM link if issue persists."
    ),
    
    "HARDWARE_PHYSICAL_DAMAGE": IntentDefinition(
        name="HARDWARE_PHYSICAL_DAMAGE",
        display_name="Hardware & Physical Damage",
        description="Physical breakage, cracked screens, water/liquid ingress, swelling batteries, broken charging ports, camera lens shattered, speaker rattling after a drop.",
        decision_boundary_note="Requires physical technician inspection or replacement parts. If user merely reports an app crashing or software freezing without physical trauma, classify as SOFTWARE_OS_GLITCH.",
        prototypical_examples=[
            "Dropped my iPhone 8 on concrete and the back glass shattered into pieces.",
            "My phone fell in the pool, speaker is crackling and charging port says liquid detected.",
            "My MacBook battery has swollen and the trackpad won't click anymore.",
            "The lightning port is loose and only charges when held at a specific angle.",
            "Green vertical line appeared on my screen after it hit the floor."
        ],
        default_action="ESCALATE_TO_HUMAN",
        default_escalation_reason="requires_hardware_inspection_or_genius_bar",
        resolution_guideline="Express concern, advise on safety (especially if swollen/liquid), guide to book an appointment at Apple Store Genius Bar or Apple Authorized Service Provider via support.apple.com/repair."
    ),
    
    "ACCOUNT_SECURITY_ICLOUD": IntentDefinition(
        name="ACCOUNT_SECURITY_ICLOUD",
        display_name="Account, Security & iCloud",
        description="Apple ID lockouts, forgot password, two-factor authentication (2FA) verification code issues, suspicious login alerts, activation lock, hacked accounts.",
        decision_boundary_note="Never collect or verify credentials over public tweet or social DM. Direct to secure authentication portal. If related to App Store billing/charges, classify as BILLING_SUBSCRIPTION_REFUND.",
        prototypical_examples=[
            "My Apple ID has been locked for security reasons and I can't receive the 2FA code on my old number.",
            "Someone in Russia tried logging into my iCloud account, what do I do?",
            "I forgot my Apple ID password and the recovery email is no longer active.",
            "Bought a used iPhone and it is locked with previous owner's iCloud Activation Lock.",
            "My iCloud storage says full even after deleting 50GB of photos."
        ],
        default_action="ESCALATE_TO_HUMAN",
        default_escalation_reason="security_sensitive_credentials_or_account_lockout",
        resolution_guideline="Strict security policy: Never ask for credentials in chat. Provide official self-recovery link (iforgot.apple.com / support.apple.com/apple-id) or escalate to Security Specialist."
    ),
    
    "BILLING_SUBSCRIPTION_REFUND": IntentDefinition(
        name="BILLING_SUBSCRIPTION_REFUND",
        display_name="Billing, Subscriptions & Refunds",
        description="Unrecognized App Store charges, unauthorized in-app purchases (often by kids), accidental subscription renewals, refund requests, payment method declined.",
        decision_boundary_note="Focuses on financial transactions and subscriptions. If the user cannot download an app due to an Apple ID password issue, classify as ACCOUNT_SECURITY_ICLOUD.",
        prototypical_examples=[
            "I was charged $59.99 for an app subscription I canceled during the free trial.",
            "My credit card was charged twice by iTunes for the same album.",
            "My 7-year-old bought $100 of Roblox coins without permission, need an immediate refund.",
            "Why is my payment method being declined on the App Store when I have funds?",
            "How do I cancel Apple Music before the next billing cycle?"
        ],
        default_action="ESCALATE_TO_HUMAN",
        default_escalation_reason="financial_transaction_and_refund_authorization",
        resolution_guideline="Provide direct link to review purchases and request refunds at reportaproblem.apple.com. Guide how to manage subscriptions in Settings > Apple ID > Subscriptions."
    ),
    
    "DEVICE_SETUP_COMPATIBILITY": IntentDefinition(
        name="DEVICE_SETUP_COMPATIBILITY",
        display_name="Device Setup & Compatibility",
        description="New device migration (Quick Start), Apple Watch pairing, AirDrop configuration, Family Sharing setup, CarPlay connectivity guide, data transfer from Android/PC.",
        decision_boundary_note="User is asking 'how do I set up or use this feature'. If setup fails due to a system bug/crash, classify as SOFTWARE_OS_GLITCH.",
        prototypical_examples=[
            "How do I transfer all my photos and WhatsApp messages from Android to my new iPhone 11?",
            "Trying to pair my Apple Watch Series 3 with my new phone and it's asking to unpair first.",
            "How do I set up Family Sharing so my daughter can share my iCloud storage?",
            "AirDrop won't show up for my friend's iPhone nearby, how do I configure receiving?",
            "Can I connect my AirPods to my Windows laptop via Bluetooth?"
        ],
        default_action="AUTO_HANDLE",
        resolution_guideline="Provide crisp step-by-step navigation instructions (e.g. Settings > General > AirDrop) and link to the relevant Apple Support Knowledge Base guide."
    ),
    
    "WARRANTY_ORDER_SHIPPING": IntentDefinition(
        name="WARRANTY_ORDER_SHIPPING",
        display_name="Warranty, Order Status & Shipping",
        description="Tracking online Apple Store deliveries, trade-in kit delays, checking AppleCare+ coverage status, tracking repair progress with Repair ID, preorder delivery dates.",
        decision_boundary_note="Focuses on supply chain, orders, and warranty entitlement lookups. If asking about physical damage repair costs, classify as HARDWARE_PHYSICAL_DAMAGE.",
        prototypical_examples=[
            "My iPhone X preorder status still says 'Preparing for Shipment', will it arrive by Friday?",
            "Where is my trade-in return box? It's been 10 days since my new phone arrived.",
            "How do I check if my MacBook Pro is still covered under AppleCare warranty?",
            "Repair ID #R12345678 says waiting for parts for 2 weeks, need an update on my laptop.",
            "UPS lost my Apple package, need someone to track this right away."
        ],
        default_action="ESCALATE_TO_HUMAN",
        default_escalation_reason="order_logistics_or_warranty_system_lookup",
        resolution_guideline="Direct user to apple.com/orderstatus or checkcoverage.apple.com. For delayed shipments or lost packages, escalate to Order Logistics Specialist via DM."
    ),
    
    "GENERAL_INQUIRY_FEEDBACK": IntentDefinition(
        name="GENERAL_INQUIRY_FEEDBACK",
        display_name="General Inquiry & Feedback",
        description="Store locations and hours, product release rumors/inquiries, general compliments, feature suggestions, broad corporate feedback.",
        decision_boundary_note="General queries that do not involve technical issues, account security, hardware breakage, or orders.",
        prototypical_examples=[
            "What time does the Regent Street Apple Store close on Sundays?",
            "Is Apple planning on releasing an SE 2 next spring?",
            "Just wanted to say the customer service rep in Covent Garden was fantastic today!",
            "Apple should really add dark mode to all native apps in the next update.",
            "Where can I recycle my old iPad 2 safely?"
        ],
        default_action="AUTO_HANDLE",
        resolution_guideline="Friendly and professional brand acknowledgment. Provide apple.com/retail for store inquiries or apple.com/feedback for product suggestions."
    )
}

ALL_INTENTS = list(INTENT_TAXONOMY.keys())
