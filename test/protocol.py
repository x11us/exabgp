#!/usr/bin/env python
# encoding: utf-8
"""
protocol.py

Created by Thomas Mangin on 2009-08-27.
Copyright (c) 2009 Exa Networks. All rights reserved.
"""

import unittest

from bgp.table import Table
from bgp.data import IP,ASN,Route,Neighbor
from bgp.message import Message, Open, Update, Notification, KeepAlive
from bgp.protocol import Protocol


from StringIO import StringIO

class Network (StringIO):
	def pending (self):
		return True


class TestProtocol (unittest.TestCase):
	routes = [Route('10.0.0.1','32','10.0.0.254'),Route('10.0.1.1','32','10.0.0.254'),Route('10.0.2.1','32','10.0.0.254')]

	def setUp(self):
		self.table = Table()
		self.table.update(self.routes)
		self.neighbor = Neighbor()
		self.neighbor.local_as = ASN(65000)
		self.neighbor.peer_as = ASN(65000)
		self.neighbor.peer_address = IP('1.2.3.4')
	
	def test_1_selfparse_open (self):
		ds = Open(65000,'1.2.3.4',30,4)
		
		txt = ds.message()
		network = Network(txt)
		#print [hex(ord(c)) for c in txt]
		bgp = Protocol(self.neighbor,network)
		bgp.follow = False

		o = bgp.read_open()
		self.assertEqual(o.version,4)
		self.assertEqual(o.asn,65000)
		self.assertEqual(o.hold_time,30)
		self.assertEqual(str(o.router_id),'1.2.3.4')
	
	def test_2_selfparse_KeepAlive (self):
		ds = KeepAlive()

		txt = ds.message()
		network = Network(txt)
		bgp = Protocol(self.neighbor,network)

		m,d = bgp.read_message()
		self.assertEqual(m,chr(4))
	
	def test_3_parse_Update (self):
		txt = ''.join([chr(c) for c in [0x0, 0x0, 0x0, 0x1c, 0x40, 0x1, 0x1, 0x2, 0x40, 0x2, 0x0, 0x40, 0x3, 0x4, 0xc0, 0x0, 0x2, 0xfe, 0x80, 0x4, 0x4, 0x0, 0x0, 0x0, 0x0, 0x40, 0x5, 0x4, 0x0, 0x0, 0x1, 0x23, 0x20, 0x52, 0xdb, 0x0, 0x7, 0x20, 0x52, 0xdb, 0x0, 0x45, 0x20, 0x52, 0xdb, 0x0, 0x47]])
		
		network = Network('')
		bgp = Protocol(self.neighbor,network)
		bgp.read_update(len(txt),txt)

	def test_4_selfparse_update_announce (self):
		ds = Update(self.table)

		txt = ds.announce(65000,65000)
		network = Network(txt)
		bgp = Protocol(self.neighbor,network)
		bgp.follow = False

		m,_ = bgp.read_message()
		self.assertEqual(m,chr(2))

	def test_5_selfparse_update_announce_multi (self):
		ds = Update(self.table)
		
		txt  = ds.announce(65000,65000)
		txt += ds.update(65000,65000)
		network = Network(txt)

		bgp = Protocol(self.neighbor,network)
		bgp.follow = False

		m,_ = bgp.read_message()
		self.assertEqual(m,chr(2))
		m,_ = bgp.read_message()
		self.assertEqual(m,chr(2))
		m,_ = bgp.read_message()
		self.assertEqual(m,chr(2))
		m,d = bgp.read_message()
		self.assertEqual(m,chr(2))
		self.assertEqual(d,chr(0)*4) 

		self.assertEqual(network.read(1),'')
		#print [hex(ord(c)) for c in msg.read(1024)]


	
if __name__ == '__main__':
	unittest.main()