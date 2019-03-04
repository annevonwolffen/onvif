from onvif import ONVIFCamera
from time import sleep

class Camera():
    def __init__(self, ip, port, user, passwd):
        # Connecting to the camera
        self.cam = ONVIFCamera(ip, port, user, passwd)

        self.request_continuous_move = None
        self.ptz = None
        # Create media service object
        self.media = self.cam.create_media_service()
        # Get target profile
        self.media_profile = self.media.GetProfiles()[0]
        self.ptz = self.cam.create_ptz_service()
        # Get PTZ configuration options for getting move ranges
        request = self.ptz.create_type('GetConfigurationOptions')
        request.ConfigurationToken = self.media_profile.PTZConfiguration._token
        self.ptz_configuration_options = self.ptz.GetConfigurationOptions(request)
        print('PTZ configuration options: ' + str(self.ptz_configuration_options))


        self.request_stop = self.ptz.create_type('Stop')
        self.request_stop.ProfileToken = self.media_profile._token

        self.request_continuous_move = self.ptz.create_type('ContinuousMove')
        self.request_continuous_move.ProfileToken = self.media_profile._token
        if self.request_continuous_move.Velocity is None:
            self.request_continuous_move.Velocity = self.ptz.GetStatus({'ProfileToken': self.media_profile._token}).Position

        self.request_absolute_move = self.ptz.create_type('AbsoluteMove')
        self.request_absolute_move.ProfileToken = self.media_profile._token

        # Create imaging service
        self.imaging = self.cam.create_imaging_service()
        # Getting available imaging services
        request = self.imaging.create_type('GetServiceCapabilities')
        service_capabilities = self.ptz.GetServiceCapabilities(request)
        print("Service capabilities: " + str(service_capabilities))
        self.request_absolute_focus = self.imaging.create_type('Move')
        self.request_absolute_focus.VideoSourceToken = self.media_profile.VideoSourceConfiguration.SourceToken
        print('Focus move options: ' + str(self.request_absolute_focus))

        request = self.imaging.create_type('GetMoveOptions')
        request.VideoSourceToken = VideoSourceToken = self.media_profile.VideoSourceConfiguration.SourceToken
        move_options = self.imaging.GetMoveOptions(request)
        print('Imaging options: ' + str(move_options))
        

    # Function to get camera's information
    def get_info(self):
        # Get Hostname
        print('Hostname is: ' + str(self.cam.devicemgmt.GetHostname().Name))
        # Get info
        print('Device information: ' + str(self.cam.devicemgmt.GetDeviceInformation()))
        # Get system date and time
        dt = self.cam.devicemgmt.GetSystemDateAndTime()
        tz = dt.TimeZone
        year = dt.UTCDateTime.Date.Year
        hour = dt.UTCDateTime.Time.Hour

        print('Timezone: ' + str(tz))

        print('Year: ' + str(year))
        print('Hour: ' + str(hour))

    def get_pos(self):
        # Getting PTZ status
        status = self.ptz.GetStatus({'ProfileToken': self.media_profile._token})

        print("PTZ position: " + str(status.Position))

    def stop(self):
        self.request_stop = self.ptz.create_type('Stop')
        self.request_stop.ProfileToken = self.media_profile._token
        self.request_stop.PanTilt = True
        self.request_stop.Zoom = True
        self.ptz.Stop(self.request_stop)
        
    def perform_continuous_move(self,timeout):
        # Start continuous move
        self.ptz.ContinuousMove(self.request_continuous_move)

        # Wait a certain time
        sleep(timeout)

        # Stop continuous move
        self.stop()

        sleep(2)
        print(str(self.request_continuous_move))

    def move_continuous(self, velocity1, velocity2, velocity3, timeout=1):
        print ('move continuous...')
        self.request_continuous_move.Velocity.PanTilt._x = velocity1
        self.request_continuous_move.Velocity.PanTilt._y = velocity2
        self.request_continuous_move.Velocity.Zoom._x = velocity3
        self.request_continuous_move.Timeout = timeout

        self.perform_continuous_move(timeout)

    def perform_absolute_move(self, x, y, z):
        print ('move absolute...')
        self.request_absolute_move.Position.PanTilt._x = x
        self.request_absolute_move.Position.PanTilt._y = y
        self.request_absolute_move.Position.Zoom._x = z

        self.stop()

        self.ptz.AbsoluteMove(self.request_absolute_move)

        print(str(self.request_absolute_move))

    def change_absolute_focus(self, x):
        print('changing focus: ' + str(x))

        self.request_absolute_focus.Focus = x
        
        self.imaging.Move(self.request_absolute_focus)

        print(str(self.request_absolute_focus))


