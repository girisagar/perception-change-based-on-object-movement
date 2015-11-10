import re
import autopy
import win32gui


def send_keystrokes(key_combo):
    on_right = key_combo.split('`')

    match_letter = re.compile('^[a-z0-9.,]$', re.IGNORECASE)

    get_ap_keys = lambda on_key: (False, on_key[1]) if on_key[0] == '(nothing)' else (on_key[0], on_key[1])

    modifier, key = get_ap_keys(on_right)

    if match_letter.match(key):
        if not modifier:
            if key == 'K_LEFT' or key == 'K_RIGHT' or key == 'K_UP' or key == 'K_DOWN':
                autopy.key.tap(autopy.key.type_string(key))
            else:
                autopy.key.type_string(key)
        else:
            autopy.key.tap(autopy.key.type_string(key), getattr(autopy.key, modifier))
    else:
        if not modifier:
            # autopy.key.type_string(key)
            autopy.key.tap(getattr(autopy.key, key))
        else:
            autopy.key.tap(getattr(autopy.key, key), getattr(autopy.key, modifier))

    # print 'Modifier: ' + modifier
    # print 'Key: ' + key


def perform_action(config, direction, method):
    active_window = win32gui.GetWindowText(win32gui.GetForegroundWindow())
    
    for window in config.get('allowed_windows'):        
        if window.get('name') in active_window and window.get('works_on') == "Face":
            # Perform action only on allowed windows
            print window.get('name')
            print 'Direction: ' + direction

            if direction == 'Right':
                # autopy.key.type_string('n')
                send_keystrokes(window.get('on_right'))

            elif direction == 'Left':                
                # autopy.key.type_string('p')
                send_keystrokes(window.get('on_left'))

            elif direction == 'Palm Open':
                send_keystrokes(window.get('on_popen'))
                # autopy.key.tap (autopy .key.K_LEFT )
                # autopy.key.type_string(',')

            elif direction == 'Palm Close':
                # autopy.key.type_string('.')
                send_keystrokes(window.get('on_pclose'))