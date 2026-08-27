"""Config flow for Product Expiration Tracker."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import CONF_PHOTO_BASE_URL, CONF_WARN_DAYS, DEFAULT_WARN_DAYS, DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema({
    vol.Optional(CONF_PHOTO_BASE_URL): cv.string,
    vol.Optional(CONF_WARN_DAYS, default=",".join(map(str, DEFAULT_WARN_DAYS))): cv.string,
})


class ProductExpirationConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Product Expiration Tracker."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        # Only allow one instance
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()
        
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate warn_days format
            try:
                warn_days_str = user_input.get(CONF_WARN_DAYS, "")
                if warn_days_str:
                    warn_days = [int(x.strip()) for x in warn_days_str.split(",")]
                    if not all(d > 0 for d in warn_days):
                        raise ValueError("All warning days must be positive")
                    user_input[CONF_WARN_DAYS] = sorted(warn_days)
                else:
                    user_input[CONF_WARN_DAYS] = DEFAULT_WARN_DAYS
            except ValueError as err:
                errors[CONF_WARN_DAYS] = "invalid_warn_days"
                _LOGGER.debug("Invalid warn_days: %s", err)

            if not errors:
                return self.async_create_entry(
                    title="Product Expiration Tracker",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
            description_placeholders={
                "warn_days_example": "30,15,7,3,1",
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> ProductExpirationOptionsFlow:
        """Get the options flow for this handler."""
        return ProductExpirationOptionsFlow(config_entry)


class ProductExpirationOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Product Expiration Tracker."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate warn_days
            try:
                warn_days_str = user_input.get(CONF_WARN_DAYS, "")
                if warn_days_str:
                    warn_days = [int(x.strip()) for x in warn_days_str.split(",")]
                    if not all(d > 0 for d in warn_days):
                        raise ValueError("All warning days must be positive")
                    user_input[CONF_WARN_DAYS] = sorted(warn_days)
                else:
                    user_input[CONF_WARN_DAYS] = DEFAULT_WARN_DAYS
            except ValueError as err:
                errors[CONF_WARN_DAYS] = "invalid_warn_days"
                _LOGGER.debug("Invalid warn_days: %s", err)

            if not errors:
                return self.async_create_entry(title="", data=user_input)

        current_photo_url = self.config_entry.options.get(
            CONF_PHOTO_BASE_URL,
            self.config_entry.data.get(CONF_PHOTO_BASE_URL, ""),
        )
        current_warn_days = self.config_entry.options.get(
            CONF_WARN_DAYS,
            self.config_entry.data.get(CONF_WARN_DAYS, DEFAULT_WARN_DAYS),
        )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional(CONF_PHOTO_BASE_URL, default=current_photo_url): cv.string,
                vol.Optional(
                    CONF_WARN_DAYS,
                    default=",".join(map(str, current_warn_days)),
                ): cv.string,
            }),
            errors=errors,
        )
