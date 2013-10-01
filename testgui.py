import sys,random
import time, serial
from PyQt4.Qt import *

########## You can change these ############
serial_debug = True   # turn random serial requests on
logging = True        # turn logging on
bad_bat_temp = 30   # max value for the battery tempurature
max_bat_voltage = 36500 # maximum battery voltage
min_bat_voltage = 26500 # maximum battery voltage
max_ary_voltage = 10000 # maximum array voltage
############################################

delay_time = .5

stop_signal = True

num_of_batteries = 40
num_of_mppts = 8

com_port = '/dev/tty.usbserial-A600c0an'
com_baudrate = 19200
timeout = 1

ser = serial.Serial()

log_file_loc = 'log/test' + time.strftime("%d_%b_%H_%M") + '.txt' #location if the log
log_file_descriptor = open(log_file_loc,'w') #file object
log_next_time = time.time() #the current epoch time in seconds
log_time_offset = 1 #in seconds

min_bat_temp    = 0
max_bat_temp    = 50

#positions of everything
#width between things is 10
back_col = 220,220,250
pen_col = 200,200,250
config_button_coord = 800,5
start_button_coord = 800,40

b_v_c = 10,10,390,385
a_v_c = 410,10,390,135
t_d_c = 410,250,390,145
s_c   = 10,405,390,385
e_c   = 410,405,390,140
soc_c = 410,555,390,95
mph_c = 410,660,190,60
mtr_c = 610,660,190,60
bty_c = 410,730,190,60
ary_c = 610,730,190,60

#title y offset
title_y_offset = 27

bat_bb_col = 0,0,0
bat_bf_col = 150,150,150
bat_fb_col = 0,0,0
bat_ff_col = 0,0,0
bat_inactive_col = 240,240,240

ary_bb_col = 0,0,0
ary_bf_col = 150,150,150
ary_fb_col = 0,0,0
ary_ff_col = 0,0,0
ary_inactive_col = 240,240,240

speed_graph_history = []
speed_graph_time_offset = 10
speed_graph_points = 20

class Battery:
	number = 1
	max_voltage = -1
	volt = -1
	temp = -1
	def __init__(self,b_n=1):
		self.number = b_n
		max_voltage = -1
		self.volt = -1
		self.mppt = -1
		self.temp = -1
	def new_voltage(self,v):
		self.volt = v
		if self.volt > self.max_voltage and max_bat_voltage > 0:
			self.max_voltage = self.volt
	def new_temp(self,t):
		#wowee
		self.temp = t
class MPPT:
	number = -1
	voltage = -1
	current = -1
	def __init__(self,b_n=1):
		self.number = b_n
		self.voltage = -1
		self.current = -1
	def new_voltage(self,v):
		self.voltage = v
	def new_voltage(self,v):
		self.current = v
class SpeedGraphConfig(QWidget):
	def __init__(self):
		QWidget.__init__(self)
		#put config stuff
		#graph time offset
		self.btn_1 = QPushButton('Time Offset', self)
		self.btn_1.setGeometry(5,1,140,30)
		self.btn_1.clicked.connect(self.showTimeDialog)
		#number of graph points
	def showTimeDialog(self):
		global speed_graph_time_offset

		ok = False
		text, ok = QInputDialog.getText(self, 'Input Dialog', 
		   'Time Offset For Graph(integer):')
		if ok and str(text).isdigit():
			if 0 < int(str(text)) <= 60:
				speed_graph_time_offset = int(str(text))
				print "speed graph offset set to " + str(speed_graph_time_offset)
			else:
				print "Number too high or low (0 < x <= 60)"
				self.showTimeDialog()
		else:
			if not ok:
				print "GUI didnt work"
				if str(text) == '':
					text = '0'
					ok = False
			if not str(text).isdigit():
				print "Not a Digit"
				print str(text)
				self.showTimeDialog()
class Config(QWidget):
	def __init__(self):
		QWidget.__init__(self)
		# put config stuff
		#  -number of batteries(1-40)
		self.btn_1 = QPushButton('# of batteries', self)
		self.btn_1.setGeometry(5,1,140,30)
		self.btn_1.clicked.connect(self.showBatteryDialog)
		#  -number of array modules
		self.btn_2 = QPushButton('# of arrays', self)
		self.btn_2.setGeometry(5,25,140,30)
		self.btn_2.clicked.connect(self.showMPPTDialog)
		#  -Port
		self.btn_3 = QPushButton('Serial Port', self)
		self.btn_3.setGeometry(5,49,140,30)
		self.btn_3.clicked.connect(self.showMPPTDialog)
		#  -number of array modules
		self.btn_4 = QPushButton('Port Speed', self)
		self.btn_4.setGeometry(5,73,140,30)
		self.btn_4.clicked.connect(self.showMPPTDialog)
		#  -number of speed graph history
		self.btn_5 = QPushButton('Speed Graph', self)
		self.btn_5.setGeometry(5,73,140,30)
		self.btn_5.clicked.connect(self.openSpeedConfig)

	def battery_conf(self):
		self.le = QLineEdit(self)
		self.le.move(130, 22)
	def showBatteryDialog(self):
		global num_of_batteries
		ok = False
		text = 'a'
		text, ok = QInputDialog.getText(self, 'Input Dialog', 
		   'Enter # of Batteries:')
		if ok and str(text).isdigit():
			if 0 < int(str(text)) < 41:
				num_of_batteries = int(str(text))				
				print "Config = ",num_of_batteries
			else:
				print "Number too high or low (0 < x <= 40)"
		else:
			if not ok:
				print "GUI didnt work"
				if str(text) == '':
					text = '0'
					ok = False
			if not str(text).isdigit():
				print "Not a Digit"
				print str(text)
	def showMPPTDialog(self):
		global num_of_mppts
		ok = False
		text = 'a'
		text, ok = QInputDialog.getText(self, 'Input Dialog', 
		   'Enter # of Arrays:')
		if ok and str(text).isdigit():
			if 0 < int(str(text)) < 9:
				num_of_mppts = int(str(text))				
				print num_of_mppts	
			else:
				print "Number too high or low (0 < x <= 8)"
		else:
			if not ok:
				print "GUI didnt work"
			if not str(text).isdigit():
				print "Not a Digit"
	def showPortDialog(self):
		global com_port
		ok = False
		text = 'a'
		text, ok = QInputDialog.getText(self, 'Input Dialog', 
		   'Enter # of Arrays:')
		if ser.isOpen():
			ser.close()
		com_port = text
	def showBaudrateDialog(self):
		global com_baudrate
		ok = False
		text = 'a'
		text, ok = QInputDialog.getText(self, 'Input Dialog', 
		   'Enter # of Arrays:')
		if ok and str(text).isdigit():
			if int(str(text)) in [ 1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200 ]:
				com_baudrate= int(str(text))			
				print com_baudrate
			else:
				print "Number not an actual serial buadrate"
		else:
			if not ok:
				print "GUI didnt work"
			if not str(text).isdigit():
				print "Not a Digit"
	def openSpeedConfig(self):
		self.s = SpeedGraphConfig()
		self.s.setGeometry(QRect(500, 200, 150, 200))
		self.s.show()
class MainWindow(QMainWindow):

	def __init__(self, *args):

		QMainWindow.__init__(self, *args)
		self.cw = QWidget(self)
		self.setCentralWidget(self.cw)

		self.config_b = QPushButton("Config", self.cw)
		self.config_b.setGeometry(QRect(config_button_coord[0],config_button_coord[1], 200, 30))

		self.start_serial_button = QPushButton("Start Serial Port", self.cw)
		self.start_serial_button.setGeometry(QRect(start_button_coord[0],start_button_coord[1], 200, 30))

		self.read_serial_button = QPushButton("Read Serial Port", self.cw)
		self.read_serial_button.setGeometry(QRect(start_button_coord[0],start_button_coord[1] + 35, 200, 30))

		self.stop_serial_button = QPushButton("Stop Serial Port", self.cw)
		self.stop_serial_button.setGeometry(QRect(start_button_coord[0],start_button_coord[1] + 70, 200, 30))
		
		self.connect(self.config_b, SIGNAL("clicked()")              , self.config)
		self.connect(self.start_serial_button, SIGNAL("clicked()")   , self.start_serial)
		self.connect(self.read_serial_button, SIGNAL("clicked()")    , self.read_serial)
		self.connect(self.stop_serial_button, SIGNAL("clicked()")    , self.stop_serial)

		self.w = None
		self.batteries = []
		self.arrays = []

		self.battery_current = None
		self.array_current = None
		self.motor_current = None
		self.motor_speed = None

		self.total_pack_voltage = -1

		self.highest_bat_voltage_val = "xx"
		self.highest_bat_voltage_num = "yy"
		self.lowest_bat_voltage_val = "xx"
		self.lowest_bat_voltage_num = "yy"

		self.cbs_module = "NOT SURE WHAT THIS IS"

		self.avg_velocity = "NOT IMPLEMENTED YET"
		self.avg_mtr_current = "NOT IMPLEMENTED YET"
		self.avg_ary_current = "NOT IMPLEMENTED YET"
		self.avg_bat_current = "NOT IMPLEMENTED YET"

	def config(self):
		print "Opening Config..."
		self.w = Config()
		self.w.setGeometry(QRect(500, 200, 150, 200))
		self.w.show()
	def setup_serial(self):
		global serial_debug
		if not serial_debug:
			global ser 
			global com_port 
			global com_baudrate 
			global timeout
			ser.close()
			ser.port = com_port 
			ser.baudrate = com_baudrate
			ser.timeout = timeout
	def start_serial(self):
		global serial_debug
		global stop_signal
		global ser

		self.delay_for_serial_read()

		if max_bat_voltage >= 0:
			for battery in self.batteries:
				battery.max_voltage = max_bat_voltage
		stop_signal = False
		self.setup_serial()
		if not serial_debug:
			ser.open()
			if not ser.isOpen():
				print "something happened open serial Didnt work"
	def stop_serial(self):
		global ser
		global stop_signal
		stop_signal = True
		ser.close()
	def read_serial(self):
		global serial_debug
		global stop_signal
		global ser
		if not stop_signal:
			# read the serial port for something
			if (ser.isOpen() or serial_debug):
				if serial_debug:
					x = " "
					c = random.randint(0,7)
					if c == 0:
						i = random.randint(0,100)
						j = random.randint(1,40)
						x = 'V[' + str(j) + ']=' + str(i) 
					elif c == 1:
						i = random.randint(0,100)
						j = random.randint(1,40)
						x = 'T[' + str(j) + ']=' + str(i) 
					elif c == 2:
						i = random.randint(0,100)
						j = random.randint(1,40)
						x = 'P[' + str((j%8)+1) + ']=' + str(i) 
					elif c == 3:
						i = float(random.randint(0,10000))/100
						x = 'BC' + '=' + str(i) 
					elif c == 4:
						i = float(random.randint(0,10000))/100
						x = 'AC' + '=' + str(i)[:5] 
					elif c == 5:
						i = float(random.randint(0,10000))/100
						x = 'MC' + '=' + str(i)[:5] 					
					elif c == 6:
						i = float(random.randint(0,10000))/100
						x = 'S' + '=' + str(i)[:5] 
				else:
					x = ser.readline().strip()
					print x
				# parse the output for something useful
				if len(x) > 0:
					input_type = x[0]
					if input_type == 'V':
						if x.split('[')[1].split(']')[0].isdigit():
							num = int(x.split('[')[1].split(']')[0])
							if x.split('=')[1].isdigit():
								val = int(x.split('=')[1])
								self.change_battery_volt(num,val)
							else:
								print "incorrect input from serial port"
						else:
							print "incorrect input from serial port"
					elif input_type == 'T':
						if x.split('[')[1].split(']')[0].isdigit():
							num = int(x.split('[')[1].split(']')[0])
							if x.split('=')[1].isdigit():
								val = int(x.split('=')[1])
								self.change_battery_temp(num,val)
							else:
								print "incorrect input from serial port"
						else:
							print "incorrect input from serial port"
					elif input_type == 'P':
						if x.split('[')[1].split(']')[0].isdigit():
							num = int(x.split('[')[1].split(']')[0])
							if x.split('=')[1].isdigit():
								val = int(x.split('=')[1])
								self.change_mppt_voltage(num,val)
							else:
								print "incorrect input from serial port"
						else:
							print "incorrect input from serial port"
					elif input_type == 'B':
						current = x.split('=')[1]
						if current.replace('.','').isdigit():
							val = float(current)
							self.change_battc_value(val)
						else:
							print "incorrect input from serial port"
					elif input_type == 'A':
						current = x.split('=')[1]
						if current.replace('.','').isdigit():
							val = float(current)
							self.change_array_value(val)
						else:
							print "incorrect input from serial port"
					elif input_type == 'M':
						current = x.split('=')[1]
						if current.replace('.','').isdigit():
							val = float(current)
							self.change_motor_value(val)
						else:
							print "incorrect input from serial port"
					elif input_type == 'S':
						speed = x.split('=')[1]
						if speed.replace('.','').isdigit():
							val = float(speed)
							self.change_car_speed(val)
						else:
							print "incorrect input from serial port"
	def change_battery_volt(self,num,volt):
		if num-1 < len(self.batteries):
			self.batteries[num-1].new_voltage(volt)

			self.total_pack_voltage = -1
			self.highest_bat_voltage_val = 0
			self.highest_bat_voltage_num = 0
			self.lowest_bat_voltage_val = 1000000
			self.lowest_bat_voltage_num = 0
			for battery in self.batteries:
				if battery.volt != -1:
					self.total_pack_voltage += battery.volt
					if battery.volt > self.highest_bat_voltage_val:
						self.highest_bat_voltage_val = battery.volt
						self.highest_bat_voltage_num = battery.number
					elif battery.volt < self.lowest_bat_voltage_val:
						self.lowest_bat_voltage_val = battery.volt
						self.lowest_bat_voltage_num = battery.number
	def change_battery_temp(self,num,temp):
		if num-1 < len(self.batteries):
			self.batteries[num-1].new_temp(temp)
	def change_mppt_voltage(self,num,volt):
		if num-1 < len(self.arrays):
			self.arrays[num-1].voltage = float(volt)
	def change_battc_value(self,val):
		#change average battery current
		self.battery_current = val
	def change_array_value(self,val):
		#change average array current
		self.array_current = val
	def change_motor_value(self,val):
		#change the motor current
		self.motor_current = val
	def change_car_speed(self,val):
		#change car speed
		self.motor_speed = val
	def delay_for_serial_read(self):
		time.sleep(delay_time)
		if not stop_signal:
			SIGNAL('delay_for_serial_read')
	def paintEvent(self,event):
		global ser
		global serial_debug

		global log_time_offset
		global log_next_time

		if (ser.isOpen() or serial_debug) and not stop_signal:
			self.read_serial()

		#check to see if we need to change the number of batteries
		if len(self.batteries) != num_of_batteries:
			self.batteries = []
			for a in xrange(0,num_of_batteries):
				self.batteries.append(Battery(b_n=a+1))
		if len(self.arrays) != num_of_mppts:
			self.arrays = []
			for a in xrange(0,num_of_mppts):
				self.arrays.append(MPPT(b_n=a+1))

		if logging and not stop_signal:
			if log_next_time < time.time():
				log_next_time = time.time() + log_time_offset
				self.log_info()


		qp = QPainter()
		qp.begin(self)
		self.draw_b_v(qp)
		self.draw_a_v(qp)
		self.draw_t_d(qp)
		self.draw_s(qp)
		self.draw_e(qp)
		self.draw_soc(qp)
		self.draw_mph(qp)
		self.draw_mtr(qp)
		self.draw_bty(qp)
		self.draw_ary(qp)
		qp.end()
		self.cw.repaint()
	def log_info(self):
		global log_file_descriptor
		#build the log buy putting all values
		s = ''

		#battery voltages
		for battery in self.batteries:
			s += str(battery.volt) + "\t"
		s += "\t"

		#battery temp
		for battery in self.batteries:
			s += str(battery.temp) + "\t"
		s += "\t"

		#array voltage
		for mppt in self.arrays:
			s += str(mppt.voltage) + "\t"
		s += "\t"

		#motor current
		s += str(self.motor_current) + "\t"

		#motor speed
		s += str(self.motor_speed) + "\t"

		log_file_descriptor.write(s + "\n")
	def draw_b_v(self,q):

		global max_bat_voltage

		global min_bat_temp
		global max_bat_temp

		def draw_single_battery(qq,px,py,volt_percentage,temp_percentage,num,inactive=False):

			#parse percentage voltage
			sx  = 25
			sy  = 75
			npx = px
			npy = py+(sy-int(volt_percentage*sy))
			nsx = sx
			nsy = int(volt_percentage*sy)

			#get the colors
			if temp_percentage != None:
				blue = int((1-temp_percentage) * 255)
				red = int((temp_percentage) * 255)
				t_bb_col = t_fb_col = t_ff_col = red,0,blue
				t_bf_col = bat_bf_col


			if inactive:
				#draw background of battery
				q.setPen(QColor(bat_inactive_col[0],bat_inactive_col[1],bat_inactive_col[2]))
				q.setBrush(QColor(bat_inactive_col[0],bat_inactive_col[1],bat_inactive_col[2]))
				q.drawRect(px,py,sx,sy)
				#print "Inactive Battery"

			else:
				if temp_percentage == None:
					#draw background of battery
					q.setPen(QColor(bat_bb_col[0],bat_bb_col[1],bat_bb_col[2]))
					q.setBrush(QColor(bat_bf_col[0],bat_bf_col[1],bat_bf_col[2]))
					q.drawRect(px,py,sx,sy)
					#draw foreground of battery
					q.setPen(QColor(bat_fb_col[0],bat_fb_col[1],bat_fb_col[2]))
					q.setBrush(QColor(bat_ff_col[0],bat_ff_col[1],bat_ff_col[2]))
					q.drawRect(npx,npy,nsx,nsy)
				else:
					if t < .9:
						#draw background of battery
						q.setPen(QColor(t_bb_col[0],t_bb_col[1],t_bb_col[2]))
						q.setBrush(QColor(t_bf_col[0],t_bf_col[1],t_bf_col[2]))
						q.drawRect(px,py,sx,sy)
						#draw foreground of battery
						q.setPen(QColor(t_fb_col[0],t_fb_col[1],t_fb_col[2]))
						q.setBrush(QColor(t_ff_col[0],t_ff_col[1],t_ff_col[2]))
						q.drawRect(npx,npy,nsx,nsy)
					else:
						pen = QPen(QColor(t_bb_col[0],t_bb_col[1],t_bb_col[2]))
						pen.setWidth(4)
						#draw background of battery
						q.setPen(pen)
						q.setBrush(QColor(t_bf_col[0],t_bf_col[1],t_bf_col[2]))
						q.drawRect(px-2,py-2,sx+4,sy+4)
						#draw foreground of battery
						q.setPen(QColor(t_fb_col[0],t_fb_col[1],t_fb_col[2]))
						q.setBrush(QColor(t_ff_col[0],t_ff_col[1],t_ff_col[2]))
						q.drawRect(npx,npy,nsx,nsy)
		#draw background
		q.setPen(QColor(pen_col[0],pen_col[1],pen_col[2]))
		q.setBrush(QColor(back_col[0],back_col[1],back_col[2]))
		q.drawRect(b_v_c[0],b_v_c[1],b_v_c[2],b_v_c[3])

		#draw title
		q.setPen(QColor(0, 0, 0))
		q.setFont(QFont('Decorative', 20))
		q.drawText(135,b_v_c[1]+title_y_offset, 'Battery Voltages')   

		#draw batteries
		offset_x = b_v_c[0] + 25
		offset_y = b_v_c[1] + 40
		for a in xrange(0,len(self.batteries)):
			if self.batteries[a].volt <= 0:
				draw_single_battery(q,offset_x,offset_y,1,1,a,inactive=True)
			else:
				#set the voltage percentage
				p = float(self.batteries[a].volt-min_bat_voltage)/float(max_bat_voltage-min_bat_voltage)
				if p > 1:
					p = 1
				if p < 0:
					p = 0
				#set the temp percentage
				if self.batteries[a].temp == -1:
					t = None
				elif self.batteries[a].temp <= min_bat_temp:
					t = 0
				elif self.batteries[a].temp >= max_bat_temp:
					t = 1
				else:
					t = (float(self.batteries[a].temp)-float(min_bat_temp))/(float(max_bat_temp)-float(min_bat_temp))
				draw_single_battery(q,offset_x,offset_y,p,t,a)
			if offset_x > (b_v_c[2] + b_v_c[0] - 75):
				offset_y += 85
				offset_x = b_v_c[0] + 25
			else:
				offset_x += 35
	def draw_a_v(self,q):

		global max_ary_voltage

		def draw_single_array(qq,px,py,volt_percentage,num,inactive=False):

			#parse percentage voltage
			sx  = 25
			sy  = 75
			npx = px
			npy = py+(sy-int(volt_percentage*sy))
			nsx = sx
			nsy = int(volt_percentage*sy)


			if inactive:
				#draw background of array
				q.setPen(QColor(bat_inactive_col[0],bat_inactive_col[1],bat_inactive_col[2]))
				q.setBrush(QColor(bat_inactive_col[0],bat_inactive_col[1],bat_inactive_col[2]))
				q.drawRect(px,py,sx,sy)

			else:

				#draw background of array
				q.setPen(QColor(ary_bb_col[0],ary_bb_col[1],ary_bb_col[2]))
				q.setBrush(QColor(ary_bf_col[0],ary_bf_col[1],ary_bf_col[2]))
				q.drawRect(px,py,sx,sy)
				#draw foreground of attay
				q.setPen(QColor(ary_fb_col[0],ary_fb_col[1],ary_fb_col[2]))
				q.setBrush(QColor(ary_ff_col[0],ary_ff_col[1],ary_ff_col[2]))
				q.drawRect(npx,npy,nsx,nsy)

		q.setPen(QColor(pen_col[0],pen_col[1],pen_col[2]))
		q.setBrush(QColor(back_col[0],back_col[1],back_col[2]))
		q.drawRect(a_v_c[0],a_v_c[1],a_v_c[2],a_v_c[3])

		#draw title
		q.setPen(QColor(0, 0, 0))
		q.setFont(QFont('Decorative', 20))
		q.drawText(540,a_v_c[1]+title_y_offset, 'Array Voltages')   

		#draw array
		offset_x = a_v_c[0] + 55
		offset_y = a_v_c[1] + 40
		for a in xrange(0,len(self.arrays)):
			if self.arrays[a].voltage < 0:
				draw_single_array(q,offset_x,offset_y,1,a,inactive=True)
			else:
				#set the voltage percentage
				p = float(self.arrays[a].voltage)/float(max_ary_voltage)
				if p > 1:
					p = 1
				draw_single_array(q,offset_x,offset_y,p,a)
			if offset_x > (a_v_c[2] + a_v_c[0] - 75):
				offset_y += 85
				offset_x = b_v_c[0] + 25
			else:
				offset_x += 35
	def draw_t_d(self,q):
		global back_col
		#draw background
		q.setPen(QColor(pen_col[0],pen_col[1],pen_col[2]))
		q.setBrush(QColor(back_col[0],back_col[1],back_col[2]))
		q.drawRect(t_d_c[0],t_d_c[1],t_d_c[2],t_d_c[3])
	def draw_s(self,q):  

		#draw the background
		q.setPen(QColor(pen_col[0],pen_col[1],pen_col[2]))
		q.setBrush(QColor(back_col[0],back_col[1],back_col[2]))
		q.drawRect(s_c[0],s_c[1],s_c[2],s_c[3])

		#draw the Title
		q.setPen(QColor(0, 0, 0))
		q.setFont(QFont('Decorative', 20))
		q.drawText(s_c[0]+20,s_c[1]+title_y_offset, 'Statistics') 

		# for the stats we need to print out
		#	total pack voltage	xx
		q.setPen(QColor(0, 0, 0))
		q.setFont(QFont('Decorative', 12))
		q.drawText(s_c[0]+20,s_c[1]+50, 'Total Pack Voltage = ' + str(float(self.total_pack_voltage)/10)[:6] + "mV") 
		#	Highest Voltage		xx(yy)
		q.setPen(QColor(0, 0, 0))
		q.setFont(QFont('Decorative', 12))
		q.drawText(s_c[0]+20,s_c[1]+70, 'Highest Voltage = ' + str(self.highest_bat_voltage_val)  + "(" + str(self.highest_bat_voltage_num) + ")") 
		#	lowest voltage		xx(yy)
		q.setPen(QColor(0, 0, 0))
		q.setFont(QFont('Decorative', 12))
		q.drawText(s_c[0]+20,s_c[1]+90, 'Lowest Voltage = ' + str(self.lowest_bat_voltage_val)  + "(" + str(self.lowest_bat_voltage_num) + ")") 
		#	CBS module			(yy)
		q.setPen(QColor(0, 0, 0))
		q.setFont(QFont('Decorative', 12))
		q.drawText(s_c[0]+20,s_c[1]+110, 'CBS Module = ' + str(self.cbs_module)) 
		#	Avg Velocity
		q.setPen(QColor(0, 0, 0))
		q.setFont(QFont('Decorative', 12))
		q.drawText(s_c[0]+20,s_c[1]+130, 'Average Velocity = ' + str(self.avg_velocity)) 
		#	Avg motor current
		q.setPen(QColor(0, 0, 0))
		q.setFont(QFont('Decorative', 12))
		q.drawText(s_c[0]+20,s_c[1]+150, 'Average Motor Current = ' + str(self.avg_mtr_current)) 
		#	Avg Array Current
		q.setPen(QColor(0, 0, 0))
		q.setFont(QFont('Decorative', 12))
		q.drawText(s_c[0]+20,s_c[1]+170, 'Average Array Current = ' + str(self.avg_ary_current)) 
		#	avg bat current
		q.setPen(QColor(0, 0, 0))
		q.setFont(QFont('Decorative', 12))
		q.drawText(s_c[0]+20,s_c[1]+190, 'Average Battery Current = ' + str(self.avg_bat_current)) 
	def draw_e(self,q):  
		global back_col
		q.setPen(QColor(pen_col[0],pen_col[1],pen_col[2]))
		q.setBrush(QColor(back_col[0],back_col[1],back_col[2]))
		q.drawRect(e_c[0],e_c[1],e_c[2],e_c[3])
	def draw_soc(self,q):
		global back_col
		q.setPen(QColor(pen_col[0],pen_col[1],pen_col[2]))
		q.setBrush(QColor(back_col[0],back_col[1],back_col[2]))
		q.drawRect(soc_c[0],soc_c[1],soc_c[2],soc_c[3])
	def draw_mph(self,q):
		global back_col
		color = QColor(pen_col[0],pen_col[1],pen_col[2])
		
		#draw background
		q.setPen(color)
		q.setBrush(QColor(back_col[0],back_col[1],back_col[2]))
		q.drawRect(mph_c[0],mph_c[1],mph_c[2],mph_c[3])

		#draw title
		q.setPen(QColor(0, 0, 0))
		q.setFont(QFont('Decorative', 20))
		q.drawText(mph_c[0]+10,mph_c[1]+title_y_offset, 'Speed') 

		#draw speed
		m_str = ""
		x_pos = mph_c[0] + 76
		if self.motor_speed == None:
			m_str = "-.-- MPH"
			x_pos += 10
		elif self.motor_speed >= 0:
			m_str = str(self.motor_speed)[:4]+" MPH"
		else:
			m_str = str(self.motor_speed)[:5]+" MPH"
			x_pos -= 9

		q.setPen(QColor(0, 0, 0))
		q.setFont(QFont('Decorative', 25))
		q.drawText(x_pos,712, m_str) 
	def draw_mtr(self,q):
		global back_col
		color = QColor(pen_col[0],pen_col[1],pen_col[2])

		#draw background
		q.setPen(color)
		q.setBrush(QColor(back_col[0],back_col[1],back_col[2]))
		q.drawRect(mtr_c[0],mtr_c[1],mtr_c[2],mtr_c[3])

		#draw title
		q.setPen(QColor(0, 0, 0))
		q.setFont(QFont('Decorative', 20))
		q.drawText(mtr_c[0]+10,mtr_c[1]+title_y_offset, 'Motor Current') 

		#draw current
		m_str = ""
		x_pos = mtr_c[0] + 76
		if self.motor_current == None:
			m_str = "-.-- (A)"
			x_pos += 10
		elif self.motor_current >= 0:
			m_str = str(self.motor_current)[:4]+" (A)"
		else:
			m_str = str(self.motor_current)[:5]+" (A)"
			x_pos -= 9

		q.setPen(QColor(0, 0, 0))
		q.setFont(QFont('Decorative', 25))
		q.drawText(x_pos,712, m_str) 
	def draw_bty(self,q):
		global back_col
		color = QColor(pen_col[0],pen_col[1],pen_col[2])

		#draw background
		q.setPen(color)
		q.setBrush(QColor(back_col[0],back_col[1],back_col[2]))
		q.drawRect(bty_c[0],bty_c[1],bty_c[2],bty_c[3])

		#draw title
		q.setPen(QColor(0, 0, 0))
		q.setFont(QFont('Decorative', 20))
		q.drawText(bty_c[0]+10,bty_c[1]+title_y_offset, 'Battery Current') 

		#draw current
		m_str = ""
		x_pos = bty_c[0] + 76
		if self.battery_current == None:
			m_str = "-.-- (A)"
			x_pos += 10
		elif self.battery_current >= 0:
			m_str = str(self.battery_current)[:4]+" (A)"
		else:
			m_str = str(self.battery_current)[:5]+" (A)"
			x_pos -= 9

		q.setPen(QColor(0, 0, 0))
		q.setFont(QFont('Decorative', 25))
		q.drawText(x_pos,782, m_str) 
	def draw_ary(self,q):
		global back_col
		color = QColor(pen_col[0],pen_col[1],pen_col[2])

		#draw background
		q.setPen(color)
		q.setBrush(QColor(back_col[0],back_col[1],back_col[2]))
		q.drawRect(ary_c[0],ary_c[1],ary_c[2],ary_c[3])

		#draw title
		q.setPen(QColor(0, 0, 0))
		q.setFont(QFont('Decorative', 20))
		q.drawText(ary_c[0]+10,ary_c[1]+title_y_offset, 'Array Current') 

		#draw current
		m_str = ""
		x_pos = ary_c[0] + 76
		if self.array_current == None:
			m_str = "-.-- (A)"
			x_pos += 10
		elif self.array_current >= 0:
			m_str = str(self.array_current)[:4]+" (A)"
		else:
			m_str = str(self.array_current)[:5]+" (A)"
			x_pos -= 9

		q.setPen(QColor(0, 0, 0))
		q.setFont(QFont('Decorative', 25))
		q.drawText(x_pos,782, m_str) 
class App(QApplication): 

	def __init__(self, *args):
		QApplication.__init__(self, *args)
		self.main = MainWindow()
		self.connect(self, SIGNAL("lastWindowClosed()"), self.byebye )
		self.main.setGeometry(200, 50, 1000, 800)
		self.main.show()
	def byebye( self ):
		log_file_descriptor.close()
		self.exit(0)

def main(args):
	global app
	app = App(args)
	app.exec_()


if __name__ == "__main__":
	main(sys.argv)



