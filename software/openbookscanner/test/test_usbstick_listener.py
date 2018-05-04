
def test_zero_on_start(usle):
    assert not usle.has_new_hardware()

def test_zero_before_one_after(usle):
    usle.listen_for_hardware()
    assert usle.has_new_hardware()

def test_new_hardware_notified_once(usle, mock):
    usle.print_state_changes()
    usle.register_hardware_observer(mock)
    usle.listen_for_hardware()
    usle.update() # not thread-safe
    usle.update()
    print(mock.new_hardware_detected.call_args_list)
    mock.new_hardware_detected.assert_called_once()
    assert mock.new_hardware_detected.call_args[0][0].is_USBStick()