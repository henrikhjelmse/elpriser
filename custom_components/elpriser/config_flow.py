from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN  # Se till att DOMAIN = "elpris" finns i const.py

class ElprisConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Hantera ett konfigurationsflöde för Elpris."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Hanterar första steget i konfigurationen."""
        errors = {}
        if user_input is not None:
            # Skapa en config entry
            return self.async_create_entry(title=f"Elpris (Område {user_input['område']})", data=user_input)

        # Schema för formuläret
        data_schema = vol.Schema({
            vol.Required("område", default=1): vol.In([1, 2, 3, 4]),
            vol.Required("update_interval", default=5): int,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors
        )
