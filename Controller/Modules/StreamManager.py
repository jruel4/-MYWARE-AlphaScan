'''

LSL Spec

This module is used for "recording" lsl streams. That means that user will pick
a stream, and module will have to buffer it it memory unti writing to a db.

Aside from that, just need to make sure my use of the MongoDB module is good.

Ok, so multiple streams will need to be tracked at once. The simplest way to do
this is to have a streams object that encapsulates state-specific activities
e.g. buffering, converting, etc.

'''
from pylsl import StreamInlet, resolve_stream

class StreamManager:
    
    def __init__(self):
        self.filename = None
        self.overwrite = False
        
    
    # select_streams
    def select_streams(self, uids=None):
        '''
        Function:
            If UIDs are passed in then quietly accept them.
            
            If no UIDs, output to console following info for all available streams:
                idx
                stream name
                stream type
                stream id
                stream uid
            Allow user to input stream idx's (seperated by commas) which to save to file.
            
            NOTE: If user inputs -1, please exit gracefully (assume the user changed their mind)
        
        Args:
            (O) uids: list of unicode strings corresponding to UIDs of streams which to include in saving
        
        Returns:
            success: int,
                1 if successful
                0 if gracefully exiting
                -1 if error
        '''
        
        if uids:
            # make sure all uids are actuall available
            pass
        else:
            # get available streams
            streams = resolve_stream()
            for n,s in enumerate(streams):
                print("index: ",n, s.name(), s.type(), s.source_id(), s.uid())
            uids = input("Please input desired stream indexes as comma separated list")
            
            if uids == -1:
                return 0
            
        # set local streams object
        self.selected_streams = {streams[i].uid():Stream(streams[i]) for i in uids}
        
        return 1

    ###
    # Saving streams
    ###
    
    # begin_saving
    def begin_saving(self, filename, metadata=None, overwrite=False):
        '''
        Function:
            Begins saving to file
        Args:
            fname: filename string for MongoDB
            (O) metadata: md, metadata structure, output from "create_metadata(...)"
            (O) overwrite: bool, whether or not to overwrite if a file already exists
        Return
        '''
        self.filename = filename
        self.overwrite = overwrite
        self.metadata = metadata
        # begin saving all streams
        for s in self.selected_streams:
            s.begin()

    # pause_saving
    def pause_saving(self):
        '''
        Function:
            Temporarily pauses the saving of data - stream may be
            resumed using "resume_saving"
        Args:
            None
        Returns:
            success: int,
                1 if successful,
                0 if already paused,
                -1 if no saving stream active
                -2 if error in pausing stream
        '''
        for s in self.selected_streams:
            s.pause()

    # resume_saving
    def resume_saving(self):
        '''
        Function:
            Resumes saving the data. Should only be called after 
        Args:
            None
        Returns:
            success: int,
                1 if successful,
                0 if already running,
                -1 if no saving stream active
                -2 if error in resuming stream
        '''
        for s in self.selected_streams:
            s.resume()

    # stop_saving
    def stop_saving(self):
        '''
        Function:
            Stops saving data; cleans up and finishes writing to MongoDB
        Args:
            None
        Returns:
            success: int,
                1 if successful,
                0 if no stream currently running,
                -1 if error stopping stream
        '''
        for s in self.selected_streams:
            s.stop()
            
        #TODO write to MongoDB
    
    ###
    # Metadata
    ###
    
    
    # create_metadata
    def create_metadata(self,user,proctor,ch_names, recording_desc,marker_desc,other_metadata):
        '''
        Function:
            Add metadata which is saved with the stream data
        Args:
            user: str, person recording is performed on
            proctor: str, person proctoring recording
            ch_names: list of str, contains all channel names
            recording_desc: str, description of recording
            marker_desc: dict, keys represent events, values are descriptions
            other_metadata: dict, keys represent metadata keys and values represent values (for MongoDB)
        Returns:
            metadata: md, metadata structure
        '''
        return {'user':user,
                'proctor':proctor,
                'ch_names':ch_names,
                'recording_desc':recording_desc,
                'marker_desc':marker_desc,
                'other_metadata':other_metadata}
    
    
    # map_marker_streams
    def map_marker_streams(self, key_events, marker_stream_uid):
        '''
        Function:
            Sets up mapping from LSL marker streams (ex. keycorder) to actual meaningful
            event labels (which are saved in the file)
        Args:
            keys_events: dict, keys correspond to LSL keyrecorder outputs (see [1]), values are the actual event labels
            marker_stream_uid: string, must be currently held in self.selected_streams
        Returns:
            None
            
        Ex:
        k_v = {
            "0 pressed" : "BAD", "NUMPAD0 pressed" : "BAD",
            "1 pressed" : "GOOD", "NUMPAD1 pressed" : "GOOD"
            }
        map_keys_to_labels(k_v)
        
        [1] LSL keyboard events: https://github.com/sccn/labstreaminglayer/wiki/Keyboard.wiki
        '''
        self.selected_streams[marker_stream_uid].set_type_marker(key_events)
    
    ###
    # Loading data
    ###
    
    
    # load_current_data
    def load_current_data(self):
        '''
        Function:
            Load data from the currently running session. Local buffers should be used for
            smaller amounts of data, this should only be used when loading large amounts of data
            and time is not a concern. For example, this may be used by a plotting function to
            plot beta power over the past 20 minutes.
            
            Beginning and end positions must be specific. A stream UID may be specified to retrieve a specific
            stream, otherwise returns all streams (including markers)
        
        Args:
            beg: None, int, float,
                If None, start at the beginning of the session
                If int (negative), start at "beg" samples back from current samples
                If int (positive), start at "beg" samples from the beginning
                If float (negative), start at "beg" seconds back from current time
                If float (positive), start at "beg" seconds from the beginning
                If 0 or 0.0, error (None should be used to indicate the beginning, not zero)
            end: None, int, float,
                If None, finish at the end of the session
                Otherwise the same as begin, except choosing where to end
            (O) stream_uid: unicode str, UID of the stream to retrieve
        
        Returns:
            data: dict,
                Keys are the UIDs of the data streams. Data is a numpy array in the
                format [nchan, nsamples], where the are the earliest samples.
                (Ex. [0,0] is the first samples recorded from channel 0, [0,1] is the second, etc...)
            data_ts: dict,
                Keys are the UIDs of the data streams.
            markers:
                Keys are the UIDs of the marker streams.
            markers_ts:
                Keys are the UIDs of the marker streams.
        
        '''
        pass
    
class Stream:
    '''
    Possible stream states:
        
        - PAUSED
        - SAVING
        
    Possible stream types:
        
        - REGULAR
        - MARKER
    '''

    def __init__(self, lsl_stream):
        self.inlet = StreamInlet(lsl_stream)
        self.state = 'PAUSED'
        self.type = 'REGULAR'
        
    def begin(self):
        pass
    
    def pause(self):
        pass
    
    def resume(self):
        pass
    
    def stop(self):
        pass
    
    def set_type_marker(self, mapping):
        self.type = 'MARKER'
        self.mapping = mapping
    
    
    
    
    
    
    
    

    
    
    
    