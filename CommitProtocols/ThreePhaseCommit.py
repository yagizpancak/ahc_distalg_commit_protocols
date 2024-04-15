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
    VOTE_ABORT = "VOTE_ABORT"
    VOTE_COMMIT = "VOTE_COMMIT"
    READY_COMMIT = "READY_COMMIT"
    COMMIT = "COMMIT"

class ThreePhaseParticipantEventTypes(Enum):
    VOTE_REQUEST = "VOTE_REQUEST"
    ABORT = "ABORT"
    PREPARE_COMMIT = "PREPARE_COMMIT"
    COMMIT = "COMMIT"

class ThreePhaseLocalCommitEventTypes(Enum):
    COMMIT = "COMMIT"
    ABORT = "ABORT"

class ThreePhaseCommitCoordinator(GenericModel):
    def __init__(self, componentname, componentinstancenumber, context=None, configurationparameters=None, num_worker_threads=1, topology=None):
        super().__init__(componentname, componentinstancenumber, context, configurationparameters, num_worker_threads, topology)

        self.number_of_participants = len(super().connectors)
        self.commit_count = 0
        self.ready_count = 0
        self.eventhandlers[ThreePhaseCoordinatorEventTypes.COMMIT] = self.on_commit
        self.eventhandlers[ThreePhaseCoordinatorEventTypes.VOTE_COMMIT] = self.on_vote_commit
        self.eventhandlers[ThreePhaseCoordinatorEventTypes.READY_COMMIT] = self.on_ready_commit
        self.eventhandlers[ThreePhaseCoordinatorEventTypes.VOTE_ABORT] = self.on_vote_abort

    def on_commit(self):
        self.number_of_participants = len(super().connectors)
        self.commit_count = 0
        self.send_down(Event(self, ThreePhaseParticipantEventTypes.VOTE_REQUEST))

    def on_vote_commit(self):
        self.commit_count += 1
        if self.commit_count == self.number_of_participants:
            self.send_down(Event(self, ThreePhaseParticipantEventTypes.PREPARE_COMMIT))

    def on_ready_commit(self):
        self.ready_count += 1
        if self.ready_count == self.number_of_participants:
            self.send_down(Event(self, ThreePhaseParticipantEventTypes.COMMIT))

    def on_vote_abort(self):
        self.send_down(Event(self, ThreePhaseParticipantEventTypes.ABORT))


class ThreePhaseCommitParticipant(GenericModel):
    def __init__(self, componentname, componentinstancenumber, context=None, configurationparameters=None, num_worker_threads=1, topology=None):
        super().__init__(componentname, componentinstancenumber, context, configurationparameters, num_worker_threads, topology)

        self.eventhandlers[ThreePhaseParticipantEventTypes.VOTE_REQUEST] = self.on_vote_request
        self.eventhandlers[ThreePhaseParticipantEventTypes.COMMIT] = self.on_commit
        self.eventhandlers[ThreePhaseParticipantEventTypes.PREPARE_COMMIT] = self.on_prepare_commit
        self.eventhandlers[ThreePhaseParticipantEventTypes.ABORT] = self.on_abort

    def on_vote_request(self, local_event):
        if local_event == ThreePhaseLocalCommitEventTypes.COMMIT:
            self.send_up(Event(self, ThreePhaseCoordinatorEventTypes.VOTE_COMMIT))
        elif local_event == ThreePhaseLocalCommitEventTypes.ABORT:
            self.send_up(Event(self, ThreePhaseCoordinatorEventTypes.VOTE_ABORT))

    def on_prepare_commit(self, is_ready: bool = True):
        if is_ready:
            self.send_up(Event(self, ThreePhaseCoordinatorEventTypes.READY_COMMIT))

    def on_commit(self):
        logger.debug(f"NAME:{self.componentname} COMPID: {self.componentinstancenumber} COMMITTED")

    def on_abort(self):
        logger.debug(f"NAME:{self.componentname} COMPID: {self.componentinstancenumber} ABORTED")