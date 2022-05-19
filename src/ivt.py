import sys
import canlib
import cantools
from canlib import canlib
from canlib.canlib import ChannelData, Stat
import re
from random import randint


class Backend():
    def __init__(self):
        self.db = cantools.database.load_file('../Core/CAN/can2.dbc')
        self.virtual = False
        self.ch = self.select_channel()
        self.ch2 = self.select_channel(-2)
        self.data = dict()
        self.channels = dict()
        self.frame_ids = [self.db.get_message_by_name("IVT_Msg_Result_I").frame_id,
                          self.db.get_message_by_name("IVT_Msg_Result_U1").frame_id,
                          self.db.get_message_by_name("IVT_Msg_Result_U2").frame_id,
                          self.db.get_message_by_name("IVT_Msg_Result_U3").frame_id]

    # Get all available channels
    def get_available_channels(self):
        channels = dict()
        for ch in range(canlib.getNumberOfChannels()):
            chd = canlib.ChannelData(ch)
            channels[ch] = chd.channel_name
        self.channels.update(channels)
        return channels

    # Send data if connected to Virtual channel
    def send_data(self):
        # For every (in this case only one) frame_id representing, Current messages, send current data
        for frame_id in self.frame_ids[:1]:
            tx_frame = self.db.get_message_by_frame_id(frame_id)

            # Create dictionary with data to be sent
            canTx = dict()
            canTx["IVT_Result_I_System_Error"] = 0
            canTx["IVT_Result_I_OCS"] = 0
            canTx["IVT_Result_I_Measurement_Error"] = 0
            canTx["IVT_Result_I_Channel_Error"] = 0
            canTx["IVT_ID_Result_I"] = 0
            canTx["IVT_MsgCount_Result_I"] = 0
            canTx["IVT_Result_I"] = randint(0, 100)

            tx_data = tx_frame.encode(canTx)
            # Send encoded data
            self.ch2.write_raw(frame_id, tx_data)

        # For every frame_id representing Voltage messages, send voltage data
        for i, frame_id in enumerate(self.frame_ids[1:]):
            tx_frame = self.db.get_message_by_frame_id(frame_id)

            # Create dictionary with data to be sent
            canTx = dict()
            canTx[f"IVT_Result_U{i+1}_System_Error"] = 0
            canTx[f"IVT_Result_U{i+1}_OCS"] = 0
            canTx[f"IVT_Result_U{i+1}_Measurement_Error"] = 0
            canTx[f"IVT_Result_U{i+1}_Channel_Error"] = 0
            canTx[f"IVT_ID_Result_U{i+1}"] = i+1
            canTx[f"IVT_MsgCount_Result_U{i+1}"] = 0
            canTx[f"IVT_Result_U{i+1}"] = randint(0, 100)

            tx_data = tx_frame.encode(canTx)
            # Send encoded data
            self.ch2.write_raw(frame_id, tx_data)

    # Get data from CAN
    def get_data(self):
        new_data = dict()
        while Stat.RX_PENDING in self.ch.readStatus():
            rx = self.ch.read()
            rx_id = rx.id
            rx_data = bytes(rx.data)
            try:
                if rx_id in self.frame_ids:
                    rx_frame = self.db.get_message_by_frame_id(rx_id)
                    data = rx_frame.decode(rx.data)
                    new_data.update(data)
            except:
                print("ERROR")
        self.data.update(new_data)
        return new_data

    # Return current important data (IVT_Result)
    def get_important_data(self):
        d = dict()
        d["IVT_Result_I"] = self.data["IVT_Result_I"]
        d["IVT_Result_U1"] = self.data["IVT_Result_U1"]
        d["IVT_Result_U2"] = self.data["IVT_Result_U2"]
        d["IVT_Result_U3"] = self.data["IVT_Result_U3"]
        return d


    # Select channel by channel id, if none selected, try to connect to CAN2,
    # if real CAN not connected, connect to VIRTUAL CAN2
    def select_channel(self, selected = -1):
        ch_real, ch_virtual = False, False
        if selected == -1:
            for ch_num in range(canlib.getNumberOfChannels()):
                chd = canlib.ChannelData(ch_num)
                # Look for Virtual CAN2 channel
                if re.search("[Vv]irtual.+(channel 1)", chd.channel_name):
                    print(f"Found Virtual CAN2 channel with channel_id: {ch_num}")
                    selected = ch_num
                    break
                # Look for Non-Virtual channel, with channel number 1.
                if not re.search("[Vv]irtual", chd.channel_name) and re.match("(channel 1)", chd.channel_name):
                    print(f"Found Non-Virtual CAN2 channel with channel_id: {ch_num}")
                    selected = ch_num
                    break
        elif selected == -2:
            for ch_num in range(canlib.getNumberOfChannels()):
                chd = canlib.ChannelData(ch_num)
                # Look for Virtual CAN1 channel
                if re.search("[Vv]irtual.+(channel 0)", chd.channel_name):
                    print(f"Found Virtual CAN1 channel with channel_id: {ch_num}")
                    selected = ch_num
                    break
        # Open selected channel, and allow virtual channel
        ch = canlib.openChannel(selected, canlib.canOPEN_ACCEPT_VIRTUAL)
        ch.setBusOutputControl(canlib.canDRIVER_NORMAL)
        # Set bitrate to 500 000
        ch.setBusParams(canlib.canBITRATE_500K)
        # Turn on bus
        ch.busOn()
        chd = canlib.ChannelData(selected)

        if bool(re.search("[Vv]irtual", chd.channel_name)):
            self.virtual = True
        return ch

    # Update data
    def update(self):
        # Only send data if on Virtual channel
        if self.virtual:
            self.send_data()
        self.get_data()

"""
c = Backend()
c.get_available_channels()
for i in range(0, 100):
    c.send_data()
    c.get_data()
    print(f"I: {c.data['IVT_Result_I']}")
    print(f"U1: {c.data['IVT_Result_U1']}")
    print(f"U2: {c.data['IVT_Result_U2']}")
    print(f"U3: {c.data['IVT_Result_U3']}")
"""
#b = Backend()


def test():
    db = cantools.database.load_file('../Core/CAN/can2.dbc')
    print(db.messages)
    print(db.get_message_by_name("IVT_Msg_Result_U1"))
    #print(db.get_message_by_name("charger_config").signals)

    num_channels = canlib.getNumberOfChannels()
    print(f"Found {num_channels} channels")
    for ch in range(num_channels):
        chd = canlib.ChannelData(ch)
        print(f"[Channel {ch}] {chd.channel_name} ({chd.card_upc_no} / {chd.card_serial_no})")
    print(Stat.RX_PENDING)
