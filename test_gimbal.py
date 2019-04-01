from control.gimbal import GimbalMessage
import struct


class TestGimbalMessage(object):

    def test_pack(self):

        gimbal_msg = GimbalMessage(serial_port='/dev/ttyUSB0', serial_baud=115200)

        # case 2: ptz control
        message = gimbal_msg.pack_send(cmd='zoom_focus', mode='set', zoom_value=-30, focus_value=50)
        import time
        time.sleep(5)
        message = gimbal_msg.pack_send(cmd='zoom', mode='in')
        time.sleep(5)
        message = gimbal_msg.pack_send(cmd='zoom', mode='out')
        time.sleep(5)
        message = gimbal_msg.pack_send(cmd='zoom', mode='stop')
        # assert ('#TPUG2wGSYE276' == message)
        # assert ('#tpUG6wGAYEC78328D' == message)
        exit(0)

        # case 1: zoom in
        message = gimbal_msg.pack(cmd_str='zoom', mode='in')
        assert ('#TPUM2wZMC015D' == message)

        # case 2: zoom out
        message = gimbal_msg.pack(cmd_str='zoom', mode='out')
        assert ('#TPUM2wZMC025E' == message)

        # case 3: zoom stop
        message = gimbal_msg.pack(cmd_str='zoom', mode='stop')
        assert ('#TPUM2wZMC005C' == message)

        # case 1: zoom get
        message = gimbal_msg.pack(cmd_str='zoom', mode='get')
        assert ('#TPUM2rZOM0063' == message)

        # case 1: focus in
        message = gimbal_msg.pack(cmd_str='focus', mode='+')
        assert ('#TPUM2wFCC013F' == message)

        # case 2: focus out
        message = gimbal_msg.pack(cmd_str='focus', mode='-')
        assert ('#TPUM2wFCC0240' == message)

        # case 3: focus stop
        message = gimbal_msg.pack(cmd_str='focus', mode='stop')
        assert ('#TPUM2wFCC003E' == message)

        # case 3: focus get
        message = gimbal_msg.pack(cmd_str='focus', mode='get')
        assert ('#TPUM2rFOC0045' == message)

        # case 2: ptz control
        message = gimbal_msg.pack(cmd_str='ptz_control', mode='set_mode', value='up')
        assert ('#TPUP2wPTZ0174' == message)

        # case 2: ptz control
        message = gimbal_msg.pack(cmd_str='ptz_control', mode='set_speed', value='low')
        assert ('#TPUP2wSPD005C' == message)

        # case 2: ptz control
        message = gimbal_msg.pack(cmd_str='ptz_control', mode='yaw_speed', value=-30)
        assert ('#TPUG2wGSYE276' == message)

        # case 2: ptz control
        message = gimbal_msg.pack(cmd_str='ptz_control', mode='yaw_angle', angle_value=-50, rate_value=50)
        assert ('#tpUG6wGAYEC78328D' == message)

        # case 2: ptz control
        message = gimbal_msg.pack(cmd_str='ptz_control', mode='angle_get')
        assert ('#TPUG2rGAC0032' == message)
        print('message(type{}): {}'.format(type(message), message))

        print('all unit test cases are SUCCESS!')

if __name__ == '__main__':
    test = TestGimbalMessage()
    test.test_pack()


