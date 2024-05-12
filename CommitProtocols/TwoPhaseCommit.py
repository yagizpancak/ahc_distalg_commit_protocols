"""
    Implementation of the Two Phase Commit Protocol.
"""

__author__ = "Yağızcan Pançak"
__contact__ = "yagizcan.pancak@metu.edu.tr"
__copyright__ = "Copyright 2024, WINSLAB"
__credits__ = ["Yağızcan Pançak"]
__date__ = "2024/04/15"
__deprecated__ = False
__email__ = "yagizcan.pancak@metu.edu.tr"
__license__ = "GPLv3"
__maintainer__ = "developer"
__status__ = "Production"
__version__ = "0.0.1"

from enum import Enum
from logging import getLogger

from adhoccomputing.GenericModel import GenericModel
from adhoccomputing.Generics import Event, ConnectorTypes

logger = getLogger("AHC")

class TwoPhaseCoordinatorEventTypes(Enum):
    """
        Enumeration of different event types for the coordinator
    """
    VOTE_RESPONSE = "VOTE_RESPONSE"
    COMMIT = "COMMIT"

class TwoPhaseParticipantEventTypes(Enum):
    """
        Enumeration of different event types for the participant
    """
    VOTE_REQUEST = "VOTE_REQUEST"
    GLOBAL_ABORT = "GLOBAL_ABORT"
    GLOBAL_COMMIT = "GLOBAL_COMMIT"

class TwoPhaseLocalCommitEventTypes(Enum):
    """
        Enumeration of participant local commit decision
    """
    LOCAL_COMMIT = "LOCAL_COMMIT"
    LOCAL_ABORT = "LOCAL_ABORT"

class TwoPhaseCommitCoordinator(GenericModel):
    """
        Class for the two-phase commit coordinator.
    """
    def __init__(self, componentname, componentinstancenumber, context=None, configurationparameters=None, num_worker_threads=1, topology=None):
        """
            Initialize the two-phase commit coordinator and set up event handlers.

            Parameters
            ----------
            componentname :str
                Component name
            componentinstancenumber :int
                Component instance number
        """
        super().__init__(componentname, componentinstancenumber, context, configurationparameters, num_worker_threads, topology)

        self.commit_count = 0
        self.eventhandlers[TwoPhaseCoordinatorEventTypes.COMMIT] = self.on_commit
        self.eventhandlers[TwoPhaseCoordinatorEventTypes.VOTE_RESPONSE] = self.on_vote_response

    def on_commit(self):
        """
            Handler for COMMIT event
            Sends VOTE_REQUEST to all participants.
        """
        self.number_of_participants = len(self.connectors[ConnectorTypes.DOWN])
        self.commit_count = 0
        self.send_down(Event(self, TwoPhaseParticipantEventTypes.VOTE_REQUEST, None))
        logger.info(f"NAME:{self.componentname} SEND VOTE REQUEST")


    def on_vote_response(self, eventobj: Event):
        """
            Handler for VOTE_RESPONSE event.
            Increments commit count and checks if all participants have voted commit.
            If so, sends COMMIT to all participants.
            If one participant have voted send ABORT to all participants.
        """
        self.commit_count += 1
        if eventobj.eventcontent == TwoPhaseLocalCommitEventTypes.LOCAL_ABORT:
            self.commit_count = 0
            self.send_down(Event(self, TwoPhaseParticipantEventTypes.GLOBAL_ABORT, None))
            logger.info(f"NAME:{self.componentname} ABORT RECEIVED, ABORTING")

        if self.commit_count == self.number_of_participants:
            self.send_down(Event(self, TwoPhaseParticipantEventTypes.GLOBAL_COMMIT, None))
            logger.info(f"NAME:{self.componentname} ALL VOTES COMMIT, COMMITTING")



class TwoPhaseCommitParticipant(GenericModel):
    """
        Class for the two-phase commit participant.
    """
    def __init__(self, componentname, componentinstancenumber, local_commit=TwoPhaseLocalCommitEventTypes.LOCAL_COMMIT, context=None, configurationparameters=None, num_worker_threads=1, topology=None):
        """
            Initialize the two-phase commit participant and set up event handlers.

            Parameters
            ----------
            componentname :str
                Component name
            componentinstancenumber :int
                Component instance number

        """
        super().__init__(componentname, componentinstancenumber, context, configurationparameters, num_worker_threads, topology)
        self.local_commit = local_commit

        self.eventhandlers[TwoPhaseParticipantEventTypes.VOTE_REQUEST] = self.on_vote_request
        self.eventhandlers[TwoPhaseParticipantEventTypes.GLOBAL_COMMIT] = self.on_commit
        self.eventhandlers[TwoPhaseParticipantEventTypes.GLOBAL_ABORT] = self.on_abort

    def on_vote_request(self, eventobj: Event):
        """
            Handler for VOTE_REQUEST event.
            Depending on local event type, sends VOTE_COMMIT or VOTE_ABORT to coordinator.
        """
        if self.local_commit == TwoPhaseLocalCommitEventTypes.LOCAL_COMMIT:
            self.send_up(Event(self, TwoPhaseCoordinatorEventTypes.VOTE_RESPONSE,
                               TwoPhaseLocalCommitEventTypes.LOCAL_COMMIT))
            logger.info(f"NAME:{self.componentname} SEND COMMIT VOTE")

        elif self.local_commit == TwoPhaseLocalCommitEventTypes.LOCAL_ABORT:
            self.send_up(Event(self, TwoPhaseCoordinatorEventTypes.VOTE_RESPONSE,
                               TwoPhaseLocalCommitEventTypes.LOCAL_ABORT))
            logger.info(f"NAME:{self.componentname} SEND ABORT VOTE")


    def on_commit(self, eventobj: Event):
        """
            Handler for COMMIT event. Logs that the participant has committed.
        """
        logger.info(f"NAME:{self.componentname} COMMITTED")

    def on_abort(self, eventobj: Event):
        """
            Handler for ABORT event. Logs that the participant has aborted.
        """
        logger.info(f"NAME:{self.componentname} ABORTED")
