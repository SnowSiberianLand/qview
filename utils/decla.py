# Decline Curve Analysis (DCA) utility module
# 2017

import numpy as np

class exponential:
	"""
	exponential decline curve analysis helper
	"""
	def __init__(self, d, q0, t0=0.0):
		"""
		d 	- nominal decline rate, fraction
		t0 	- initial production time
		q0 	- initial production rate
		"""

		self.d = d 
		self.D = -np.log(1.-d)
		self.t0 = t0
		self.q0 = q0

	def rate_impl(self, t):
		return self.q0*np.exp(-self.D*(t-self.t0))

	def rate(self, t):
		"""
		returns rate at time t
		# t could be: number, list of number or numpy.array
		# result is number, list or numpy array
		"""

		# wrap list with numpy array
		if type(t).__name__!='list':
			return self.rate_impl(t)

		t = np.array(t)
				
		qarr = self.rate_impl(t)
		return qarr.tolist()

	def cum_impl(self, t):
		return self.q0/self.D*(1-np.exp(-self.D*(t-self.t0)))

	def cum(self, t):
		"""
		returns cumulative production at time t
		# t could be: number, list of number or numpy.array
		# result is number, list or numpy array
		"""

		# wrap list with numpy array
		if type(t).__name__!='list':
			return self.cum_impl(t)

		t = np.array(t)
				
		qarr = self.cum_impl(t)
		return qarr.tolist()

	def cum2(self, q1, q2):
		return (q1-q2)/self.d

	def Np(self, qlim):
		"""
		reserves to economic limit (defined by rate qlim)
		"""
		return (self.q0-qlim)/self.d

class hyperbolic:
	"""
	hyperbolic decline curve analysis helper
	"""
	def __init__(self, b, D0, q0, t0=0.0):
		"""
		b   - coefficient 
		d0 	- initial decline rate, fraction
		t0 	- initial production time
		q0 	- initial production rate
		"""

		self.b  = b
		self.D0 = D0 
		self.t0 = t0
		self.q0 = q0

	def rate_impl(self, t):
		return self.q0/((1+self.b*self.D0*(t-self.t0))**(1./self.b))

	def rate(self, t):
		"""
		returns rate at time t
		# t could be: number, list of number or numpy.array
		# result is number, list or numpy array
		"""

		# wrap list with numpy array
		if type(t).__name__!='list':
			return self.rate_impl(t)

		t = np.array(t)
				
		qarr = self.rate_impl(t)
		return qarr.tolist()

	def cum_impl(self, t):
		return self.q0/(1-self.b)/self.D0*(1 - (1 + self.b*self.D0*t)**(1-1./self.b) )

	def cum(self, t):
		"""
		returns cumulative production at time t
		# t could be: number, list of number or numpy.array
		# result is number, list or numpy array
		"""

		# wrap list with numpy array
		if type(t).__name__!='list':
			return self.cum_impl(t)

		t = np.array(t)
				
		qarr = self.cum_impl(t)
		return qarr.tolist()

def test():

	vt = [1,2,3,4]

	print('\n---- exponential:')
	tf = exponential(0.1, 100, 0)
	vq = tf.rate(vt)
	vcum = tf.cum(vt)
	print('\t t=', vt)
	#print('\t q=', vq)
	print('\t q= ['+', '.join('{:.2f}'.format(val) for i, val in enumerate(vq))+']' )
	#print('\t Q=', vcum)
	print('\t Q= ['+', '.join('{:.2f}'.format(val) for i, val in enumerate(vcum))+']' )

	b = 0.5
	print('\n---- hyperbolic: b={0}'.format(b))
	tf = hyperbolic(b, 0.1, 100, 0)
	vq = tf.rate(vt)
	vcum = tf.cum(vt)
	print('\t t=', vt)
	#print('\t q=', vq)
	print('\t q= ['+', '.join('{:.2f}'.format(val) for i, val in enumerate(vq))+']' )
	#print('\t Q=', vcum)
	print('\t Q= ['+', '.join('{:.2f}'.format(val) for i, val in enumerate(vcum))+']' )

if __name__ == "__main__":
	test()

	