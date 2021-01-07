
from sqlalchemy.dialects.postgresql import ENUM


dlstate_enum   = ENUM('new', 'fetching', 'processing', 'complete', 'error', 'skipped', 'removed', 'disabled', 'specialty_blocked', 'specialty_deferred', 'manually_deferred', 'specialty_ready', name='dlstate_enum')
itemtype_enum  = ENUM('western', 'eastern', 'unknown',            name='itemtype_enum')

nu_item_enum   = ENUM('unverified', 'valid', 'rejected', 'disabled', 'manual_validate',          name='nu_item_enum')
