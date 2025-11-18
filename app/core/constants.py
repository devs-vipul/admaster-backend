"""
Application constants - Non-sensitive default values
These are business logic constants, not configuration
"""
from app.models.campaign import ConversionGoal, ConversionGoalIcon, BiddingStrategyType


# Campaign defaults (business logic - not sensitive)
DEFAULT_CONVERSION_GOAL = ConversionGoal.WEBSITE_TRAFFIC
DEFAULT_CONVERSION_GOAL_ICON = ConversionGoalIcon.WEBSITE_TRAFFIC
DEFAULT_DATA_SOURCE = "user"
DEFAULT_BIDDING_STRATEGY_TYPE = BiddingStrategyType.MAXIMIZE_CLICKS

# Supported bidding strategy types (business logic)
DEFAULT_BIDDING_STRATEGY_TYPES = [
    {
        "name": "MAXIMIZE_CLICKS",
        "value": "maximize_clicks",
        "type": "target_amount",
    }
]

# Campaign status defaults
DEFAULT_CAMPAIGN_STATUS = "draft"
DEFAULT_CAN_HAVE_CONVERSIONS = False

# Budget defaults (can be overridden by env vars)
DEFAULT_CURRENCY = "INR"  # Default currency code
DEFAULT_DAILY_BUDGET = 0.0  # Default daily budget

