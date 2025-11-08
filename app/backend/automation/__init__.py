# Platform automation package

from .base import (
    AdData,
    AutomationManager,
    PlatformAutomationBase,
    PlatformCredentials,
    PostResult,
    PostStatus,
    automation_manager,
)
from .craigslist import CraigslistAutomation
from .ebay import EBayAutomation
from .facebook import FacebookMarketplaceAutomation
from .offerup import OfferUpAutomation

# Register all platforms with the global manager
automation_manager.register_platform(FacebookMarketplaceAutomation())
automation_manager.register_platform(CraigslistAutomation())
automation_manager.register_platform(OfferUpAutomation())
automation_manager.register_platform(EBayAutomation())

__all__ = [
    "AdData",
    "AutomationManager",
    "CraigslistAutomation",
    "EBayAutomation",
    "FacebookMarketplaceAutomation",
    "OfferUpAutomation",
    "PlatformAutomationBase",
    "PlatformCredentials",
    "PostResult",
    "PostStatus",
    "automation_manager",
]
