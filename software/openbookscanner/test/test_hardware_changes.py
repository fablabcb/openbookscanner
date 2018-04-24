from pytest import fixture


class TestObserver:
    """Test the observer behavior."""

    @fixture
    def observer(self, mock, hardware_listener):
        hardware_listener.register_hardware_observer(mock)
        return mock
        
    def test_no_new_hardware(self, observer, hardware_listener):
        assert not hardware_listener.has_new_hardware()
        hardware_listener.notify_about_new_hardware()
        observer.new_hardware_detected.assert_not_called()

    def test_noone_is_notified_just_by_addding(self, observer, hardware_listener):
        hardware = object()
        hardware_listener.found_new_hardware(hardware)
        assert hardware_listener.has_new_hardware()
        observer.new_hardware_detected.assert_not_called()

    def test_new_hardware_was_added(self, observer, hardware_listener):
        hardware = object()
        hardware_listener.found_new_hardware(hardware)
        hardware_listener.notify_about_new_hardware()
        observer.new_hardware_detected.assert_called_once_with(hardware)


class TestStateTransition:
    """Test that the states are correctly transitioned."""
    
    def test_driver_not_supported(self, hardware_listener):
        assert hardware_listener.state.is_detecting_driver_support
        timeout(lambda: hardware_listener.state.could_not_detect_driver_support)



