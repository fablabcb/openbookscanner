from pytest import fixture


class TestObserver:
    """Test the observer behavior."""
        
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
        @timeout
        def check_for_state_update():
            hardware_listener.update()
            return hardware_listener.state.could_not_detect_driver_support
        assert not hardware_listener.state.finding_hardware_changes

    def test_driver_is_supported(self, hardware_listener):
        hardware_listener.driver_support = True
        @timeout
        def check_for_state_update():
            hardware_listener.update()
            return hardware_listener.state.finding_hardware_changes
        assert hardware_listener.state.finding_hardware_changes

    def test_new_hardware_added(self, hardware_listener, observer):
        hardware_listener.driver_support = True
        hw = object()
        hardware_listener.new_test_hardware.append(hw)
        @timeout
        def check_for_state_update():
            #print(hardware_listener.get_hardware(), hardware_listener.new_test_hardware)
            hardware_listener.update()
            return observer.new_hardware_detected.called
        observer.new_hardware_detected.assert_called_once_with(hw)
        

