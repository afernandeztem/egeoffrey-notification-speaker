### play a notification out loud through an attached speaker
## HOW IT WORKS: 
## DEPENDENCIES:
# OS: mpg123
# Python: 
## CONFIGURATION:
# required: device, engine (picotts|google)
# optional: 
## COMMUNICATION:
# INBOUND: 
# - NOTIFY: receive a notification request
# OUTBOUND: 

from sdk.python.module.notification import Notification

import sdk.python.utils.command
import sdk.python.utils.exceptions as exception

class Speaker(Notification):
    # What to do when initializing
    def on_init(self):
        # configuration settings
        self.house = {}
        # require configuration before starting up
        self.config_schema = 1
        self.add_configuration_listener("house", 1, True)
        self.add_configuration_listener(self.fullname, "+", True)

    # What to do when running
    def on_start(self):
        pass
        
    # What to do when shutting down
    def on_stop(self):
        pass
        
    # play an audio file
    def play(self, filename):
        device = "-t alsa "+str(self.config["device"]) if self.config["device"] is not None else ""
        self.log_debug(sdk.python.utils.command.run("play "+filename+" "+device, background=False))

   # What to do when ask to notify
    def on_notify(self, severity, text):
        # TODO: queue if already playing something
        self.log_debug("Saying: "+text)
        output_file = "/tmp/audio_output.wav"
        # use the picotts engine
        if self.config["engine"] == "picotts": 
            # create the wav file
            self.log_debug(sdk.python.utils.command.run(["pico2wave", "-l", self.house["language"], "-w", output_file, text], shell=False))
            # play it
            self.play(output_file)
        # use the google API
        elif self.config["engine"] == "google": 
            # create the wav file
            self.log_debug(sdk.python.utils.command.run(["gtts-cli", "-l", self.house["language"], "-o", output_file+".mp3", text], shell=False))
            self.log_debug(sdk.python.utils.command.run(["mpg123", "-w", output_file, output_file+".mp3"], shell=False))
            # play it
            self.play(output_file)

     # What to do when receiving a new/updated configuration for this module    
    def on_configuration(self, message):
        if message.args == "house" and not message.is_null:
            if not self.is_valid_configuration(["language"], message.get_data()): return False
            self.house = message.get_data()
        # module's configuration
        if message.args == self.fullname and not message.is_null:
            if message.config_schema != self.config_schema: 
                return False
            if not self.is_valid_configuration(["engine"], message.get_data()): return False
            self.config = message.get_data()