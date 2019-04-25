MODULE_NAME = 'events'
COMMAND = '$' + MODULE_NAME

NO_CHANNELS = 'Please ensure you add at least 1 channel marked as "events". Otherwise, alerts will not show.'

SUCCESS_EVENT_ADD = 'Your custom event **{}** was added with an ending date of **{}**.'
SUCCESS_EVENT_DEL = 'Your custom event **{}** has been successfully deleted.'

FAIL_EVENT_ADD = 'Your custom event could not be added. Verify if it already exists.\nYou may also be at the limit of 15 events.'
FAIL_EVENT_NAME = 'You cannot add this event as it has the same name as a permanent event.'
FAIL_EVENT_NAME_INVALID = 'Your custom event name is invalid.'
FAIL_EVENT_UPDATE = 'You cannot update nonexistent events.'
FAIL_EVENT_DEL = 'Your custom event could not be deleted.'
FAIL_NO_EVENTS = 'No events were found. Verify file permissions.'

FAIL_INVALID_DATE = 'Your date was invalid.'
