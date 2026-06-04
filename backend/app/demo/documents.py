"""
50 pre-built sample documents for demo purposes.
Includes contracts, invoices, reports, and correspondence — with ~10 designed
to trigger specific failure modes in the pipeline.

Failure-inducing documents are tagged with comments explaining what should break.
"""

from __future__ import annotations

from app.models import RawDocument


def get_demo_documents() -> list[RawDocument]:
    """Return all 50 demo documents."""
    return [RawDocument(content=d["content"], source=d["source"], metadata=d.get("metadata", {})) for d in DEMO_DOCS]


DEMO_DOCS = [
    # ═══════════════════════════════════════════════════════════════════════════
    # CONTRACTS (15 total, 5 failure-inducing)
    # ═══════════════════════════════════════════════════════════════════════════

    {
        "source": "demo_contract_01",
        "content": """CONSULTING SERVICES AGREEMENT

This Consulting Services Agreement ("Agreement") is entered into as of January 15, 2025, by and between Meridian Tech Solutions Inc., a Delaware corporation ("Company"), and Sarah Chen, an independent consultant ("Consultant").

1. SCOPE OF SERVICES
The Consultant shall provide software architecture review and optimization services for the Company's cloud infrastructure platform, including but not limited to: system design review, performance analysis, and security assessment.

2. COMPENSATION
The Company shall pay the Consultant a fixed fee of $45,000 for the engagement, payable in three installments of $15,000 each upon completion of each project milestone.

3. TERM
This Agreement shall commence on February 1, 2025, and shall continue until April 30, 2025, unless terminated earlier in accordance with Section 7.

4. CONFIDENTIALITY
The Consultant agrees to maintain strict confidentiality regarding all proprietary information, trade secrets, and business strategies disclosed during the engagement.

Signed:
_________________          _________________
Meridian Tech Solutions    Sarah Chen
Date: January 15, 2025    Date: January 15, 2025"""
    },

    {
        "source": "demo_contract_02",
        "content": """NON-DISCLOSURE AGREEMENT

This Non-Disclosure Agreement ("NDA") is made effective as of March 3, 2025, between Quantum Dynamics Corp ("Disclosing Party") and Robert Alvarez ("Receiving Party").

WHEREAS, the Disclosing Party possesses certain confidential and proprietary information relating to quantum computing algorithms and hardware specifications;

WHEREAS, the Receiving Party desires to receive certain confidential information for the purpose of evaluating a potential business collaboration;

NOW, THEREFORE, in consideration of the mutual covenants herein, the parties agree as follows:

1. Definition of Confidential Information: All technical data, trade secrets, algorithms, source code, hardware designs, business plans, customer lists, and financial information.

2. Obligations: The Receiving Party shall hold and maintain the Confidential Information in strict confidence for the sole and exclusive benefit of the Disclosing Party.

3. Term: This NDA shall remain in effect for a period of three (3) years from the date of execution.

4. Remedies: The Receiving Party acknowledges that any breach may cause irreparable harm and that the Disclosing Party shall be entitled to seek equitable relief.

IN WITNESS WHEREOF, the parties have executed this Agreement.

Quantum Dynamics Corp          Robert Alvarez
By: Dr. Emily Watson            Date: March 3, 2025
Title: Chief Technology Officer"""
    },

    {
        "source": "demo_contract_03",
        "content": """EMPLOYMENT CONTRACT

This Employment Contract is entered into between GlobalServe International Ltd. ("Employer") and Michael Torres ("Employee") effective April 1, 2025.

POSITION: Senior Data Engineer
DEPARTMENT: Data Infrastructure
REPORTING TO: VP of Engineering, Lisa Park
LOCATION: Austin, Texas (hybrid - 3 days in office)

COMPENSATION AND BENEFITS:
- Base Salary: $165,000 per annum
- Signing Bonus: $20,000 (subject to 1-year cliff)
- Annual Bonus: Up to 15% of base salary based on performance
- Equity: 5,000 RSUs vesting over 4 years with 1-year cliff
- Health Insurance: Comprehensive medical, dental, and vision
- PTO: 20 days per year plus 10 company holidays

TERM: This is an at-will employment agreement. Either party may terminate with 30 days written notice.

NON-COMPETE: Employee agrees to a 12-month non-compete clause covering direct competitors in the data infrastructure space within the United States.

Michael Torres                  GlobalServe International Ltd.
Date: March 25, 2025           By: James Bradford, HR Director
                                Date: March 25, 2025"""
    },

    # FAILURE: Contract with NO DATES — should confuse extraction
    {
        "source": "demo_contract_04_no_dates",
        "metadata": {"expected_failure": "extraction", "failure_type": "context_loss"},
        "content": """PARTNERSHIP AGREEMENT

This Partnership Agreement is made between TechForward Solutions and DataBridge Analytics for the purpose of jointly developing and marketing an integrated analytics platform.

The parties hereby agree to the following terms and conditions:

CONTRIBUTIONS:
- TechForward Solutions shall contribute its proprietary machine learning framework and engineering team resources.
- DataBridge Analytics shall contribute its data pipeline infrastructure and customer acquisition channels.

PROFIT SHARING:
Profits and losses shall be shared equally (50/50) between the partners.

MANAGEMENT:
Both partners shall have equal management rights and responsibilities. Major decisions require unanimous consent.

DISSOLUTION:
The partnership may be dissolved by mutual agreement or by either party providing written notice. Upon dissolution, assets shall be divided according to each partner's capital contribution.

GOVERNING LAW:
This agreement shall be governed by the laws of the State of California.

TechForward Solutions          DataBridge Analytics
By: _______________           By: _______________"""
    },

    # FAILURE: Contract with ambiguous parties — hard to tell who is who
    {
        "source": "demo_contract_05_ambiguous_parties",
        "metadata": {"expected_failure": "extraction", "failure_type": "extraction_hallucination"},
        "content": """SERVICE LEVEL AGREEMENT

The provider shall deliver services meeting the following service levels to the client organization per the terms discussed and agreed upon in previous correspondence dated sometime last quarter.

Uptime Guarantee: The platform shall maintain availability as previously agreed.
Response Time: Support tickets shall be addressed within the timeframes outlined in the appendix (see attached, not included here).
Data Processing: The system shall handle the volume requirements as specified in the technical requirements document referenced earlier.

Penalties for non-compliance with the above service levels shall be applied as outlined in the master services agreement between the parties.

The terms of this SLA shall be reviewed quarterly by both organizations and amended as necessary with mutual written consent.

This agreement supplements and is governed by the master services agreement currently in effect between the organizations."""
    },

    {
        "source": "demo_contract_06",
        "content": """SOFTWARE LICENSE AGREEMENT

This Software License Agreement ("License") is granted by NovaSoft Inc. ("Licensor") to Pinnacle Healthcare Group ("Licensee") effective May 1, 2025.

1. GRANT OF LICENSE
Licensor hereby grants Licensee a non-exclusive, non-transferable license to use the NovaCare Patient Management System ("Software") for a period of 24 months.

2. LICENSE FEE
Licensee shall pay an annual license fee of $125,000, payable in quarterly installments of $31,250.

3. SUPPORT AND MAINTENANCE
Licensor shall provide 24/7 technical support and quarterly software updates at no additional cost during the license period.

4. DATA SECURITY
The Software complies with HIPAA regulations. Licensor shall maintain SOC 2 Type II certification throughout the license term.

5. INTELLECTUAL PROPERTY
All intellectual property rights in the Software remain with the Licensor. Licensee acquires no ownership rights.

NovaSoft Inc.                    Pinnacle Healthcare Group
By: David Kim, CEO              By: Dr. Angela Martinez, COO
Date: April 28, 2025            Date: April 28, 2025"""
    },

    {
        "source": "demo_contract_07",
        "content": """REAL ESTATE LEASE AGREEMENT

This Lease Agreement is made on June 1, 2025, between Hartfield Property Management LLC ("Landlord") and Velocity Coworking Inc. ("Tenant").

PREMISES: Suite 400-410, Lakeside Business Center, 2200 Innovation Drive, Seattle, WA 98101
LEASE TERM: 36 months, commencing August 1, 2025, through July 31, 2028
MONTHLY RENT: $8,500 per month, with annual increases of 3%
SECURITY DEPOSIT: $17,000 (equivalent to 2 months' rent)

PERMITTED USE: General office, coworking space, and educational workshop facility.

MAINTENANCE: Landlord responsible for structural repairs, HVAC, and common areas. Tenant responsible for interior maintenance and janitorial services.

INSURANCE: Tenant shall maintain commercial general liability insurance with minimum coverage of $1,000,000.

Hartfield Property Management     Velocity Coworking Inc.
By: Patricia Hartfield             By: Jason Wu, Founder
Date: June 1, 2025               Date: June 1, 2025"""
    },

    {
        "source": "demo_contract_08",
        "content": """INDEPENDENT CONTRACTOR AGREEMENT

This Agreement is made as of February 10, 2025, between CloudScale Systems ("Client") and Priya Sharma ("Contractor").

SERVICES: The Contractor shall design and implement a Kubernetes-based microservices deployment pipeline, including CI/CD automation, monitoring dashboards, and disaster recovery procedures.

RATE: $175 per hour, not to exceed 160 hours per month.
ESTIMATED DURATION: 3 months (February 2025 - April 2025)
TOTAL ESTIMATED COST: $84,000

DELIVERABLES:
- Infrastructure-as-Code repository (Terraform/Pulumi)
- CI/CD pipeline configuration (GitHub Actions)
- Monitoring stack (Prometheus, Grafana, PagerDuty integration)
- Disaster recovery runbook and automated failover scripts
- Knowledge transfer sessions (minimum 4 hours)

PAYMENT TERMS: Net 15 from invoice submission. Invoices submitted bi-weekly.

CloudScale Systems               Priya Sharma
By: Tom Henderson, CTO           Date: February 10, 2025
Date: February 10, 2025"""
    },

    {
        "source": "demo_contract_09",
        "content": """DATA PROCESSING AGREEMENT

Effective Date: March 15, 2025

BETWEEN: FinEdge Analytics Inc. ("Data Processor") AND CrestBank Financial ("Data Controller")

PURPOSE: This agreement governs the processing of personal data by the Data Processor on behalf of the Data Controller in connection with the provision of fraud detection and risk analysis services.

CATEGORIES OF DATA SUBJECTS: Bank customers, account holders, transaction counterparties
TYPES OF PERSONAL DATA: Names, account numbers, transaction histories, IP addresses, device fingerprints
PROCESSING ACTIVITIES: Real-time transaction monitoring, pattern analysis, risk scoring, regulatory reporting

SECURITY MEASURES:
- AES-256 encryption at rest and in transit
- Multi-factor authentication for all system access
- Annual penetration testing by independent third party
- SOC 2 Type II compliance maintained continuously

DATA RETENTION: Processed data retained for 7 years per regulatory requirements. Raw data purged after 90 days.

BREACH NOTIFICATION: Processor shall notify Controller within 24 hours of discovering any data breach.

FinEdge Analytics Inc.           CrestBank Financial
By: Rachel Moore, DPO            By: Steven Park, CISO
Date: March 15, 2025            Date: March 15, 2025"""
    },

    # FAILURE: Ambiguous — could be contract or correspondence
    {
        "source": "demo_contract_10_ambiguous",
        "metadata": {"expected_failure": "classification", "failure_type": "misclassification"},
        "content": """Dear Board Members,

Following our discussion last Thursday, I wanted to confirm the key terms we agreed upon for the Henderson acquisition. As discussed, we'll proceed with the following:

- Purchase price: $4.2 million, subject to customary adjustments
- Closing target: End of Q3 2025
- Due diligence period: 60 days from today
- Key personnel retention: 18-month commitments from the top 5 leaders
- Earnout structure: Additional $800K based on Year 1 revenue targets

Please review and let me know if I've captured everything correctly. Our legal team at Morrison & Keats will prepare the formal purchase agreement once we have alignment.

I'll also need signatures from at least three board members before we can proceed with the LOI. Margaret, since you raised concerns about the earnout structure, perhaps we can discuss your proposed modifications at Monday's meeting?

Best regards,
Catherine Wells
Chief Executive Officer
Apex Ventures Group"""
    },

    {
        "source": "demo_contract_11",
        "content": """SUPPLY AGREEMENT

This Supply Agreement ("Agreement") is entered into as of January 20, 2025, by GreenLeaf Materials Co. ("Supplier") and EcoBuild Construction ("Buyer").

1. PRODUCTS: Sustainable building materials including recycled steel beams, bamboo composite panels, and eco-friendly insulation products as specified in Exhibit A.

2. MINIMUM ORDER: Buyer commits to minimum quarterly orders of $75,000.

3. PRICING: Fixed pricing for the first 12 months per the attached price schedule. Prices subject to annual review with maximum 5% increase.

4. DELIVERY: FOB destination, within 14 business days of order confirmation. Supplier bears risk of loss during transit.

5. QUALITY: All products must meet or exceed LEED certification standards. Supplier provides certificates of compliance with each shipment.

6. WARRANTY: Supplier warrants products for 10 years against material defects.

GreenLeaf Materials Co.          EcoBuild Construction
By: Mark Sullivan, VP Sales      By: Diana Reyes, Procurement Dir.
Date: January 20, 2025          Date: January 20, 2025"""
    },

    {
        "source": "demo_contract_12",
        "content": """MERGER AGREEMENT - SUMMARY OF TERMS

Parties: Orion Financial Services Inc. ("Orion") and Atlas Wealth Management LLC ("Atlas")
Effective Date: July 1, 2025
Structure: Stock-for-stock merger with Atlas merging into Orion

KEY TERMS:
Exchange Ratio: 1.35 Orion shares for each Atlas share
Total Transaction Value: Approximately $280 million based on Orion's current market capitalization
Board Composition: Combined board of 11 members (7 from Orion, 4 from Atlas)
CEO: Margaret Chen (current Orion CEO) to lead combined entity
Headquarters: Consolidated at Orion's Chicago headquarters

CONDITIONS PRECEDENT:
- Regulatory approval from SEC, FINRA, and state regulators
- Shareholder approval by both companies (majority vote required)
- No material adverse change in either company's financial condition
- Completion of due diligence by both parties

BREAK-UP FEE: $14 million payable by the terminating party

Orion Financial Services         Atlas Wealth Management
Margaret Chen, CEO               William Foster, Managing Partner
Date: May 15, 2025              Date: May 15, 2025"""
    },

    # FAILURE: Contract with mixed currencies — extraction should struggle
    {
        "source": "demo_contract_13_mixed_currencies",
        "metadata": {"expected_failure": "extraction", "failure_type": "extraction_hallucination"},
        "content": """INTERNATIONAL DISTRIBUTION AGREEMENT

This Distribution Agreement is made between KyotoTech Manufacturing KK (Japan) and EuroDistrib GmbH (Germany) effective April 1, 2025.

TERRITORY: European Union member states, United Kingdom, Switzerland, and Norway.

PRICING AND PAYMENTS:
- Product Line A (Consumer Electronics): ¥45,000,000 per quarter (approximately €280,000 at current exchange)
- Product Line B (Industrial Components): Base price of £125,000 per shipment, with volume discounts
- Product Line C (Specialty Parts): $89,500 USD per order, minimum 4 orders per year
- Payment terms vary by product line: Net 30 for JPY, Net 45 for GBP, Net 60 for USD
- All invoices subject to exchange rate adjustment clause (±5% band)
- Additional handling fee: CHF 2,500 per shipment to Switzerland

WARRANTY RESERVES: 3% of gross revenue held in escrow, denominated in EUR.

ANNUAL MINIMUM COMMITMENT: Equivalent of €1.2 million across all product lines.

KyotoTech Manufacturing KK       EuroDistrib GmbH
Takeshi Yamamoto, President       Klaus Mueller, Geschäftsführer
Date: March 28, 2025             Date: March 28, 2025"""
    },

    {
        "source": "demo_contract_14",
        "content": """RESEARCH COLLABORATION AGREEMENT

Between: Stanford University ("University") and BioGenesis Therapeutics Inc. ("Company")
Effective: September 1, 2025

PROJECT: Development of novel CRISPR-based gene therapy approaches for rare neurological disorders.

PRINCIPAL INVESTIGATOR: Dr. Amanda Liu, Department of Genetics

FUNDING:
- Company shall provide $2,400,000 over 3 years ($800,000 annually)
- University provides lab facilities, equipment access, and graduate student support
- Budget allocation: 60% personnel, 25% materials/supplies, 15% overhead

INTELLECTUAL PROPERTY:
- Pre-existing IP remains with the originating party
- Joint inventions: shared ownership with Company having first right of commercial license
- Publications: University retains right to publish, subject to 90-day Company review period

TERM: 3 years with option to extend for 2 additional years.

Stanford University               BioGenesis Therapeutics Inc.
Dr. Amanda Liu, PI                Dr. James Porter, CSO
Dr. Richard Hayes, VP Research    Date: August 20, 2025
Date: August 20, 2025"""
    },

    # FAILURE: Very short contract — minimal information for extraction
    {
        "source": "demo_contract_15_sparse",
        "metadata": {"expected_failure": "extraction", "failure_type": "context_loss"},
        "content": """MUTUAL NDA

Parties agree to keep shared info confidential. Standard terms apply. Duration: 2 years. Governing law: NY."""
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # INVOICES (12 total, 3 failure-inducing)
    # ═══════════════════════════════════════════════════════════════════════════

    {
        "source": "demo_invoice_01",
        "content": """INVOICE

Invoice Number: INV-2025-0847
Date: March 15, 2025
Due Date: April 14, 2025

FROM:
Brightpath Digital Agency
1250 Market Street, Suite 300
San Francisco, CA 94103
Tax ID: 82-4937281

BILL TO:
FreshCo Organic Foods Inc.
890 Broadway, 4th Floor
New York, NY 10003

DESCRIPTION OF SERVICES:

| Item | Description | Hours | Rate | Amount |
|------|-------------|-------|------|--------|
| 1 | Website Redesign - UX Research & Wireframing | 45 | $150 | $6,750 |
| 2 | Visual Design (Homepage + 8 interior pages) | 60 | $150 | $9,000 |
| 3 | Frontend Development (React/Next.js) | 80 | $175 | $14,000 |
| 4 | CMS Integration (Contentful) | 25 | $175 | $4,375 |
| 5 | QA Testing & Bug Fixes | 15 | $125 | $1,875 |

Subtotal: $36,000
Sales Tax (8.625%): $3,105
TOTAL DUE: $39,105

Payment Terms: Net 30. Late payments subject to 1.5% monthly interest.
Accepted Payment Methods: ACH Transfer, Wire Transfer, Check

Thank you for your business!"""
    },

    {
        "source": "demo_invoice_02",
        "content": """INVOICE #20250312

Vendor: Atlas Cloud Infrastructure
123 Technology Blvd, Austin, TX 78701
EIN: 47-2938571

Client: Redwood Health Systems
4500 Medical Center Drive, Portland, OR 97201

Invoice Date: March 12, 2025
Payment Due: April 11, 2025
PO Number: PO-RHS-2025-089

Services Rendered (February 2025):

Cloud Hosting (Enterprise Tier).............$12,500.00
Database Management (PostgreSQL cluster).....$3,200.00
CDN & Edge Computing.........................$1,800.00
Security Monitoring & SOC Services...........$4,500.00
Backup & Disaster Recovery...................$2,100.00
Professional Services (Migration Assist).....$6,400.00

Subtotal:           $30,500.00
Volume Discount:    -$3,050.00 (10%)
Subtotal after disc: $27,450.00
Tax:                 $0.00 (Tax exempt - healthcare)
TOTAL:              $27,450.00

Wire Transfer Details:
Bank: First National Bank
Routing: 021000021
Account: 483927156
Reference: INV-20250312"""
    },

    {
        "source": "demo_invoice_03",
        "content": """PURCHASE ORDER / INVOICE

PO Number: PO-2025-1547
Invoice Number: SI-88421
Date: February 28, 2025
Delivery Date: March 15, 2025

Seller: Precision Manufacturing Corp
2800 Industrial Way, Detroit, MI 48201

Buyer: SkyHigh Aerospace Engineering
7700 Space Center Blvd, Houston, TX 77058

ITEMS ORDERED:

1. Titanium alloy brackets (Ti-6Al-4V) x 500 units
   Unit Price: $45.00 | Total: $22,500.00

2. Carbon fiber composite panels (3mm) x 200 units
   Unit Price: $128.00 | Total: $25,600.00

3. Aerospace-grade fastener kit x 50 sets
   Unit Price: $89.00 | Total: $4,450.00

4. Custom machined mounting plates x 100 units
   Unit Price: $215.00 | Total: $21,500.00

Subtotal: $74,050.00
Shipping (freight): $2,800.00
Insurance: $740.50
TOTAL: $77,590.50

Terms: Net 45 | FOB: Destination
Quality Cert Required: AS9100D compliance documentation"""
    },

    # FAILURE: Invoice with mixed currencies — amounts ambiguous
    {
        "source": "demo_invoice_04_mixed_currencies",
        "metadata": {"expected_failure": "extraction", "failure_type": "extraction_hallucination"},
        "content": """INTERNATIONAL SERVICES INVOICE

Invoice: ISI-2025-0034
Date: April 5, 2025

Provider: MultiLingual Solutions AG, Zurich, Switzerland
Client: Pacific Trade Corporation, Singapore

Translation Services (March 2025):
- Japanese to English technical docs: ¥850,000
- German to English legal filings: €4,200
- Mandarin to English marketing: ¥125,000 (Chinese Yuan, NOT Japanese Yen)
- French to English correspondence: €1,800
- Hindi to English compliance docs: ₹245,000

Interpretation Services:
- Live conference interpretation (3 days): CHF 8,500
- Video remote interpretation (12 hrs): $2,400 USD

Technology Fee: SGD 1,200
Rush Surcharge: 15% applied to Japanese translations only

All amounts payable in USD at the exchange rate on invoice date.
Estimated USD Total: approximately $18,750

Payment: Wire transfer within 30 days."""
    },

    # FAILURE: Invoice with missing amounts — incomplete data
    {
        "source": "demo_invoice_05_missing_amounts",
        "metadata": {"expected_failure": "extraction", "failure_type": "context_loss"},
        "content": """INVOICE

From: QuickShip Logistics
To: Downtown Retail Partners

Invoice #: QS-9921
Date: March 20, 2025

Delivery Services - March 2025:

1. Standard deliveries (Zone A) - quantity as per daily manifests
2. Express deliveries (Zone B) - per agreed rate card
3. Weekend/holiday surcharges - applicable days TBD
4. Fuel surcharge - percentage to be calculated at month end
5. Insurance - as per master agreement terms

Previous balance: carried forward from February
Credits: pending review

TOTAL: To be finalized upon reconciliation

Please remit payment upon receipt of finalized invoice.
Contact billing@quickship.example.com for questions."""
    },

    {
        "source": "demo_invoice_06",
        "content": """TAX INVOICE

GST Invoice No: TI-2025-3892
Date of Issue: March 1, 2025
Supply Date: February 28, 2025

Supplier: DataVault Storage Solutions Pty Ltd
ABN: 51 824 753 961
Address: Level 12, 200 George Street, Sydney NSW 2000

Recipient: Canberra Federal Agency
ABN: 73 104 832 576

Description of Supply:

1. Enterprise NAS Storage (100TB) - $45,000.00
2. SSD Cache Modules (x8) - $12,000.00
3. Redundant Power Supply Units (x4) - $3,200.00
4. Installation & Configuration (40 hrs) - $8,000.00
5. 3-Year Premium Support Agreement - $15,000.00

Subtotal (excl. GST): $83,200.00
GST (10%): $8,320.00
TOTAL (incl. GST): $91,520.00

Payment Terms: Government Net 30
BSB: 032-051 | Account: 287463"""
    },

    {
        "source": "demo_invoice_07",
        "content": """FREELANCE INVOICE

From: Alex Rivera, Independent Designer
alex@riveradesign.co
123 Creative Lane, Portland, OR 97205

To: Sunset Brewing Company
456 Hop Avenue, Bend, OR 97701

Invoice #: AR-2025-014
Date: April 1, 2025
Due: April 15, 2025

Project: Complete Brand Identity Refresh

Phase 1: Discovery & Strategy
- Brand audit and competitor analysis: $2,500
- Customer persona development: $1,500
- Brand positioning workshop (2 days): $3,000

Phase 2: Visual Identity
- Logo design (5 concepts, 3 rounds revision): $5,000
- Color palette and typography system: $2,000
- Brand guidelines document (40 pages): $3,500

Phase 3: Applications
- Packaging design (6 SKUs): $9,000
- Merchandise templates (8 items): $2,400
- Social media templates (15 templates): $1,800

Subtotal: $30,700
Discount (returning client, 5%): -$1,535
TOTAL DUE: $29,165

Venmo: @alexrivera-design
PayPal: alex@riveradesign.co"""
    },

    {
        "source": "demo_invoice_08",
        "content": """MEDICAL BILLING STATEMENT

Provider: ClearView Ophthalmology Associates
NPI: 1234567890
Address: 3100 Eye Care Boulevard, Suite 200, Miami, FL 33101

Patient: Jennifer Walsh
DOB: 05/12/1988
Insurance: BlueCross BlueShield - Policy #BCB-992847

Date of Service: March 10, 2025

Services Rendered:
CPT 92004 - Comprehensive eye exam (new patient): $350.00
CPT 92134 - OCT scan, retina: $125.00
CPT 76514 - Corneal pachymetry: $75.00
CPT 92083 - Visual field examination: $200.00

Total Charges: $750.00
Insurance Adjustment: -$225.00
Insurance Payment: -$393.75
Patient Copay (collected): -$40.00

PATIENT BALANCE DUE: $91.25

Please remit within 30 days. Payment plan available for balances over $500."""
    },

    {
        "source": "demo_invoice_09",
        "content": """SUBSCRIPTION INVOICE

Acme SaaS Platform
Invoice #: ACME-2025-03-PRO
Billing Period: March 1 - March 31, 2025
Account: Westfield Media Group (ID: WMG-4821)

Plan: Enterprise Pro (Annual)
Base subscription (50 seats): $4,999/month

Add-ons:
- Additional seats (x20 @ $50/seat): $1,000
- Advanced Analytics module: $500
- API access (Premium tier): $750
- Priority support: $300
- Custom SSO integration: $200

Monthly Total: $7,749.00
Annual prepay discount applied: -$774.90

Amount Due This Period: $6,974.10

Auto-renewal date: January 1, 2026
Payment method: Visa ending in 4521"""
    },

    {
        "source": "demo_invoice_10",
        "content": """CATERING INVOICE

Bella Cucina Catering Co.
789 Culinary Way, Chicago, IL 60601
Phone: (312) 555-0199

Event: Annual Company Gala
Client: Stratton & Partners Law Firm
Event Date: March 22, 2025
Guest Count: 175

Menu Selections:
Appetizers (3 passed selections): $2,625
Salad Course: $1,312
Entree - Filet Mignon (x90): $5,400
Entree - Pan-Seared Salmon (x60): $3,000
Entree - Vegetarian Risotto (x25): $875
Dessert Station: $1,750
Coffee & Tea Service: $437.50

Bar Package (Premium Open Bar, 4 hrs): $8,750

Rentals:
Linen Package: $875
China & Flatware: $700
Glassware: $525

Staffing (15 servers, 3 bartenders, 1 captain x 6 hrs): $4,320

Food Subtotal: $15,399.50
Bar: $8,750.00
Rentals: $2,100.00
Staff: $4,320.00
Subtotal: $30,569.50
Service Charge (20%): $6,113.90
Tax (10.25%): $3,758.40
TOTAL: $40,441.80

Deposit Received: -$15,000.00
BALANCE DUE: $25,441.80

Due upon receipt. Thank you!"""
    },

    {
        "source": "demo_invoice_11",
        "content": """LEGAL SERVICES INVOICE

Morrison & Keats LLP
Attorneys at Law
One Financial Center, 42nd Floor
Boston, MA 02111

Client: TechNova Startup Inc.
Matter: Series B Financing
Matter #: 2025-MK-1847

Invoice Date: March 31, 2025
Invoice #: LI-048291

Professional Services (March 2025):

Partner - Catherine Wells (28.5 hrs @ $850/hr): $24,225.00
Senior Associate - David Park (45.2 hrs @ $550/hr): $24,860.00
Associate - Maria Santos (62.0 hrs @ $375/hr): $23,250.00
Paralegal - James Chen (18.5 hrs @ $195/hr): $3,607.50

Total Professional Fees: $75,942.50

Disbursements:
Filing fees (SEC): $2,847.00
Corporate search (3 states): $450.00
Document production/copying: $325.00
Travel (NY meetings): $1,284.00

Total Disbursements: $4,906.00

TOTAL THIS INVOICE: $80,848.50

Payment Terms: Net 30
Trust Account Balance: $25,000.00 (will be applied to this invoice upon request)"""
    },

    # FAILURE: Looks like an invoice but is actually more of a report
    {
        "source": "demo_invoice_12_ambiguous",
        "metadata": {"expected_failure": "classification", "failure_type": "misclassification"},
        "content": """Q1 2025 FINANCIAL SUMMARY - BILLING DEPARTMENT

Total invoices issued: 847
Total revenue billed: $2,847,291
Average invoice value: $3,361
Collection rate: 94.2%
Days sales outstanding (DSO): 38 days

Top clients by billing:
1. Meridian Healthcare - $425,000 (82 invoices)
2. TechForward Inc - $312,000 (24 invoices)
3. GlobalServe Corp - $287,500 (45 invoices)

Outstanding receivables: $165,847
Write-offs this quarter: $12,400 (0.4% of total)
Disputed invoices: 14 ($47,200 total)

Comparison to Q4 2024:
- Revenue up 12% ($2,542,000 → $2,847,291)
- DSO improved by 3 days (41 → 38)
- Collection rate improved 1.8% (92.4% → 94.2%)

Recommendations:
1. Implement automated follow-up for invoices >30 days past due
2. Review pricing for top 5 clients (contracts expiring Q2)
3. Consider early payment discount program (2/10 net 30)"""
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # REPORTS (13 total, 2 failure-inducing)
    # ═══════════════════════════════════════════════════════════════════════════

    {
        "source": "demo_report_01",
        "content": """QUARTERLY PERFORMANCE REPORT
Q1 2025 | Engineering Department

Prepared by: VP of Engineering, Lisa Park
Distribution: Executive Leadership Team
Date: April 5, 2025

EXECUTIVE SUMMARY
The engineering team delivered strong results in Q1 2025, completing 94% of planned sprint commitments and launching two major features ahead of schedule. Technical debt reduction exceeded targets by 15%.

KEY METRICS:
- Sprint velocity: 142 points/sprint (up from 128 in Q4 2024)
- Bug escape rate: 2.1% (target: <3%)
- System uptime: 99.97% (target: 99.95%)
- Mean time to recovery (MTTR): 4.2 minutes (down from 8.7 min)
- Deployment frequency: 47 deployments (up 34% from Q4)

MAJOR DELIVERABLES:
1. Real-time collaboration engine (shipped Feb 15)
2. Advanced search with semantic matching (shipped Mar 8)
3. SOC 2 Type II audit preparation (90% complete)
4. Database migration to Aurora PostgreSQL (completed Mar 22)

TEAM:
- Current headcount: 48 engineers
- New hires: 6 (4 senior, 2 mid-level)
- Attrition: 1 (voluntary, relocated)
- Open positions: 3 (2 senior backend, 1 staff SRE)

RISKS AND MITIGATIONS:
1. Increased load from new partnership integration (mitigation: capacity planning underway)
2. Legacy authentication system needs replacement by Q3 (mitigation: RFC in review)

NEXT QUARTER PRIORITIES:
- Launch mobile API v2
- Complete SOC 2 audit
- Implement feature flag system
- Reduce P95 latency by 20%"""
    },

    {
        "source": "demo_report_02",
        "content": """MARKET RESEARCH REPORT

Title: AI-Powered Customer Service Tools - Market Analysis 2025
Prepared for: ProductBoard Inc.
Analyst: Jennifer Walsh, Senior Market Analyst
Date: March 2025

1. MARKET OVERVIEW
The global AI customer service market reached $12.4 billion in 2024 and is projected to grow at a CAGR of 24.3% through 2029, reaching $36.8 billion. Key drivers include rising customer expectations, labor cost pressures, and advances in large language models.

2. COMPETITIVE LANDSCAPE
Leading players and estimated market share:
- Zendesk AI: 18%
- Salesforce Einstein: 15%
- Intercom Fin: 12%
- Freshworks Freddy: 8%
- Others: 47%

3. KEY FINDINGS
- 73% of enterprises plan to increase AI customer service spending in 2025
- Average cost reduction from AI implementation: 35-45%
- Customer satisfaction scores with AI-first support are 12% higher than traditional
- Average implementation time: 4-6 months for enterprise deployments
- Top concern among buyers: data privacy and hallucination risk (cited by 68%)

4. RECOMMENDATIONS
a) Position product as "AI-augmented" rather than "AI-replaced" — human-in-the-loop messaging resonates strongly
b) Invest in vertical-specific solutions (healthcare, fintech, e-commerce top priorities)
c) Build robust evaluation/testing tools — buyers increasingly require proof of accuracy before purchase

5. METHODOLOGY
Survey of 340 enterprise decision-makers across 12 industries. Supplemented with 25 in-depth interviews and analysis of 50 vendor case studies."""
    },

    {
        "source": "demo_report_03",
        "content": """INCIDENT POST-MORTEM REPORT

Incident ID: INC-2025-0342
Severity: P1 (Critical)
Duration: 3 hours 47 minutes
Date: March 18, 2025, 14:23 - 18:10 UTC

SUMMARY:
Complete API outage affecting all production services due to a misconfigured database connection pool following a routine configuration change.

IMPACT:
- 100% of API requests returned 503 errors
- Approximately 2.4 million failed requests
- 12,500 unique users affected
- Estimated revenue impact: $47,000
- SLA breach: 3 enterprise customers

TIMELINE:
14:23 - Config change deployed to production (connection pool max reduced from 100 to 10)
14:25 - Monitoring alerts fire for elevated error rates
14:31 - On-call engineer acknowledges alert
14:45 - Initial investigation focuses on application servers (incorrect assumption)
15:30 - Database team engaged, identifies connection pool exhaustion
15:45 - Root cause identified: config change in PR #4821
16:00 - Rollback initiated
16:15 - Rollback fails due to config caching
16:45 - Direct database config override applied
17:30 - Services begin recovering
18:10 - Full recovery confirmed

ROOT CAUSE:
A configuration change (PR #4821) intended to optimize staging environment connection pools was accidentally applied to production. The change reduced max connections from 100 to 10, causing connection starvation under normal load.

CONTRIBUTING FACTORS:
1. No environment-specific config validation in CI/CD pipeline
2. Config changes not flagged for additional review
3. Monitoring alert thresholds too generous (3-minute delay)
4. Rollback procedure did not account for config caching layer

ACTION ITEMS:
1. [P0] Add environment validation to config deployment pipeline - Owner: Tom Henderson - Due: March 25
2. [P0] Implement config change approval workflow - Owner: Lisa Park - Due: April 1
3. [P1] Reduce monitoring alert threshold to 30 seconds - Owner: SRE Team - Due: March 22
4. [P1] Document and test config rollback procedure - Owner: Platform Team - Due: April 5
5. [P2] Add config diff preview to deployment UI - Owner: DevTools Team - Due: April 15"""
    },

    {
        "source": "demo_report_04",
        "content": """ANNUAL SUSTAINABILITY REPORT 2024

Organization: PacificGreen Energy Corp
Reporting Period: January 1 - December 31, 2024
Framework: GRI Standards, TCFD Recommendations

HIGHLIGHTS:
- Total renewable energy generated: 4.8 TWh (up 22% from 2023)
- Carbon emissions (Scope 1+2): 12,400 tCO2e (down 31% from baseline)
- Water consumption reduced by 18% through recycling initiatives
- Zero workplace fatalities for 8th consecutive year
- $2.1 million invested in community development programs

ENVIRONMENTAL METRICS:
Solar capacity: 2,100 MW installed
Wind capacity: 1,400 MW installed
Energy storage: 850 MWh battery capacity
Grid reliability: 99.4% uptime
Land restoration: 340 acres rehabilitated

SOCIAL METRICS:
Total employees: 3,200
Gender diversity: 38% women (up from 34% in 2023)
Employee training: Average 42 hours per employee
Community investment: $2.1 million across 45 programs
Safety: TRIR of 0.42 (industry average: 1.1)

GOVERNANCE:
Board independence: 80% (8 of 10 directors)
Board diversity: 40% women, 30% underrepresented minorities
Executive compensation linked to ESG targets: 25% of variable pay

2025 TARGETS:
- Achieve 6 TWh renewable generation
- Reduce Scope 1+2 emissions by additional 15%
- Reach 42% gender diversity
- Install 500 MWh additional storage capacity"""
    },

    {
        "source": "demo_report_05",
        "content": """SECURITY AUDIT REPORT

Client: Nexus Financial Technologies
Audit Period: February 1-28, 2025
Auditor: CyberShield Consulting Group
Classification: CONFIDENTIAL

1. EXECUTIVE SUMMARY
Overall security posture: MODERATE (Score: 72/100, up from 65 in previous audit)

Critical findings: 2 (down from 5)
High findings: 7 (down from 9)
Medium findings: 15
Low findings: 23

2. CRITICAL FINDINGS

FINDING C-1: SQL Injection Vulnerability in Legacy API
Severity: Critical | CVSS: 9.1
Location: /api/v1/reports endpoint
Description: Parameterized queries not used in 3 legacy endpoints, allowing potential data exfiltration.
Remediation: Implement parameterized queries. Estimated effort: 2 days.
Status: Fix in progress (ETA: March 7, 2025)

FINDING C-2: Exposed AWS Credentials in Public Repository
Severity: Critical | CVSS: 9.8
Location: GitHub repository nexus-deploy-scripts
Description: AWS access keys with administrative privileges found in commit history.
Remediation: Rotate all affected credentials immediately. Implement secrets scanning.
Status: Credentials rotated. Secrets scanning enabled.

3. POSITIVE OBSERVATIONS
- MFA enabled for 100% of employee accounts
- Encryption at rest implemented across all databases
- Incident response plan tested quarterly
- Patch management SLA consistently met (<72 hours for critical patches)

4. RECOMMENDATIONS SUMMARY
a) Implement Web Application Firewall (WAF) - Priority: High
b) Conduct Red Team exercise - Priority: Medium
c) Upgrade TLS to 1.3 across all services - Priority: Medium
d) Implement runtime application security (RASP) - Priority: Low"""
    },

    {
        "source": "demo_report_06",
        "content": """CLINICAL TRIAL INTERIM REPORT

Protocol: BG-NT-2024-001
Drug: BG-7042 (Neurotrophic Factor Mimetic)
Phase: Phase 2b
Indication: Early-stage Alzheimer's Disease
Sponsor: BioGenesis Therapeutics Inc.

DATA CUTOFF: February 28, 2025
ENROLLED: 342 patients (target: 400)
SITES: 28 active sites across US, Canada, and EU

EFFICACY RESULTS (INTERIM):
Primary Endpoint (ADAS-Cog11 change from baseline at 26 weeks):
- Treatment arm (n=171): -3.2 points (SD: 4.1)
- Placebo arm (n=171): -1.1 points (SD: 3.9)
- Difference: -2.1 points (p=0.003, 95% CI: -3.4 to -0.8)

Secondary Endpoints:
- CDR-SB: Treatment showed 28% less decline (p=0.018)
- MMSE: 1.4 point advantage for treatment (p=0.041)
- Biomarkers: 15% reduction in CSF tau levels in treatment arm

SAFETY:
Serious Adverse Events: 12 (7 treatment, 5 placebo)
Treatment-related SAEs: 2 (both resolved)
Discontinuation rate: 8% (comparable between arms)
Most common AEs: headache (22%), nausea (15%), fatigue (12%)

DSMB RECOMMENDATION: Continue trial without modification.

NEXT STEPS:
- Complete enrollment by April 2025
- 52-week primary analysis: Q4 2025
- Regulatory interactions for Phase 3 planning: Q1 2026"""
    },

    {
        "source": "demo_report_07",
        "content": """PRODUCT ANALYTICS REPORT
February 2025

Product: TaskFlow Pro (Project Management SaaS)
Prepared by: Analytics Team

USER METRICS:
Monthly Active Users (MAU): 124,500 (up 8.2% MoM)
Daily Active Users (DAU): 45,200 (up 6.1% MoM)
DAU/MAU Ratio: 36.3% (healthy engagement)
New Signups: 8,920
Trial-to-Paid Conversion: 14.2% (up from 12.8%)
Churn Rate: 3.1% (down from 3.8%)

FEATURE USAGE (Top 10):
1. Task Creation: 2.4M events
2. Board View: 1.8M events
3. Comments/Mentions: 1.2M events
4. File Attachments: 890K events
5. Time Tracking: 720K events
6. Gantt Chart: 580K events
7. Automations: 420K events
8. Calendar Integration: 380K events
9. Custom Fields: 310K events
10. API Usage: 280K events

NEW FEATURE PERFORMANCE:
AI Task Suggestions (launched Feb 3):
- Adoption: 23% of active users tried it
- Retention: 45% used it more than once
- CSAT: 4.1/5.0
- Impact on task creation: +15% for adopters

REVENUE:
MRR: $892,000 (up 11.3%)
ARPU: $7.17
LTV: $231
CAC: $84
LTV/CAC: 2.75x"""
    },

    {
        "source": "demo_report_08",
        "content": """ENVIRONMENTAL IMPACT ASSESSMENT

Project: Riverside Solar Farm Development
Location: Clark County, Nevada
Developer: SunPeak Renewable Energy LLC
Date: March 2025

1. PROJECT DESCRIPTION
Proposed 150 MW solar photovoltaic facility on 800 acres of previously disturbed desert land. Includes battery energy storage system (200 MWh) and 5-mile transmission interconnection.

2. ENVIRONMENTAL FINDINGS

Flora & Fauna:
- Desert tortoise survey: 3 individuals found, relocation plan approved by USFWS
- No endangered plant species identified in project area
- Migratory bird assessment: low risk (no major flyway intersection)

Water Resources:
- No permanent water bodies within project boundary
- Estimated construction water use: 250 acre-feet (dust suppression, panel washing)
- Operational water use: 15 acre-feet annually (panel cleaning)
- Zero impact on local aquifer projected

Air Quality:
- Construction phase: temporary PM10 increases mitigated by water trucks
- Operational phase: net positive (displacing 180,000 tCO2/year from fossil generation)

Visual Impact:
- Nearest residence: 2.3 miles
- Glare analysis: no significant impact on roads or airports
- Perimeter landscaping plan to screen facility from County Road 215

3. MITIGATION MEASURES
- $2.4 million habitat conservation fund
- Tortoise exclusion fencing during construction
- Revegetation of temporary disturbance areas within 2 years
- Stormwater management plan with retention basins

4. CONCLUSION
The project is expected to have minor, mitigable environmental impacts and significant positive climate benefits."""
    },

    # FAILURE: Looks like a report but is really correspondence
    {
        "source": "demo_report_09_ambiguous",
        "metadata": {"expected_failure": "classification", "failure_type": "misclassification"},
        "content": """Subject: Analysis of Q1 Results and Recommendations

Hi Team,

I wanted to share my thoughts on our Q1 performance and where I think we should focus for Q2. I know the formal report will come from finance next week, but I think it's important we start discussing strategy now.

My analysis shows we're trending 8% below our revenue targets, primarily due to the delayed launch of the enterprise tier. However, our user growth metrics are actually ahead of plan, which gives me confidence we can recover in Q2 if we accelerate the enterprise launch.

Specifically, I recommend:
1. Pull the enterprise launch forward to April 15 (from May 1)
2. Increase the SDR team by 2 headcount to handle inbound pipeline
3. Offer a promotional rate for annual enterprise contracts signed before June 30

The competitive landscape is also shifting — I noticed Competitor X launched a similar feature last week. We should discuss how this affects our positioning.

Can we set up a 90-minute strategy session this Thursday? I'll prepare more detailed slides.

Thanks,
Rachel
VP of Product"""
    },

    {
        "source": "demo_report_10",
        "content": """EMPLOYEE ENGAGEMENT SURVEY RESULTS

Survey Period: February 15-28, 2025
Response Rate: 82% (264 of 322 employees)
Administered by: HR Department, GlobalServe International

OVERALL ENGAGEMENT SCORE: 76/100 (Industry benchmark: 72)

CATEGORY SCORES:
Leadership & Management: 78/100
Career Development: 71/100
Compensation & Benefits: 74/100
Work-Life Balance: 80/100
Team Collaboration: 82/100
Company Culture: 77/100
Communication: 69/100
Innovation & Empowerment: 73/100

TOP STRENGTHS (Highest rated items):
1. "My team collaborates effectively" - 4.3/5.0
2. "I feel respected by my colleagues" - 4.2/5.0
3. "My manager supports my professional growth" - 4.1/5.0
4. "I have flexibility in how I do my work" - 4.1/5.0

TOP CONCERNS (Lowest rated items):
1. "I understand the company's strategic direction" - 3.2/5.0
2. "Communication between departments is effective" - 3.3/5.0
3. "I see a clear path for advancement" - 3.4/5.0
4. "I feel fairly compensated for my role" - 3.5/5.0

YEAR-OVER-YEAR TREND:
2023: 71 → 2024: 74 → 2025: 76 (Consistent improvement)

ACTION PLAN:
1. Monthly all-hands with CEO strategy updates (addressing #1 concern)
2. Cross-functional project program launch (addressing #2)
3. Career framework documentation by Q3 (addressing #3)
4. Market compensation review in April (addressing #4)"""
    },

    # FAILURE: Extremely technical jargon — extraction might hallucinate
    {
        "source": "demo_report_11_jargon",
        "metadata": {"expected_failure": "extraction", "failure_type": "extraction_hallucination"},
        "content": """SEMICONDUCTOR PROCESS NODE TRANSITION ANALYSIS

Migration Target: N3E → N2 (GAA-FET Architecture)
Wafer Fab: TSMC Fab 20, Hsinchu Science Park

Process Specifications:
- Gate pitch: 48nm (vs 54nm on N3E)
- Metal pitch: 28nm M1 (vs 30nm on N3E)
- Fin-to-nanosheet transition: 4-sheet GAAFET
- Sheet width: 25-40nm configurable
- DTCO-enabled library: 6T SRAM bitcell area: 0.021μm²
- EUV layers: 20+ (vs 15 on N3E), including backside power delivery
- BEOL: 15 metal layers with hybrid Cu/Ru metallization

Expected Performance:
- Logic density improvement: 1.15x over N3E
- Speed improvement: 10-15% at iso-power
- Power reduction: 25-30% at iso-speed
- Vmin improvement enabling sub-0.5V operation

Design Challenges:
- CFET integration for logic-on-logic stacking
- Backside power delivery network (BSPDN) IR drop management
- Self-aligned contacts with <2nm overlay budget
- Interconnect RC delay mitigation at scaled pitches

Yield Ramp Projections:
D0 target: <0.15/cm² by HVM qualification
Expected yield at tape-out+6: 75-80% for mobile SoC
Risk-production: Q2 2025 | HVM: Q4 2025"""
    },

    {
        "source": "demo_report_12",
        "content": """LOGISTICS OPTIMIZATION REPORT

Client: FastTrack Delivery Services
Prepared by: RouteMaster Consulting
Date: March 2025

CURRENT STATE ANALYSIS:
Fleet size: 120 vehicles (80 vans, 30 trucks, 10 EVs)
Daily deliveries: ~4,200
Average route efficiency: 72%
Fuel cost (monthly): $184,000
Driver hours (monthly): 22,400

OPTIMIZATION OPPORTUNITIES:

1. Route Optimization
Current: Static routes assigned weekly
Proposed: Dynamic routing with real-time traffic integration
Expected improvement: 18% reduction in total miles driven
Savings: $33,000/month in fuel + $12,000/month in driver hours

2. Fleet Electrification
Phase 1 (2025): Replace 20 vans with EVs
Phase 2 (2026): Replace additional 30 vans
Total investment: $1.8 million
ROI period: 28 months
Annual savings after ROI: $420,000

3. Warehouse Layout
Current picking efficiency: 145 items/hour
Proposed (zone-based system): 210 items/hour
Implementation cost: $95,000
Monthly savings: $28,000

TOTAL POTENTIAL SAVINGS: $73,000/month ($876,000/year)
IMPLEMENTATION INVESTMENT: $2.1 million
PAYBACK PERIOD: 29 months"""
    },

    {
        "source": "demo_report_13",
        "content": """DATA QUALITY ASSESSMENT REPORT

System: Customer Data Platform (CDP)
Assessment Date: March 2025
Assessor: Data Governance Team

OVERALL DATA QUALITY SCORE: 78.4/100

DIMENSION SCORES:
Completeness: 85.2% (target: 95%)
- Missing email addresses: 12.3% of customer records
- Missing phone numbers: 18.7%
- Missing industry classification: 8.1%

Accuracy: 82.1% (target: 90%)
- Invalid email format: 3.2%
- Outdated addresses (>2 years): 14.5%
- Duplicate records identified: 4,821 (2.1% of total)

Consistency: 71.3% (target: 85%)
- Name format inconsistencies: 22.4% (mixed case, abbreviations)
- Date format variations: 5 different formats in use
- Currency field inconsistencies: 3.8%

Timeliness: 76.8% (target: 90%)
- Records not updated in >12 months: 31.2%
- Average record age: 14.3 months

IMPACT ANALYSIS:
- Marketing campaign bounce rate attributed to data quality: 8.4%
- Sales team time spent on data cleanup: estimated 12 hrs/week
- Customer support misroutes due to incorrect data: ~45/month

REMEDIATION PLAN:
1. Implement real-time email validation at point of entry
2. Deploy deduplication engine (estimated cost: $45,000)
3. Establish quarterly data refresh program
4. Create data quality dashboard for ongoing monitoring
5. Mandatory field validation for critical attributes"""
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # CORRESPONDENCE (10 total, 2 failure-inducing)
    # ═══════════════════════════════════════════════════════════════════════════

    {
        "source": "demo_correspondence_01",
        "content": """Subject: Re: Partnership Proposal - DataFlow Analytics

Dear Mr. Henderson,

Thank you for taking the time to meet with us last Tuesday. We thoroughly enjoyed learning about CloudScale Systems' infrastructure capabilities and believe there is significant synergy between our organizations.

After reviewing the partnership proposal with our executive team, I'm pleased to confirm our interest in moving forward. We'd like to propose the following next steps:

1. Technical Integration Workshop (Week of April 7)
   Our CTO, Marcus Rivera, would like to schedule a 2-day workshop with your engineering team to explore API integration possibilities. We can host at our San Francisco office or arrange a virtual session.

2. Pilot Program
   We propose a 90-day pilot with 3-5 of our mid-market clients to validate the integration. We'd provide the client relationships and data; you'd provide the infrastructure and support.

3. Revenue Sharing Discussion
   Once the pilot results are in, we should formalize the revenue sharing model. Our initial thinking is a 70/30 split (70% to the primary service provider for each deal).

Could we schedule a call next week to align on timing? My assistant, Jennifer Walsh, can coordinate calendars — she's cc'd on this email.

Looking forward to building something great together.

Best regards,
Patricia Chen
CEO, DataFlow Analytics
patricia@dataflow.example.com
(415) 555-0734"""
    },

    {
        "source": "demo_correspondence_02",
        "content": """MEMORANDUM

TO: All Department Heads
FROM: James Bradford, Chief Human Resources Officer
DATE: March 10, 2025
RE: Updated Remote Work Policy - Effective April 1, 2025

Following extensive feedback from the employee engagement survey and department head consultations, we are implementing the following updates to our remote work policy:

HYBRID WORK SCHEDULE:
- All employees may work remotely up to 3 days per week (increased from 2)
- Core in-office days: Tuesday and Thursday (previously Monday, Wednesday, Friday)
- Department heads may designate one additional collaboration day per month

ELIGIBILITY:
- Available to all full-time employees who have completed their 90-day probationary period
- Performance-based: employees on performance improvement plans must work on-site full-time
- Role-specific exceptions may apply (facilities, reception, lab personnel)

HOME OFFICE STIPEND:
- One-time setup allowance increased to $1,000 (from $500)
- Monthly internet/utilities stipend: $75
- Ergonomic assessment available upon request

EXPECTATIONS:
- Maintain regular working hours (flexibility with manager approval)
- Video-on for team meetings
- Respond to messages within 2 hours during business hours
- In-office attire policy applies on office days

Please share this memo with your teams and direct any questions to hr@company.com.

James Bradford
CHRO, GlobalServe International"""
    },

    {
        "source": "demo_correspondence_03",
        "content": """Dear Dr. Liu,

I hope this message finds you well. I'm writing to formally invite you to deliver the keynote address at the 2025 International Conference on Computational Biology, to be held October 15-17, 2025, at the Singapore Convention Centre.

Conference Theme: "From Sequence to Function: AI-Driven Biological Discovery"

Your groundbreaking work on CRISPR-guided gene therapy, particularly the recent publication in Nature Biotechnology (January 2025), has garnered significant attention in our community. We believe your insights would be invaluable to our expected audience of 1,200+ researchers and industry professionals.

KEYNOTE DETAILS:
- Date: October 15, 2025 (Opening Day)
- Time: 9:00 AM - 10:00 AM (50 min talk + 10 min Q&A)
- Topic: At your discretion, though we'd love to hear about your latest findings on neurotrophic factor mimetics
- Honorarium: $5,000 USD
- Travel: Business class airfare + 4 nights at the Marina Bay Sands (conference hotel)

We would also welcome your participation in an afternoon panel discussion on "Ethics and Regulation of Gene Therapy" if your schedule permits.

Please let us know by May 15, 2025, if you are able to accept. We are happy to accommodate any special requirements.

With warm regards,
Professor Anil Kapoor
Conference Chair
Department of Computational Biology
National University of Singapore
anil.kapoor@nus.edu.sg"""
    },

    {
        "source": "demo_correspondence_04",
        "content": """Subject: Urgent: Server Migration Timeline Update

Hi DevOps Team,

I need to flag a critical change to our migration timeline. After this morning's discovery meeting with the database team, we've identified several issues that require us to push back Phase 2 of the server migration.

THE PROBLEM:
Our initial assessment underestimated the complexity of migrating the legacy Oracle databases. Specifically:
- 3 databases have undocumented stored procedures (estimated 400+ procedures total)
- Cross-database dependencies we didn't map in Phase 1
- Custom Oracle-specific features (Materialized Views, DB Links) that don't have direct PostgreSQL equivalents

REVISED TIMELINE:
- Phase 2 original target: April 15, 2025
- Phase 2 revised target: May 30, 2025
- Additional engineering effort: ~320 hours
- Additional cost: approximately $56,000

WHAT I NEED FROM YOU:
1. Review the attached dependency map and flag anything I missed
2. Identify which services can be migrated independently (to parallelise work)
3. Confirm your team's availability for the extended timeline

I've already briefed Tom Henderson (CTO) and he's aligned with the delay. But we need to notify the affected product teams ASAP — they're planning feature launches that depend on the new infrastructure.

Can we sync tomorrow at 10 AM? I've sent a calendar invite.

Thanks,
Priya Sharma
Senior Infrastructure Engineer
priya@cloudscale.example.com"""
    },

    {
        "source": "demo_correspondence_05",
        "content": """Dear Valued Customer,

RE: Notice of Service Terms Update - Effective June 1, 2025

We are writing to inform you of important updates to our Terms of Service that will take effect on June 1, 2025. These changes reflect our ongoing commitment to transparency, data protection, and service quality.

KEY CHANGES:

1. DATA RETENTION POLICY
We are reducing our default data retention period from 36 months to 24 months for inactive accounts. Active accounts are unaffected. You may request extended retention through your account settings.

2. API RATE LIMITS
To ensure fair usage and platform stability, we are implementing tiered rate limits:
- Starter plan: 1,000 requests/hour (new limit)
- Professional plan: 10,000 requests/hour (unchanged)
- Enterprise plan: 100,000 requests/hour (increased from 50,000)

3. UPTIME SLA
We are strengthening our uptime commitment:
- Previous: 99.5% monthly uptime guarantee
- Updated: 99.9% monthly uptime guarantee
- SLA credits increased to 25% of monthly fee for breaches

4. PRIVACY UPDATES
In compliance with new state privacy regulations, we've updated our data processing practices. Full details available at privacy.example.com/2025-update.

NO ACTION REQUIRED if you wish to continue under the updated terms. If you have concerns, please contact support@example.com before May 15, 2025.

Thank you for your continued trust.

Customer Success Team
Acme SaaS Platform"""
    },

    {
        "source": "demo_correspondence_06",
        "content": """Subject: Thank You + Follow-up from Interview

Dear Ms. Park,

Thank you so much for taking the time to interview me yesterday for the Senior Data Engineer position at GlobalServe International. I truly enjoyed our conversation about the data infrastructure challenges your team is tackling, particularly the real-time pipeline migration.

A few thoughts that came to mind after our discussion:

1. Regarding the Kafka throughput issue you mentioned — I encountered a very similar situation at my current role. We solved it by implementing a custom partitioning strategy based on tenant ID rather than random assignment, which reduced our P99 latency from 450ms to 85ms. I'd love to share more details about this approach.

2. I was particularly excited about the opportunity to work on the new event sourcing architecture. My experience with EventStoreDB and temporal data modeling at DataBridge Analytics would translate directly.

3. The team culture you described — especially the emphasis on blameless post-mortems and knowledge sharing — strongly aligns with how I believe high-performing engineering teams should operate.

I remain very enthusiastic about the opportunity and believe my background in distributed systems and real-time data processing would allow me to make meaningful contributions from day one.

Please don't hesitate to reach out if you need any additional information or references.

Best regards,
Michael Torres
michael.torres@email.com
(512) 555-0847"""
    },

    {
        "source": "demo_correspondence_07",
        "content": """TO: Legal Department
FROM: Diana Reyes, Director of Procurement
DATE: April 2, 2025
SUBJECT: Vendor Contract Dispute - GreenLeaf Materials Co.

Colleagues,

I'm escalating a dispute with one of our key suppliers, GreenLeaf Materials Co., regarding recent deliveries that do not meet our agreed-upon quality specifications.

BACKGROUND:
We have a Supply Agreement (executed January 20, 2025) with GreenLeaf for sustainable building materials. The agreement specifies that all products must meet LEED certification standards, with certificates of compliance accompanying each shipment.

THE ISSUE:
Our last three shipments (received Feb 15, Feb 28, and March 14) contained bamboo composite panels that failed our internal quality testing:
- Shipment #1: Moisture content 14% (spec: max 12%)
- Shipment #2: Tensile strength 15% below specification
- Shipment #3: LEED certification documents not provided; panels visually damaged

FINANCIAL IMPACT:
- Value of disputed shipments: $47,500
- Replacement material costs: $52,000 (sourced from alternate vendor at premium)
- Project delay costs: estimated $85,000 (2-week delay on Riverside project)

REQUESTED ACTIONS:
1. Issue formal notice of breach under Section 6 (warranty provisions)
2. Demand replacement materials or full credit within 15 business days
3. Reserve our rights regarding delay damages
4. Evaluate whether to exercise termination rights

Please advise on the strongest legal approach. I'll compile the inspection reports and testing data for your review.

Diana Reyes
Procurement Director
EcoBuild Construction"""
    },

    # FAILURE: Looks like correspondence but is essentially a contract/agreement
    {
        "source": "demo_correspondence_08_like_contract",
        "metadata": {"expected_failure": "classification", "failure_type": "misclassification"},
        "content": """Hi Alex,

Great chatting yesterday! As discussed, here are the terms for the freelance project:

You'll handle all the UI/UX design for our new mobile app. We're looking at 6 screens total. Budget is $12,000 flat rate, with $4,000 upfront, $4,000 at midpoint review, and $4,000 on completion.

Timeline: 6 weeks starting April 7. You'll own none of the IP — all designs transfer to us on payment. We get unlimited revisions during the project period, but after delivery you'll charge $150/hr for changes.

If either of us wants out, 1 week written notice and you keep payment for work completed.

If this all sounds good, just reply "confirmed" and we'll consider this our binding agreement. No need for a formal contract — we've worked together enough times.

Cheers,
Jason Wu
Founder, Velocity Coworking"""
    },

    {
        "source": "demo_correspondence_09",
        "content": """Subject: Board Meeting Minutes - March 28, 2025

Dear Board Members,

Please find below the minutes from our quarterly board meeting held on March 28, 2025, at the Company's headquarters in Chicago, IL.

ATTENDEES:
- Margaret Chen (Chair & CEO)
- William Foster (Vice Chair)
- Dr. Elena Vasquez (Independent Director)
- Robert Kim (Independent Director)
- Sarah O'Brien (CFO, non-voting)
- Legal counsel: Morrison & Keats LLP (Catherine Wells)

AGENDA ITEMS:

1. Q1 Financial Review (Sarah O'Brien)
   - Revenue: $12.4M (vs $11.8M plan, +5.1%)
   - EBITDA: $2.1M (17% margin, up from 15%)
   - Cash position: $18.7M
   - Board APPROVED Q1 financial statements unanimously.

2. Strategic Acquisition Discussion
   - CEO presented opportunity to acquire Henderson Analytics
   - Proposed price: $4.2M (3.2x trailing revenue)
   - Board APPROVED due diligence proceeding, with $50K budget
   - William Foster abstained due to personal relationship with target CEO

3. Executive Compensation Review
   - Board APPROVED FY2025 executive bonus pool of $800K
   - CEO equity refresh: 50,000 RSUs vesting over 3 years APPROVED (4-1, Foster abstained)

4. Risk Committee Update (Dr. Vasquez)
   - Cybersecurity insurance renewed at $2.5M coverage
   - Regulatory compliance: no outstanding issues
   - Updated risk register reviewed and accepted

NEXT MEETING: June 27, 2025

Respectfully submitted,
Catherine Wells
Corporate Secretary"""
    },

    {
        "source": "demo_correspondence_10",
        "content": """Dear Dr. Martinez,

RE: Patient Referral - Jennifer Walsh (DOB: 05/12/1988)

I am referring the above patient to your retinal surgery practice for evaluation and potential surgical intervention.

CLINICAL HISTORY:
Ms. Walsh presented to our office on March 10, 2025, with complaints of progressive visual distortion and floaters in her right eye over the past 3 weeks. She has no significant past ocular history and her systemic health is unremarkable except for well-controlled asthma.

EXAMINATION FINDINGS:
- Visual Acuity: OD 20/50 (reduced from 20/20 at last exam), OS 20/20
- IOP: OD 16 mmHg, OS 15 mmHg
- Anterior segment: Normal OU
- Dilated fundus exam: OD - Posterior vitreous detachment with vitreoretinal traction at superotemporal arcade. Small horseshoe tear identified at 1:30 position.
- OCT: Subretinal fluid extending to fovea, central macular thickness 425μm (OD)
- OS: Normal

ASSESSMENT:
Right eye rhegmatogenous retinal detachment, macula-off, secondary to horseshoe retinal tear.

I have counseled the patient on the urgency of evaluation and she understands the time-sensitive nature of this referral. She is available for urgent appointment.

Please contact my office if you need additional information.

Sincerely,
Dr. Robert Kim, OD
ClearView Ophthalmology Associates
Phone: (305) 555-0120
Fax: (305) 555-0121"""
    },
]
