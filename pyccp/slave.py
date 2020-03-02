#!/usr/bin/env python
# -*- coding: utf-8 -*-

__copyright__ = """
    pySART - Simplified AUTOSAR-Toolkit for Python.

   (C) 2009-2016 by Christoph Schueler <cpu12.gems@googlemail.com>

   All Rights Reserved

  This program is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 2 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License along
  with this program; if not, write to the Free Software Foundation, Inc.,
  51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""

import enum
from can import Bus, Message

from pyccp import ccp
from pyccp.messages.command_receive import CommandCodes
from pyccp.messages.data_transmission import DTOType
from pyccp.messages.command_return import ReturnCodes
from pyccp.logger import Logger


def getLEWord(payload):
    return payload[1] << 8 | payload[0]


def getBEWord(payload):
    return payload[0] << 8 | payload[1]


class SlaveState(enum.IntEnum):

    DISCONNECTED = 1
    CONNECTED = 2


class Slave(object):
    def __init__(self, stationAddress, transport: Bus, memory):
        self.stationAddress = stationAddress
        self.transport = transport
        self.masterAddress = 0x0815
        self._mta = 0x0000
        self.ctr = 0x00
        self.setState(SlaveState.DISCONNECTED)
        self.logger = Logger("pyccp.slave")
        # Ignore telegrams if not connected.

    def receive(self, cmo):
        """
        :param cmo: CAN Message Object
        :type cmo: `CANMessageObject`
        """
        print("Received: {}".format(cmo))
        self.logger.debug("Received: {}".format(cmo))
        self.commandHandler(cmo)

    def setState(self, state):
        self.state = SlaveState(state)

    def getState(self):
        return self.state

    def sendDTO(self, returnCode, counter, payload=[0, 0, 0, 0, 0]):
        payload = list(payload) + [0] * (5 - len(payload))
        message = Message(
            arbitration_id=self.masterAddress,
            data=[DTOType.COMMAND_RETURN_MESSAGE, returnCode, counter, *payload],
        )
        self.transport.send(message)

    def sendDTOIfConnected(self, returnCode, counter, payload=[]):
        if self.state == SlaveState(SlaveState.CONNECTED):
            self.sendDTO(returnCode, counter, payload)

    def commandHandler(self, cmo):
        cmd = cmo.data[0]
        counter = cmo.data[1]
        payload = cmo.data[2:]
        handler = self.COMMAND_HANDLERS.get(cmd, None)
        if handler:
            handler(self, counter, payload)
        else:
            pass  # TODO: CCP error handling.

    def onConnect(self, counter, payload):
        self.logger.debug("onConnect")
        stationAddress = getLEWord(payload[0:])
        # print("connecting", counter, payload)
        if stationAddress == self.stationAddress:
            self.setState(SlaveState.CONNECTED)
            self.sendDTO(ReturnCodes.ACKNOWLEDGE, counter)
        else:
            self.setState(SlaveState.DISCONNECTED)

    def onGetCCPVersion(self, counter, payload):
        # This command is expected to be executed prior to the EXCHANGE_ID command.
        self.logger.debug("onGetCCPVersion")
        self.sendDTO(ReturnCodes.ACKNOWLEDGE, counter, ccp.CCP_VERSION)
        # self.sendDTOIfConnected(ReturnCodes.ACKNOWLEDGE, counter, ccp.CCP_VERSION)

    def onTest(self, counter, payload):
        self.logger.debug("onTest")

    def onExchangeId(self, counter, payload):
        self.logger.debug("onExchangeId")

    def onSetMta(self, counter, payload):
        self.logger.debug("onSetMta")

    def onDnload(self, counter, payload):
        self.logger.debug("onDnload")

    def onDnload6(self, counter, payload):
        self.logger.debug("onDnload6")

    def onUpload(self, counter, payload):
        self.logger.debug("onUpload")

    def onShortUp(self, counter, payload):
        """
        0xff    0x00 0x23 0x10 0x11 0x12 0x13
        """
        self.logger.debug("onShortUp")

    def onGetDaqSize(self, counter, payload):
        self.logger.debug("onGetDaqSize")

    def onSetDaqPtr(self, counter, payload):
        self.logger.debug("onSetDaqPtr")

    def onWriteDaq(self, counter, payload):
        self.logger.debug("onWriteDaq")

    def onStartStopAll(self, counter, payload):
        self.logger.debug("onStartStopAll")

    def onStartStop(self, counter, payload):
        self.logger.debug("onStartStop")

    def onDisconnect(self, counter, payload):
        self.logger.debug("onDisconnect")

    def onSetSStatus(self, counter, payload):
        self.logger.debug("onSetSStatus")

    def onGetSStatus(self, counter, payload):
        self.logger.debug("onGetSStatus")

    def onBuildChksum(self, counter, payload):
        self.logger.debug("onBuildChksum")

    def onClearMemory(self, counter, payload):
        self.logger.debug("onClearMemory")

    def onProgram(self, counter, payload):
        self.logger.debug("onProgram")

    def onProgram6(self, counter, payload):
        self.logger.debug("onProgram6")

    def onMove(self, counter, payload):
        self.logger.debug("onMove")

    def onGetActiveCalPage(self, counter, payload):
        self.logger.debug("onGetActiveCalPage")

    def onSelectCalPage(self, counter, payload):
        self.logger.debug("onSelectCalPage")

    def onUnlock(self, counter, payload):
        self.logger.debug("onUnlock")

    def onGetSeed(self, counter, payload):
        self.logger.debug("onGetSeed")

    COMMAND_HANDLERS = {
        CommandCodes.CONNECT: onConnect,
        CommandCodes.GET_CCP_VERSION: onGetCCPVersion,
        CommandCodes.TEST: onTest,
        CommandCodes.EXCHANGE_ID: onExchangeId,
        CommandCodes.SET_MTA: onSetMta,
        CommandCodes.DNLOAD: onDnload,
        CommandCodes.DNLOAD_6: onDnload6,
        CommandCodes.UPLOAD: onUpload,
        CommandCodes.SHORT_UP: onShortUp,
        CommandCodes.GET_DAQ_SIZE: onGetDaqSize,
        CommandCodes.SET_DAQ_PTR: onSetDaqPtr,
        CommandCodes.WRITE_DAQ: onWriteDaq,
        CommandCodes.START_STOP_ALL: onStartStopAll,
        CommandCodes.START_STOP: onStartStop,
        CommandCodes.DISCONNECT: onDisconnect,
        CommandCodes.SET_S_STATUS: onSetSStatus,
        CommandCodes.GET_S_STATUS: onGetSStatus,
        CommandCodes.BUILD_CHKSUM: onBuildChksum,
        CommandCodes.CLEAR_MEMORY: onClearMemory,
        CommandCodes.PROGRAM: onProgram,
        CommandCodes.PROGRAM_6: onProgram6,
        CommandCodes.MOVE: onMove,
        CommandCodes.GET_ACTIVE_CAL_PAGE: onGetActiveCalPage,
        CommandCodes.SELECT_CAL_PAGE: onSelectCalPage,
        CommandCodes.UNLOCK: onUnlock,
        CommandCodes.GET_SEED: onGetSeed,
    }
