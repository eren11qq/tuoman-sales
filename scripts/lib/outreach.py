"""
Outreach template variable substitution and channel routing.

Used by outreach-generator skill for structured message generation.
"""

import re
from typing import Optional


class OutreachGenerator:
    """Template-based outreach message generator with variable substitution."""

    # Channel → template letter mapping based on lead signals
    CHANNEL_ROUTES = {
        "funded": ("脉脉", "A"),
        "hiring": ("脉脉", "B"),
        "platform": ("脉脉", "C"),
        "soe": ("邮件", "E"),
        "warm_intro": ("微信", "G"),
        "cold": ("脉脉", "H"),
        "content_capacity": ("脉脉", "I"),
        "content_quality": ("脉脉", "J"),
        "tool_integration": ("脉脉", "K"),
        "compliance": ("邮件", "L"),
    }

    def __init__(self, variables: dict[str, str]):
        """
        Args:
            variables: Dict of template variables. Required keys prefixed with ``your_``
                       must be filled by the user; lead keys come from research.
        """
        self.vars = variables

    def substitute(self, template: str) -> str:
        """Replace ``{variable_name}`` placeholders with known values.

        Unknown variables are left as-is (marked for manual fill).
        """
        def _replacer(match: re.Match) -> str:
            key = match.group(1)
            return self.vars.get(key, match.group(0))
        return re.sub(r"\{(\w+)\}", _replacer, template)

    def route_channel(self, lead_type: str) -> tuple[str, str]:
        """
        Determine channel and template letter from lead classification.

        Args:
            lead_type: One of the CHANNEL_ROUTES keys.

        Returns:
            (channel_name, template_letter)
        """
        return self.CHANNEL_ROUTES.get(lead_type, ("脉脉", "H"))

    def generate_first_message(self, template_text: str, lead_type: str = "funded") -> dict:
        """
        Generate a first outreach message.

        Returns:
            dict with channel, template, message, and follow-up plan.
        """
        channel, template_letter = self.route_channel(lead_type)
        message = self.substitute(template_text)

        return {
            "channel": channel,
            "template": template_letter,
            "message": message,
            "follow_up_day1": f"Day 1 ({channel}): Initial message sent",
            "follow_up_day3": f"Day 3: Follow-up with new information",
            "follow_up_day7": f"Day 7: Final touch with graceful exit",
        }

    def classify_lead(
        self,
        industry_segment: str,
        funded: bool = False,
        hiring: bool = False,
        is_platform: bool = False,
    ) -> str:
        """Classify lead into route type."""
        if is_platform:
            return "platform"
        if industry_segment == "国有企业":
            return "soe"
        if funded:
            return "funded"
        if hiring:
            return "hiring"
        return "content_capacity"
