# config_flow.py
from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN, PRICE_AREAS

class ElprisConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Hantera ett konfigurationsflöde för Elpris."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Hanterar första steget i konfigurationen."""
        errors = {}
        
        if user_input is not None:
            # Skapa en config entry med områdets namn
            area_name = PRICE_AREAS[str(user_input['område'])]
            return self.async_create_entry(
                title=f"Elpris ({area_name})", 
                data=user_input
            )

        # Schema för formuläret med områdesnamn
        area_options = {int(k): v for k, v in PRICE_AREAS.items()}
        
        data_schema = vol.Schema({
            vol.Required("område", default=1): vol.In(
                {k: v for k, v in area_options.items()}
            ),
            vol.Required("update_interval", default=5): int,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors
        )