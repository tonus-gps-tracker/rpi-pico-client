class LocationDTO:

	def __init__(self, timestamp = 0, latitude = 0.0, longitude = 0.0, altitude = 0.0, speed = 0.0, n_satellites = 0) -> None:
		self.timestamp = timestamp
		self.latitude = latitude
		self.longitude = longitude
		self.altitude = altitude
		self.speed = speed
		self.n_satellites = n_satellites

	def __str__(self):
		return f'{self.timestamp},{self.latitude},{self.longitude},{self.altitude},{'{:.2f}'.format(self.speed)},{self.n_satellites}'