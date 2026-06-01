"""
FAQ Database Seed Script.

Programmatically generates 200 high-variance, realistic FAQ entries
across 8 categories and injects them into the SQLite database.
Each category receives exactly 25 FAQs.

Usage:
    python -m backend.seed_db

Author: CodeAlpha Intern | Registration ID: Akshay Saxena
"""

import sys
import os
from pathlib import Path

# Ensure the project root is on the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.database import init_database, execute_query, execute_many, get_connection


# ============================================================
# Category Definitions
# ============================================================

CATEGORIES: list[dict[str, str]] = [
    {"name": "Account Management", "icon": "👤"},
    {"name": "Orders & Shipping", "icon": "📦"},
    {"name": "Technical Support", "icon": "🔧"},
    {"name": "Billing & Payments", "icon": "💳"},
    {"name": "Product Information", "icon": "📱"},
    {"name": "Security & Privacy", "icon": "🔒"},
    {"name": "Returns & Refunds", "icon": "↩️"},
    {"name": "General & Company", "icon": "🏢"},
]


# ============================================================
# FAQ Templates by Category (25 per category = 200 total)
# ============================================================

FAQS: dict[str, list[dict[str, str]]] = {
    "Account Management": [
        {
            "question": "How do I create a new account?",
            "answer": "To create a new account, click the 'Sign Up' button on our homepage. Enter your email address, create a strong password (minimum 8 characters with uppercase, lowercase, and numbers), and verify your email through the confirmation link we'll send you. The entire process takes less than 2 minutes."
        },
        {
            "question": "How can I reset my forgotten password?",
            "answer": "Click 'Forgot Password' on the login page, enter your registered email address, and we'll send a secure reset link valid for 24 hours. Click the link, set your new password, and you're back in. If you don't receive the email, check your spam folder or contact support."
        },
        {
            "question": "Can I change my account email address?",
            "answer": "Yes! Go to Settings > Account Details > Email Address and click 'Change Email.' You'll need to verify the new email address through a confirmation link. Your old email will receive a notification about the change for security purposes."
        },
        {
            "question": "How do I update my profile information?",
            "answer": "Navigate to your Profile page by clicking your avatar in the top-right corner. From there, you can edit your display name, bio, profile picture, phone number, and notification preferences. Changes are saved automatically."
        },
        {
            "question": "How do I delete my account permanently?",
            "answer": "Go to Settings > Account > Delete Account. You'll be asked to confirm by entering your password. Please note that account deletion is irreversible — all your data, order history, and saved preferences will be permanently erased within 30 days."
        },
        {
            "question": "What should I do if my account is locked?",
            "answer": "Accounts are temporarily locked after 5 failed login attempts for security. Wait 30 minutes for automatic unlock, or use the 'Forgot Password' flow to reset immediately. If the issue persists, contact our support team with your registered email for manual review."
        },
        {
            "question": "How do I enable two-factor authentication?",
            "answer": "Go to Settings > Security > Two-Factor Authentication and toggle it on. You can choose between SMS verification codes or an authenticator app (Google Authenticator, Authy). We strongly recommend enabling 2FA for enhanced account security."
        },
        {
            "question": "Can I have multiple accounts with the same email?",
            "answer": "No, each email address can only be associated with one account. This policy ensures account security and prevents duplicate registrations. If you need separate accounts, please use different email addresses for each."
        },
        {
            "question": "How do I change my username or display name?",
            "answer": "Go to Settings > Profile > Display Name. You can change your display name up to 3 times within a 30-day period. Usernames must be unique, between 3-30 characters, and can contain letters, numbers, and underscores."
        },
        {
            "question": "How do I link my social media accounts?",
            "answer": "Navigate to Settings > Connected Accounts. You can link your Google, Facebook, Apple, or GitHub accounts for faster login. Click 'Connect' next to the desired platform and authorize the connection. You can disconnect anytime."
        },
        {
            "question": "What are the password requirements for my account?",
            "answer": "Passwords must be at least 8 characters long and include a mix of uppercase letters, lowercase letters, numbers, and at least one special character (!@#$%^&*). We also check against commonly breached passwords for your safety."
        },
        {
            "question": "How do I switch between a personal and business account?",
            "answer": "Go to Settings > Account Type. Click 'Upgrade to Business' or 'Switch to Personal.' Business accounts have access to additional features like team management, invoicing, and analytics. Switching preserves all your existing data."
        },
        {
            "question": "Can I temporarily deactivate my account instead of deleting it?",
            "answer": "Yes, go to Settings > Account > Deactivate Account. This hides your profile and pauses all notifications while keeping your data intact. You can reactivate anytime by simply logging back in within 12 months."
        },
        {
            "question": "How do I manage my notification preferences?",
            "answer": "Go to Settings > Notifications. You can customize email, push, and SMS notification preferences for orders, promotions, account alerts, and support updates. You can also set 'Do Not Disturb' hours to pause all non-critical notifications."
        },
        {
            "question": "What happens to my data if I don't log in for a long time?",
            "answer": "Accounts remain active indefinitely, but we may send re-engagement emails after 6 months of inactivity. After 24 months, dormant accounts may be flagged for review, but we'll always notify you before any action is taken on your data."
        },
        {
            "question": "How do I set up account recovery options?",
            "answer": "Go to Settings > Security > Recovery Options. Add a recovery phone number and backup email address. You can also generate one-time recovery codes — store these securely as they can be used if you lose access to your primary authentication method."
        },
        {
            "question": "Can I export all my account data?",
            "answer": "Yes, go to Settings > Privacy > Download My Data. We'll compile your complete data package including profile info, order history, chat logs, and preferences into a downloadable ZIP file. This process may take up to 48 hours for large accounts."
        },
        {
            "question": "How do I change my account language and region settings?",
            "answer": "Go to Settings > Preferences > Language & Region. Choose your preferred language from 30+ supported options and set your region for accurate pricing, shipping estimates, and content localization. Changes take effect immediately."
        },
        {
            "question": "What is account verification and how do I complete it?",
            "answer": "Account verification confirms your identity for enhanced features and trust badges. Go to Settings > Verification, upload a government-issued ID, and take a selfie for facial matching. Verification is reviewed within 24-48 hours."
        },
        {
            "question": "How can I see devices logged into my account?",
            "answer": "Go to Settings > Security > Active Sessions. You'll see all devices currently logged in with their location, browser, and last activity time. You can remotely sign out of any device by clicking 'Revoke Access' next to it."
        },
        {
            "question": "How do I set up a profile picture?",
            "answer": "Click your avatar in the navigation bar, then select 'Edit Profile.' Click the camera icon on your current avatar to upload a new image. We support JPG, PNG, and GIF formats up to 5MB. The image will be automatically cropped to a circle."
        },
        {
            "question": "Can I merge two separate accounts into one?",
            "answer": "Account merging isn't automated, but our support team can assist. Contact us with both account emails, and after identity verification, we can transfer order history, bookmarks, and credits to your preferred account. The other account will be closed."
        },
        {
            "question": "How do I update my phone number on file?",
            "answer": "Go to Settings > Account Details > Phone Number. Enter your new number and verify it via SMS code. Your old number will be unlinked immediately. If you use SMS-based 2FA, make sure to update that setting as well."
        },
        {
            "question": "What email notifications will I receive after signing up?",
            "answer": "After registration, you'll receive a welcome email, email verification link, and optional onboarding tips over the first week. You'll also get transactional emails for orders and security alerts. Marketing emails are opt-in only."
        },
        {
            "question": "Is there an age requirement to create an account?",
            "answer": "Yes, you must be at least 13 years old (or 16 in certain jurisdictions) to create an account, in compliance with COPPA and GDPR regulations. Users under 18 may have certain features restricted based on local laws."
        },
    ],
    "Orders & Shipping": [
        {
            "question": "How do I track my order?",
            "answer": "Once your order ships, you'll receive a tracking email with a link and tracking number. You can also check the status anytime by going to My Orders in your account dashboard. We support real-time tracking for all major carriers including UPS, FedEx, and USPS."
        },
        {
            "question": "What are the available shipping options and their delivery times?",
            "answer": "We offer Standard Shipping (5-7 business days, free on orders over $50), Express Shipping (2-3 business days, $9.99), and Overnight Shipping (next business day, $19.99). Delivery times may vary during peak seasons and holidays."
        },
        {
            "question": "Can I change my shipping address after placing an order?",
            "answer": "You can modify your shipping address within 1 hour of placing the order. Go to My Orders, click the order, and select 'Edit Address.' After the order enters processing, address changes must be requested through our support team and aren't guaranteed."
        },
        {
            "question": "Do you ship internationally?",
            "answer": "Yes, we ship to over 100 countries worldwide. International shipping typically takes 7-14 business days depending on the destination. Import duties and taxes are the responsibility of the recipient and are calculated at checkout for transparency."
        },
        {
            "question": "What happens if my package is lost or damaged in transit?",
            "answer": "Contact our support team within 7 days of the expected delivery date. We'll initiate a carrier investigation and, depending on the outcome, either reship the order at no cost or issue a full refund. All shipments include basic transit insurance."
        },
        {
            "question": "Can I schedule a specific delivery date?",
            "answer": "We offer scheduled delivery for Express and Overnight orders. During checkout, you can select a preferred delivery date (excluding weekends and holidays). Standard shipping deliveries cannot be scheduled but will arrive within the estimated window."
        },
        {
            "question": "How do I cancel an order before it ships?",
            "answer": "Go to My Orders, select the order, and click 'Cancel Order.' Cancellation is instant if the order hasn't entered processing. If it's already being prepared, submit a cancellation request and we'll attempt to stop it. Refunds are processed within 3-5 business days."
        },
        {
            "question": "What is your minimum order amount for free shipping?",
            "answer": "Free standard shipping is available on all orders of $50 or more within the continental United States. Orders under $50 incur a flat $5.99 standard shipping fee. Premium members enjoy free shipping on all orders regardless of amount."
        },
        {
            "question": "Do you offer same-day delivery?",
            "answer": "Same-day delivery is available in select metropolitan areas (New York, Los Angeles, Chicago, San Francisco) for orders placed before 12 PM local time. This service costs $24.99 and is available for eligible in-stock items only."
        },
        {
            "question": "Can I ship to a P.O. Box or APO/FPO address?",
            "answer": "We can ship to P.O. Boxes via USPS Standard and Priority Mail. APO/FPO/DPO addresses are also supported with delivery times of 10-21 business days. Note that Express and Overnight shipping options are not available for these address types."
        },
        {
            "question": "How do I combine multiple orders into one shipment?",
            "answer": "If your orders haven't shipped yet, contact support within 2 hours of placing the second order, and we'll consolidate them into a single shipment. This can save on shipping costs and reduce packaging waste."
        },
        {
            "question": "What carriers do you use for shipping?",
            "answer": "We partner with UPS, FedEx, USPS, and DHL for domestic and international deliveries. The carrier is selected based on your shipping speed, destination, and package dimensions to ensure the fastest and most cost-effective delivery."
        },
        {
            "question": "My tracking number isn't working. What should I do?",
            "answer": "Tracking numbers can take 24-48 hours to activate after the shipping label is created. If it still doesn't work after 48 hours, contact our support team with your order number. We'll verify the tracking details and provide an update."
        },
        {
            "question": "Can I add items to an existing order?",
            "answer": "Unfortunately, items cannot be added to an existing order once it's placed. However, you can place a new order and contact support to request shipment consolidation, which may save on shipping if the original order hasn't shipped yet."
        },
        {
            "question": "What packaging materials do you use?",
            "answer": "We use eco-friendly packaging made from 85% recycled materials. Fragile items are cushioned with biodegradable packing peanuts. All our boxes and mailers are FSC-certified and fully recyclable. We're committed to reducing our environmental footprint."
        },
        {
            "question": "Do you provide shipping insurance?",
            "answer": "All orders include complimentary basic transit insurance covering the full value up to $200. For high-value orders, you can add Premium Insurance at checkout for $4.99, which covers up to $2,000 and includes priority claims processing."
        },
        {
            "question": "Can I send an order as a gift with gift wrapping?",
            "answer": "Yes! Select 'This is a gift' during checkout to add premium gift wrapping ($4.99) and a personalized message card. The packing slip will exclude pricing information. Gift receipts can be included for easy returns by the recipient."
        },
        {
            "question": "What happens if I'm not home when my package arrives?",
            "answer": "For standard deliveries, the carrier will leave the package at your door or a safe location. For signature-required shipments, the carrier will leave a notice and attempt redelivery the next business day, or you can pick it up at the nearest facility."
        },
        {
            "question": "How do I view my complete order history?",
            "answer": "Log into your account and navigate to My Orders. You'll see a chronological list of all past orders with status, tracking info, and invoice links. You can filter by date range, status, or search by order number. Order history is retained for 5 years."
        },
        {
            "question": "Do you offer freight or bulk shipping for large orders?",
            "answer": "Yes, for orders exceeding 150 lbs or 10+ units, we offer LTL freight shipping with dedicated tracking. Contact our business sales team at business@example.com for custom quotes. Freight orders typically arrive within 5-10 business days."
        },
        {
            "question": "Can I have my order held at a carrier location for pickup?",
            "answer": "Yes, during checkout select 'Hold at Location' and choose a nearby UPS Store, FedEx Office, or USPS location. You'll be notified when the package arrives and have 7 days to pick it up with a valid photo ID."
        },
        {
            "question": "What is your signature requirement policy?",
            "answer": "Signature confirmation is automatically required for orders over $200 and all international shipments. You can opt into or out of signature requirements for eligible orders during checkout. Adult signature is required for age-restricted items."
        },
        {
            "question": "How do I get notified about my delivery status?",
            "answer": "We send proactive notifications via email and push notifications at each milestone: order confirmed, packed, shipped, out for delivery, and delivered. You can customize which notifications you receive in Settings > Notifications."
        },
        {
            "question": "Do you offer carbon-neutral or eco-friendly shipping?",
            "answer": "Yes, we offset the carbon footprint of every shipment through certified environmental programs. At checkout, you can also choose 'Green Shipping' which uses consolidated ground delivery routes, arriving in 7-10 days at a reduced environmental cost."
        },
        {
            "question": "Can I redirect a package that's already in transit?",
            "answer": "For UPS and FedEx shipments, you can request a redirect through the carrier's website using your tracking number. Redirect fees apply ($5-15 depending on the carrier). USPS packages can be redirected via Package Intercept for $15.25."
        },
    ],
    "Technical Support": [
        {
            "question": "The website is loading very slowly. What can I do?",
            "answer": "Try clearing your browser cache and cookies, disabling browser extensions, or switching to a different browser (we recommend Chrome, Firefox, or Edge). Check your internet connection speed at speedtest.net. If issues persist, our status page at status.example.com shows any ongoing performance issues."
        },
        {
            "question": "I'm getting a login error even though my password is correct.",
            "answer": "This can happen due to browser cache issues or case sensitivity. Try clearing your cookies, ensure Caps Lock is off, and use the 'Forgot Password' flow to reset. If using social login, verify you're selecting the correct provider. Contact support if the issue persists."
        },
        {
            "question": "Which web browsers are supported?",
            "answer": "We fully support the latest two versions of Google Chrome, Mozilla Firefox, Microsoft Edge, Safari (macOS/iOS), and Opera. Internet Explorer is not supported. For the best experience, keep your browser updated to the latest version."
        },
        {
            "question": "The mobile app keeps crashing on startup. How do I fix it?",
            "answer": "First, ensure your app is updated to the latest version from the App Store or Google Play. Try force-closing and reopening the app. If crashes persist, uninstall and reinstall the app. Clear the app cache in your device settings. We support iOS 15+ and Android 10+."
        },
        {
            "question": "How do I clear my browser cache and cookies?",
            "answer": "In Chrome: Settings > Privacy > Clear Browsing Data. In Firefox: Settings > Privacy & Security > Clear Data. In Safari: Preferences > Privacy > Manage Website Data. Select 'Cached images and files' and 'Cookies' then click Clear. Restart your browser afterward."
        },
        {
            "question": "Images on the site aren't loading properly. What should I do?",
            "answer": "Check if your browser is blocking images (Settings > Site Settings > Images). Disable any ad blockers temporarily. Try hard-refreshing the page (Ctrl+Shift+R on Windows, Cmd+Shift+R on Mac). If on a slow connection, images may take longer to load."
        },
        {
            "question": "I can't complete checkout — the page freezes.",
            "answer": "Disable any browser extensions (especially ad blockers and VPNs) which can interfere with payment processing. Try checkout in an incognito/private window. Ensure JavaScript is enabled. If using a corporate network, your firewall may be blocking payment APIs."
        },
        {
            "question": "How do I enable JavaScript in my browser?",
            "answer": "In Chrome: Settings > Privacy > Site Settings > JavaScript > Allowed. In Firefox: about:config > search 'javascript.enabled' > set to true. In Safari: Preferences > Security > Enable JavaScript. Our website requires JavaScript to function properly."
        },
        {
            "question": "The search function isn't returning relevant results.",
            "answer": "Try using more specific keywords or phrases instead of single words. Check for typos. Use our category filters to narrow results. If searching for a product, try the exact product name or model number. Our search supports natural language queries."
        },
        {
            "question": "I'm receiving error code 403 when accessing certain pages.",
            "answer": "Error 403 means access is denied. This can occur if your IP has been temporarily rate-limited (try again in 15 minutes), if you're using a VPN that's been flagged, or if the page requires authentication. Try logging in again or disabling your VPN."
        },
        {
            "question": "How do I report a bug or technical issue?",
            "answer": "Use the bug report form at Help > Report an Issue. Include your browser/OS version, steps to reproduce the issue, and any error messages or screenshots. Our engineering team reviews all reports within 24 hours and may follow up for additional details."
        },
        {
            "question": "Push notifications aren't working on my device.",
            "answer": "Ensure notifications are enabled: iOS: Settings > [App Name] > Notifications > Allow. Android: Settings > Apps > [App Name] > Notifications. Also check your in-app notification settings. Battery saver modes can block background notifications on Android."
        },
        {
            "question": "I'm having trouble uploading files or images.",
            "answer": "Supported formats are JPG, PNG, GIF, and PDF. Maximum file size is 10MB per file. Ensure your file isn't corrupted by opening it locally first. If uploading multiple files, try one at a time. Slow internet connections may cause upload timeouts."
        },
        {
            "question": "The website looks broken or has layout issues.",
            "answer": "This usually indicates a CSS caching issue. Hard-refresh the page (Ctrl+Shift+R). If the issue persists, try zooming to 100% (Ctrl+0), disabling browser zoom overrides, and ensuring no accessibility extensions are modifying the page layout."
        },
        {
            "question": "How do I check if there's a service outage?",
            "answer": "Visit our real-time status page at status.example.com for current system health. You can subscribe to incident updates via email or SMS. We also post updates on our @examplesupport Twitter/X account during major outages."
        },
        {
            "question": "Two-factor authentication codes aren't being received.",
            "answer": "SMS codes may be delayed by carrier issues. Wait 2 minutes, then request a new code. For authenticator apps, ensure your device clock is synced (auto time must be enabled). You can use backup recovery codes as an alternative."
        },
        {
            "question": "Can I use the platform on a tablet or iPad?",
            "answer": "Yes, our platform is fully responsive and optimized for tablets including iPad (Safari/Chrome), Samsung Galaxy Tab, and Fire HD tablets. You can use either our mobile app or the web version in your tablet's browser for the best experience."
        },
        {
            "question": "My payment was charged but the order shows as failed.",
            "answer": "Don't worry — this is usually a temporary authorization hold, not an actual charge. The hold will automatically release within 3-5 business days. Do not attempt to place the order again. Contact support with the error details for immediate assistance."
        },
        {
            "question": "How do I disable dark mode on the platform?",
            "answer": "Go to Settings > Appearance > Theme and select 'Light Mode.' You can also choose 'System Default' to match your operating system's theme preference. Theme changes apply instantly across all pages without requiring a page refresh."
        },
        {
            "question": "Videos on the site won't play. How do I fix this?",
            "answer": "Ensure your browser supports HTML5 video (all modern browsers do). Disable hardware acceleration if you see a black screen: Chrome > Settings > System > Hardware Acceleration. Check that your browser isn't blocking media autoplay."
        },
        {
            "question": "How do I use keyboard shortcuts on the platform?",
            "answer": "Press '?' on any page to see available keyboard shortcuts. Common shortcuts: Ctrl+K for search, Ctrl+/ for help, 'g' then 'h' for home, 'g' then 'o' for orders. Keyboard navigation fully supports screen readers for accessibility."
        },
        {
            "question": "The site is showing in the wrong language.",
            "answer": "The site detects your browser language by default. To change it, click the globe icon in the footer or go to Settings > Preferences > Language. You can choose from 30+ languages. Language preference is saved to your account across devices."
        },
        {
            "question": "I'm having issues with the live chat support widget.",
            "answer": "The chat widget requires JavaScript and may be blocked by ad blockers (especially uBlock Origin). Whitelist our domain in your ad blocker settings. If the widget doesn't appear, try using a different browser or clear your cache."
        },
        {
            "question": "How do I enable accessibility features?",
            "answer": "Go to Settings > Accessibility. Options include high contrast mode, increased font size, reduced motion (disables animations), screen reader optimization, and keyboard-only navigation mode. We comply with WCAG 2.1 AA standards."
        },
        {
            "question": "Why am I being rate-limited or seeing CAPTCHA challenges?",
            "answer": "Rate limiting occurs when our system detects unusual activity patterns (rapid page loads, repeated API calls). This is a security measure. Wait 15 minutes and try again. Using a VPN or shared network can trigger this. CAPTCHAs verify you're not a bot."
        },
    ],
    "Billing & Payments": [
        {
            "question": "What payment methods do you accept?",
            "answer": "We accept Visa, Mastercard, American Express, Discover, PayPal, Apple Pay, Google Pay, and Shop Pay. For business accounts, we also accept wire transfers and purchase orders. All payments are processed through PCI-DSS Level 1 compliant gateways."
        },
        {
            "question": "How do I update my credit card or payment information?",
            "answer": "Go to Settings > Payment Methods. Click 'Edit' on the card you want to update or 'Add New Card' to add a different one. For security, you'll need to re-enter the full card details. We use tokenized storage — we never see or store your full card number."
        },
        {
            "question": "Where can I find and download my invoices?",
            "answer": "Navigate to My Orders > click any order > 'Download Invoice.' You can also access all invoices at Settings > Billing > Invoice History. Invoices are available in PDF format and include itemized details, taxes, and shipping costs."
        },
        {
            "question": "Why was my payment declined?",
            "answer": "Common reasons include: insufficient funds, expired card, incorrect billing address (must match card), bank fraud prevention blocks, or international transaction restrictions. Contact your bank to authorize the transaction, then try again. Our support team can provide the specific decline code."
        },
        {
            "question": "Do you offer installment payment plans or buy-now-pay-later?",
            "answer": "Yes, we partner with Affirm, Klarna, and Afterpay for flexible payment options. Split your purchase into 4 interest-free payments or choose monthly financing for 6-12 months. Available for orders between $50 and $3,000 subject to credit approval."
        },
        {
            "question": "How do I apply a promo code or discount coupon?",
            "answer": "Enter your promo code in the 'Discount Code' field during checkout and click 'Apply.' Only one promo code can be used per order. Promo codes cannot be combined with other offers unless stated. Check the code's expiration date and minimum order requirements."
        },
        {
            "question": "I was charged the wrong amount. What should I do?",
            "answer": "Review your order details in My Orders to verify the charges including tax and shipping. If there's a discrepancy, contact our billing team within 30 days of the charge. Provide your order number and the amount you expected. We'll investigate and correct any errors."
        },
        {
            "question": "Do you charge sales tax on orders?",
            "answer": "Sales tax is calculated based on your shipping destination in compliance with local, state, and federal tax laws. Tax amounts are displayed during checkout before you confirm payment. Tax-exempt customers can submit their exemption certificate via Settings > Tax Information."
        },
        {
            "question": "How do I set up automatic recurring payments?",
            "answer": "For subscription services, go to Settings > Subscriptions > Payment Method. Toggle 'Auto-renewal' and select your preferred payment method. You'll be charged automatically before each renewal period. Cancel anytime before the next billing cycle."
        },
        {
            "question": "Can I get a refund if a price drops after my purchase?",
            "answer": "We offer a 14-day price protection guarantee. If an item you purchased drops in price within 14 days, contact support with your order number and we'll refund the difference to your original payment method or issue account credit."
        },
        {
            "question": "What currency are prices displayed in?",
            "answer": "Prices default to USD but can be displayed in 25+ currencies. Change your currency at the bottom of any page or in Settings > Preferences > Currency. Note that exchange rates are updated daily, and your bank may charge a foreign transaction fee."
        },
        {
            "question": "How do I request a payment receipt?",
            "answer": "Payment receipts are automatically emailed after each successful transaction. You can also download them from My Orders > [Order] > 'Download Receipt.' Receipts include transaction ID, payment method, itemized charges, and tax breakdown."
        },
        {
            "question": "Is it safe to save my credit card on your platform?",
            "answer": "Absolutely. We use industry-standard AES-256 encryption and PCI-DSS Level 1 compliance for payment data. Your card numbers are tokenized through Stripe — we never store raw card details on our servers. All transactions use HTTPS with TLS 1.3 encryption."
        },
        {
            "question": "How do I dispute a charge I don't recognize?",
            "answer": "First, check if any family members or authorized users made the purchase. If the charge is unauthorized, contact us immediately through Help > Billing Dispute. We'll investigate within 48 hours. For fraud, we recommend also contacting your bank's fraud department."
        },
        {
            "question": "Do you offer student, military, or senior discounts?",
            "answer": "Yes! Students with a valid .edu email get 15% off, active military and veterans get 20% off (verified through ID.me), and seniors (65+) get 10% off. Register at Settings > Discount Programs. Discounts apply to eligible items at checkout."
        },
        {
            "question": "What is your pre-authorization hold policy?",
            "answer": "When you place an order, we place a temporary authorization hold on your payment method to verify funds. This hold drops off automatically in 3-7 business days if the order is cancelled. The actual charge occurs only when the order ships."
        },
        {
            "question": "Can I split payment between multiple cards or methods?",
            "answer": "Currently, you can split payment between a gift card/store credit and one payment method. Splitting between two credit cards isn't supported. However, you can use PayPal, which allows you to link multiple funding sources within your PayPal account."
        },
        {
            "question": "How do I redeem a gift card or store credit?",
            "answer": "Enter the gift card code in the 'Gift Card' field at checkout. Store credits are automatically applied. You can check your gift card balance at Settings > Gift Cards. Remaining balances carry forward to future orders. Gift cards never expire."
        },
        {
            "question": "What is your subscription cancellation and billing policy?",
            "answer": "Cancel your subscription anytime at Settings > Subscriptions > Cancel. You'll retain access until the end of your current billing period. No partial refunds for mid-cycle cancellations. Annual subscribers cancelling within 30 days of renewal get a full refund."
        },
        {
            "question": "Are there any hidden fees I should know about?",
            "answer": "No hidden fees — ever. The price at checkout is the final price you pay, including itemized tax and shipping. International orders may incur customs duties charged by your country's customs authority, which are displayed as estimates at checkout."
        },
        {
            "question": "How do I transfer store credit to another user?",
            "answer": "Store credits are non-transferable between accounts for security reasons. However, you can purchase a digital gift card using your store credit and send it to another user. Gift cards can be purchased in any denomination from $5 to $500."
        },
        {
            "question": "What happens if my free trial expires?",
            "answer": "When your free trial ends, you'll be asked to select a paid plan to continue using premium features. No charges are made automatically — you must explicitly upgrade. Your data is preserved for 30 days after trial expiration, giving you time to decide."
        },
        {
            "question": "How do I get a tax invoice for my business purchases?",
            "answer": "Switch to a Business account at Settings > Account Type, then add your business details (name, tax ID, address). All future invoices will include your business information. Previous orders can be re-issued as business invoices upon request."
        },
        {
            "question": "Do you offer loyalty points or cashback rewards?",
            "answer": "Yes! Our Rewards program earns 1 point per $1 spent. Earn bonus points for reviews (50 pts), referrals (200 pts), and birthday (100 pts). Redeem 100 points for $1 off. Points never expire as long as your account remains active with purchases every 12 months."
        },
        {
            "question": "How long does a payment refund take to process?",
            "answer": "Refunds are initiated within 24 hours of approval. Credit/debit cards take 5-10 business days to reflect the refund. PayPal refunds appear within 3-5 business days. Store credits are applied instantly. Check with your bank if the refund doesn't appear after the expected timeframe."
        },
    ],
    "Product Information": [
        {
            "question": "How do I find product specifications and details?",
            "answer": "Every product page includes a 'Specifications' tab with detailed technical specs, dimensions, weight, materials, and compatibility info. You can also find downloadable spec sheets, user manuals, and comparison tools on premium product pages."
        },
        {
            "question": "Are your product reviews genuine and verified?",
            "answer": "Yes, all reviews marked 'Verified Purchase' are from customers who actually bought the product through our platform. We use AI-powered review moderation to filter spam and fake reviews. We never pay for or incentivize positive reviews."
        },
        {
            "question": "How do I compare multiple products side by side?",
            "answer": "Click the 'Compare' checkbox on up to 4 product cards, then click the 'Compare Selected' bar that appears at the bottom. This opens a detailed comparison table showing specs, pricing, ratings, and feature differences across your selections."
        },
        {
            "question": "Can I get notified when an out-of-stock product is available?",
            "answer": "Yes, click the 'Notify Me' button on any out-of-stock product page. Enter your email and you'll receive an alert within minutes of restocking. We also show estimated restock dates when available. Back-in-stock notifications have a 90% accuracy rate."
        },
        {
            "question": "What warranty do your products come with?",
            "answer": "Most products include the manufacturer's standard warranty (typically 1-2 years). Electronics carry a minimum 1-year warranty. Extended warranty plans (2 or 3 additional years) can be purchased at checkout for eligible products. Warranty claims are processed within 5 business days."
        },
        {
            "question": "Do you sell refurbished or open-box products?",
            "answer": "Yes, our 'Renewed' collection features certified refurbished products tested to work like new, with a 90-day guarantee. Open-box items are discounted 15-30% and include original accessories. Both categories are clearly labeled with condition grades (A/B/C)."
        },
        {
            "question": "How often are new products added to the catalog?",
            "answer": "We add 50-100 new products weekly across all categories. Major product launches happen monthly. Follow our 'New Arrivals' page or subscribe to category-specific newsletters to stay updated. Pre-order options are available for highly anticipated releases."
        },
        {
            "question": "Can I request a product that you don't currently carry?",
            "answer": "Absolutely! Use the 'Request a Product' form under Help > Suggestions. Include the product name, brand, and where you've seen it. Our merchandising team reviews all requests monthly, and popular requests are prioritized for addition."
        },
        {
            "question": "What does the product compatibility checker do?",
            "answer": "The compatibility checker on accessory pages lets you enter your device model to verify if the accessory will work with your specific device. It checks against our database of 50,000+ device models. Results show 'Compatible,' 'Partially Compatible,' or 'Not Compatible.'"
        },
        {
            "question": "Are your product images accurate representations?",
            "answer": "We strive for 100% accuracy in product photography. All images are professionally shot under standardized lighting. Colors may vary slightly due to monitor calibration. Products include multiple angles, zoom capability, and many feature 360-degree view or video demos."
        },
        {
            "question": "How do I read and interpret product ratings?",
            "answer": "Products are rated 1-5 stars. Our algorithm weighs recent reviews more heavily and factors in review quality. A 'Quality Score' badge appears for products with 4.0+ stars and 50+ reviews. You can filter reviews by star rating, date, and whether they include photos."
        },
        {
            "question": "Do you provide product samples or trials?",
            "answer": "Select beauty, skincare, and food categories offer free sample packs with qualifying orders. Software products typically include 14-30 day free trials. Some electronics can be tried risk-free for 30 days under our 'Try Before You Buy' program."
        },
        {
            "question": "What materials are used in your eco-friendly product line?",
            "answer": "Our Green Collection features products made from recycled materials (recycled plastic, reclaimed wood, organic cotton), sustainably sourced components, and biodegradable packaging. Each product displays its environmental certifications (FSC, GOTS, Cradle to Cradle)."
        },
        {
            "question": "How do I find products on sale or with discounts?",
            "answer": "Visit our 'Deals' page for current promotions, or use the 'Sort by: Price – Lowest' filter on category pages. Enable 'Price Drop Alerts' on product pages to be notified of discounts. Members get early access to sales events, and flash sales run every Friday."
        },
        {
            "question": "Can I purchase products in bulk or wholesale?",
            "answer": "Yes, our Business portal offers bulk pricing with tiered discounts: 10+ units (5% off), 50+ units (15% off), 100+ units (25% off). Create a Business account and contact our B2B team for custom quotes on large orders. Net-30 payment terms available."
        },
        {
            "question": "What are your best-selling products right now?",
            "answer": "Visit the 'Trending' or 'Best Sellers' section on our homepage, updated in real-time based on sales velocity, reviews, and engagement. Each category also has its own best-sellers list. Our editorial team curates weekly 'Staff Picks' with expert recommendations."
        },
        {
            "question": "How do I check product availability in my area?",
            "answer": "On the product page, enter your ZIP code in the 'Check Availability' box. This shows in-stock status at nearby fulfillment centers and estimated delivery dates for your location. Some products are region-specific and may not be available in all areas."
        },
        {
            "question": "Do your products come with user manuals or guides?",
            "answer": "Yes, most products include physical manuals in the box and digital PDF versions on the product page under 'Documentation.' We also offer setup video tutorials, quick-start guides, and community forums with user tips for popular products."
        },
        {
            "question": "What is the difference between similar product models?",
            "answer": "Use our 'Compare Models' feature on product family pages to see a detailed breakdown of differences in specs, features, pricing, and target use cases. Our buying guides in the Learning Center also explain which model is best for different user needs."
        },
        {
            "question": "Are product bundles available at a discounted price?",
            "answer": "Yes, we curate product bundles offering 10-25% savings compared to purchasing items individually. Look for 'Bundle & Save' tags on compatible products. You can also build custom bundles on select product pages by adding recommended accessories."
        },
        {
            "question": "How do I write a product review?",
            "answer": "Go to My Orders > [Order] > 'Write a Review' next to the purchased item. Rate 1-5 stars, write your experience (minimum 20 characters), and optionally upload photos or videos. Reviews are moderated and published within 24-48 hours."
        },
        {
            "question": "What does 'pre-order' mean and when will I be charged?",
            "answer": "Pre-order reserves a product before its official release date. You're charged when the item ships, not when you place the pre-order. Pre-orders can be cancelled anytime before shipment. You'll receive the product on or shortly after the launch date."
        },
        {
            "question": "Do you offer product customization or engraving?",
            "answer": "Select products offer customization options including engraving (text and simple graphics), color selection, monogramming, and custom sizing. Look for the 'Customize' button on eligible product pages. Custom orders take 3-5 additional business days."
        },
        {
            "question": "Are replacement parts and accessories available separately?",
            "answer": "Yes, replacement parts and official accessories are available on the product's page under 'Related Accessories' and in our dedicated Accessories category. We stock parts for products up to 5 years after discontinuation. Third-party compatible options are also listed."
        },
        {
            "question": "How do I know if a product is authentic and not counterfeit?",
            "answer": "We source directly from manufacturers and authorized distributors. Every product includes an authenticity guarantee. Look for the 'Authentic' badge and serial number verification tool on the product page. We offer full refunds for any confirmed counterfeit products."
        },
    ],
    "Security & Privacy": [
        {
            "question": "How is my personal data protected?",
            "answer": "We employ enterprise-grade security: AES-256 encryption at rest, TLS 1.3 encryption in transit, SOC 2 Type II certified data centers, and regular third-party penetration testing. Your data is stored in geo-redundant facilities with 24/7 monitoring and intrusion detection systems."
        },
        {
            "question": "What data do you collect about me?",
            "answer": "We collect: account info (name, email, phone), order history, payment tokens (not full card numbers), device/browser info for security, and anonymized usage analytics. We never sell personal data to third parties. Full details are in our Privacy Policy."
        },
        {
            "question": "How do I request deletion of my personal data under GDPR?",
            "answer": "Go to Settings > Privacy > 'Request Data Deletion' or email privacy@example.com. Under GDPR Article 17, we process deletion requests within 30 days. Some data may be retained for legal compliance (tax records, fraud prevention) as disclosed in our retention policy."
        },
        {
            "question": "Do you share my information with third parties?",
            "answer": "We share limited data only with: payment processors (Stripe) for transactions, shipping carriers for delivery, and analytics providers (anonymized). We never sell your data. All third-party partners are contractually bound by data processing agreements and GDPR compliance."
        },
        {
            "question": "How do I enable two-factor authentication for extra security?",
            "answer": "Go to Settings > Security > Two-Factor Authentication. Choose SMS, email, or authenticator app (recommended). Scan the QR code with Google Authenticator, Authy, or Microsoft Authenticator. Generate and save backup codes for emergency access."
        },
        {
            "question": "What should I do if I suspect unauthorized access to my account?",
            "answer": "Immediately: 1) Change your password, 2) Enable 2FA if not already active, 3) Check Settings > Security > Active Sessions and revoke unknown devices, 4) Review recent orders and payment methods, 5) Contact support for a security audit. We'll lock the account if needed."
        },
        {
            "question": "How do I manage cookie preferences?",
            "answer": "Click the cookie icon in the bottom-left corner or go to Settings > Privacy > Cookie Preferences. You can toggle: Essential (always on), Analytics, Functional, and Advertising cookies independently. We respect Do Not Track browser signals."
        },
        {
            "question": "Is my payment information stored securely?",
            "answer": "Payment data is handled by Stripe, a PCI-DSS Level 1 certified processor. We only store tokenized references — never your actual card numbers, CVVs, or PINs. Tokens are encrypted with AES-256 and can only be used within our payment system."
        },
        {
            "question": "What is your data retention policy?",
            "answer": "Account data: retained while active + 30 days after deletion. Order history: 7 years (tax compliance). Payment tokens: until card removal. Analytics: anonymized after 24 months. Chat/support logs: 3 years. You can request earlier deletion for non-regulated data."
        },
        {
            "question": "How do I report a security vulnerability?",
            "answer": "Email security@example.com with details. We run a responsible disclosure program — confirmed vulnerabilities earn bounties from $100-$10,000 depending on severity. Do not publicly disclose vulnerabilities before we've had 90 days to address them."
        },
        {
            "question": "Do you comply with GDPR, CCPA, and other privacy regulations?",
            "answer": "Yes, we fully comply with GDPR (EU), CCPA/CPRA (California), LGPD (Brazil), PIPEDA (Canada), and POPIA (South Africa). Our Data Protection Officer oversees compliance. We conduct annual privacy audits and maintain detailed data processing records."
        },
        {
            "question": "How do I opt out of marketing communications?",
            "answer": "Click 'Unsubscribe' at the bottom of any marketing email, or go to Settings > Notifications > Marketing and toggle off all channels. Transactional emails (order confirmations, security alerts) cannot be opted out of as they contain essential service information."
        },
        {
            "question": "Can I see a log of all activity on my account?",
            "answer": "Yes, go to Settings > Security > Activity Log. This shows all logins, password changes, payment method updates, order placements, and profile edits with timestamps, IP addresses, and device info for the past 90 days."
        },
        {
            "question": "What is your policy on law enforcement data requests?",
            "answer": "We review every government request individually. We require valid legal process (subpoena, court order, or warrant) and notify affected users when legally permitted. We publish an annual Transparency Report detailing the number and nature of requests received."
        },
        {
            "question": "How do I know if my account has been involved in a data breach?",
            "answer": "In the unlikely event of a breach affecting your data, we'll notify you via email and in-app alert within 72 hours as required by GDPR. We monitor for breaches continuously using threat intelligence feeds. You can check your email at haveibeenpwned.com independently."
        },
        {
            "question": "What encryption standards do you use?",
            "answer": "Data at rest: AES-256 encryption. Data in transit: TLS 1.3 with HSTS. Passwords: bcrypt with per-user salts and 12+ work factor rounds. API keys: SHA-256 hashing. Database backups: encrypted and stored in separate geographic regions."
        },
        {
            "question": "Can I restrict my account to specific IP addresses?",
            "answer": "Business accounts can enable IP whitelisting at Settings > Security > IP Restrictions. Add trusted IP addresses or CIDR ranges. Login attempts from non-whitelisted IPs will be blocked and you'll receive a security alert. This feature is available on Pro and Enterprise plans."
        },
        {
            "question": "How do I revoke third-party app access to my account?",
            "answer": "Go to Settings > Connected Apps & Services. You'll see all authorized third-party applications. Click 'Revoke Access' next to any app you want to disconnect. This immediately invalidates their OAuth tokens and they can no longer access your data."
        },
        {
            "question": "Does your platform use AI, and how does it affect my data?",
            "answer": "We use AI for search relevance, product recommendations, and customer support chatbot responses. AI processing is done on our servers, not shared externally. Your personal data used for AI is anonymized. You can opt out of personalized AI features in Settings > Privacy."
        },
        {
            "question": "What happens to my data during a system backup?",
            "answer": "Backups are encrypted (AES-256) and stored in geographically separate data centers. Backup data is subject to the same access controls as live data. Backups older than 90 days are automatically purged. Deleted account data is removed from backups within 30 days."
        },
        {
            "question": "How secure is the password reset process?",
            "answer": "Password reset links use cryptographically random tokens, expire after 1 hour, and can only be used once. We verify the request against the registered email. If suspicious activity is detected (e.g., foreign IP), additional identity verification is required."
        },
        {
            "question": "Do you perform background security testing?",
            "answer": "Yes, we conduct quarterly penetration tests by independent security firms, continuous automated vulnerability scanning, and annual SOC 2 Type II audits. Our security team monitors for threats 24/7 using SIEM tools and automated anomaly detection."
        },
        {
            "question": "Can I configure login notifications for my account?",
            "answer": "Yes, go to Settings > Security > Login Notifications. Options include: email alerts for each login, push notifications for logins from new devices, and weekly security summaries. You can also enable 'Require approval for new device' for maximum security."
        },
        {
            "question": "What is your child privacy protection policy?",
            "answer": "We comply with COPPA and do not knowingly collect data from children under 13 (or 16 in the EU). If we discover a child's account, it's promptly deleted. Parental consent is required for users aged 13-18 in applicable jurisdictions."
        },
        {
            "question": "How do I download a copy of all data you hold about me?",
            "answer": "Go to Settings > Privacy > 'Download My Data' to submit a GDPR/CCPA data access request. We'll compile your complete data portfolio (profile, orders, messages, analytics) into a machine-readable format (JSON/CSV) within 72 hours, emailed as a secure download link."
        },
    ],
    "Returns & Refunds": [
        {
            "question": "What is your return policy?",
            "answer": "We offer a 30-day hassle-free return policy on most items. Products must be in original condition with tags and packaging. Electronics have a 15-day return window. Perishable goods, personalized items, and intimate apparel are final sale. Start a return at My Orders > 'Return Item.'"
        },
        {
            "question": "How do I initiate a return?",
            "answer": "Go to My Orders, select the order, and click 'Return Item.' Choose the item(s) and reason for return. You'll receive a prepaid shipping label via email. Pack the item securely and drop it off at the designated carrier location. Returns are processed within 5-7 business days of receipt."
        },
        {
            "question": "Do I have to pay for return shipping?",
            "answer": "Return shipping is free for defective items, wrong items, or our errors. For change-of-mind returns, a flat $5.99 return shipping fee is deducted from your refund. Premium members enjoy free return shipping on all items. We provide prepaid labels for all returns."
        },
        {
            "question": "How long does it take to receive my refund?",
            "answer": "Once we receive your return, inspection takes 2-3 business days. Refunds are then processed: credit/debit cards (5-10 business days), PayPal (3-5 business days), store credit (instant). You'll receive email confirmation at each stage of the process."
        },
        {
            "question": "Can I exchange an item instead of returning it?",
            "answer": "Yes! Select 'Exchange' instead of 'Return' in My Orders. Choose the replacement item (different size, color, or variant). If the exchange item costs more, you'll pay the difference. If it costs less, we'll refund the difference. Exchanges ship with free express shipping."
        },
        {
            "question": "What items are not eligible for return?",
            "answer": "Non-returnable items include: gift cards, downloaded software/digital content, perishable goods, personalized/custom items, intimate apparel, hazardous materials, and items marked 'Final Sale.' Defective items in these categories can still be returned for a refund."
        },
        {
            "question": "Can I return an item without the original packaging?",
            "answer": "We prefer returns in original packaging, but it's not strictly required for most items. The item must be in resalable condition. Electronics and high-value items must include all original accessories, manuals, and cables. Missing packaging may result in a 15% restocking fee."
        },
        {
            "question": "What if I received a damaged or defective item?",
            "answer": "Contact us within 48 hours with photos of the damage. We'll arrange free return shipping and either send a replacement immediately (before receiving the damaged item back) or issue a full refund — your choice. No restocking fees apply for damaged/defective items."
        },
        {
            "question": "Can I return an item purchased with a gift card?",
            "answer": "Yes, items purchased with a gift card are refunded as store credit to a new digital gift card emailed to you. The store credit never expires and can be used on any future purchase. If the purchase used multiple payment methods, each is refunded proportionally."
        },
        {
            "question": "How do I track my return shipment?",
            "answer": "Use the prepaid return label tracking number (included in your return confirmation email) to track the shipment on the carrier's website. We also send you notifications when: return label is created, package is in transit, return is received, and refund is processed."
        },
        {
            "question": "What is a restocking fee and when does it apply?",
            "answer": "A 15% restocking fee applies to: opened electronics returned after 7 days, items without original packaging, and large/heavy items requiring special handling. Restocking fees never apply to defective items, wrong items, or returns within 48 hours of delivery."
        },
        {
            "question": "Can I return an item purchased during a sale?",
            "answer": "Yes, sale items follow the same 30-day return policy. Your refund will be for the price you actually paid (sale price), not the original retail price. Clearance items marked 'Final Sale' cannot be returned except for defects."
        },
        {
            "question": "I received the wrong item. What should I do?",
            "answer": "We sincerely apologize! Contact support or go to My Orders > 'Report Issue' > 'Wrong Item Received.' We'll ship the correct item immediately with expedited shipping at no charge and provide a prepaid label for the wrong item. Keep the wrong item if we instruct you to."
        },
        {
            "question": "How do I return a gift I received?",
            "answer": "If the gift included a gift receipt, use the gift return code on our website to initiate a return. Refunds for gift returns are issued as store credit. Without a gift receipt, we can look up the order using the gift-giver's email with their permission."
        },
        {
            "question": "Can I return items to a physical store location?",
            "answer": "If you're near one of our retail locations, you can return online purchases in-store for instant processing. Bring the item, your order confirmation (email or app), and a valid photo ID. In-store returns are processed faster and refunds appear within 3-5 business days."
        },
        {
            "question": "What if my return is rejected or denied?",
            "answer": "If a return is denied due to condition issues (heavy use, damage, missing parts), we'll email you with specific reasons and photos. You can: 1) Appeal the decision, 2) Request the item be shipped back to you, or 3) Accept a partial refund if applicable."
        },
        {
            "question": "Do you offer free returns for all items?",
            "answer": "Premium members enjoy unlimited free returns. Standard accounts get free returns on defective/wrong items. Change-of-mind returns incur a $5.99 fee. During promotional events, we occasionally offer free returns for all customers as a limited-time benefit."
        },
        {
            "question": "How do partial refunds work?",
            "answer": "Partial refunds are issued when: items are returned in less-than-original condition (worn, missing parts), after the standard return window (at our discretion), or when a restocking fee applies. The refund amount is determined during inspection and communicated before processing."
        },
        {
            "question": "Can I cancel a return I already initiated?",
            "answer": "Yes, if you haven't shipped the return yet, go to My Orders > Returns and click 'Cancel Return.' If the item is already in transit, contact support immediately. Once we receive and inspect the return, the cancellation window closes and the refund process begins."
        },
        {
            "question": "What is your warranty claim vs. return policy difference?",
            "answer": "Returns are for dissatisfaction within 30 days — you get a refund. Warranty claims are for defects that develop after the return window but within the warranty period — you get a repair, replacement, or credit. Warranty claims go through the manufacturer or our extended warranty team."
        },
        {
            "question": "How do I return a subscription box or recurring delivery item?",
            "answer": "Individual items from subscription boxes can be returned within 15 days of delivery. To stop future deliveries, cancel the subscription at Settings > Subscriptions. Returns on subscription items are refunded as store credit, not back to the original payment method."
        },
        {
            "question": "Is there a holiday extended return policy?",
            "answer": "Yes! Items purchased between November 1 and December 31 have an extended return window until January 31 of the following year. This gives gift recipients plenty of time to decide. The extended policy applies to all returnable items, including sale items."
        },
        {
            "question": "What condition must returned items be in?",
            "answer": "Items should be unworn/unused with original tags, accessories, and packaging. Light inspection (trying on clothing, testing electronics) is acceptable. Items showing signs of extended use, washing, or damage beyond inspection may be subject to partial refund or rejection."
        },
        {
            "question": "How do I return oversized or heavy items like furniture?",
            "answer": "For items over 70 lbs or oversized dimensions, we arrange a carrier pickup from your address at no cost for defective items. For change-of-mind returns, a pickup fee of $49.99 applies. Schedule a pickup window when initiating the return."
        },
        {
            "question": "Can I get an instant refund before the return arrives?",
            "answer": "Trusted customers with a positive return history may qualify for 'Instant Refund' — credited immediately upon shipping the return. This is automatically offered at checkout for eligible returns. If the return is not received within 14 days, the refund may be reversed."
        },
    ],
    "General & Company": [
        {
            "question": "What are your customer service hours?",
            "answer": "Our support team is available: Live Chat — 24/7/365, Phone — Mon–Fri 8 AM to 10 PM EST, Sat–Sun 9 AM to 6 PM EST, Email — responses within 4 hours during business hours. Holiday hours may vary and are posted on our Contact page in advance."
        },
        {
            "question": "How do I contact customer support?",
            "answer": "Multiple channels: Live Chat (click the chat icon bottom-right), Phone (1-800-EXAMPLE), Email (support@example.com), Social Media (@examplesupport on Twitter/X and Facebook), or submit a ticket via Help > Contact Us. Average response times are under 5 minutes for chat."
        },
        {
            "question": "Where is your company headquartered?",
            "answer": "Our headquarters is in San Francisco, California, with additional offices in New York, London, Singapore, and Bangalore. Our fulfillment centers are strategically located across the US, EU, and Asia-Pacific to ensure fast delivery worldwide."
        },
        {
            "question": "Do you have a mobile app?",
            "answer": "Yes! Download our app from the Apple App Store (iOS 15+) or Google Play Store (Android 10+). The app offers exclusive features: barcode scanning, AR product preview, push notifications for deals, and faster checkout with biometric authentication."
        },
        {
            "question": "What is your company's mission and values?",
            "answer": "Our mission is to deliver exceptional products with outstanding customer experience while maintaining ethical business practices. Our core values: Customer First, Innovation, Transparency, Sustainability, and Inclusivity guide every decision we make."
        },
        {
            "question": "Are you hiring? How do I apply for a job?",
            "answer": "Yes, we're always looking for talented people! Visit our Careers page at careers.example.com for current openings. We offer competitive salaries, equity, remote work options, unlimited PTO, and comprehensive benefits. Most positions allow remote or hybrid work."
        },
        {
            "question": "Do you have a referral or affiliate program?",
            "answer": "Yes! Our referral program gives you and your friend $20 off when they make their first purchase using your referral link. Our affiliate program offers 5-12% commission on sales generated through your content. Sign up at partners.example.com."
        },
        {
            "question": "How do I provide feedback about my experience?",
            "answer": "We value your feedback! Options: post-interaction surveys (emailed after support tickets), the feedback form at Help > Share Feedback, our community forums, or email feedback@example.com directly. We read every submission and implement top suggestions quarterly."
        },
        {
            "question": "Do you have a blog or learning center?",
            "answer": "Yes, our Learning Center (blog.example.com) features buying guides, product tutorials, industry news, and expert tips updated weekly. We also publish an email newsletter every Thursday with curated content. All content is free and doesn't require registration."
        },
        {
            "question": "What social media platforms are you active on?",
            "answer": "Follow us: Instagram (@example), Twitter/X (@example), Facebook (facebook.com/example), YouTube (youtube.com/example), LinkedIn (linkedin.com/company/example), and TikTok (@example). We share product launches, behind-the-scenes content, and exclusive deals."
        },
        {
            "question": "Do you have physical retail store locations?",
            "answer": "We operate 25 flagship stores in major US cities and 10 international locations. Find your nearest store at example.com/stores. Stores offer in-person shopping, product demos, repair services, and same-day pickup for online orders."
        },
        {
            "question": "What are your sustainability and environmental initiatives?",
            "answer": "We're committed to carbon neutrality by 2027. Current initiatives: 100% renewable energy in operations, plastic-free packaging goal by 2026, certified B Corporation status, 1% of revenue donated to environmental organizations, and a product recycling program."
        },
        {
            "question": "How do I become a brand ambassador or partner?",
            "answer": "Apply at partners.example.com/ambassadors. We look for passionate community members with authentic voices. Ambassadors receive product samples, exclusive discounts (30%), early access to launches, and commission on referred sales. All social media sizes welcome."
        },
        {
            "question": "Do you offer corporate or enterprise solutions?",
            "answer": "Yes, our Enterprise team provides bulk purchasing, custom branding, dedicated account management, volume discounts, and API integrations. Contact enterprise@example.com or call our business line for a tailored proposal. We serve Fortune 500 companies and SMBs alike."
        },
        {
            "question": "What charitable organizations do you support?",
            "answer": "We partner with: UNICEF (children's education), The Ocean Cleanup (environmental), Habitat for Humanity (housing), and local food banks. Our 'Purchase with Purpose' program donates $1 per order to your chosen charity. Employees receive paid volunteer days."
        },
        {
            "question": "How do I report a counterfeit or fraudulent listing?",
            "answer": "Click 'Report' on any suspicious product listing, or email trust@example.com with the listing URL and concerns. Our Trust & Safety team investigates all reports within 24 hours. Confirmed counterfeit listings are removed and sellers are permanently banned."
        },
        {
            "question": "What accessibility accommodations do you provide?",
            "answer": "Our platform complies with WCAG 2.1 AA standards. Features include: screen reader compatibility, keyboard-only navigation, high contrast mode, adjustable text size, video captions, alt text on images, and an accessibility statement at example.com/accessibility."
        },
        {
            "question": "Do you offer gift cards?",
            "answer": "Yes! Digital gift cards ($10–$500) are delivered instantly via email. Physical gift cards ($25–$200) ship in premium packaging, perfect for gifting. Gift cards never expire and can be used across our entire catalog. Check your balance at Settings > Gift Cards."
        },
        {
            "question": "How do I unsubscribe from emails or newsletters?",
            "answer": "Click 'Unsubscribe' at the bottom of any email, or go to Settings > Notifications > Email Preferences and deselect the categories you want to opt out of. You can also reply 'STOP' to any SMS message. Changes take effect within 24 hours."
        },
        {
            "question": "What is your dispute resolution or arbitration policy?",
            "answer": "We prefer resolving issues directly — contact support first. If unsatisfied, request escalation to a senior specialist. For unresolved disputes, we offer free mediation through an independent ombudsman. Formal arbitration details are in our Terms of Service, Section 12."
        },
        {
            "question": "How do I stay informed about product recalls or safety notices?",
            "answer": "We email affected customers directly for any recall. Safety notices are posted at example.com/safety. Enable 'Safety Alerts' in notification settings for proactive updates. We work closely with the CPSC and relevant authorities on all recall actions."
        },
        {
            "question": "Do you price match competitors?",
            "answer": "Yes! We offer a Price Match Guarantee against authorized retailers. Find a lower price within 14 days of purchase? Contact us with proof (URL or screenshot). We'll match the price and give you an additional 5% off. Excludes marketplace sellers and flash sales."
        },
        {
            "question": "What are your terms of service and legal policies?",
            "answer": "Our Terms of Service, Privacy Policy, Cookie Policy, and Acceptable Use Policy are available at example.com/legal. These documents are written in plain language and last updated quarterly. We notify registered users of any material changes via email 30 days in advance."
        },
        {
            "question": "Can I visit your office or headquarters for a tour?",
            "answer": "We offer monthly campus tours at our San Francisco headquarters for students, partners, and community members. RSVP at example.com/visits. Tours include our innovation lab, fulfillment demo, and a Q&A with team members. Virtual tours are available on request."
        },
        {
            "question": "How has the company grown since it was founded?",
            "answer": "Founded in 2018 with a team of 5, we've grown to 2,000+ employees across 6 countries, serving over 10 million customers worldwide. Key milestones: Series B funding (2020), B Corporation certification (2022), carbon neutrality commitment (2023), and global expansion (2024)."
        },
    ],
}


def seed_categories() -> dict[str, int]:
    """Seed the categories table and return a name-to-ID mapping.

    Returns:
        dict[str, int]: Mapping of category name to database ID.

    Time Complexity: O(C) where C is the number of categories
    Space Complexity: O(C)
    """
    category_map: dict[str, int] = {}

    for cat in CATEGORIES:
        # Check if category already exists
        existing = execute_query(
            "SELECT id FROM categories WHERE name = ?",
            (cat["name"],),
            fetch_one=True,
        )
        if existing:
            category_map[cat["name"]] = existing["id"]
        else:
            cat_id = execute_query(
                "INSERT INTO categories (name, icon) VALUES (?, ?)",
                (cat["name"], cat["icon"]),
            )
            category_map[cat["name"]] = cat_id

    return category_map


def seed_faqs(category_map: dict[str, int]) -> int:
    """Seed the FAQs table with all 200 programmatically defined entries.

    Args:
        category_map: Mapping of category name to database ID.

    Returns:
        int: Total number of FAQs inserted.

    Time Complexity: O(F) where F is the total FAQ count (200)
    Space Complexity: O(F)
    """
    total_inserted: int = 0

    for category_name, faq_list in FAQS.items():
        cat_id: int = category_map[category_name]

        for faq in faq_list:
            # Check for duplicate
            existing = execute_query(
                "SELECT id FROM faqs WHERE question = ? AND category_id = ?",
                (faq["question"], cat_id),
                fetch_one=True,
            )
            if not existing:
                execute_query(
                    "INSERT INTO faqs (category_id, question, answer) VALUES (?, ?, ?)",
                    (cat_id, faq["question"], faq["answer"]),
                )
                total_inserted += 1

    return total_inserted


def main() -> None:
    """Execute the full database seeding pipeline.

    Pipeline:
        1. Initialize database schema
        2. Seed categories
        3. Seed 200 FAQs across 8 categories
        4. Report results

    Time Complexity: O(C + F) where C=categories, F=FAQs
    Space Complexity: O(F) for the FAQ data structures
    """
    print("=" * 60)
    print("  CodeAlpha FAQ Chatbot — Database Seeder")
    print("  Registration ID: Akshay Saxena")
    print("=" * 60)

    # Step 1: Initialize schema
    print("\n[1/3] Initializing database schema...")
    init_database()

    # Step 2: Seed categories
    print("[2/3] Seeding categories...")
    category_map: dict[str, int] = seed_categories()
    print(f"       ✅ {len(category_map)} categories ready.")

    # Step 3: Seed FAQs
    print("[3/3] Seeding FAQs...")
    total: int = seed_faqs(category_map)
    print(f"       ✅ {total} FAQs inserted.")

    # Summary
    total_in_db = execute_query(
        "SELECT COUNT(*) AS count FROM faqs",
        fetch_one=True,
    )
    print(f"\n{'=' * 60}")
    print(f"  Total FAQs in database: {total_in_db['count']}")
    print(f"  Categories: {len(category_map)}")

    for name, cat_id in category_map.items():
        count = execute_query(
            "SELECT COUNT(*) AS count FROM faqs WHERE category_id = ?",
            (cat_id,),
            fetch_one=True,
        )
        icon = next(c["icon"] for c in CATEGORIES if c["name"] == name)
        print(f"    {icon} {name}: {count['count']} FAQs")

    print(f"{'=' * 60}")
    print("  ✅ Database seeding complete!")


if __name__ == "__main__":
    main()
