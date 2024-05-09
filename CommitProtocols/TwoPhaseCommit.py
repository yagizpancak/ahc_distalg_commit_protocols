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

import networkx
from adhoccomputing.GenericModel import GenericModel
from adhoccomputing.Generics import Event

logger = getLogger("AHC")

class TwoPhaseCoordinatorEventTypes(Enum):
    """
        Enumeration of different event types for the coordinator
    """
    VOTE_ABORT = "VOTE_ABORT"
    VOTE_COMMIT = "VOTE_COMMIT"
    COMMIT = "COMMIT"

class TwoPhaseParticipantEventTypes(Enum):
    """
        Enumeration of different event types for the participant
    """
    VOTE_REQUEST = "VOTE_REQUEST"
    ABORT = "ABORT"
    COMMIT = "COMMIT"

class TwoPhaseLocalCommitEventTypes(Enum):
    """
        Enumeration of participant local commit decision
    """
    COMMIT = "COMMIT"
    ABORT = "ABORT"

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
        self.eventhandlers[TwoPhaseCoordinatorEventTypes.VOTE_COMMIT] = self.on_vote_commit
        self.eventhandlers[TwoPhaseCoordinatorEventTypes.VOTE_ABORT] = self.on_vote_abort

    def on_commit(self):
        """
            Handler for COMMIT event
            Sends VOTE_REQUEST to all participants.
        """
        self.number_of_participants = len(self.connectors)
        self.commit_count = 0
        self.send_down(Event(self, TwoPhaseParticipantEventTypes.VOTE_REQUEST, TwoPhaseLocalCommitEventTypes.ABORT))

    def on_vote_commit(self, eventobj: Event):
        """
            Handler for VOTE_COMMIT event.
            Increments commit count and checks if all participants have voted commit.
            If so, sends COMMIT to all participants.
        """
        self.commit_count += 1
        if self.commit_count == self.number_of_participants:
            self.send_down(Event(self, TwoPhaseParticipantEventTypes.COMMIT, None))

    def on_vote_abort(self, eventobj: Event):
        """
            Handler for VOTE_ABORT event.
            Sends ABORT to all participants.
        """
        self.send_down(Event(self, TwoPhaseParticipantEventTypes.ABORT, None))


class TwoPhaseCommitParticipant(GenericModel):
    """
        Class for the two-phase commit participant.
    """
    def __init__(self, componentname, componentinstancenumber, context=None, configurationparameters=None, num_worker_threads=1, topology=None):
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

        self.eventhandlers[TwoPhaseParticipantEventTypes.VOTE_REQUEST] = self.on_vote_request
        self.eventhandlers[TwoPhaseParticipantEventTypes.COMMIT] = self.on_commit
        self.eventhandlers[TwoPhaseParticipantEventTypes.ABORT] = self.on_abort

    def on_vote_request(self, eventobj: Event):
        """
            Handler for VOTE_REQUEST event.
            Depending on local event type, sends VOTE_COMMIT or VOTE_ABORT to coordinator.

            Parameters
            ----------
            local_event : TwoPhaseParticipantEventTypes
                Local commit event type
        """
        if eventobj.eventcontent == TwoPhaseLocalCommitEventTypes.COMMIT:
            self.send_up(Event(self, TwoPhaseCoordinatorEventTypes.VOTE_COMMIT, None))
        elif eventobj.eventcontent == TwoPhaseLocalCommitEventTypes.ABORT:
            self.send_up(Event(self, TwoPhaseCoordinatorEventTypes.VOTE_ABORT, None))


    def on_commit(self, eventobj: Event):
        """
            Handler for COMMIT event. Logs that the participant has committed.
        """
        print(f"NAME:{self.componentname} COMPID: {self.componentinstancenumber} COMMITTED")

    def on_abort(self, eventobj: Event):
        """
            Handler for ABORT event. Logs that the participant has aborted.
        """
        print(f"NAME:{self.componentname} COMPID: {self.componentinstancenumber} ABORTED")


networkx.graph_atlas(10)
