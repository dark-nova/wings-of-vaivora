MODULE_NAME = 'events'
COMMAND = '$' + MODULE_NAME

EMOJI_ALERT = '<:alert:532316827259502612>'

NO_CHANNELS = 'Please ensure you add at least 1 channel marked as "events". Otherwise, alerts will not show.'

SUCCESS_EVENT_ADD = 'Your custom event **{}** was added with an ending date of **{}**.'
SUCCESS_EVENT_DEL = 'Your custom event **{}** has been successfully deleted.'
SUCCESS_ENABLED = 'You have successfully enabled the **{}** permanent event.'
SUCCESS_DISABLED = 'You have successfully disabled the **{}** permanent event.'

FAIL_EVENT_ADD = 'Your custom event could not be added. Verify if it already exists.\nYou may also be at the limit of 15 events.'
FAIL_EVENT_NAME = 'You cannot add this event as it has the same name as a permanent event.'
FAIL_EVENT_NAME_INVALID = 'Your custom event name is invalid.'
FAIL_EVENT_NAME_PERM = 'You entered an invalid permanent event name.'
FAIL_EVENT_UPDATE = 'You cannot update nonexistent events.'
FAIL_EVENT_DEL = 'Your custom event could not be deleted.'
FAIL_NO_EVENTS = 'No events were found. Verify file permissions.'
FAIL_EVENT_TOGGLE = 'Your command could not be processed. The permanent event\'s state could not be toggled.'

FAIL_INVALID_DATE = 'Your date was invalid.'
