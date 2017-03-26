###############################################################################
##
##  Copyright (c) Crossbar.io Technologies GmbH
##
##  Licensed under the Apache License, Version 2.0 (the "License");
##  you may not use this file except in compliance with the License.
##  You may obtain a copy of the License at
##
##      http://www.apache.org/licenses/LICENSE-2.0
##
##  Unless required by applicable law or agreed to in writing, software
##  distributed under the License is distributed on an "AS IS" BASIS,
##  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##  See the License for the specific language governing permissions and
##  limitations under the License.
##
###############################################################################

from case import Case
import struct

class Case1_1_9(Case):

   DESCRIPTION = """Send text message with non-minimal-encoded payload length."""

   EXPECTATION = """Client must close the session."""

   def onConnectionLost(self, failedByMe):
      Case.onConnectionLost(self, failedByMe)      
      if self.p.connectionWasOpen and not self.p.closedByMe:
         ## mark the test pass if client close the session
         self.passed = True
         self.result = self.resultClose
         self.behavior = Case.OK
         if self.p.remoteCloseCode in self.expectedClose["closeCode"]:
            self.behaviorClose = Case.OK
         else:
            self.behaviorClose = Case.WRONG_CODE
            self.resultClose = ""

   def onOpen(self):
      test_pl = 690 ## whatever between 0-65535
      payload = "*" * test_pl

      self.expected = [];
      self.expectedClose = {"closedByMe":False,"closeCode":[self.p.CLOSE_STATUS_CODE_PROTOCOL_ERROR],"requireClean":False}

      ## create craft WebSocket Header
      opcode=1; rsv = 0; _mask = 0; fin = 1;

      ## first 1 byte
      b0 = 0
      b0 = fin << 7
      b0 |= (rsv % 8) << 4
      b0 |= opcode % 128
      
      ## mask + payload_len
      b1 = 0      ## initalize
      b1 = _mask << 7 ## mask
      b1 |= 127 ## use extended payload length
      el = struct.pack('>Q',test_pl)

      raw = b''.join([chr(b0),chr(b1),el,payload])

      self.p.trafficStats.outgoingWebSocketFrames += 1
      self.p.logFrames = True;

      self.p.sendData(raw , sync = True, chopsize = test_pl+len(raw))
      self.p.killAfter(1)
