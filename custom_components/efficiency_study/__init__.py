import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, Event
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.event import async_track_state_change_event

from .const import (
    DOMAIN,
    CONF_INFLUX_URL,
    CONF_INFLUX_TOKEN,
    CONF_INFLUX_ORG,
    CONF_INFLUX_BUCKET,
    CONF_HOUSE_ID,
    CONF_MONITORED_ENTITIES,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Home Efficiency Study from a config entry."""
    
    hass.data.setdefault(DOMAIN, {})

    url = entry.data.get(CONF_INFLUX_URL, "").rstrip("/")
    token = entry.data.get(CONF_INFLUX_TOKEN)
    org = entry.data.get(CONF_INFLUX_ORG)
    bucket = entry.data.get(CONF_INFLUX_BUCKET)
    house_id = entry.data.get(CONF_HOUSE_ID)
    
    write_url = f"{url}/api/v2/write?org={org}&bucket={bucket}&precision=ns"
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "text/plain"
    }
    
    session = async_get_clientsession(hass)

    async def state_change_listener(event: Event):
        """Handle state changes and push to InfluxDB."""
        new_state = event.data.get("new_state")
        if new_state is None:
            return
            
        entity_id = new_state.entity_id
        state = new_state.state
        
        if state in ("unknown", "unavailable"):
            return
        
        # Attempt to cast state to float, otherwise encode as a string line protocol field
        try:
            val = float(state)
            val_str = str(val)
        except ValueError:
            # Escape quotes in string state
            safe_state = str(state).replace('"', '\\"')
            val_str = f'"{safe_state}"'
            
        safe_house_id = str(house_id).replace(" ", "\\ ").replace(",", "\\,").replace("=", "\\=")
        
        # InfluxDB Line Protocol: measurement,tags fields timestamp
        payload = f"efficiency_study,entity_id={entity_id},house_id={safe_house_id} value={val_str}"
        
        _LOGGER.debug("Efficiency Study uploading state change for %s: %s", entity_id, payload)
        
        try:
            async with session.post(write_url, headers=headers, data=payload) as response:
                if response.status in (200, 204):
                    _LOGGER.debug("Successfully wrote %s to InfluxDB", entity_id)
                else:
                    text = await response.text()
                    _LOGGER.error("Failed to write to InfluxDB: %s. Response: %s", response.status, text)
        except Exception as err:
            _LOGGER.error("Error writing to InfluxDB: %s", err)

    entities = entry.options.get(CONF_MONITORED_ENTITIES, [])
    
    unsub = None
    if entities:
        unsub = async_track_state_change_event(hass, entities, state_change_listener)
        
    hass.data[DOMAIN][entry.entry_id] = {
        "unsub": unsub
    }
    
    # Reload the integration when options change (e.g. user selects different sensors)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    data = hass.data[DOMAIN].get(entry.entry_id)
    if data and data.get("unsub"):
        data["unsub"]()
        
    hass.data[DOMAIN].pop(entry.entry_id)
    return True

async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await hass.config_entries.async_reload(entry.entry_id)
