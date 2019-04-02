import logging
import struct
import serial
import traceback

# create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# create file handler
log_path = "./log.log"
fh = logging.FileHandler(log_path)
fh.setLevel(logging.WARN)

# create formatter
fmt = "%(asctime)-15s %(levelname)s %(filename)s %(lineno)d %(process)d %(message)s"
datefmt = "%a %d %b %Y %H:%M:%S"
formatter = logging.Formatter(fmt, datefmt)

# add handler and formatter to logger
fh.setFormatter(formatter)
logger.addHandler(fh)


class CmdM:
    cmd_M_type = 'M'

    zoom_ctl  = 'wZMC'
    zoom_get  = 'rZOM'
    focus_ctl = 'wFCC'
    focus_get = 'rFOC'

    zoom_focus_set = 'wZFP'

    cam_resv_set    = 'wCZR' # not supported by vendor still


class CmdP:
    cmd_P_type = 'P'

    ptz_ctl     = 'wPTZ'

    ptz_mode = {
            'stop': '00',
            'up'  : '01',
            'down': '02',
            'left': '03',
            'right': '04',
            'center': '05',
            'follow': '06',
            'yaw_lock': '07',
            'follow_yaw_lock_switch': '08',
            'calibrate': '09',
            }

    spd_ctl     = 'wSPD'

    spd_mode = {
            'low': '00',
            'medium'  : '01',
            'high': '02',
            'left': '03',
            }

    gim_spd_yaw_ctl = 'wGSY'
    gim_spd_pit_ctl = 'wGSP'
    gim_spd_rll_ctl = 'wGSR'
    gim_spd_yaw_pit_ctl = 'wGSM'

    gim_ang_yaw_ctl = 'wGAY'
    gim_ang_pit_ctl = 'wGAP'
    gim_ang_rll_ctl = 'wGAR'
    gim_ang_yaw_pit_ctl = 'wGAM'

    gim_ang_get = 'rGAC'

    # not supported
    gim_ang_resv_set  = 'wGPE'
    gim_ang_resv_read = 'rGAR'
    gim_ang_resv_call = 'cGAR'

    scene_day_night_switch = 'wIRC'

class CmdD:
    cmd_D_type = 'D'

    AWB_set = 'wAWB'

    class AWBType:
        auto = '0'
        night = '1'
        incandescent = '2'
        fluorescent = '3'
        warm_fluorescent = '4'
        daylight = '5'
        couldy_daylight = '6'
        twilight = '7'
        shade = '8'
        AWB_inc = 'A'
        AWB_dec = 'B'
        AWB_null = 'N'

    AWB_type = AWBType()

    ISO_set = 'wISO'
    class ISOType:
        auto = '0'
        ISO100 = '1'
        ISO200 = '2'
        ISO400 = '3'
        ISO800 = '4'
        ISO1600 = '5'
        ISO_inc = 'A'
        ISO_dec = 'B'
        ISO_null = 'N'

    ISO_type = ISOType()

    EV_set = 'wEVS'
    class EVType:
        minus_3 = '0'
        minus_2 = '1'
        minus_1 = '2'
        EV_0    = '3'
        EV_1    = '4'
        EV_2    = '5'
        EV_3    = '6'
        EV_inc  = 'A'
        EV_dec  = 'B'
        EV_null = 'N'

    EV_type = EVType()

    PIC_size_set = 'wPIC'
    class PicSizeType:
        size_400w = '0'
        size_800w = '1'
        size_1300w = '2'
        size_1600w = '3'
        size_inc = 'A'
        size_dec = 'B'
        size_null = 'N'

    pic_size_type = PicSizeType()

    VID_size_set = 'wVID'
    class VidSizeType:
        size_720p = '0'
        size_1080p = '0'
        size_inc = 'A'
        size_dec = 'B'
        size_null = 'N'

    vid_size_type = VidSizeType()

    PIP_mode_set = 'wPIP'
    class PipModeType:
        type_m_s = '0'
        type_m   = '1'
        type_s_m = '2'
        type_s   = '3'
        type_inc = 'A'
        type_dec = 'B'

    pip_mode_type = PipModeType()

    gim_spd_yaw_ctl = 'wGSY'
    gim_spd_pit_ctl = 'wGSP'
    gim_spd_rll_ctl = 'wGSR'
    gim_spd_yaw_pit_ctl = 'wGSM'

    gim_ang_yaw_ctl = 'wGAY'
    gim_ang_pit_ctl = 'wGAP'
    gim_ang_rll_ctl = 'wGAR'
    gim_ang_yaw_pit_ctl = 'wGAM'

    gim_ang_get = 'rGAC'

    # not supported
    gim_ang_resv_set  = 'wGPE'
    gim_ang_resv_read = 'rGAR'
    gim_ang_resv_call = 'cGAR'


# usage GimbalMessage("/dev/ttyUSB0", serial_baud=9600)
class GimbalMessage(object):
    # serial_port = None
    def __init__(self, serial_port=None, serial_baud=115200):
        if serial_port is not None:
            try:
                self.serial_port = serial.Serial(serial_port, serial_baud, timeout=2)  # 2s timeout
            except:
                traceback.print_exc()
        else:
            self.serial_port = None

        # for now, just fix-size cmd ('#tp' is for dynamic-size cmd)
        # self.head = '#TPU' # 'U' is UART

        #
        self.crc = 'RR'

    def send_to(self, data):
        if self.serial_port is not None:
            self.serial_port.write(data.encode())
        else:  # just for debug
            logger.error('send to {raw_data} but no serial port available'.format(raw_data=data))
        pass

    def receive_from(self, data_len):
        """
        :return: BE order bytes from serial port
        """

        recv_data = self.serial_port.read(data_len)
        # return struct.unpack('>{}B'.format(recv_data), recv_data)
        return recv_data

    def to_hex(self, val, nbits=8):
        if nbits == 8:
            return ('{:02x}'.format((val + (1 << nbits)) % (1 << nbits))).upper()
        elif nbits == 16:
            return ('{:04x}'.format((val + (1 << nbits)) % (1 << nbits))).upper()

    def pack(self, cmd_str, **data):
        """
        :param cmd_str: e.g. yaw, ...
        :param data: dict format, e.g. mode=start
        :return: packed message(BE order bytes)
        """

        logger.info('pack data {dt}'.format(dt=data))

        message = []

        if cmd_str == 'zoom':
            head = '#TPU'
            cmd = ''
            lens = ''
            val = ''
            if data['mode'] == 'in':
                cmd = CmdM.zoom_ctl
                lens = '2'
                val = '01' # according to protocol, TODO: need move to CmdM define class
            elif data['mode'] == 'out':
                cmd = CmdM.zoom_ctl
                lens = '2'
                val = '02' # according to protocol, TODO: need move to CmdM define class
            elif data['mode'] == 'stop':
                cmd = CmdM.zoom_ctl
                lens = '2'
                val = '00' # according to protocol, TODO: need move to CmdM define class
            elif data['mode'] == 'get':
                cmd = CmdM.zoom_get
                lens = '2'
                val = '00' # according to protocol, TODO: need move to CmdM define class
            else:
                logger.error('unsupported mode type {type}'.format(type=data['mode']))
                return False

            # struct it
            message = head + CmdM.cmd_M_type + lens + cmd + val
            self.crc = self.to_hex(sum(map(ord, message)))
            message = message + self.crc

        elif cmd_str == 'focus':
            head = '#TPU'
            cmd = ''
            lens = ''
            val = ''

            if data['mode'] == '+':
                cmd = CmdM.focus_ctl
                lens = '2'
                val = '01'  # according to protocol, TODO: need move to CmdM define class
            elif data['mode'] == '-':
                cmd = CmdM.focus_ctl
                lens = '2'
                val = '02'  # according to protocol, TODO: need move to CmdM define class
            elif data['mode'] == 'stop':
                cmd = CmdM.focus_ctl
                lens = '2'
                val = '00'  # according to protocol, TODO: need move to CmdM define class
            elif data['mode'] == 'get':
                cmd = CmdM.focus_get
                lens = '2'
                val = '00'  # according to protocol, TODO: need move to CmdM define class
            else:
                logger.error('unsupported mode type {type}'.format(type=data['mode']))
                return False

            # struct it
            message = head + CmdM.cmd_M_type + lens + cmd + val
            self.crc = self.to_hex(sum(map(ord, message)))
            message = message + self.crc

        elif cmd_str == 'zoom_focus':
            head = '#tpU'
            cmd = ''
            lens = ''
            val = ''

            if data['mode'] == 'set':
                cmd = CmdM.zoom_focus_set
                lens = '8'
                val = self.to_hex(data['zoom_value'], 16)
                val = val + self.to_hex(data['focus_value'], 16)
            else:
                logger.error('unsupported mode type {type}'.format(type=data['mode']))
                return False

            # struct it
            message = head + CmdM.cmd_M_type + lens + cmd + val
            self.crc = self.to_hex(sum(map(ord, message)))
            message = message + self.crc
            # message = '#tpUM8wZFPFFB400320F'

        elif cmd_str == 'ptz_control':
            head = ''
            cmd_type = ''
            cmd = ''
            lens = ''
            val = ''

            if data['mode'] == 'set_mode':
                head = '#TPU'
                cmd_type = 'P'
                cmd = CmdP.ptz_ctl
                lens = '2'
                val = CmdP.ptz_mode[data['value']]
            elif data['mode'] == 'set_speed':
                head = '#TPU'
                cmd_type = 'P'
                cmd = CmdP.spd_ctl
                lens = '2'
                val = CmdP.spd_mode[data['value']]
            elif data['mode'] == 'yaw_speed':
                head = '#TPU'
                cmd_type = 'G'
                cmd = CmdP.gim_spd_yaw_ctl
                lens = '2'
                val = self.to_hex(data['value'])
            elif data['mode'] == 'pitch_speed':
                head = '#TPU'
                cmd_type = 'G'
                cmd = CmdP.gim_spd_pit_ctl
                lens = '2'
                val = self.to_hex(data['value'])
            elif data['mode'] == 'roll_speed':
                head = '#TPU'
                cmd_type = 'G'
                cmd = CmdP.gim_spd_rll_ctl
                lens = '2'
                val = self.to_hex(data['value'])
            elif data['mode'] == 'yaw_pitch_speed':
                head = '#tpU'
                cmd_type = 'G'
                cmd = CmdP.gim_spd_yaw_pit_ctl
                lens = '4'
                val = self.to_hex(data['yaw_value']) + self.to_hex(data['pitch_value'])
            elif data['mode'] == 'yaw_angle':
                head = '#tpU'
                cmd_type = 'G'
                cmd = CmdP.gim_ang_yaw_ctl
                lens = '6'
                val = self.to_hex(data['angle_value']*100, 16) + self.to_hex(data['rate_value'])
            elif data['mode'] == 'pitch_angle':
                head = '#tpU'
                cmd_type = 'G'
                cmd = CmdP.gim_ang_pit_ctl
                lens = '6'
                val = self.to_hex(data['angle_value']*100, 16) + self.to_hex(data['rate_value'])
            elif data['mode'] == 'roll_angle':
                head = '#tpU'
                cmd_type = 'G'
                cmd = CmdP.gim_ang_rll_ctl
                lens = '6'
                val = self.to_hex(data['angle_value']*100, 16) + self.to_hex(data['rate_value'])
            elif data['mode'] == 'yaw_pitch_angle':
                head = '#tpU'
                cmd_type = 'G'
                cmd = CmdP.gim_ang_yaw_pit_ctl
                lens = 'C'
                val = self.to_hex(data['yaw_value']*100, 16) + self.to_hex(data['yaw_rate'])
                val = val + self.to_hex(data['pitch_value']*100, 16) + self.to_hex(data['pitch_rate'])
            elif data['mode'] == 'angle_get':
                head = '#TPU'
                cmd_type = 'G'
                cmd = CmdP.gim_ang_get
                lens = '2'
                val = '00'
            else:
                logger.error('unsupported mode type {type}'.format(type=data['mode']))
                return False

            # struct it
            message = head + cmd_type + lens + cmd + val
            self.crc = self.to_hex(sum(map(ord, message)))
            message = message + self.crc
        else:
            logger.error('unsupported command {cmd}'.format(cmd=cmd_str))
            return False

        logger.debug('pack message {msg}'.format(msg=message))
        return message

    def pack_send(self, cmd, **data_in):
        if 'get' in data_in['mode']:
            self.send_to(self.pack(cmd_str=cmd, **data_in))
            # get attitude
            import time
            time.sleep(0.05)
            recv_len = 4  # need to be diff with cmds
            return self.receive_from(recv_len)
        else:
            # self.send_to(self.pack(cmd_str=cmd, **data_in))
            msg = self.pack(cmd_str=cmd, **data_in)
            print('send [{}] done'.format(msg))
            self.send_to(msg)
            import time
            time.sleep(0.05)
            recv_len = 4  # need to be diff with cmds
            recv_str = self.receive_from(32)
            print('get [{}] done'.format(recv_str.decode()))
            return None
        pass

    def unpack(self):
        pass



