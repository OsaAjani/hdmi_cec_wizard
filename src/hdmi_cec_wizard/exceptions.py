class FollowerStoppedException (Exception) :
    """
        This exception is raised when the cec-follower program stopped
        its up to the user to decide if he must reload it with HDMICECWizard.start_follower(),
        ignore it, or stop the all program.

        You can access the process info in process_result
    """
    def __init__(self, message, process_result):            
        # Call the base class constructor with the parameters it needs
        super().__init__(message)
            
        self.process_result = process_result
    pass


class ResponseTimeoutException (Exception) :
    """
        This exception is raised when a command issued by cec-ctl have received a Timeout response
    """
    pass