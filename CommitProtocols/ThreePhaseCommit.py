"""
    Implementation of the Three Phase Commit Protocol.
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
from adhoccomputing.Generics import Event

logger = getLogger("AHC")

class ThreePhaseCoordinatorEventTypes(Enum):
    """
        Enumeration of different event types for the coordinator
    """
    VOTE_ABORT = "VOTE_ABORT"
    VOTE_COMMIT = "VOTE_COMMIT"
    READY_COMMIT = "READY_COMMIT"
    COMMIT = "COMMIT"

class ThreePhaseParticipantEventTypes(Enum):
    """
        Enumeration of different event types for the participant
    """
    VOTE_REQUEST = "VOTE_REQUEST"
    ABORT = "ABORT"
    PREPARE_COMMIT = "PREPARE_COMMIT"
    COMMIT = "COMMIT"

class ThreePhaseLocalCommitEventTypes(Enum):
    """
        Enumeration of participant local commit decision
    """
    COMMIT = "COMMIT"
    ABORT = "ABORT"

class ThreePhaseCommitCoordinator(GenericModel):
    """
        Class for the three-phase commit coordinator.
    """
    def __init__(self, componentname, componentinstancenumber, context=None, configurationparameters=None, num_worker_threads=1, topology=None):
        """
            Initialize the three-phase commit coordinator and set up event handlers.

            Parameters
            ----------
            componentname :str
                Component name
            componentinstancenumber :int
                Component instance number

        """
        super().__init__(componentname, componentinstancenumber, context, configurationparameters, num_worker_threads, topology)

        self.number_of_participants = len(super().connectors)
        self.commit_count = 0
        self.ready_count = 0
        self.eventhandlers[ThreePhaseCoordinatorEventTypes.COMMIT] = self.on_commit
        self.eventhandlers[ThreePhaseCoordinatorEventTypes.VOTE_COMMIT] = self.on_vote_commit
        self.eventhandlers[ThreePhaseCoordinatorEventTypes.READY_COMMIT] = self.on_ready_commit
        self.eventhandlers[ThreePhaseCoordinatorEventTypes.VOTE_ABORT] = self.on_vote_abort

    def on_commit(self):
        """
            Handler for COMMIT event
            Sends VOTE_REQUEST to all participants.
        """
        self.number_of_participants = len(super().connectors)
        self.commit_count = 0
        self.send_down(Event(self, ThreePhaseParticipantEventTypes.VOTE_REQUEST))

    def on_vote_commit(self):
        """
            Handler for VOTE_COMMIT event.
            Increments commit count and checks if all participants have voted commit.
            If so, sends COMMIT to all participants.
        """
        self.commit_count += 1
        if self.commit_count == self.number_of_participants:
            self.send_down(Event(self, ThreePhaseParticipantEventTypes.PREPARE_COMMIT))

    def on_ready_commit(self):
        """
            Handler for READY_COMMIT event.
            Increments ready count and checks if all participants are ready.
            If so, sends COMMIT to all participants.
        """
        self.ready_count += 1
        if self.ready_count == self.number_of_participants:
            self.send_down(Event(self, ThreePhaseParticipantEventTypes.COMMIT))

    def on_vote_abort(self):
        """
            Handler for VOTE_ABORT event.
            Sends ABORT to all participants.
        """
        self.send_down(Event(self, ThreePhaseParticipantEventTypes.ABORT))


class ThreePhaseCommitParticipant(GenericModel):
    """
        Class for the three-phase commit participant.
    """
    def __init__(self, componentname, componentinstancenumber, context=None, configurationparameters=None, num_worker_threads=1, topology=None):
        """
            Initialize the three-phase commit participant and set up event handlers.

            Parameters
            ----------
            componentname :str
                Component name
            componentinstancenumber :int
                Component instance number

        """
        super().__init__(componentname, componentinstancenumber, context, configurationparameters, num_worker_threads, topology)

        self.eventhandlers[ThreePhaseParticipantEventTypes.VOTE_REQUEST] = self.on_vote_request
        self.eventhandlers[ThreePhaseParticipantEventTypes.COMMIT] = self.on_commit
        self.eventhandlers[ThreePhaseParticipantEventTypes.PREPARE_COMMIT] = self.on_prepare_commit
        self.eventhandlers[ThreePhaseParticipantEventTypes.ABORT] = self.on_abort

    def on_vote_request(self, local_event):
        """
            Handler for VOTE_REQUEST event.
            Depending on local event type, sends VOTE_COMMIT or VOTE_ABORT to coordinator.

            Parameters
            ----------
            local_event : ThreePhaseParticipantEventTypes
                Local commit event type
        """
        if local_event == ThreePhaseLocalCommitEventTypes.COMMIT:
            self.send_up(Event(self, ThreePhaseCoordinatorEventTypes.VOTE_COMMIT))
        elif local_event == ThreePhaseLocalCommitEventTypes.ABORT:
            self.send_up(Event(self, ThreePhaseCoordinatorEventTypes.VOTE_ABORT))

    def on_prepare_commit(self, is_ready: bool = True):
        """
            Handler for PREPARE_COMMIT event.
            If is_ready is True, sends READY_COMMIT to coordinator.

            Parameters
            ----------
            is_ready : bool
                Flag indicating if participant is ready.
        """
        if is_ready:
            self.send_up(Event(self, ThreePhaseCoordinatorEventTypes.READY_COMMIT))

    def on_commit(self):
        """
            Handler for COMMIT event. Logs that the participant has committed.
        """
        logger.debug(f"NAME:{self.componentname} COMPID: {self.componentinstancenumber} COMMITTED")

    def on_abort(self):
        """
            Handler for ABORT event. Logs that the participant has aborted.
        """
        logger.debug(f"NAME:{self.componentname} COMPID: {self.componentinstancenumber} ABORTED")