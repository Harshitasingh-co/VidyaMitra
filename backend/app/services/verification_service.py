"""
Verification Service - Fraud detection and verification logic

This service handles comprehensive verification of internship listings,
including domain authenticity checks, platform legitimacy verification,
red flag detection, and trust score calculation.
"""

from typing import List, Dict, Any, Optional
import re
import logging
from datetime import datetime

from app.models.internship import (
    InternshipListing,
    VerificationResult,
    VerificationResultCreate,
    VerificationStatus,
    VerificationSignals,
    RedFlag,
    RedFlagSeverity,
)

logger = logging.getLogger(__name__)


class VerificationService:
    """Fraud detection and verification logic"""
    
    # Known legitimate platforms
    KNOWN_PLATFORMS = {
        "internshala",
        "linkedin",
        "wellfound",
        "aicte",
        "nsdc",
        "company career page",
        "company careers",
        "naukri",
        "indeed",
        "glassdoor",
    }
    
    # Non-official email domains (red flag)
    NON_OFFICIAL_DOMAINS = {
        "gmail.com",
        "yahoo.com",
        "hotmail.com",
        "outlook.com",
        "rediffmail.com",
        "ymail.com",
    }
    
    # Keywords indicating registration fees
    REGISTRATION_FEE_KEYWORDS = [
        "registration fee",
        "registration charge",
        "enrollment fee",
        "joining fee",
        "application fee",
        "processing fee",
        "security deposit",
        "refundable deposit",
        "pay to apply",
        "payment required",
    ]
    
    # Keywords indicating WhatsApp-only contact
    WHATSAPP_ONLY_KEYWORDS = [
        "whatsapp only",
        "contact on whatsapp",
        "whatsapp for details",
        "message on whatsapp",
        "whatsapp number",
        "dm on whatsapp",
    ]
    
    # Keywords indicating vague descriptions
    VAGUE_DESCRIPTION_KEYWORDS = [
        "various tasks",
        "general work",
        "miscellaneous duties",
        "as assigned",
        "other duties",
        "flexible role",
        "multiple responsibilities",
    ]
    
    def __init__(self, db_client=None):
        """
        Initialize the verification service
        
        Args:
            db_client: Optional database client for caching results
        """
        self.db = db_client
        logger.info("VerificationService initialized")
    
    def check_domain_authenticity(self, company: str, domain: Optional[str]) -> bool:
        """
        Verify if domain matches company and is not a free email service
        
        Args:
            company: Company name
            domain: Company domain (e.g., "techcorp.com")
            
        Returns:
            True if domain is authentic, False otherwise
        """
        if not domain:
            logger.debug(f"No domain provided for company: {company}")
            return False
        
        # Normalize domain
        domain = domain.lower().strip()
        
        # Check again after stripping - empty string should return False
        if not domain:
            logger.debug(f"Empty domain after stripping for company: {company}")
            return False
        
        # Check if it's a non-official email domain
        if domain in self.NON_OFFICIAL_DOMAINS:
            logger.warning(f"Non-official domain detected: {domain}")
            return False
        
        # Check if domain contains company name (basic heuristic)
        company_normalized = company.lower().strip()
        # Remove common suffixes like "pvt ltd", "inc", "corp", etc.
        company_normalized = re.sub(r'\s+(pvt\.?|ltd\.?|inc\.?|corp\.?|llc|limited|private)$', '', company_normalized)
        company_normalized = re.sub(r'[^a-z0-9]', '', company_normalized)
        
        # Extract all parts of the domain (to handle subdomains like careers.techcorp.com)
        domain_parts = domain.split('.')
        
        # Check each part of the domain (excluding common TLDs)
        tlds = {'com', 'org', 'net', 'edu', 'gov', 'co', 'in', 'io', 'ai'}
        for part in domain_parts:
            if part not in tlds:
                part_normalized = re.sub(r'[^a-z0-9]', '', part)
                # Check if company name is in domain part or vice versa
                if company_normalized in part_normalized or part_normalized in company_normalized:
                    logger.debug(f"Domain {domain} matches company {company}")
                    return True
        
        # If no match, consider it suspicious
        logger.debug(f"Domain {domain} does not match company {company}")
        return False
    
    def check_platform_legitimacy(self, platform: Optional[str]) -> bool:
        """
        Check if platform is known and trusted
        
        Args:
            platform: Platform name (e.g., "Internshala", "LinkedIn")
            
        Returns:
            True if platform is known and legitimate, False otherwise
        """
        if not platform:
            logger.debug("No platform provided")
            return False
        
        # Normalize platform name
        platform_normalized = platform.lower().strip()
        
        # Check against known platforms
        is_known = platform_normalized in self.KNOWN_PLATFORMS
        
        if is_known:
            logger.debug(f"Platform {platform} is known and legitimate")
        else:
            logger.debug(f"Platform {platform} is unknown")
        
        return is_known
    
    def detect_red_flags(self, internship: Dict[str, Any]) -> List[RedFlag]:
        """
        Detect fraud indicators in internship listing
        
        Args:
            internship: Internship listing data (dict or InternshipListing)
            
        Returns:
            List of detected red flags
        """
        red_flags = []
        
        # Convert to dict if it's a Pydantic model
        if hasattr(internship, 'model_dump'):
            internship_dict = internship.model_dump()
        else:
            internship_dict = internship
        
        # Extract fields
        title = internship_dict.get('title', '').lower()
        company = internship_dict.get('company', '').lower()
        stipend = internship_dict.get('stipend', '').lower()
        responsibilities = internship_dict.get('responsibilities', [])
        company_domain = internship_dict.get('company_domain', '')
        
        # Combine text fields for keyword search
        combined_text = f"{title} {company} {stipend} {' '.join(responsibilities)}".lower()
        
        # 1. Check for registration fees
        for keyword in self.REGISTRATION_FEE_KEYWORDS:
            if keyword in combined_text:
                red_flags.append(RedFlag(
                    type="registration_fee",
                    severity=RedFlagSeverity.HIGH,
                    description="Asks for registration or enrollment fee"
                ))
                logger.warning(f"Registration fee red flag detected: {keyword}")
                break
        
        # 2. Check for WhatsApp-only contact
        for keyword in self.WHATSAPP_ONLY_KEYWORDS:
            if keyword in combined_text:
                red_flags.append(RedFlag(
                    type="whatsapp_only",
                    severity=RedFlagSeverity.HIGH,
                    description="Uses WhatsApp as the only contact method"
                ))
                logger.warning(f"WhatsApp-only red flag detected: {keyword}")
                break
        
        # 3. Check for non-official email domain
        if company_domain and company_domain.lower() in self.NON_OFFICIAL_DOMAINS:
            red_flags.append(RedFlag(
                type="non_official_email",
                severity=RedFlagSeverity.HIGH,
                description="Uses non-official email domain (Gmail, Yahoo, etc.)"
            ))
            logger.warning(f"Non-official email red flag detected: {company_domain}")
        
        # 4. Check for unrealistic stipend
        # Extract numeric value from stipend string
        stipend_match = re.search(r'₹?\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*k?', stipend)
        if stipend_match:
            stipend_value = float(stipend_match.group(1).replace(',', ''))
            # Check if 'k' is present (thousands)
            if 'k' in stipend.lower():
                stipend_value *= 1000
            
            # Flag if stipend is unrealistically high (>50,000 per month for freshers)
            if stipend_value > 50000:
                red_flags.append(RedFlag(
                    type="unrealistic_stipend",
                    severity=RedFlagSeverity.MEDIUM,
                    description=f"Unrealistically high stipend (₹{stipend_value:,.0f}) for internship"
                ))
                logger.warning(f"Unrealistic stipend red flag detected: ₹{stipend_value}")
        
        # 5. Check for vague job descriptions
        if responsibilities:
            responsibilities_text = ' '.join(responsibilities).lower()
            vague_count = sum(1 for keyword in self.VAGUE_DESCRIPTION_KEYWORDS if keyword in responsibilities_text)
            
            # If multiple vague keywords or very short responsibilities
            if vague_count >= 2 or (len(responsibilities) == 1 and len(responsibilities[0]) < 50):
                red_flags.append(RedFlag(
                    type="vague_description",
                    severity=RedFlagSeverity.MEDIUM,
                    description="Job responsibilities are vague or poorly defined"
                ))
                logger.warning("Vague description red flag detected")
        else:
            # No responsibilities listed at all
            red_flags.append(RedFlag(
                type="vague_description",
                severity=RedFlagSeverity.MEDIUM,
                description="No job responsibilities specified"
            ))
            logger.warning("No responsibilities red flag detected")
        
        logger.info(f"Detected {len(red_flags)} red flags for internship")
        return red_flags
    
    def calculate_trust_score(
        self,
        signals: VerificationSignals,
        red_flags: List[RedFlag]
    ) -> int:
        """
        Calculate overall trust score (0-100) based on signals and red flags
        
        Scoring logic:
        - Start with base score of 50
        - Add points for positive signals:
          - Official domain: +20
          - Known platform: +20
          - Company verified: +10
        - Subtract points for red flags:
          - High severity: -20 per flag
          - Medium severity: -10 per flag
          - Low severity: -5 per flag
        
        Args:
            signals: Verification signals (positive indicators)
            red_flags: List of detected red flags (negative indicators)
            
        Returns:
            Trust score between 0 and 100
        """
        # Start with base score
        score = 50
        
        # Add points for positive signals
        if signals.official_domain:
            score += 20
            logger.debug("Added 20 points for official domain")
        
        if signals.known_platform:
            score += 20
            logger.debug("Added 20 points for known platform")
        
        if signals.company_verified:
            score += 10
            logger.debug("Added 10 points for company verification")
        
        # Subtract points for red flags
        for flag in red_flags:
            if flag.severity == RedFlagSeverity.HIGH:
                score -= 20
                logger.debug(f"Subtracted 20 points for high severity flag: {flag.type}")
            elif flag.severity == RedFlagSeverity.MEDIUM:
                score -= 10
                logger.debug(f"Subtracted 10 points for medium severity flag: {flag.type}")
            elif flag.severity == RedFlagSeverity.LOW:
                score -= 5
                logger.debug(f"Subtracted 5 points for low severity flag: {flag.type}")
        
        # Ensure score is within bounds [0, 100]
        score = max(0, min(100, score))
        
        logger.info(f"Calculated trust score: {score}")
        return score
    
    async def verify_internship(self, internship: InternshipListing) -> VerificationResult:
        """
        Comprehensive verification of internship listing
        
        This method performs all verification checks and returns a complete
        verification result with status, trust score, signals, and red flags.
        
        Args:
            internship: Internship listing to verify
            
        Returns:
            VerificationResult with complete verification analysis
        """
        logger.info(f"Starting verification for internship: {internship.title} at {internship.company}")
        
        # Check verification signals
        official_domain = self.check_domain_authenticity(
            internship.company,
            internship.company_domain
        )
        
        known_platform = self.check_platform_legitimacy(internship.platform)
        
        # Company verification would require external API calls (LinkedIn, Crunchbase, etc.)
        # For now, we'll set it to False (can be enhanced later)
        company_verified = False
        
        signals = VerificationSignals(
            official_domain=official_domain,
            known_platform=known_platform,
            company_verified=company_verified
        )
        
        # Detect red flags
        red_flags = self.detect_red_flags(internship)
        
        # Calculate trust score
        trust_score = self.calculate_trust_score(signals, red_flags)
        
        # Determine verification status based on trust score
        if trust_score >= 80:
            status = VerificationStatus.VERIFIED
        elif trust_score >= 50:
            status = VerificationStatus.USE_CAUTION
        else:
            status = VerificationStatus.POTENTIAL_SCAM
        
        logger.info(f"Verification complete: {status.value} (trust score: {trust_score})")
        
        # Create verification result
        verification_result = VerificationResult(
            id=str(internship.id) + "_verification",  # Temporary ID
            internship_id=str(internship.id),
            status=status,
            trust_score=trust_score,
            verification_signals=signals,
            red_flags=red_flags,
            verification_notes=self._generate_verification_notes(signals, red_flags, trust_score),
            last_verified=datetime.now(),
            created_at=datetime.now()
        )
        
        return verification_result
    
    def _generate_verification_notes(
        self,
        signals: VerificationSignals,
        red_flags: List[RedFlag],
        trust_score: int
    ) -> str:
        """
        Generate human-readable verification notes
        
        Args:
            signals: Verification signals
            red_flags: Detected red flags
            trust_score: Calculated trust score
            
        Returns:
            Verification notes string
        """
        notes = []
        
        # Add positive signals
        if signals.official_domain:
            notes.append("✓ Official company domain verified")
        if signals.known_platform:
            notes.append("✓ Listed on known platform")
        if signals.company_verified:
            notes.append("✓ Company verified on external sources")
        
        # Add red flag warnings
        if red_flags:
            notes.append(f"\n⚠ {len(red_flags)} red flag(s) detected:")
            for flag in red_flags:
                notes.append(f"  - {flag.description}")
        
        # Add overall assessment
        if trust_score >= 80:
            notes.append("\n✅ This internship appears legitimate and safe to apply.")
        elif trust_score >= 50:
            notes.append("\n⚠️ Exercise caution. Verify details before applying.")
        else:
            notes.append("\n❌ High risk of fraud. Avoid this internship.")
        
        return "\n".join(notes)
